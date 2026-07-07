# ECDA Preschool Demand Forecasting at Subzone Level

## Question

> There is concern over mismatch of demand and supply for preschools... ECDA has asked your team to forecast the subzone-level demand for preschool services, in particular those providing childcare (18 months to 6 years) programmes, over the next 5 years, to determine where they should prioritise building/relocating preschools. Assume each preschool can accommodate up to 100 children. In addition, ECDA staff want a tool they can use to make subsequent decisions on a regular basis.

## Files

- `ECDA_Preschool_Demand_Forecasting_Final.ipynb`: full analysis notebook.
- `data/`: input files (population census 2000-2025, BTO mapping, births/fertility, ECDA centre listing, URA subzone boundaries).
- `outputs/`: all generated tables, the geocode cache, and the Streamlit prototype.

## How to run

1. Create a virtual environment and install dependencies:
   ```bash
   pip install pandas numpy scikit-learn openpyxl xgboost prophet geopandas shapely pyogrio requests jupyter
   ```
2. Place the input files in `data/` (already done in this folder).
3. Open `ECDA_Preschool_Demand_Forecasting_Final.ipynb` and run all cells.
4. Outputs are written to `outputs/`.

Note: Step 12 (mapping ECDA centres to subzones) geocodes each unique postal
code against the live OneMap API. Results are cached in
`outputs/centre_geocode_cache.csv`, so only the first run is slow (roughly
10-15 minutes for ~1,700 postal codes); later runs only geocode codes that are
new or previously failed. This step requires internet access.

## Method summary

1. **Demand definition** — population data is by single year of age, so
   demand for children aged 18 months-6 years is approximated as
   `0.5 x Age 1 + Age 2 + Age 3 + Age 4 + Age 5 + Age 6` (half of the age-1
   cohort, since roughly the second half of that year is 18-24 months).
2. **Historical panel** — population census editions from 2000-2025 are
   cleaned, concatenated, and aggregated into a subzone x year demand panel.
   Subzone names that don't exist in the most recent census (i.e. subzones
   that were renamed/merged/dissolved between Master Plan editions) are
   dropped — see "Data quality notes" below.
3. **Forward-looking features** — BTO project completions (lagged 1-3 years,
   converted to an assumed child count via `BTO_CHILD_FACTOR = 0.12`) and
   national birth/fertility rates are added as features.
4. **Three forecasting models** — Linear Regression, Prophet, and XGBoost are
   backtested on 2021-2025 with a proper walk-forward split (retrained per
   test year using only prior data). The model with the lowest RMSE
   (XGBoost) is selected for the final 2026-2030 forecast.
5. **Supply estimation** — the ECDA centre listing is geocoded (postal code →
   lat/lon via OneMap) and spatially joined to URA subzone polygons. Each
   centre is assumed to hold 100 children (per the problem statement).
   Three supply scenarios test sensitivity to how `KN` (kindergarten) and
   `NA` (unlabelled service model) centres are treated.
6. **Gap and priority ranking** — for each subzone, `shortfall = forecast
   demand - estimated capacity`, `additional centres needed = ceil(shortfall
   / 100)`. Subzones are ranked by additional centres needed, then shortfall
   size, then BTO-driven demand pressure.
7. **Tool prototype** — a Streamlit app (`outputs/streamlit_app.py`) reads
   the generated CSVs and lets ECDA staff browse the priority ranking and
   supply-scenario sensitivity by year.

## Headline results (this run)

| Year | Forecast demand (children) | Estimated capacity | Shortfall | Additional centres needed | Subzones with shortfall |
|---|---|---|---|---|---|
| 2026 | 192,925 | 171,700 | 48,388 | 538 | 116 / 332 |
| 2030 | 179,140 | 171,700 | 42,281 | 476 | 102 / 332 |

Best backtest model: **XGBoost** (RMSE ≈ 621, vs. 867 for Linear and 988 for
Prophet, on 1,660 held-out subzone-year predictions from 2021-2025).

Top priority subzones for 2026 include Tampines North, Punggol Matilda,
Yishun East, Bukit Batok Brickworks, and Sengkang Fernvale — see
`outputs/top_priority_subzones.csv` for the full ranked list per year, and
`outputs/scenario_summary.csv` for how the gap changes under the
`strict_childcare` / `base_preschool` / `broad_all` supply assumptions.

## Data quality notes

A few data-quality issues turned out to matter enough for the numbers that
they're worth calling out explicitly rather than leaving as implicit code:

1. **Subzone boundaries change across census editions.** The population
   panel is stitched together from several census editions (2000-2020 Excel
   sheets, then separate 2021-2025 CSVs), and Singapore's subzone boundaries
   get revised periodically. Some subzone names only present in the older
   sheets (e.g. "Sengkang - Sungei Serangoon West") don't exist in the
   current census at all. Left unfiltered, these deprecated subzones still
   get forecasted from decade-old data and can dominate the output — in an
   early pass, 13 of the top 20 "priority" subzones for 2026 turned out to
   be names that no longer exist, some with a fabricated demand of several
   thousand children and zero real-world supply to compare against. The
   notebook now drops any subzone not present in the latest census year
   before forecasting (see the markdown note in the demand-construction
   cell).
2. **Rolling-window features need to respect subzone boundaries.** Lag and
   rolling-mean features are built with
   `grp["col"].transform(lambda s: s.shift(1).rolling(window).mean())` so
   each subzone's window only ever sees its own history. A naive
   `shift().rolling()` chained directly off the groupby object silently
   drops back to a global (ungrouped) window and mixes different subzones
   together near their boundaries — worth watching for if this pipeline
   gets extended.
3. **OneMap rate-limits aggressively** (HTTP 429 after roughly 8 rapid
   requests), so the geocoding step uses retry + exponential backoff, and
   the cache only remembers postal codes that resolved successfully -
   otherwise a rate-limited run permanently understates supply for every
   centre it failed to place, since a bad cache entry would never get
   retried.

## Other things worth knowing (not fixed, by design or for time reasons)

- **`BTO_CHILD_FACTOR = 0.12` and the 3-year lag split are unvalidated
  assumptions**, not derived from data. Worth a sensitivity check before
  this number is quoted externally.
- **Priority score weights (`additional_centres_needed * 1000 +
  shortfall_children + bto_demand_addition * 2`) are arbitrary.** They
  produce a reasonable-looking ranking here but aren't derived or
  sensitivity-tested — treat the ranking as directionally right, not
  precise.
- **A single best model (by aggregate RMSE) is applied to every subzone.**
  Some subzones may forecast better with a different model; per-subzone
  model selection would be a natural next iteration.
- **Brand-new subzones with an upcoming BTO but no population history yet**
  (e.g. land not yet built out) still won't appear in the forecast, since
  the forecast loop only iterates over subzones with historical demand
  rows. For the tool's stated goal of factoring in "upcoming BTO sites",
  this is a real gap worth flagging to ECDA — greenfield sites need a
  separate demand-seeding rule (e.g. a standard occupancy curve applied to
  BTO unit counts alone).
- **Centres that fail the postal→subzone spatial join** (e.g. point falls
  just outside a polygon boundary) are silently excluded from supply. The
  notebook prints `mapped_rate` so this is visible, but it's not corrected
  for.

## Deployment sketch for the recurring tool

- Package the notebook's steps 1-16 as a scheduled pipeline (e.g. a script
  run monthly/quarterly when ECDA refreshes population stats, centre
  listings, or BTO plans), writing to the same `outputs/` CSVs.
- The Streamlit app (`outputs/streamlit_app.py`) is a thin read-only layer
  over those CSVs — run it with:
  ```bash
  cd outputs
  streamlit run streamlit_app.py
  ```
  For a persistent internal tool, the pipeline would run on a schedule
  (e.g. Airflow/cron) and the Streamlit app would point at whichever storage
  (S3/GCS bucket, internal DB) the pipeline writes to, rather than local CSVs.
