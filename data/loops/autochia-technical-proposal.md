# AutoCHIA: Autonomous Closed-Loop Co-Design in CHIA
## Technical Proposal & Architecture

**Track**: Cross-SoC Optimization of Cache Hierarchies / Microarchitectural Analysis  
**Target Venue**: A³ Workshop, MICRO 2026

---

### 1. Task Overview
Modern Hardware/Software (HW/SW) co-design requires navigating complex, multi-tool workflows comprising architectural simulators, synthesis suites, compilers, and profiling platforms. While the CHIA framework introduces modular abstractions to orchestrate these agentic flows, manually assembling multi-stage loops—binding simulator nodes, specifying environments, and formulating feedback heuristics—remains a significant barrier to entry.

We propose **AutoCHIA**, a hierarchical meta-agent framework that takes high-level, natural language hardware objectives (e.g., *"Optimize L2/L3 cache hierarchies and prefetch policies for irregular memory-bound graph workloads on RISC-V"*) and autonomously:
1. Decomposes the goal into an executable CHIA Directed Acyclic Graph (DAG).
2. Synthesizes and executes the loop across heterogeneous simulator backends.
3. Ingests execution telemetry in real time, iteratively mutates architectural parameters, and outputs Pareto-optimal designs.

---

### 2. Methodology & Loop Design
AutoCHIA operates as a two-tier closed loop consisting of the following modules:

```
[ Natural Language Goal ]
           │
           ▼
┌──────────────────────────────────────┐
│        Meta-Planner Layer            │  <-- Gemini 1.5 Pro
│   Translates Goal into compliant DAG  │
└──────────────────────────────────────┘
           │
           ▼ (CHIA DAG Configuration)
┌──────────────────────────────────────┐
│    Execution & Telemetry Layer       │  <-- CHIA Runtime Worker Nodes
│ Drives Simulators: gem5 / ChampSim    │
└──────────────────────────────────────┘
           │
           ▼ (stats.txt & logs)
┌──────────────────────────────────────┐
│    Closed-Loop Feedback Optimizer    │  <-- Computes MPKI & IPC
│ Evaluates bottlenecks & mutates params│
└──────────────────────────────────────┘
           │
           └──── (Iterative Parameter Adjustment) ────┘
```

#### Meta-Planner Layer
Utilizes **Gemini 1.5 Pro** with structured schema validation over indexed CHIA APIs. This layer translates natural language prompts into syntactically compliant CHIA execution DAGs, dynamically mapping and binding required simulator and profiler nodes.

#### Execution & Telemetry Layer
Deploys the synthesized loop via CHIA's Ray-based distributed runtime. The loop orchestrates various hardware simulators (**gem5**, **ChampSim**, or **Spike**) running standard, memory-intensive benchmark kernels such as the Graph Algorithm Processing Benchmark Suite (**GAPBS**) and **CRONO**.

#### Closed-Loop Feedback Optimizer
An evaluation node programmatically parses raw simulation logs (e.g., `stats.txt` or hardware performance counters), calculates Misses Per Kilo-Instruction (**MPKI**) and instructions per cycle (**IPC**), diagnoses memory subsystem bottlenecks, and iteratively mutates architectural parameters (cache line size, associativity, and prefetch throttle limits) until convergence is reached.

---

### 3. Expected Results
*   **Open-Source AutoCHIA Package**: An upstream-ready, modular CHIA extension enabling zero-shot generation and autonomous execution of co-design loops.
*   **Automated Cache Optimization Demonstration**: Achieving a **>15% reduction in MPKI** and improved overall IPC compared to default Least-Recently-Used (LRU) baseline cache-replacement policies across intensive graph-processing workloads.
*   **Final Deliverables**: A fully reproducible public GitHub repository and a 4-page A3 Workshop paper outlining the architecture and experimental results.

---

### 4. Cloud Compute & Credit Budget
The total requested budget of **$850** is justified across the following resource categories:

| Resource Category | Description & Justification | Estimated Cost |
| :--- | :--- | :--- |
| **Gemini 1.5 Pro / Flash APIs** | Meta-loop generation, schema validation, and multi-turn iterative reasoning (~3.5M tokens/day) | **$350** |
| **GCP Compute Engine (n2-standard-16)** | Multi-threaded gem5/ChampSim simulation sweeps and automated test harness runs | **$450** |
| **Cloud Storage & Artifacts** | Benchmark trace datasets, container image hosting, and checkpoint logging | **$50** |
| **Total Requested Credits** | | **$850** |
