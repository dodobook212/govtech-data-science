# COE Price Prediction & Quota Elasticity

Selected model: Ridge baseline (lowest RMSE on the 2021-2025 time-based holdout).

- MAE: S$4,109
- RMSE: S$6,460
- MAPE: 4.0%
- R2: 0.81

Quota alone doesn't tell the full story. What the model actually leans on is
demand pressure - bids received per unit of quota. Add quota while demand
stays flat and the bid-to-quota ratio drops, which is what pulls predicted
premiums down in the simulation below.

Latest-round simulation:

- Category A: baseline predicted premium S$123,183; +100 quota -> S$121,275 (-1,908); +300 quota -> S$116,970 (-6,212).
- Category B: baseline predicted premium S$124,972; +100 quota -> S$121,976 (-2,996); +300 quota -> S$115,135 (-9,837).

Caveat: this is a model-based sensitivity check, not a causal estimate.
Announcing more quota could itself change bidding behaviour, which this
setup can't capture. A proper causal read would need something like a
quasi-experimental design around past quota announcement shocks.
