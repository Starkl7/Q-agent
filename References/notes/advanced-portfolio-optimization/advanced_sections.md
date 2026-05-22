# Advanced Sections

## Parameter Estimation

- Chapter 3 is where the math starts to matter: VAR/VMA/VARMA setups, shrinkage estimators, random matrix denoising, and detoning.
- Chapter 4 is important if you want factor-model inputs that are more stable than raw sample moments.
- Chapter 5 is the key bridge from equilibrium views to practical portfolio construction through Black-Litterman.
- Chapter 6 is advanced because the choice of codependence metric changes clustering, diversification, and downstream optimization behavior.

## Optimization Core

- Chapter 7 matters for alternative risk measures and the convex formulation behind them.
- Chapter 8 is the core allocation engine: return-risk trade-offs, objective design, and solver-aware formulations.
- Chapter 9 adds real-world constraints, which is where elegant theory starts colliding with actual portfolio mandates.
- Chapter 10 covers risk parity, which is widely used but easy to misuse if covariance inputs are unstable.
- Chapter 11 is advanced because robust optimization forces explicit treatment of estimation error rather than assuming the inputs are correct.

## Machine Learning Portfolio Design

- Chapter 12 covers hierarchical clustering portfolios, which are useful when covariance estimation is noisy.
- Chapter 13 moves into graph-theory-based portfolios, which is more structural and less standard than classic mean-variance workflows.

## Backtesting and Synthetic Data

- Chapter 14 is worth attention because synthetic data generation affects stress testing and robustness claims.
- Chapter 15 matters because portfolio ideas that look strong in optimization can still fail under realistic backtesting rules.

## Best First Pass

- Start with Chapters 3, 5, 8, 10, 11, and 12.
- If the goal is research infrastructure, add Chapters 14 and 15 early.
- If the goal is clustering-based allocation, focus on Chapters 6, 12, and 13 together.
