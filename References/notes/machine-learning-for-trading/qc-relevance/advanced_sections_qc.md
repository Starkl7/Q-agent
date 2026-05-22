# QuantConnect Relevance for Advanced Sections

## Good Fit for LEAN

- Factor engineering, factor evaluation, and alpha-library work map well if the inputs can be built from LEAN data or precomputed offline.
- Tree ensembles work well when training happens offline and the algorithm consumes stored predictions or compact model artifacts.
- HRP or other portfolio-construction logic can be implemented in LEAN once the inputs are already clean and point-in-time safe.
- Topic or embedding features can be used in LEAN if document processing is done outside the algorithm and loaded as custom data or ObjectStore artifacts.

## Fits LEAN with Heavy Custom Data or Offline Infrastructure

- XBRL filing workflows need a custom ingestion and point-in-time availability layer.
- Cointegration and pairs selection are feasible, but large-universe formation logic is usually better done offline with results pushed into the strategy.
- Deep learning models can be consumed in LEAN, but training inside a normal backtest is usually the wrong place to do it.
- Autoencoder, GAN, and embedding pipelines are better treated as offline research systems that publish features, scenarios, or forecasts.

## Poor Fit for Standard LEAN Backtests

- Full NASDAQ ITCH limit order book reconstruction is far beyond the default bar-based research flow and needs specialized tick data plus custom market-simulation assumptions.
- GPU-heavy training loops for CNN, RNN, GAN, or RL models do not belong inside standard backtests.
- RL agents trained directly against a simple historical backtest can look good for the wrong reasons if the environment omits slippage, latency, and action constraints.

## Practical QC Substitutions

- Replace full order-book work with quote- and trade-derived microstructure proxies when only bar or quote data is available.
- Replace live text parsing inside the algorithm with offline feature generation and point-in-time joins.
- Replace end-to-end online model training with periodic batch retraining and artifact deployment.
- Replace notebook-only diagnostics with stored metrics, walk-forward outputs, and explicit schema versions.

## LEAN Implementation Biases To Watch

- Point-in-time alignment is the main failure mode for filing, factor, and text features.
- Universe churn can break rolling-model assumptions if identifiers and history windows are not handled carefully.
- Execution realism matters more as horizons get shorter; alpha from microstructure-style signals can disappear under realistic costs.
- Model confidence outputs are only useful if they affect position sizing, risk limits, or trade filtering in a consistent way.
