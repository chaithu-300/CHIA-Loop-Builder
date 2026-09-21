# RTLScout: Joint Agentic Code and Synthesis Optimization for Efficient Digital Circuits
## Paper Reference & Overview

### 1. Abstract and Core Concept
RTLScout is a joint optimization framework that addresses a major challenge in Electronic Design Automation (EDA): the extreme sensitivity of gate-level PPA results to both the RTL source code structure and the specific downstream synthesis recipes. RTLScout simultaneously explores and optimizes both dimensions using cooperative AI agents.

### 2. Multi-Agent Optimization Pipeline
*   **Agentic Code Refactoring**: Employs LLM agents to rewrite high-level RTL structures (such as restructuring multiplexer trees or adder networks).
*   **Agentic Gate-Level Rewriting**: Integrates symbolic e-graph rewriting with technology-aware cost functions (Yosys) to optimize the gate netlist.
*   **Arithmetic Architecture Scanning**: Automatically sweeps alternative hardware structures (e.g., parallel prefix architectures or Dadda/Wallace multipliers) to match the target workload constraints.
*   **Quantitative PPA Feedback**: Drives the physical design flow using Yosys and OpenROAD, feeding exact, post-placement power, performance, and area metrics back to the agents to guide the search.

### 3. Empirical Evaluation
*   Evaluated on a fully IEEE-754-compliant 16-bit floating-point multiplication unit with exception support.
*   RTLScout successfully navigated the combined search space to deliver an overall area reduction of 35% while fully preserving timing constraints and functional correctness.
