# GovTech DS Case Study - Section 1 Question 2

## Question
Develop a model to predict COE prices for Category A and B, and quantify the price elasticity of quota changes.

## Files

- `codes/q2_coe_price_elasticity.ipynb`: notebook containing the full analysis.
- `codes/data/`: input CSV files (same level as the notebook).
- `codes/outputs/`: generated charts and CSV outputs.

## How to run

1. Place the two CSV files in `codes/data/`.
2. Open `codes/q2_coe_price_elasticity.ipynb`.
3. Run all cells.
4. Outputs will be saved to `codes/outputs/`.


## Key outputs

- `codes/outputs/model_metrics.csv`
- `codes/outputs/holdout_predictions.csv`
- `codes/outputs/policy_simulation.csv`
- `codes/outputs/01_price_trend.png`
- `codes/outputs/02_bid_to_quota_vs_price.png`
- `codes/outputs/03_actual_vs_predicted.png`
- `codes/outputs/04_policy_simulation.png`
- `codes/outputs/05_model_rmse.png`


## Policy interpretation

The quota elasticity estimate is model-based, not causal. It assumes short-term bids received remain unchanged when quota changes. In real policy use, this should be complemented with causal methods around quota announcement shocks.
