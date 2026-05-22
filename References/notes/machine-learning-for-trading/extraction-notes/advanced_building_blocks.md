# Advanced Building Blocks

Reusable research and implementation patterns extracted from the advanced parts of the book.

## Data Pipelines

- Order book research pipeline: raw messages -> book state reconstruction -> queue and imbalance features -> short-horizon labels.
- Filing NLP pipeline: filing ingestion -> entity and form normalization -> section extraction -> timestamp alignment -> document features.
- Text corpus pipeline: dedupe -> sentence/token cleanup -> n-grams or phrases -> vocabulary control -> model-ready matrix or embeddings.

## Factor Research Loop

- Start with point-in-time data and explicit rebalancing frequency.
- Build factors with transparent transforms before adding denoising layers.
- Evaluate with rank IC, turnover, quantile spreads, stability across windows, and implementation cost.
- Separate signal quality from portfolio-construction quality.

## Time-Series Modeling Pattern

- Diagnose stationarity first.
- Create rolling windows with no future leakage.
- Refit on a schedule that matches the decay of the relationship.
- Compare forecasts to a dumb baseline before trusting a complex model.

## Bayesian Workflow Pattern

- Make the prior explicit.
- Decide whether uncertainty itself changes decisions such as sizing or model choice.
- Use posterior predictive checks, not just parameter summaries.
- Prefer Bayesian methods when confidence bands matter operationally.

## Tree-Model Workflow

- Generate lagged and cross-sectional features with strict point-in-time rules.
- Use purged or otherwise time-aware validation.
- Save feature importance and SHAP outputs alongside predictions.
- Inspect turnover and concentration before converting scores into trades.

## Unsupervised Learning Pattern

- Use PCA or ICA for compression or latent structure, not for storytelling by default.
- Treat t-SNE and UMAP as visualization tools.
- Re-test cluster stability across windows before using clusters in allocation rules.
- Use HRP as a robust allocator when covariance estimates are noisy or sample sizes are thin.

## Deep Learning Pattern

- Confirm that dataset size and signal complexity justify the model capacity.
- Separate representation learning, prediction, and trading layers in evaluation.
- Track training and validation curves, not just final loss.
- Save the exact preprocessing and normalization state used during training.

## Generative and RL Pattern

- For synthetic data, evaluate diversity, fidelity, and usefulness separately.
- For RL, define the state, action, reward, and constraints before picking the algorithm.
- Keep market frictions, delays, and position limits inside the environment instead of bolting them on afterward.
- Require strong supervised or rules-based baselines before trusting a policy-learning result.
