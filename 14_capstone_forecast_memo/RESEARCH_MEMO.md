# Research Memo — Henry Hub Forecast (Capstone)

Write this like applied energy research, not a code dump. 2-4 pages. Each chart
referenced needs a sentence on what it shows AND what it does not show.

## Executive summary

3-5 sentences a busy reader can act on: the forecast you built, whether it beats
the baselines and the market benchmark out of sample, your confidence, and the
single biggest caveat. Lead with the finding, not the method.

## 1. Problem

What question are you answering and why does it matter for a gas-market analyst?
State the target/horizon/origin in one sentence.

## 2. Data and key decisions

Sources (with units, frequency, range) and the decisions that most shaped the
result: frequency alignment, missing-value handling, and especially the
information-availability / leakage decisions (when was each value public?). Point
to the data dictionary.

## 3. Baseline results

The 3 honest comparisons — persistence, seasonal-naive, futures benchmark — and
their out-of-sample scores. Explain WHY each is the right (or wrong) null for your
target. The futures benchmark is a strong null; beating it is hard and that is the
point.

## 4. Final model

What model, what features, and WHY you stopped where you did (when did added
complexity stop improving out-of-sample skill?). Note that you only fit the model
after the baselines were in place.

## 5. Results and comparison

Out-of-sample metrics for every forecaster, expressed as skill vs baseline, not
just raw RMSE. State plainly whether the model wins, and by how much. Include the
uncertainty interval and its measured empirical coverage.

## 6. Error analysis

WHEN does the model miss? Break errors down by regime/season/year. Is the mean
error dominated by a few spike periods? A model great in calm years and awful in
spikes is a specific, reportable weakness.

## 7. Key drivers

What predicted well, and how stable is that across folds? Compare two importance
views if you used them. Phrase drivers as *predictive of* price, NOT *causing*
price — name confounds (storage and HDD share seasonality, etc.).

## 8. Limitations

Specific, not generic. Include the required statement of what would make the model
FAIL out of sample (regime shift beyond training range, a fundamental published
too late to use in time, a collinear feature flipping sign).

## 9. Deployment & maintenance

How the model would run live: retraining cadence/trigger, monitoring of live error
and input drift, and the condition under which you would stop trusting it.

## 10. Next questions

3 concrete next experiments. Prefer better/cleaner data or a sharper benchmark
over mechanically stacking more algorithms.
