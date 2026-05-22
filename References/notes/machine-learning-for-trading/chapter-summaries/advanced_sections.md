# Advanced Sections

These notes are outline-driven. They are meant to mark the technical parts of the book that are worth deeper study or separate implementation work.

## Market Microstructure and Filings

Source chapters:
- Chapter 02 - Market & Fundamental Data

Advanced TOC sections:
- Reconstructing the limit order book from NASDAQ ITCH
- Working with XBRL-encoded electronic filings

Why this is advanced:
- Order book reconstruction is event-driven state management, not simple bar-based analysis.
- Filing work adds schema parsing, issuer/entity normalization, and reporting-timeline problems.

What to retain:
- Microstructure features depend on message order, queue state, spread, and signed flow.
- Filing features depend on point-in-time availability, not fiscal period labels alone.
- Both workflows are data-engineering-heavy before any ML starts.

## Factor Engineering and Portfolio Construction

Source chapters:
- Chapter 04 - Alpha Factor Research
- Chapter 05 - Portfolio Optimization and Performance Evaluation
- Chapter 24 - Alpha Factor Library

Advanced TOC sections:
- Wavelets and Kalman filters for de-noising
- Mean-variance optimization and alternatives
- Multivariate factor evaluation

Why this is advanced:
- Most mistakes come from unstable preprocessing or over-trusting noisy factor performance.
- Portfolio construction turns signal quality into realized risk, turnover, and crowding.

What to retain:
- A factor is not useful until it survives point-in-time alignment, neutralization, and out-of-sample evaluation.
- De-noising can improve signal extraction, but it can also bury implementation assumptions if it is not transparent.
- Portfolio design is part of the model, not a post-processing afterthought.

## Time-Series and Bayesian Modeling

Source chapters:
- Chapter 09 - Time Series Models
- Chapter 10 - Bayesian ML

Advanced TOC sections:
- ARIMA and SARIMAX
- Volatility forecasting with ARCH/GARCH-style models
- VAR models
- Cointegration and pairs trading
- Bayesian updating, probabilistic programming, Bayesian Sharpe, stochastic volatility

Why this is advanced:
- These models are assumption-sensitive and easy to misuse on non-stationary market data.
- Bayesian methods add a second layer of complexity because you are modeling both parameters and uncertainty.

What to retain:
- Stationarity checks, rolling recalibration, and regime drift matter more than one-off in-sample fit.
- Cointegration is about stable long-run relationships, not just high correlation.
- Bayesian outputs are useful when confidence and posterior uncertainty affect sizing or model selection.

## Tree Ensembles and Unsupervised Learning

Source chapters:
- Chapter 12 - Boosting your Trading Strategy
- Chapter 13 - Unsupervised Learning

Advanced TOC sections:
- LightGBM, XGBoost, and CatBoost workflows
- SHAP and partial dependence for model interpretation
- PCA and ICA for data-driven factors
- Manifold learning with t-SNE and UMAP
- Hierarchical clustering and hierarchical risk parity

Why this is advanced:
- Boosted trees are often strong baselines, but feature leakage and cross-validation errors can make them look much better than they are.
- Unsupervised methods are powerful but easy to over-interpret because there is no ground truth target.

What to retain:
- Tree models need time-aware validation, careful feature generation, and turnover-aware signal conversion.
- PCA factors can help with compression and latent structure, but they can drift as the covariance structure changes.
- t-SNE and UMAP are primarily exploratory, not portfolio rules by themselves.
- HRP is most useful as a robust allocation framework when covariance estimation is noisy.

## NLP Representation Learning

Source chapters:
- Chapter 15 - Topic Modeling
- Chapter 16 - Word Embeddings

Advanced TOC sections:
- LSI, pLSA, and LDA
- Topic evaluation and visualization
- word2vec, GloVe, and custom embeddings
- Domain-specific embeddings for financial news and SEC filings

Why this is advanced:
- Text models fail quietly when preprocessing, vocabulary control, or timestamp alignment is weak.
- Financial text adds sparse labels, shifting language, and domain-specific terminology.

What to retain:
- Topic models are useful for document structure, clustering, and feature generation, but topic stability matters.
- Embeddings are useful when context matters more than raw token counts.
- Filing and earnings-call features need publication timestamps and entity linking before they are tradable.

## Deep Learning Architectures

Source chapters:
- Chapter 17 - Deep Learning
- Chapter 18 - CNN
- Chapter 19 - RNN
- Chapter 20 - Autoencoders

Advanced TOC sections:
- Neural network design, regularization, and optimization
- CNNs for images and time-series-as-images
- LSTM and GRU sequence models
- Autoencoders, seq2seq autoencoders, and variational autoencoders
- Conditional autoencoders for return forecasts

Why this is advanced:
- These chapters shift from feature engineering by hand toward learned representations and larger training loops.
- Model capacity, data volume, hardware, and monitoring all become first-class concerns.

What to retain:
- Deep models are only worth the complexity if the data type or scale actually benefits from representation learning.
- CNN and RNN architectures should be matched to data geometry: grid-like data for CNNs, sequential dependencies for RNNs.
- Autoencoders are best viewed as representation tools first and trading models second.

## Synthetic Data and Trading Agents

Source chapters:
- Chapter 21 - GANs
- Chapter 22 - Deep Reinforcement Learning

Advanced TOC sections:
- TimeGAN and synthetic time-series generation
- DQN-style agents and OpenAI Gym trading environments

Why this is advanced:
- Both chapters move away from direct supervised prediction into simulator-dependent learning.
- Evaluation is harder because realism, stability, and usefulness are all separate questions.

What to retain:
- Synthetic data is only valuable if it preserves structure that improves downstream learning or robustness tests.
- RL performance is highly dependent on environment design, reward definition, action space, and market-friction realism.
- Backtest overfitting risk is even higher when the agent can repeatedly adapt to a narrow simulated world.
