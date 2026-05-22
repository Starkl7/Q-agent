# Understanding Deep Learning Notes

Working notes for selected chapters of *Understanding Deep Learning* by Simon Prince
(`books/UnderstandingDeepLearning/`).

UDL is a general deep-learning textbook, not finance-specific. These notes intentionally
cover only the chapters that have a plausible payoff for quant work in this workspace.
Computer-vision, image-generation, and game-RL material is skipped on purpose — the goal
is foundational depth where it supports signal research, not a parallel ML curriculum.
Treat `repos/machine-learning-for-trading/` as the primary finance-targeted reference;
reach for UDL when ML4Trading's coverage of the underlying mechanics is too shallow.

## Quant-relevant chapters

| Ch | Topic | Why it pays rent |
|---|---|---|
| 5 | Loss functions | Picking the right loss for noisy financial targets (Huber, quantile, NLL) |
| 6 | Fitting models | SGD/Adam behaviour on small, noisy tabular data |
| 7 | Gradients & initialization | Why deep nets misbehave on price-feature inputs |
| 8 | Performance & regularization | Dropout, weight decay, early stopping — the only things keeping a financial NN honest |
| 9 | Training neural networks | Schedulers, batch sizes, label smoothing — applied to walk-forward training |
| 12 | Transformers | Sequence models for order book / news / regime detection |
| 16 | Normalizing flows | Density estimation for return distributions and risk |
| 19 | Reinforcement learning | Foundations for the RL hedging work in `notes/ai-trading/` |
| 20 | Graph neural networks | Cross-sectional models that respect sector / supply-chain structure |

Chapters explicitly *not* worth notes here: 10 (CNNs for images), 11 (residual nets in
vision), 14–15 (unsupervised image models), 17–18 (diffusion / GANs for images),
21 (deep learning theory — read once, no notes).

## Structure

- `chapter-summaries/`: one short summary per chapter listed above
- `qc-relevance/`: how each topic maps (or doesn't) to LEAN, walk-forward backtests,
  and the data available in this workspace

## Naming

- `ch08_summary.md`, `ch08_qc_relevance.md`, etc.
- If a chapter becomes a real strategy, spin up a project in `MyProjects/` rather than
  growing these notes.
</content>
</invoke>