# AgenticDSE: A Multi-Agent Design Space Exploration Framework for Chiplet Accelerators
### Presented at the Architecture 2.0 Workshop (ISCA 2026)

## 1. Overview and Core Challenge
Chiplet-based accelerators introduce an incredibly complex design space, including choices for 2.5D/3D packaging, heterogeneous core counts, local cache capacities, and network-on-chip (NoC) routing topologies. Navigating this space with conventional simulators is computationally prohibitive.

**AgenticDSE** introduces a multi-agent design space exploration (DSE) framework featuring multi-phase Bayesian Optimization.

## 2. Methodology & Architecture
AgenticDSE decomposes the massive chiplet search parameters into isolated, specialized agent layers:
* **NoC and Interconnect Agent**: Optimizes network routing, bandwidth allocation, and physical chiplet placement to minimize data transfer latency.
* **Memory Hierarchy Agent**: Explores tile-level L1/L2 cache sizing, set associativity, and off-chip HBM interface routing.
* **Core Compute Agent**: Configures heterogeneous processing element (PE) counts and matrix-execution unit dimensions.
* **Multi-Phase Bayesian Optimization (BO)**: A global coordination agent aggregates recommendations, building a surrogate cost model (PPA vs. packaging cost) to steer Bayesian search away from physically unfeasible chiplet layouts.

## 3. Impact on Hardware Design
AgenticDSE significantly accelerates the discovery of Pareto-optimal chiplet accelerator configurations, enabling rapid architectural pathfinding for high-performance AI workloads.