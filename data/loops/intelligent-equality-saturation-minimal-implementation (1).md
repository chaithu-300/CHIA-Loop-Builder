# Intelligent Equality Saturation: From Hierarchical Prospection to a Minimal Implementation
### Presented at the Architecture 2.0 Workshop (ISCA 2026)

## 1. Overview and Core Challenge
Equality saturation is a powerful technique in compiler optimization and hardware compilation. It operates by applying rewrite rules to represent an expression as an e-graph of equivalent forms, then extracting the optimal representation. However, e-graphs often suffer from "combinatorial explosion," making the search for the minimal implementation extremely slow on large programs.

This work introduces **Intelligent Equality Saturation**, applying agentic heuristics to guide the rewriting process.

## 2. Methodology & Architecture
* **Hierarchical Prospection**: An agent analyzes the e-graph structure and prospectively evaluates which class of rewrite rules (e.g., algebraic simplification, loop-unrolling, datapath merging) is most likely to yield significant PPA reductions.
* **Dynamic Rule Pruning**: Active agents prune redundant or high-latency paths in the e-graph, preventing the graph from saturating with low-value equivalences.
* **Minimal Implementation Search**: Focuses the optimization search space toward target hardware compiler instructions (e.g., lower-level CIRCT or LLVM representations), extracting optimized code in a fraction of the time of standard saturation algorithms.

## 3. Core Contribution
By guiding rewrite applications with intelligent heuristics, this framework maintains the formal verification guarantees of equality saturation while rendering it scalable to large-scale hardware descriptions and compiler IRs.