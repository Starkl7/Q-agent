# Multi-Signal Markowitz Strategy Concept

## Purpose

This note explains the attached strategy framework. The strategy is a long-only equity allocation model that combines multiple signals across momentum, macro regime, positioning, valuation, earnings, volatility, and risk management.

The core idea is:

1. Build several independent alpha and risk signals.
2. Normalize each signal so it is comparable across stocks, sectors, countries, or time.
3. Transform each signal through a bounded response function into a uniform `[-1, +1]` score.
4. Combine the signals with a correlation-aware Markowitz-style optimizer.
5. Size positions using volatility targeting so exposure falls during high-risk periods and rises during calmer periods.

The attachment describes 11 signals, but some are grouped under broader categories. CTA momentum contributes four related signals, and regime probability contributes three related signals.

## Common Signal Processing

All signals follow a common pipeline:

1. **Raw measurement**
   - Compute the raw feature, such as price momentum, earnings revision balance, option volume spike, PMI state, or downside volatility.

2. **Volatility adjustment**
   - Adjust each signal using a rolling volatility estimate, typically a three-month window.
   - This prevents high-volatility inputs from dominating lower-volatility signals.

3. **Normalization**
   - Normalize time-series signals against their own history.
   - Normalize cross-sectional signals relative to the current universe.
   - Typical methods include z-scores, ranks, winsorization, and rolling percentiles.

4. **Response function**
   - Map normalized values into a bounded `[-1, +1]` signal.
   - The response function reduces tail risk by preventing extreme raw values from creating extreme portfolio weights.
   - Linear, logistic, hyperbolic tangent, clipped z-score, or piecewise functions could be used.

5. **Correlation-aware combination**
   - Combine signals using a Markowitz-style optimization.
   - The optimizer should account for signal volatility and signal correlation, not simply average all signals.
   - Highly correlated signals should receive less combined influence than diversified signals.

6. **Turnover control**
   - The attachment references typical turnover around `2.4x` per year.
   - In implementation, turnover should be controlled with rebalance frequency, minimum trade thresholds, signal smoothing, and transaction-cost-aware constraints.

## Signal 1: CTA Momentum

**What it captures:** trend persistence and behavioral momentum.

**Universe levels:**

- Individual stocks
- Industry indexes
- Sector indexes
- Country equity indexes

**Construction:**

- Apply CTA-style trend-following momentum across multiple horizons.
- The attachment suggests a six- to twelve-month range as the most useful region.
- The signal reflects both strength and direction of price trends.
- Normalize the resulting score and map it into `[-1, +1]`.

**Implementation note:** this can be built with rolling total returns, exponentially weighted trend estimates, moving-average crossovers, or time-series regression slopes. A practical first version should start with six- and twelve-month total return, skipping the most recent month if we want a classic momentum definition.

## Signal 2: Regime Probability

**What it captures:** business-cycle alignment.

**Universe levels:**

- Stocks
- Industries
- Sectors

**Construction:**

- Use OECD Composite Leading Indicators, or a practical macro proxy if OECD data is unavailable.
- Define four regimes using indicator level and direction of change:
  - Expansion
  - Slowdown
  - Downturn
  - Recovery
- Estimate the probability of each regime.
- Compute expected stock, industry, or sector returns conditional on historical performance in similar regime mixes.
- Normalize and scale the final score.

**Implementation note:** this is naturally a time-series macro signal applied to cross-sectional assets. A first version can use monthly macro data and map each sector to historical return behavior by regime.

## Signal 3: Crowding

**What it captures:** positioning and consensus risk.

**Construction:**

- Combine positioning measures such as:
  - Prime brokerage exposure
  - Stock lending data
  - 13F filings
  - Proprietary positioning data
- Apply a nonlinear response:
  - Trend-following behavior during the build-up phase.
  - Contrarian behavior when positioning becomes extreme.
- Map the resulting value into `[-1, +1]`.

**Implementation note:** some data in the attachment is proprietary. In QuantConnect, a practical proxy could use short interest, institutional ownership, fund-flow proxies, abnormal volume, borrow availability if available, or delayed 13F holdings. This signal should be treated as a later-stage enhancement unless the required data is available.

## Signal 4: EPS Growth: ML Versus Consensus

**What it captures:** risk of analyst upgrades, downgrades, and earnings surprises.

**Construction:**

- Build a model that forecasts next-twelve-month EPS growth using:
  - Historical EPS
  - Macro variables
  - Sector variables
  - Quantitative factors
- Compare the model forecast against analyst consensus.
- A larger positive gap implies higher probability of a positive earnings surprise.

**Implementation note:** the attachment references a UBS machine-learning model. A local version would need analyst consensus estimates and historical fundamentals. If IBES access is available through WRDS, this can be modeled more directly. Without IBES, QuantConnect Fundamental data can support a simpler proxy.

## Signal 5: Extreme Rates Momentum

**What it captures:** the effect of fast and large bond-yield moves on equity risk appetite.

**Construction:**

- Apply CTA-style momentum to local 10-year government yields.
- Use an inverse-pi style response function:
  - Strong yield trends, whether up or down, are negative for equities.
  - Stable rates are supportive.
- Focus on speed and magnitude, not direction alone.

**Implementation note:** the signal can be computed from rolling changes in 10-year yields, absolute trend strength, and volatility-adjusted yield momentum. It should likely act as a market or country-level risk adjustment rather than a single-stock alpha signal.

## Signal 6: Risk Targeting

**What it captures:** dynamic exposure management.

**Construction:**

- The signal is long-only.
- Position size is scaled by:

```text
portfolio volatility target, 3-year rolling
------------------------------------------------
stock volatility, 3-month rolling
```

- The strategy de-risks automatically during sell-offs.
- Exposure increases when volatility and correlations fall.

**Implementation note:** risk targeting belongs in portfolio construction, not alpha generation. It should cap position weights and total gross exposure so the strategy remains long-only and avoids unstable leverage.

## Signal 7: Up and Down Volatility

**What it captures:** asymmetric positioning and reversal risk.

**Construction:**

1. Split historical returns into gains and losses.
2. Compute rolling volatility of positive-return days and negative-return days separately.
3. Take the spread between downside volatility and upside volatility.
4. Apply a response function and normalize.

**Interpretation:**

High downside volatility relative to upside volatility can indicate crowded bearish positioning. The attachment treats this as a contrarian signal.

**Implementation note:** define the sign carefully. If downside volatility is much higher than upside volatility, the raw spread may be positive, but the final score should reflect the intended contrarian behavior.

## Signal 8: Options Volumes

**What it captures:** investor nervousness, hedging demand, and delayed capitulation.

**Construction:**

- Aggregate call and put volumes at the single-stock level.
- Smooth the series with a rolling window.
- Standardize the result with a rolling z-score.
- Map it through a response function.

**Interpretation:**

Option-volume spikes often precede forced selling, volatility events, or trend continuation.

**Implementation note:** this needs single-stock option volume data. In QuantConnect, options data may be available in cloud backtests, but local coverage depends on available data. A first version can use total option volume, put-call volume ratio, or abnormal option volume.

## Signal 9: Adjusted Forward P/E

**What it captures:** valuation adjusted for balance-sheet quality.

**Construction:**

- Start with the standard forward P/E ratio.
- Adjust the price numerator for balance-sheet strength, leverage, or quality.
- Normalize the adjusted valuation cross-sectionally.

**Interpretation:**

This improves raw value by penalizing companies with weak balance sheets.

**Implementation note:** a practical version can combine forward P/E, debt-to-equity, interest coverage, profitability, accruals, and earnings quality. Lower adjusted valuation should generally map to a higher score, subject to quality controls.

## Signal 10: Sector PMI: New Orders

**What it captures:** forward-looking sector demand.

**Construction:**

- Use sector-level PMI New Orders indexes.
- Define four states:
  - Low and improving
  - High and deteriorating
  - Low and deteriorating
  - High and improving
- Combine state probabilities, giving higher weight when level and momentum agree.
- Apply the time-series macro signal to sectors and then to stocks.

**Implementation note:** this is a sector allocation overlay. The final stock score can inherit the score of the stock's sector, possibly blended with stock-specific signals.

## Signal 11: Earnings Revisions

**What it captures:** changes in analyst expectations.

**Construction:**

- Measure net upward versus downward EPS estimate revisions.
- Implement the signal cross-sectionally as a relative signal.
- Even small changes in expectations can historically drive significant price moves.

**Implementation note:** if IBES estimates are available, this can be measured directly from analyst estimate changes. Without IBES, use QuantConnect fundamentals where possible or approximate with changes in consensus EPS, estimate count, or recent earnings surprise data.

## Portfolio Construction

The combined strategy should be built in layers:

1. **Signal atoms**
   - Pure functions for each signal calculation.
   - No QuantConnect dependencies.

2. **Signal molecules**
   - Normalization, response functions, volatility adjustment, and cross-sectional ranking.

3. **Alpha organism**
   - Orchestrates all available signals and produces final per-symbol expected returns or scores.

4. **Portfolio organism**
   - Combines signals with covariance estimates.
   - Applies risk targeting, long-only constraints, max weight constraints, and turnover controls.

5. **Execution organism**
   - Converts target weights into orders.
   - Applies trade thresholds to reduce churn.

## Practical QuantConnect Build Plan

Start with the signals that can be implemented using readily available equity price and fundamental data:

1. CTA momentum
2. Up/down volatility
3. Risk targeting
4. Adjusted forward P/E
5. Earnings revisions, if fundamental estimate data is available

Then add macro and alternative-data signals:

1. Regime probability
2. Extreme rates momentum
3. Sector PMI New Orders
4. Options volumes
5. Crowding
6. EPS growth model versus consensus

This staged approach keeps the first implementation testable while leaving room for richer data later.

## Key Risks and Open Questions

- Several signals depend on proprietary or licensed datasets.
- The optimizer can overfit if expected returns are noisy or covariance estimates are unstable.
- Response functions must be chosen carefully because they define how aggressively the strategy reacts to extremes.
- Turnover and transaction costs are central to whether the strategy is viable.
- Data timing must be handled carefully to avoid lookahead bias, especially for fundamentals, analyst estimates, macro releases, PMI, 13F data, and options data.
- Risk targeting can unintentionally increase exposure after calm periods, so max leverage and max position constraints are required.

## Minimal First Version

A realistic first implementation would be:

- Monthly rebalance.
- Universe of liquid US equities.
- Signals:
  - Six- and twelve-month momentum.
  - Up/down volatility spread.
  - Balance-sheet-adjusted value.
  - Basic earnings revision proxy if available.
- Signal processing:
  - Rolling z-scores.
  - Winsorization.
  - `tanh` response function into `[-1, +1]`.
- Portfolio:
  - Long-only top-ranked basket.
  - Volatility-scaled weights.
  - Max symbol weight.
  - Turnover threshold.

This version captures the structure of the attachment without depending immediately on every proprietary data source.
