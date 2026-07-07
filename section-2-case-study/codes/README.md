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
   dropped — see "Bugs found and fixed" below.
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

## Bugs found and fixed while running this notebook

The notebook was written assuming a different environment (`/mnt/data`,
uploaded files with `(1)`/`(2)` suffixes) and had three issues that were
silently producing wrong numbers rather than raising errors:

1. **Paths didn't match this machine.** `FILE_DIR = Path("/mnt/data")` and
   filenames like `respopagesex2000to2020e(1).xlsx` don't exist locally —
   fixed to `Path("data")` with the actual filenames.
2. **Incorrect rolling-window feature (real logic bug, not just a path
   issue).** The lag/rolling feature cell did
   `grp["col"].shift(1).rolling(3).mean().reset_index(level=[0,1], drop=True)`.
   `shift(1)` on a groupby object returns a plain (ungrouped) Series, so the
   subsequent `.rolling(3)` computed a window that crossed subzone
   boundaries instead of respecting them — and on this pandas version it
   also crashed outright (`IndexError: Too many levels`). Fixed to
   `grp["col"].transform(lambda s: s.shift(1).rolling(3).mean())`, which is
   the pattern correctly used elsewhere in the sibling Q2 notebook.
3. **Stale/deprecated subzones contaminated the priority ranking.** The
   population panel spans several census editions (2000-2020 Excel sheets,
   then separate 2021-2025 CSVs); Singapore's subzone boundaries are
   periodically revised, so some subzone names only present in the older
   sheets (e.g. "Sengkang - Sungei Serangoon West") don't exist in the
   current census at all. Left unfiltered, these deprecated subzones still
   got forecasted from their old, decade-stale data and dominated the
   output: **13 of the top 20 "priority" subzones for 2026 were names that
   no longer exist**, several with a fabricated demand of several thousand
   children and zero real-world supply to compare against. Fixed by
   dropping any subzone not present in the latest census year before
   forecasting (see the markdown note in the notebook's demand-construction
   cell for detail).
4. **Geocoding failed silently under load (found during the fix, not in the
   original code review — introduced and then fixed within this session).**
   OneMap starts returning HTTP 429 after roughly 8 rapid requests; the
   original `except Exception: return None, None` swallowed this without
   retry, so the first full run resolved only ~360 of ~1,700 postal codes,
   collapsing estimated capacity to a fifth of its real value. Fixed with
   retry + exponential backoff, and the cache now only remembers postal
   codes that resolved successfully so a rate-limited run doesn't
   permanently poison later runs.

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
