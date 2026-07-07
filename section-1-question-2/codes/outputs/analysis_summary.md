# Section 1 Question 2 - COE Price Prediction & Quota Elasticity

## Executive summary

This analysis models COE premiums for Category A and B using auction-level bidding data. The final selected model is **Ridge baseline**, chosen by lowest RMSE on a time-based holdout set.

Holdout performance for the selected model:

- MAE: S$4,109
- RMSE: S$6,460
- MAPE: 4.0%
- R²: 0.81

## Main policy insight

Quota matters, but it should not be analysed in isolation. A more policy-relevant indicator is **demand pressure**, measured as bids received per available quota. When quota increases while demand is held constant, the bid-to-quota ratio falls, and the model estimates lower premiums.

## Latest-round policy simulation

- Category A: baseline predicted premium S$123,183; +100 quota -> S$121,275 (-1,908); +300 quota -> S$116,970 (-6,212).
- Category B: baseline predicted premium S$124,972; +100 quota -> S$121,976 (-2,996); +300 quota -> S$115,135 (-9,837).

## Important interpretation caveat

This is a model-based sensitivity analysis, not a causal estimate. In reality, announcing more quota may also change bidding behaviour. For a stronger causal estimate, LTA could combine this with quasi-experimental methods around quota announcement shocks.
