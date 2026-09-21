# ARES: Adaptive Reasoning-Effort Steering for PPA- and Cost-Aware RTL Optimization with LLM Agents
## Paper Reference & Overview

### 1. Abstract and Core Challenge
Large language model (LLM) agents optimize RTL designs by iterating over code edits, synthesis runs, and PPA analysis. However, every call to a frontier model incurs a direct API dollar cost. Prior RTL agent frameworks failed to normalize their final performance against their total computational cost, often relying on fixed reasoning budgets per call. ARES addresses this by treating the reasoning-effort budget as a steerable, dynamic parameter.

### 2. Core Innovations
*   **Dynamic Effort Steering**: Instead of spending high reasoning budgets uniformly across all iterations, ARES uses a "patience counter." It starts with low-effort, low-cost LLM queries. It escalates to deeper reasoning-effort levels (e.g., models with extended chain-of-thought tokens) only when progress stalls.
*   **Cost-Aware Accounting**: Introduces a normalized dollar-cost-per-call metric plotted alongside the Figure of Merit (FoM), enabling fair evaluation across different optimizers.
*   **Memory Ablation Findings**: Empirical results demonstrate that highly engineered long-term memory frameworks do not provide reliable benefits over simple historical context concatenation of the agent's trials.

### 3. Empirical Results
*   On unseen test designs, ARES achieves a 23-27% deeper Figure of Merit reduction at equal normalized cost compared to fixed-effort baselines.
*   Closes up to 83% of the performance gap between raw LLM drafts and highly hand-optimized multiply-accumulate (MAC) units.
*   Achieves 25% deeper optimization than state-of-the-art frameworks like Dr. RTL while consuming only 12% of the input/output tokens.
