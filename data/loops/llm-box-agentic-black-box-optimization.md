# LLM-Box: An Agentic Framework for Guided Black-Box Optimization

## Metadata
* **Authors/Organization**: Sujay Pandit, Akanksha Jain, Rami Cohen, Zhijie Deng, Sagar Karandikar, Sagi Perel, Anand Raghunathan, and Parthasarathy Ranganathan (NVIDIA / UC Berkeley / Purdue)
* **Venue/Date**: NeurIPS / ML for Systems Workshop, November 2025
* **Category**: 📄 Research / 📊 Report
* **Reference**: [CHIA Paper Reference [79]](https://openreview.net/forum?id=W2htGuo9de)

## Executive Summary
Mapping modern Large Language Models onto specialized, heterogeneous hardware accelerators is a high-dimensional, non-convex optimization problem. **LLM-Box** is an agentic search framework designed to find Pareto-optimal compiler configurations, memory allocations, and mapping choices, significantly reducing the time spent searching infeasible execution regions.

## Key Technical Themes & Insights

### 1. The High-Dimensional DSE Problem
* **Combinatorial Explosion**: Compiler options, quantization precision thresholds, cluster routing paths, tensor slicing parameters, and scheduling schemes form a massive, discrete design-space exploration (DSE) boundary.
* **Infeasible Region Bottleneck**: Standard black-box optimizers (such as random search or classic Bayesian Optimization) spend up to 80% of their compute budgets executing invalid or extremely suboptimal compiler configurations that crash the target system.

### 2. Agentic Guided Search (LLM-Box)
* **LLM as the Prior Guide**: LLM-Box uses a reasoning agent to analyze the mathematical architecture of the model being mapped, outputting localized "hypotheses" about which configurations will run efficiently.
* **Pruning Infeasible Points**: The agent prunes the search space by evaluating candidate parameter pairs before they are ever compiled or run, bypassing configurations that are structurally guaranteed to cause memory overflow or resource underutilization.

### 3. Results & Convergence Acceleration
* **Search Speedup**: LLM-Box reaches Pareto-optimal compiler and hardware mapping configurations in **12x fewer search steps** compared to state-of-the-art Bayesian optimizers.
* **Real-World Impact**: Evaluated on mapping LLM architectures (like LLaMA-style transformer blocks) onto specialized tensor processors, the agent autonomously discovered mapping configurations that lowered execution latency by 18% compared to hand-tuned industrial baseline settings.
