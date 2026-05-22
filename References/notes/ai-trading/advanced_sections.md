# Advanced Sections

## Chapter 7 - Reinforcement Learning for Hedging

- This is the most advanced chapter in the current AI-trading set.
- The key ideas are discrete hedging under realistic frictions, simulation-based training, policy learning, and deployment in a QuantConnect workflow.
- The sections to revisit first are the simplified RL approach, the identification/simulation/refinement loop, and the implementation details around the policy network.

## Chapter 8 - Corrective AI and Conditional Parameter Optimization

- This chapter is advanced because it is not just forecasting; it is using ML to filter or correct an existing trading or portfolio process.
- The most useful parts are Corrective AI, Conditional Parameter Optimization, feature engineering, and the seasonal FX application.
- Operationally, this is closer to meta-labeling and adaptive parameter selection than to end-to-end autonomous trading.

## Chapter 9 - LLMs and Generative AI in Trading

- This chapter is advanced in workflow design rather than in financial math.
- The important pieces are model selection, prompt engineering before fine-tuning, retrieval-augmented use cases, and cost/performance trade-offs.
- For practical implementation, the useful distinction is between research-assistant workflows and genuinely tradable model outputs.

## Repo Examples Worth Revisiting

- SVM plus wavelets, PCA plus clustering, Temporal CNN, Amazon Chronos, and FinBERT are the highest-signal examples if the goal is transferable strategy ideas.
- The LLM summarization example is useful as a research-augmentation pattern, but it still needs careful timestamping and downstream signal design.

## Best First Pass

- Start with Chapter 7 if you want the most original material.
- Read Chapter 8 next if you already have baseline strategies and want a predictive overlay.
- Read Chapter 9 when the bottleneck is text-heavy research workflow rather than price modeling.
