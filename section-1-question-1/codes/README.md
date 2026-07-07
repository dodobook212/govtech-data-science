# Section 1 Question 1 - HDB Resale Portal and property agents

## Objective

Quantify the business impact of the HDB Resale Portal, launched in January 2018, on property agents using data from 2017 onwards.

## Data used

1. `Resale flat prices based on registration date from Jan-2017 onwards.csv`
   - Used to count total HDB resale transactions.

2. `CEASalespersonsPropertyTransactionRecordsresidential.csv`
   - Filtered to `property_type == HDB` and `transaction_type == RESALE`.
   - Used to count CEA salesperson representation records.

## Important interpretation note

The CEA dataset does not contain a unique transaction ID. Therefore, CEA rows are treated as **agent representation records**, not unique transactions.

The main proxy metric is:

```text
Agent representation records per 100 HDB resale transactions
= CEA HDB resale representation records / HDB resale transactions × 100
```

This measures agent business activity intensity in the HDB resale market.

## How to run

1. Place the two CSV files in a folder named `data/`.
2. Open `codes/q1_hdb_agent_impact.ipynb`.
3. Run all cells.
4. Outputs will be saved to `outputs/`.

## Outputs

- `yearly_metrics.csv`
- `monthly_metrics.csv`
- `impact_summary.csv`
- `town_change_2017_vs_latest_full_year.csv`
- `chart_1_hdb_resale_volume.png`
- `chart_2_agent_intensity.png`
- `chart_3_market_vs_agent_records.png`
- `chart_4_top_town_declines.png`
