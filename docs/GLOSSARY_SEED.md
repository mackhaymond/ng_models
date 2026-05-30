# Glossary Seed

The learner should keep expanding this file throughout the curriculum — add your own
entries, examples, and "gotchas" as you hit them. But it is meant to be **genuinely
useful right now**: it is a ground-up reference for the whole Henry Hub forecasting
curriculum, written for a strong general programmer who is new to the specific
math (stats / time series / ML) and to the specific Python package interfaces
(pandas, matplotlib, statsmodels, pmdarima, scikit-learn, lightgbm, xgboost, scipy).

How to read this file:
- Each entry is 1-3 plain-English sentences. Where it helps, there is a **formula**
  and an **Intuition** line.
- API entries show the *interface you actually call*, not just the concept.
- `→ See` cross-references link related entries.
- Sections are ordered roughly from "concepts you need first" to "things you do last."

Contents:
1. [Market terms](#1-market-terms)
2. [NG fundamentals](#2-ng-fundamentals)
3. [Time series & statistics](#3-time-series--statistics)
4. [Stationarity & diagnostics](#4-stationarity--diagnostics)
5. [Classical forecasting models](#5-classical-forecasting-models)
6. [Weather & degree days](#6-weather--degree-days)
7. [Features, data plumbing & leakage](#7-features-data-plumbing--leakage)
8. [Machine learning](#8-machine-learning)
9. [Forecast evaluation](#9-forecast-evaluation)
10. [Uncertainty, intervals & risk](#10-uncertainty-intervals--risk)
11. [Modeling workflow terms](#11-modeling-workflow-terms)
12. [Python / package cheat-sheet](#12-python--package-cheat-sheet)

---

## 1. Market terms

- **Henry Hub**: A major U.S. natural gas pricing point in Louisiana and the reference point for many U.S. gas contracts.
- **Spot price**: Price for near-term physical commodity delivery.
- **Futures contract**: Exchange-traded contract for delivery or financial exposure at a specified future period.
- **Prompt/front month**: The nearest futures contract month that is still actively trading.
- **Contango**: Later-dated futures prices above nearer prices. *Intuition:* the market is willing to pay more for gas later — often a sign of comfortable near-term supply or storage/carry costs. → See [Roll yield](#roll-yield).
- **Backwardation**: Later-dated futures prices below nearer prices. *Intuition:* near-term gas is at a premium — often tight supply or strong immediate demand.
- **Basis**: Price difference between two locations or between a local price and a benchmark.
- <a id="settlement-price"></a>**Settlement price**: The official end-of-session price an exchange assigns to a contract, used to mark positions to market and compute margin. It is *not* the last trade — it is a defined daily reference (often a volume-weighted average over a closing window).
- <a id="contract-month"></a>**Contract month (delivery month)**: The calendar month a futures contract delivers/settles for. Each month is a *separate* instrument (e.g., the July contract vs. the August contract); a "continuous front-month" series stitches successive prompt months together. → See [Roll yield](#roll-yield).
- <a id="market-implied-expectation"></a>**Market-implied expectation**: What current prices reveal about the market's collective view of the future (e.g., the futures curve is a rough read on expected forward prices). It reflects supply/demand *and* a risk premium, so it is a noisy expectation, not a clean prediction. → See [Why futures are not forecasts](#why-futures-are-not-forecasts).
- <a id="roll-yield"></a>**Roll yield**: The return earned (or lost) purely from rolling a futures position from an expiring contract into the next one as the curve converges to spot. *Intuition:* in **contango** you roll "up the hill" (sell cheap-near, buy expensive-far) and bleed yield; in **backwardation** you roll "down the hill" and gain. → See [Contango](#1-market-terms), [Continuous series](#contract-month).
- <a id="why-futures-are-not-forecasts"></a>**Why futures are NOT forecasts**: A futures price is a *tradeable equilibrium today*, set by hedgers, speculators, storage economics, and risk premia — not a best-estimate of the future spot price. It can be systematically biased (e.g., persistent contango), it is anchored to no-arbitrage relationships, and it does not minimize forecast error. Use the curve as a **benchmark and as a feature**, but evaluate your model against realized prices, not against the curve. → See [Market-implied expectation](#market-implied-expectation), [Baseline](#baseline).

---

## 2. NG fundamentals

- **Working gas in storage**: Gas available in underground storage for withdrawal (above the permanent "base/cushion gas" that keeps wells pressurized).
- **Injection**: Net addition to storage.
- **Withdrawal**: Net draw from storage.
- **Dry gas production**: Marketable natural gas after removing liquids and impurities.
- <a id="marketed-vs-dry"></a>**Marketed vs. dry production**: *Marketed* production is gross gas removed (minus reinjected/vented/flared and nonhydrocarbon gases); *dry* production is marketed production *after* natural gas liquids (NGLs) and remaining impurities are stripped out. Dry production is the number that actually meets pipeline-quality demand, so it is usually the one you model. → See [Supply-demand balance](#supply-demand-balance).
- **Power burn**: Natural gas consumed for electricity generation.
- <a id="power-burn-marginal"></a>**Power burn / gas-fired generation as marginal**: In many U.S. power markets, gas plants are the *marginal* (last, price-setting) generator — so when electricity demand rises, gas burn rises, tightening the gas balance. *Intuition:* gas burn is the demand "shock absorber," and it is highly weather- and price-sensitive, which makes it a key swing variable in forecasts. → See [Power/gas burn](#supply-demand-balance), module `13_power_gas_burn_gridstatus_optional`.
- **LNG exports**: Liquefied natural gas exported from the U.S.
- **HDD/CDD**: Heating/cooling degree days; weather proxies for heating/cooling demand. → See [HDD/CDD formula](#hdd-cdd) in the weather section.
- <a id="five-year-average"></a>**Five-year average / seasonal norm**: The average of a quantity (typically storage) for the same week-of-year across the prior five years; the industry's default "normal" reference line. *Intuition:* gas is intensely seasonal, so comparing to "this week historically" is more meaningful than comparing to last week. → See [Inventory deviation](#inventory-deviation), [Seasonality](#seasonality).
- <a id="inventory-deviation"></a>**Inventory / storage deviation (surplus or deficit)**: Current working gas in storage minus the five-year average for the same week, often also reported vs. last year. A large *deficit* (below norm) is bullish for price; a large *surplus* is bearish. → See [Five-year average](#five-year-average).
- <a id="working-gas-capacity"></a>**Working-gas (demonstrated) capacity**: The maximum working gas the storage system can hold; "percent full" = working gas / capacity. *Intuition:* as storage nears capacity late in injection season, injections must slow, which can pressure prices.
- <a id="injection-withdrawal-season"></a>**Injection vs. withdrawal season**: Roughly **April–October** gas is injected into storage (low heating demand); roughly **November–March** it is withdrawn (winter heating). The "shoulder" transition months are when surprises move price most. → See [Seasonality](#seasonality).
- <a id="supply-demand-balance"></a>**Supply-demand balance identity**: The accounting identity that must hold over any period:

  **production + imports + storage_withdrawals = consumption + exports + storage_injections**

  Equivalently, **production + imports − consumption − exports = storage change (Δ inventory)**. *Intuition:* gas can't vanish — anything produced/imported that isn't consumed/exported must end up in (or come out of) storage. This identity is the backbone of fundamentals-based forecasting: estimate the pieces you can, and the balance tells you what storage *should* do. → See module `07_supply_demand_balance`.
- <a id="net-exports"></a>**Net exports**: Exports minus imports (pipeline + LNG). A positive and rising figure means the U.S. is sending more gas abroad, tightening the domestic balance. → See [Supply-demand balance](#supply-demand-balance).

---

## 3. Time series & statistics

- <a id="white-noise"></a>**White noise**: A sequence of uncorrelated, zero-mean, constant-variance random values — pure unpredictable "static." *Intuition:* if your model's **residuals** look like white noise, you've squeezed out all the predictable structure; anything left is irreducible. → See [Residual](#residual), [Ljung-Box](#ljung-box).
- <a id="autocorrelation"></a>**Autocorrelation (serial correlation)**: The correlation of a series with a lagged copy of itself. *Intuition:* "how much does today resemble k days ago?" Gas prices are strongly autocorrelated at short lags (today ≈ yesterday). → See [ACF](#acf).
- <a id="acf"></a>**ACF (autocorrelation function)**: Autocorrelation as a function of lag k, plotted as a bar at each lag. Reading it: a slow decay suggests non-stationarity/trend; spikes at seasonal lags (e.g., 7 or 12) suggest seasonality. *API:* `statsmodels.graphics.tsaplots.plot_acf(series, lags=40)`. → See [PACF](#pacf), [Differencing](#differencing).
- <a id="pacf"></a>**PACF (partial autocorrelation function)**: The correlation between the series and its lag-k value *after removing* the influence of all shorter lags. *Intuition:* the ACF mixes direct + indirect effects; the PACF isolates the *direct* effect of lag k. A PACF that cuts off sharply after lag p hints at an **AR(p)** model. *API:* `statsmodels.graphics.tsaplots.plot_pacf(series, lags=40, method="ywm")`. → See [AR](#ar).
- <a id="lag"></a>**Lag**: A shifted-back copy of a series (value k steps ago). *API:* `series.shift(k)` in pandas. → Contrast with [Release/publication lag](#release-lag).
- <a id="seasonality"></a>**Seasonality**: A pattern that repeats on a fixed period (daily, weekly, yearly). Gas has a strong **annual** seasonal cycle (winter heating, summer cooling). → See [SARIMA](#sarima), [Five-year average](#five-year-average).
- <a id="trend"></a>**Trend**: A slow, persistent up/down drift over time, separate from seasonality and noise.
- <a id="aic"></a>**AIC (Akaike Information Criterion)**: A model-selection score that trades off fit against complexity: **AIC = 2k − 2·ln(L̂)** (k = number of parameters, L̂ = maximized likelihood). *Intuition:* lower is better; it rewards fit but penalizes adding parameters so you don't overfit. Use it to compare candidate ARIMA orders on the *same* data. → See [BIC](#bic), [Overfitting](#overfitting).
- <a id="bic"></a>**BIC (Bayesian Information Criterion)**: Like AIC but with a heavier complexity penalty: **BIC = k·ln(n) − 2·ln(L̂)** (n = sample size). *Intuition:* BIC penalizes complexity more as data grows, so it tends to pick simpler models than AIC. Lower is better. → See [AIC](#aic).
- <a id="in-sample-out-of-sample"></a>**In-sample vs. out-of-sample**: *In-sample* = data the model was fit on; *out-of-sample* = data it never saw. *Intuition:* in-sample error flatters the model; only out-of-sample error estimates real forecasting skill. Always report out-of-sample. → See [Walk-forward validation](#walk-forward), [Overfitting](#overfitting), [Leakage](#leakage).
- <a id="walk-forward"></a>**Walk-forward / rolling-origin validation**: Backtesting for time series: fit on data up to time t, forecast t+1…t+h, then roll the origin forward and repeat, never using future data to predict the past. *Intuition:* it mimics how you'd actually deploy — make a call, wait, see what happened, advance. Two flavors: **expanding window** (training set grows) and **rolling/sliding window** (fixed-length training set that moves). *API:* `sklearn.model_selection.TimeSeriesSplit`. → See [Backtest](#backtest), [Cross-validation for time series](#cv-time-series).

---

## 4. Stationarity & diagnostics

- <a id="stationarity"></a>**Stationarity**: A series is (weakly) stationary when its mean, variance, and autocorrelation structure do **not** change over time — no trend, no changing volatility, no drift. *Intuition:* a stationary series is "statistically the same wherever you stand on the timeline," which is what most classical models (AR/MA/ARIMA) assume. Prices are usually non-stationary; *returns/differences* are closer to stationary. → See [Differencing](#differencing), [ADF/KPSS](#adf-kpss).
- <a id="differencing"></a>**Differencing**: Replacing each value with the change from the prior value, `y_t − y_{t-1}`, to remove trend and induce stationarity. *Intuition:* a wandering price becomes a (more) stable series of day-to-day moves. The "d" in ARIMA(p,**d**,q) is how many times you difference; **seasonal differencing** `y_t − y_{t-s}` (the "D" in SARIMA) removes a repeating seasonal level. *API:* `series.diff()` (and `series.diff(s)` for seasonal). → See [Stationarity](#stationarity), [SARIMA](#sarima).
- <a id="adf-kpss"></a>**ADF & KPSS tests**: Two hypothesis tests for stationarity that complement each other.
  - **ADF (Augmented Dickey-Fuller)** — null hypothesis: "has a unit root" (i.e., *non*-stationary). A small p-value (< 0.05) lets you reject non-stationarity → series looks stationary. *API:* `statsmodels.tsa.stattools.adfuller(series)`.
  - **KPSS** — null hypothesis: "is stationary." Here a small p-value means *reject stationarity* → non-stationary (the logic is flipped from ADF). *API:* `statsmodels.tsa.stattools.kpss(series)`.
  *Intuition:* run both — agreement is reassuring; if they disagree, you likely have a borderline/trend-stationary case and should difference or detrend and re-test. → See [Differencing](#differencing).
- <a id="ljung-box"></a>**Ljung-Box test**: A test for whether a group of autocorrelations (up to lag k) are jointly zero — used on **residuals** to check they are white noise. Null hypothesis: "no remaining autocorrelation." A large p-value is *good* (residuals look like noise → model captured the structure). *API:* `statsmodels.stats.diagnostic.acorr_ljungbox(resid, lags=[10])`. → See [White noise](#white-noise), [Residual](#residual).

---

## 5. Classical forecasting models

- <a id="ar"></a>**AR — Autoregressive(p)**: Predicts the next value as a weighted sum of its own p past values plus noise: **y_t = c + φ₁y_{t-1} + … + φ_p y_{t-p} + ε_t**. *Intuition:* "tomorrow is a blend of recent days." Identify p from where the **PACF** cuts off. → See [PACF](#pacf), [ARIMA](#arima).
- <a id="ma"></a>**MA — Moving Average(q)**: Predicts the next value from the last q forecast *errors*: **y_t = c + ε_t + θ₁ε_{t-1} + … + θ_q ε_{t-q}**. *Intuition:* "recent shocks/surprises echo forward for a while." Identify q from where the **ACF** cuts off. (Note: this is the MA *model*, distinct from a rolling-mean smoother also casually called a "moving average.") → See [ACF](#acf), [ARIMA](#arima).
- <a id="arima"></a>**ARIMA(p,d,q)**: Combines **AR(p)** + **d** rounds of **differencing** + **MA(q)** — the workhorse for a single stationary-after-differencing series. *Intuition:* difference until stationary (d), then explain the result with past values (p) and past errors (q). *API:* `statsmodels.tsa.arima.model.ARIMA(y, order=(p,d,q)).fit()`. → See [Differencing](#differencing), [pmdarima](#pmdarima).
- <a id="sarima"></a>**SARIMA / SARIMAX**: **SARIMA** adds a *seasonal* (P,D,Q,s) block to ARIMA to capture a repeating cycle of period s (e.g., s=12 monthly, s=7 weekly). **SARIMAX** further adds e**X**ogenous regressors — outside drivers like HDD, storage, or production. *Intuition:* SARIMA handles the calendar; the "X" lets weather/fundamentals inform the forecast. *API:* `statsmodels.tsa.statespace.sarimax.SARIMAX(y, order=(p,d,q), seasonal_order=(P,D,Q,s), exog=X).fit()`. → See [Seasonality](#seasonality), [Exogenous variable](#exogenous).
- <a id="exogenous"></a>**Exogenous variable (exog / X)**: An external input the model uses to help predict the target but does not itself model (e.g., degree days driving demand). *Caution:* to forecast the future you must supply future exog values — which themselves must be known or forecast without **leakage**. → See [SARIMAX](#sarima), [Leakage](#leakage), [As-of join](#as-of-join).
- <a id="exponential-smoothing"></a>**Exponential smoothing (SES / Holt / Holt-Winters)**: A family that forecasts by weighting recent observations more heavily, with weights decaying exponentially into the past.
  - **SES (Simple Exponential Smoothing)** — level only, for series with no trend or seasonality: **ŷ_{t+1} = αy_t + (1−α)ŷ_t** (α ∈ [0,1] is the smoothing rate; higher α = more reactive).
  - **Holt's linear** — adds a trend component.
  - **Holt-Winters** — adds a seasonal component (additive or multiplicative); a strong, simple seasonal baseline.
  *API:* `statsmodels.tsa.holtwinters.ExponentialSmoothing(y, trend="add", seasonal="add", seasonal_periods=12).fit()`. → See [Baseline](#baseline), [Seasonality](#seasonality).
- <a id="pmdarima"></a>**pmdarima (auto_arima)**: A library that automatically searches ARIMA/SARIMA orders by minimizing **AIC/BIC**, so you don't hand-tune (p,d,q)(P,D,Q,s). *API:* `pmdarima.auto_arima(y, seasonal=True, m=12)`. *Caution:* it still can overfit and still needs out-of-sample validation. → See [AIC](#aic), [Walk-forward](#walk-forward).

---

## 6. Weather & degree days

- <a id="weather-normal"></a>**Weather normal**: The long-run average weather for a given location and day-of-year (climatology), typically a 30-year average. The reference against which actual weather is judged. → See [Temperature anomaly](#temperature-anomaly), [Five-year average](#five-year-average).
- <a id="temperature-anomaly"></a>**Temperature anomaly**: Actual temperature minus the weather **normal** for that day/location. *Intuition:* "how much warmer or colder than usual" — what actually drives *surprise* demand and price moves.
- <a id="hdd-cdd"></a>**HDD / CDD formula**: Degree days convert temperature into heating/cooling demand relative to a comfort baseline (commonly **65°F**) using daily average temperature `Tavg`:

  **HDD = max(65 − Tavg, 0)**  (cold days → heating)
  **CDD = max(Tavg − 65, 0)**  (hot days → cooling)

  *Intuition:* a 25°F day is 40 HDD (lots of heating demand); a 65°F day is 0 of both. Summed over a period, they proxy total heating/cooling energy need. → See [Power burn](#power-burn-marginal).
- <a id="pop-weighted-dd"></a>**Population-weighted degree days**: Degree days averaged across regions weighted by population (or gas-consuming load), since demand follows people, not land area. *Intuition:* 10 HDD in a dense metro matters far more for national gas demand than 10 HDD over empty desert. → See [HDD/CDD](#hdd-cdd).
- <a id="yoy"></a>**Year-over-year (YoY) change**: A value compared with the same period one year earlier (e.g., this April's consumption vs last April's), as a difference or percent. *Intuition:* differencing by 12 months cancels the repeating seasonal cycle, so what's left is the *news* — genuine growth or decline, not "it's winter again." Contrast with month-over-month, which is dominated by seasonality. → See [Anomaly](#anomaly), [Seasonality](#seasonality), [Differencing](#differencing).
- <a id="anomaly"></a>**Anomaly (deviation from normal)**: Actual value minus its expected seasonal/historical norm (e.g., storage minus its five-year average for that week). *Intuition:* the part of a series that is *surprising* given the calendar — usually far more informative for price than the raw level. → See [Five-year average](#five-year-average), [Temperature anomaly](#temperature-anomaly), [Storage deviation](#storage-deviation).
- <a id="correlation-causation"></a>**Correlation vs. causation**: Two series moving together (correlation) does not establish that one *drives* the other (causation) — both may follow a third driver, the link may reverse, or it may be coincidence. *Intuition:* in gas markets weather, storage, production, and price all co-move; a model exploiting correlation can forecast yet still be wrong about *why*. Never state a causal claim that a controlled comparison or mechanism doesn't support. → See [Leakage](#leakage), [Feature importance](#feature-importance).

---

## 7. Features, data plumbing & leakage

- **Leakage**: Use of information that would not have been known at forecast time. *Intuition:* the silent killer of backtests — it makes models look brilliant in testing and fail live. → See [As-of join](#as-of-join), [Release lag](#release-lag), [In-sample vs out-of-sample](#in-sample-out-of-sample).
- <a id="as-of-join"></a>**As-of join**: A merge that, for each target timestamp, attaches the most recent value that was *actually available as of that time* — never a value published later. *Intuition:* the disciplined way to avoid **leakage** when combining series with different release schedules. *API:* `pandas.merge_asof(left, right, on="date", direction="backward")` (sort both first). → See [Release lag](#release-lag), [Feature table](#feature-table).
- <a id="release-lag"></a>**Lag vs. release/publication lag**: A **lag** (`shift(k)`) is a modeling choice — deliberately using a past value. A **release/publication lag** is a *fact about the data*: when a figure becomes public vs. the period it describes (e.g., weekly storage for the week ending Friday is published the next Thursday). *Intuition:* you must align features to *publication* time, not the period they cover, or you leak. → See [As-of join](#as-of-join), [Leakage](#leakage).
- <a id="imputation"></a>**Imputation**: Filling missing values with a principled estimate (forward-fill, interpolation, model-based) rather than dropping rows. *Caution for time series:* only use information available *before* the gap — back-fills and global means leak the future. *API:* `df.ffill()`, `series.interpolate()`, `sklearn.impute.SimpleImputer`. → See [Leakage](#leakage).
- <a id="feature-table"></a>**Feature table / model matrix (design matrix, X)**: The rectangular table where each row is one observation and each column is one predictor (feature), plus a separate target column (y). *Intuition:* every model ultimately consumes this X (and y) — building it correctly (right alignment, no leakage) is most of the work. → See [As-of join](#as-of-join), [Feature scaling](#feature-scaling), module `09_feature_table_leakage`.
- <a id="feature-scaling"></a>**Feature scaling (standardize / normalize)**: Rescaling features to comparable ranges, e.g., standardize to mean 0, std 1: **z = (x − μ) / σ**. *Why it matters:* **linear / regularized models and distance-based methods need it** — features on bigger numeric scales otherwise dominate coefficients and penalties. **Tree models (random forest, gradient boosting) do NOT need it** — they split on thresholds, so monotonic rescaling changes nothing. *API:* `sklearn.preprocessing.StandardScaler` (fit on train only, then transform train+test — fitting on all data leaks). → See [Regularization](#regularization), [Leakage](#leakage).

---

## 8. Machine learning

- <a id="overfitting"></a>**Overfitting**: When a model learns noise/quirks of the training data instead of the real signal, so it scores great in-sample but poorly out-of-sample. *Intuition:* memorizing the answers to the practice test instead of learning the subject. Defenses: simpler models, **regularization**, proper **cross-validation**, more data. → See [Regularization](#regularization), [In-sample vs out-of-sample](#in-sample-out-of-sample), [AIC](#aic).
- <a id="hyperparameter"></a>**Hyperparameter**: A setting you choose *before* training that the model does not learn from data (e.g., tree depth, learning rate, regularization strength λ). *Intuition:* the model learns *parameters*; you tune *hyperparameters* — usually via cross-validation. → See [Cross-validation for time series](#cv-time-series).
- <a id="regularization"></a>**Regularization (L1 / L2 / ridge / lasso / elastic-net)**: Adding a penalty on coefficient size to the loss so the model stays simpler and generalizes better.
  - **L2 / Ridge** — penalizes the sum of *squared* coefficients (`λ·Σβ²`); shrinks coefficients toward (but not to) zero. Good when many features each matter a little.
  - **L1 / Lasso** — penalizes the sum of *absolute* coefficients (`λ·Σ|β|`); can drive some coefficients exactly to zero → automatic feature selection.
  - **Elastic-net** — a blend of L1 and L2.
  *Intuition:* λ (alpha in sklearn) controls strength — bigger λ = simpler model, less overfitting, more bias. *API:* `sklearn.linear_model.Ridge`, `Lasso`, `ElasticNet`. *Note:* scale features first. → See [Feature scaling](#feature-scaling), [Hyperparameter](#hyperparameter), [Overfitting](#overfitting).
- <a id="cv-time-series"></a>**Cross-validation for time series**: Splitting data into train/validation folds to estimate out-of-sample performance — but for time series the splits must respect **time order** (train only on the past, validate on the future). Ordinary shuffled k-fold **leaks** and is invalid here. *API:* `sklearn.model_selection.TimeSeriesSplit(n_splits=5)`. → See [Walk-forward](#walk-forward), [Leakage](#leakage).
- <a id="gradient-boosting"></a>**Gradient boosting (LightGBM / XGBoost)**: An ensemble that builds many small decision trees **sequentially**, each new tree fitting the *residual errors* of the running ensemble. *Intuition:* iterative residual-fitting — start with a rough guess, then keep training little trees that correct what's still wrong; the **learning rate** controls how big each correction is. Strong on tabular feature tables, captures nonlinearity and interactions, needs no feature scaling. *API:* `lightgbm.LGBMRegressor(...)`, `xgboost.XGBRegressor(...)`. *Key hyperparameters:* `n_estimators`, `learning_rate`, `max_depth`/`num_leaves`, plus regularization (`reg_lambda`, etc.). → See [Hyperparameter](#hyperparameter), [Feature importance](#feature-importance), [Residual](#residual).
- <a id="feature-importance"></a>**Feature importance**: A score ranking how much each feature contributed to the model. *Caution:* tree "gain/split" importances can be biased toward high-cardinality features and don't show direction. → See [Permutation importance](#permutation-importance).
- <a id="permutation-importance"></a>**Permutation importance**: Measure a feature's importance by randomly shuffling its column and seeing how much the model's out-of-sample score degrades — the bigger the drop, the more the model relied on it. *Intuition:* "break this one input and see how much it hurts," model-agnostic and more trustworthy than built-in importances. *API:* `sklearn.inspection.permutation_importance(model, X_val, y_val)`. → See [Feature importance](#feature-importance).

---

## 9. Forecast evaluation

- **Residual**: Actual value minus predicted value (`y − ŷ`). Diagnostic raw material — patterns in residuals reveal what the model missed. → See [White noise](#white-noise), [Ljung-Box](#ljung-box).
- <a id="mae"></a>**MAE (Mean Absolute Error)**: Average of `|y − ŷ|`. *Intuition:* typical error size in the target's own units; robust to outliers; treats a $1 miss as $1. *API:* `sklearn.metrics.mean_absolute_error`. Use when you care about typical-sized errors and don't want big misses to dominate.
- <a id="rmse"></a>**RMSE (Root Mean Squared Error)**: `sqrt(mean((y − ŷ)²))`. *Intuition:* like MAE but **squares** errors first, so it punishes large misses much harder; same units as the target. *API:* `sklearn.metrics.mean_squared_error(..., squared=False)`. Use when big errors are especially costly (e.g., price spikes).
- <a id="mape"></a>**MAPE (Mean Absolute Percentage Error)**: `mean(|y − ŷ| / |y|)`, a percentage. *Intuition:* scale-free, easy to communicate. **Zero/near-zero pitfall:** it explodes (→ ∞) when actuals are near zero and is undefined at exactly zero, and it asymmetrically penalizes over- vs. under-forecasts. Avoid for series that can hit ~0. → See [sMAPE](#smape).
- <a id="smape"></a>**sMAPE (symmetric MAPE)**: `mean(2·|y − ŷ| / (|y| + |ŷ|))`. *Intuition:* a bounded, more symmetric cousin of MAPE that behaves better near zero (denominator uses both actual and forecast), though it still has quirks. Use instead of MAPE when actuals can get small.
- **Drawdown**: The peak-to-trough decline of a quantity (e.g., a P&L or price series) over a period; a risk measure of "worst slide from a high." → See module `12_uncertainty_spikes_risk`.

*Choosing a metric:* report **MAE** for an interpretable typical error, **RMSE** when large misses matter most, and a percentage metric (**sMAPE** over MAPE) only when a scale-free comparison across series is needed and values stay away from zero.

---

## 10. Uncertainty, intervals & risk

- **Prediction interval**: Range intended to contain future outcomes at a stated coverage rate (e.g., a 90% interval should contain the actual 90% of the time). *Intuition:* a point forecast is a guess; the interval is your honesty about uncertainty. → See [Empirical coverage](#empirical-coverage), [Quantile forecast](#quantile-forecast).
- <a id="quantile-forecast"></a>**Quantile forecast**: Predicting a specific quantile of the outcome (e.g., the 10th, 50th, 90th percentile) instead of just the mean. *Intuition:* stack several quantiles to build a full **prediction interval** (e.g., P10–P90 = 80% interval). *API:* `lightgbm`/`xgboost` with quantile objective, or `sklearn.linear_model.QuantileRegressor`. → See [Pinball loss](#pinball-loss).
- <a id="pinball-loss"></a>**Pinball / quantile loss**: The loss function that, when minimized, yields an unbiased estimate of a target quantile τ; it penalizes under- and over-prediction *asymmetrically* by τ vs. (1−τ). *Intuition:* for the 90th percentile it punishes under-shooting ~9× harder than over-shooting, pushing the forecast up to the right quantile. Use it to *train* and *score* quantile forecasts. → See [Quantile forecast](#quantile-forecast).
- <a id="empirical-coverage"></a>**Empirical coverage**: The fraction of actuals that *actually* fell inside your prediction intervals out-of-sample. *Intuition:* the reality check on intervals — if your "90%" interval only catches 70% of outcomes, it's too narrow (overconfident). → See [Calibration](#calibration).
- <a id="calibration"></a>**Calibration**: How well stated probabilities/intervals match observed frequencies; a *well-calibrated* 90% interval has ~90% empirical coverage. *Intuition:* being right about *how often you're right*. → See [Empirical coverage](#empirical-coverage), [Prediction interval](#10-uncertainty-intervals--risk).
- <a id="spike-event"></a>**Spike / threshold event**: A discrete, rare, large move — e.g., price jumping above a set threshold (a "spike"). Often modeled separately (as a classification or exceedance-probability problem) because rare extremes are poorly captured by error-minimizing point forecasts. *Intuition:* the moves that matter most for risk are exactly the ones a plain RMSE model smooths over. → See [Drawdown](#9-forecast-evaluation), module `12_uncertainty_spikes_risk`.

---

## 11. Modeling workflow terms

- **Forecast origin**: Date/time when a forecast is made. → See [Walk-forward](#walk-forward).
- **Target date**: Date/time being forecast.
- **Horizon**: Distance from forecast origin to target date.
- <a id="baseline"></a>**Baseline**: Simple reference forecast a model must beat (e.g., "tomorrow = today" naive, seasonal-naive, or the **five-year average**). *Intuition:* skill is *relative* — a fancy model that can't beat "last value" has no value. → See [Why futures are not forecasts](#why-futures-are-not-forecasts), [Exponential smoothing](#exponential-smoothing).
- **Backtest**: Historical simulation of how forecasts would have performed. Must use **walk-forward** logic and avoid **leakage** to be trustworthy. → See [Walk-forward](#walk-forward), [Leakage](#leakage).

---

## 12. Python / package cheat-sheet

Quick orientation to the libraries this curriculum uses. These are *what each tool is for*, not full docs.

- **pandas**: Tabular/time-series data handling — the `DataFrame` (table) and `Series` (one column). Core moves you'll use constantly: `df.resample("D").mean()` (change frequency), `series.shift(k)` (**lag**), `series.diff()` (**differencing**), `series.rolling(7).mean()` (rolling stats), `pd.merge_asof(...)` (**as-of join**), `df.ffill()` (forward-fill **imputation**). Index your time series by a `DatetimeIndex`. → See [Feature table](#feature-table), [Lag](#lag).
- **matplotlib**: Plotting. `fig, ax = plt.subplots(); ax.plot(series); plt.show()`. Used for ACF/PACF plots, forecast-vs-actual, residual diagnostics.
- **statsmodels**: Classical statistics & time series — `ARIMA`, `SARIMAX`, `ExponentialSmoothing`, stationarity tests (`adfuller`, `kpss`), `acorr_ljungbox`, and `plot_acf`/`plot_pacf`. Your home for [classical models](#5-classical-forecasting-models) and [diagnostics](#4-stationarity--diagnostics).
- **pmdarima**: `auto_arima` for automatic ARIMA/SARIMA order selection by AIC/BIC. → See [pmdarima](#pmdarima).
- **scikit-learn (sklearn)**: General ML toolkit with a uniform `fit`/`predict` interface — linear & regularized models (`Ridge`, `Lasso`, `ElasticNet`, `QuantileRegressor`), preprocessing (`StandardScaler`, `SimpleImputer`), time-aware splitting (`TimeSeriesSplit`), metrics (`mean_absolute_error`, `mean_squared_error`), and `permutation_importance`. → See [ML section](#8-machine-learning), [Forecast evaluation](#9-forecast-evaluation).
- **lightgbm / xgboost**: Gradient-boosted decision trees for tabular forecasting; both expose sklearn-style `LGBMRegressor` / `XGBRegressor`, support quantile objectives for [quantile forecasts](#quantile-forecast), and need no feature scaling. → See [Gradient boosting](#gradient-boosting).
- **scipy**: Scientific computing — distributions and statistical tests (`scipy.stats`), optimization, interpolation. Handy for fitting distributions to residuals and building/checking [prediction intervals](#10-uncertainty-intervals--risk).
