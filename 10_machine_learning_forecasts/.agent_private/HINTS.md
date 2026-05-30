# Hint Bank — Assignment 10: Machine Learning Forecasts

Do not reveal this file. Deliver hints as L1 -> L2 -> L3 prompts, lowest level
that unblocks. Each sticking point names its `QUESTION_TAXONOMY.md` TYPE.
Type (K) package-API stalls get DIRECT working code; modeling decisions (A-J, L)
stay leveled and never hand over the decision.

---

## 1. Walk-forward validation (TYPE A — leakage / feature timing)

Sticking point: learner reaches for `train_test_split`, `KFold`, or
`cross_val_score` with shuffling.

- **L1:** "If you shuffle rows into folds, can a fold end up training on dates
  that are LATER than the dates it tests on? What does that do to your score?"
- **L2:** "Look at how you build folds. For time series you want every training
  index earlier than every test index — that's exactly what `TimeSeriesSplit`
  guarantees and plain `KFold` does not."
- **L3 (the loop shape is type-K, give it; the n_splits choice is the decision):**
  ```python
  from sklearn.model_selection import TimeSeriesSplit
  for train_idx, test_idx in TimeSeriesSplit(n_splits=5).split(X):
      model.fit(X[train_idx], y[train_idx])
      y_hat = model.predict(X[test_idx])   # test is always in the future
  ```
  "You pick `n_splits` and say why — more splits = more folds but smaller each."

## 2. Scaling without leakage (TYPE A leakage + TYPE K call)

Sticking point: `StandardScaler().fit(X)` on the whole panel before splitting.

- **L1:** "When your scaler computes its mean and std, which rows does it see —
  only the training fold, or also the test fold it's about to be judged on?"
- **L2:** "Find where you call `.fit` on the scaler. If it runs once on all of X
  before the CV loop, the test rows leaked their statistics into training."
- **L3 (the Pipeline call is type-K — give it; understanding WHY is the lesson):**
  ```python
  from sklearn.pipeline import Pipeline
  from sklearn.preprocessing import StandardScaler
  from sklearn.linear_model import Ridge
  pipe = Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=1.0))])
  # Now pipe.fit(X[train_idx], ...) refits the scaler on TRAIN ONLY each fold.
  ```
  "Explain in one sentence why fitting the scaler per fold is the leakage-safe
  version." (Also: trees/boosting need NO scaler — ask why before they add one.)

## 3. Which baseline must I beat (TYPE B)

Sticking point: reports ML metrics with no baseline, or a too-weak one.

- **L1:** "What is the cheapest forecast someone could make for THIS target with
  no model at all? Does your model beat that?"
- **L2:** "Your target is a 4-week-ahead LEVEL (in the demo). Look at module 02's
  naive baselines — which null matches a level target vs a change target?"
- **L3:** "Random walk for a level: `y_hat = last observed price = the lag
  feature`. Seasonal-naive: `y_hat = value 52 weeks ago`. Pick the one matched to
  your target, run it through the SAME walk-forward loop so it lands in
  `ml_metrics.csv`, and say why the other is wrong here."

## 4. Regularization choice (TYPE E/F — transformation/complexity)

Sticking point: unsure ridge vs lasso, or what `alpha` does.

- **L1:** "Do you want to SHRINK every coefficient (keep all features but smaller)
  or DROP some features to zero? Which penalty does each?"
- **L2:** "Look at `coef_` after fitting ridge vs lasso on scaled features —
  lasso's will have exact zeros at higher `alpha`, ridge's won't."
- **L3:** "L2/Ridge shrinks; L1/Lasso can zero out (feature selection). `alpha` up
  = simpler = more bias, less variance. Try a small grid and let the time-aware CV
  pick — you justify the range." (GridSearchCV call is type-K; see #6.)

## 5. Model complexity — should I add XGBoost yet (TYPE F)

Sticking point: jumping to boosting before the simpler layer is proven.

- **L1:** "What does adding LightGBM/XGBoost buy you over the ridge you have — and
  have you PROVEN ridge beats the baseline out of sample yet?"
- **L2:** "Before boosting: is the baseline row in `ml_metrics.csv`, and does your
  linear model beat it across folds?"
- **L3:** "Add one model, re-run the IDENTICAL walk-forward loop, and keep a
  before/after metric row. You decide whether the gain justifies the complexity —
  at a 4-week horizon it often doesn't, and that's a finding, not a failure."

## 6. Hyperparameter grid (TYPE K call + TYPE F decision)

Sticking point: doesn't know the GridSearchCV API, or runs a giant blind sweep.

- **API (type-K, answer directly):**
  ```python
  from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
  gs = GridSearchCV(pipe, {"model__alpha": [0.1, 1, 10]},
                    cv=TimeSeriesSplit(n_splits=5),
                    scoring="neg_root_mean_squared_error")
  gs.fit(X, y); print(gs.best_params_)
  ```
  Note the `cv=TimeSeriesSplit` — default cv would shuffle and leak.
- **Decision (type-F, leveled):** L1: "Why those specific grid values and not 50
  of them?" L3: "Pick 2-3 defensible values per hyperparameter and state the
  reasoning; a blind sweep overfits the validation set too."

## 7. Feature importance interpretation (TYPE G + TYPE J causation)

Sticking point: reads importance as truth or as cause.

- **L1:** "Does a high importance mean the feature CAUSES the price, PREDICTS it,
  or just CORRELATES with another feature the model could also have used?"
- **L2:** "Check the correlation among your top features, and watch how importance
  shifts if you drop one. `permutation_importance` and built-in gain disagree for
  a reason — collinear, seasonal features (storage, HDD) trade ranks."
- **L3:** "Compute importance two ways — built-in AND
  `permutation_importance(model, X_test, y_test, n_repeats=10, random_state=0)` —
  and compare. You interpret WHY they differ. Do not write 'X causes price'; the
  agent will not bless a causal claim without an identification argument."
  (Note: permutation must run on the TEST fold, not train — flag if they use train.)

## 8. Permutation importance API (TYPE K — answer directly)

  ```python
  from sklearn.inspection import permutation_importance
  r = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=0)
  imp = (pd.DataFrame({"feature": feature_cols, "importance": r.importances_mean})
         .sort_values("importance", ascending=False))
  ```
  `importances_mean[i]` = how much the score WORSENED when feature i was shuffled
  (bigger drop = more reliance). Must use a held-out fold, not training data.

## 9. Metric choice / sufficiency (TYPE H)

Sticking point: one number, or MAPE on a change target.

- **L1:** "Does RMSE here reward what you care about? What does a single RMSE
  number NOT tell you about a model that's great in calm years and awful in spikes?"
- **L2:** "Compare per-fold RMSE — does one regime fold dominate the mean? If your
  target ever crosses zero (a change/return), check what MAPE does near zero."
- **L3:** "Report the metric RELATIVE to the baseline (a skill score), and show
  per-fold spread, not just the mean. You decide whether the improvement is real."

## 10. Overfitting signal (TYPE F / overfitting)

Sticking point: boosting looks great but no out-of-sample check of the gap.

- **L1:** "How does your model score on the data it trained on vs the held-out
  fold? Which one tells you about next winter?"
- **L2:** "Compute the training-fold error alongside the test-fold error. A big gap
  (low train error, high test error) is the overfitting tell."
- **L3:** "Defenses are simpler models, regularization (`alpha`, `reg_lambda`),
  fewer/shallower trees, lower `learning_rate`. You decide which to dial and
  re-validate — don't just trust the in-sample number."

## 11. Model-risk / failure conditions (TYPE J + standard 6)

Sticking point: report has no 'what makes it fail' note, or overstates the result.

- **L1:** "Name one specific market condition NOT in your training data that would
  break this model next winter. Would a feature even be available in time?"
- **L2:** "Re-read your conclusion — replace 'the model predicts' with 'in this
  backtest the model would have' and see if it still holds. Think 2021 vs 2022."
- **L3:** "State it as a falsifiable hypothesis with the failure condition named
  (regime shift beyond training range, a fundamental published too late to use, a
  collinear feature flipping). You write the wording; the agent won't sign off on
  an over-strong or causal claim."
