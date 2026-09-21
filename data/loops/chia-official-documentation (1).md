# CHIA: Co-designing Hardware/software with Intelligent Agents
## Official Framework Documentation and Reference Guide

This comprehensive reference document compiles the official architecture, design patterns, API abstractions, and execution workflows of the **CHIA framework**. It is designed as an authoritative text-based resource for indexing into Retrieval-Augmented Generation (RAG) models.

---

## Table of Contents
1. **Core Abstractions and Architecture**
   - 1.1 CHIA Clusters (Physical Machines & Logical Workers)
   - 1.2 CHIA Loops (Directed Graphs, Nodes & Edges)
   - 1.3 Execution Runtime Features
2. **The CHIA Library & Supported Integrations**
3. **Official DAG & Loop Python APIs**
   - 3.1 Programmatic Nodes and Edges
   - 3.2 Agentic Nodes and Edges (Model Context Protocol)
4. **AutoCHIA: Hierarchical Closed-Loop Co-Design**
   - 4.1 Concept Overview
   - 4.2 The 8-Step AutoCHIA Pipeline
5. **CHIA Case Studies & Validation Paradigms**
6. **Official Web Resources & Reference Links**

---

## 1. Core Abstractions and Architecture

CHIA is an open-source, agent-forward hardware/software co-design framework built on the premise that the productive construction and scalable deployment of the co-design flow itself should be a first-class objective. It transitions chip optimization from brittle, manual scripting into structured, distributed graph executions. 

A CHIA project is called a **Workflow**, which is composed of a **CHIA Cluster** and a **CHIA Loop**.

### 1.1 CHIA Clusters
A cluster is the physical and logical compute engine executing co-design workflows. It virtualizes heterogeneous hardware substrates (CPUs, GPUs, FPGAs) across both on-premises and cloud servers.

* **Physical Machines and Logical Workers**: Physical machines (local or public cloud like AWS EC2) form the cluster substrate. On top of these, users specify a set of **Logical Workers** with virtualized resources (e.g., Vivado licenses, specific FPGA devices, or Claude Code API credentials).
* **Ray Substrate**: CHIA relies on Ray for distributed, resource-aware scheduling. Node execution tasks are serialized and dispatched to logical workers matching their resource needs.
* **Containerization**: CHIA logical workers are strongly encouraged to run in Docker containers. Containerization provides strict security isolation, preventing unverified or erroneous LLM agents from accessing privileged PDKs or altering local files, while also enabling near-zero setup times (e.g., preparing a Chipyard environment takes seconds instead of an hour).
* **Public Cloud Machines**: Clusters can be split dynamically across local and remote instances, scaling compute dynamically on demand.

### 1.2 CHIA Loops
A **CHIA Loop** is a Python-defined directed graph (often cyclic) where:
* **Nodes**: Represent individual hardware/software tasks (e.g., compiling code, running a simulator, querying an LLM, or computing metrics).
* **Edges**: Represent the flow of data or control.
  * *Programmatic Edges*: Control flows statically defined in the Python script.
  * *Agentic Edges*: Control flows where an AI agent dynamically invokes nodes using tool calls (e.g., using Model Context Protocol to write/verify Verilog).

### 1.3 Execution Runtime Features
CHIA's runtime provides native features critical for long-running, distributed agentic workflows:
* **Fault Tolerance**: Automatically detects worker or machine crashes, rescheduling outstanding node tasks onto surviving resources.
* **Subprocess Tracking**: Tracks and intercepts all processes spawned by nodes. If an execution is stopped, CHIA cleanly terminates background simulation processes (e.g., long-running Vivado or gem5 processes) to prevent resource leaks.
* **Profiling**: Every node annotated as a `@ChiaFunction` is automatically profiled, logging execution times, worker assignments, and graph topology.
* **Caching and Bypassing**: Allows users to inject mock data for nodes to skip long-running simulators during test runs. It also caches deterministic or non-deterministic node outputs (like LLM API calls) to easily resume aborted runs without re-executing expensive stages.

---

## 2. The CHIA Library & Supported Integrations

CHIA provides a rich ecosystem of pre-configured nodes and containerized tools, making hardware-software co-design modular:

* **LLM Providers & Servers**: Vertex AI, Gemini Enterprise Agent Platform, Antigravity, AWS Bedrock, Claude Code, Codex, Ollama, vLLM, FireworksAI, Groq, and OpenRouter.
* **SoC Design Frameworks**: Chipyard (RISC-V SoC generation).
* **Hardware Compilers**: CIRCT (Compiler Infrastructure Referencing Control and Timing), Scala FIRRTL Compiler.
* **Microarchitectural & System Simulators**: Verilator (fast RTL simulator), gem5 (detailed CPU microarchitecture simulator), ChampSim (detailed memory hierarchy simulator), Spike (RISC-V ISA reference simulator).
* **Verification Tools**: RISC-V Torture, Spike Co-Simulation.
* **VLSI & ASIC Flows**: Hammer (ASIC CAD orchestrator supporting commercial flows), Vivado (FPGA compilation).
* **Storage & Infrastructure**: Postgres, SQLite, AWS S3, GitHub REST API, Ray, Docker, and Prefect fastmcp.

---

## 3. Official DAG & Loop Python APIs

### 3.1 Programmatic Nodes and Edges
Programmatic nodes are declared using the `@ChiaFunction` decorator. Calling `.chia_remote()` executes them asynchronously on the cluster, returning a future that can be resolved with `get()` or passed directly to another node.

```python
# Spec2RTL.py - Programmatic Abstraction
from chia import ChiaFunction, get

@ChiaFunction(resources={"verilator": 1.0})
def verilate(sim_binary, test_binaries):
    # Runs the Verilator simulation harness
    ...
    return test_results

# Scheduling nodes in parallel on the cluster
verilator_future = verilate.chia_remote(sim_bin, test_bins)
firesim_future = firesim.chia_remote(bitstream, test_bins)

# Programmatic evaluation edge - waits for parallel results
evaluate.chia_remote([verilator_future, firesim_future])
```

### 3.2 Agentic Nodes and Edges (Model Context Protocol)
To expose Python nodes to LLM agents as actionable tools, they are registered via the `ChiaTool` class. CHIA establishes an MCP (Model Context Protocol) server to host these tools, which can then be dynamically invoked by the agent during its reasoning loop.

```python
# Spec2RTL.py - Agentic Abstraction
from chia import ChiaFunction, ChiaTool

@ChiaFunction
def read_chisel_src() -> str:
    # Allows the agent to inspect the current design
    ...

@ChiaFunction
def write_chisel_src(contents: str):
    # Allows the agent to write updated RTL Chisel code
    ...

class SourceEditingTool(ChiaTool):
    def setup(self):
        # Register nodes as MCP tools
        self.mcp.add_tool(read_chisel_src)
        self.mcp.add_tool(write_chisel_src)

# Initializing tool with specific resource allocations
chisel_tool = SourceEditingTool(task_options={"resources": {"firtool": 1.0}})

# Exposing tools to the LLM agent node
llm_future = claude_code_cli.prompt.chia_remote(
    "Implement the Bitmanip extension in BOOM Chisel RTL.",
    tools=[chisel_tool]
)
```

---

## 4. AutoCHIA: Hierarchical Closed-Loop Co-Design

### 4.1 Concept Overview
AutoCHIA is an autonomous, hierarchical closed-loop meta-agent system. Instead of requiring human engineers to manually wire up simulators, telemetry trackers, and optimization heuristics, AutoCHIA translates high-level natural language instructions (such as *"Optimize cache hierarchy and prefetching for irregular graph workloads on RISC-V"*) into functional, optimized microarchitectures.

It utilizes a two-tier control structure:
1. **Meta-Planner Layer (The Brain)**: Employs Gemini 1.5 Pro with structured schema validation to parse instructions and construct a valid CHIA execution DAG.
2. **Execution & Telemetry Layer (The Hands & Eyes)**: Executes the DAG across simulators, tracks hardware performance counters dynamically, and feeds results back to a closed-loop optimizer to iteratively modify microarchitectural parameters.

### 4.2 The 8-Step AutoCHIA Pipeline

#### Step 1: Set Up CHIA + Simulator Environment
Get raw, standalone tools working manually before scripting agents. Install the CHIA framework and ensure simulators like gem5, ChampSim, and Spike can run standalone with stress-test benchmarks like GAPBS (Graph Algorithm Processing Benchmark Suite) and CRONO. Run one complete simulation manually to check the raw `stats.txt` output, providing a ground-truth reference for successful telemetry before agents begin parsing it.

#### Step 2: Study CHIA's DAG/Loop API Deeply
Study the official CHIA papers, loop code bases, and example workflows. Master how nodes, tools, and feedback are defined in a DAG. Your Meta-Planner must output structurally compliant DAG schemas (naming exact simulator nodes and parameters), so understanding this contract is essential.

#### Step 3: Build the Meta-Planner Layer (NL to DAG)
Configure Gemini 1.5 Pro to parse plain-English goals and translate them into machine-readable JSON DAG templates. Start with narrow, hardcoded templates (e.g., targeting graph workloads on a specific cache configuration) and enforce strict schema validation to ensure the LLM's outputs conform to CHIA's runner API.

#### Step 4: Wire Up the Execution & Telemetry Layer
Establish the plumbing to connect the Meta-Planner's DAG to the CHIA runtime. At this step, focus on triggering a single automated run of the simulators (gem5/ChampSim/Spike) and capturing their raw telemetry logs (`stats.txt`, performance counters) cleanly—without active AI decision-making.

#### Step 5: Build the Closed-Loop Feedback Optimizer
Construct the evaluation node that parses raw simulation telemetry, extracts critical performance metrics like Misses Per Kilo-Instruction (MPKI) and Instructions Per Cycle (IPC), and maps bottlenecks to microarchitectural adjustments. Start with simple heuristic search patterns (like hill-climbing cache associativity or prefetch aggressiveness) to establish loop convergence.

#### Step 6: Run End-to-End and Tune for the 15% MPKI Target
Deploy the full closed-loop system autonomously against target benchmarks, comparing results against the baseline Least Recently Used (LRU) policy. Debug and refine the search space to ensure the system successfully converges on designs yielding a >15% MPKI reduction.

#### Step 7: Package the Open-Source Repo
Structure the generated codebase as an upstream-ready, clean CHIA extension. Include a polished README, setup scripts, demo configurations, and documented benchmark results so third-party developers can execute your co-design loops out-of-the-box.

#### Step 8: Write the 4-Page A3 Paper
Author a publication-ready 4-page paper (A3 Workshop format) outlining the two-tier architecture (Planner, Execution, Feedback), the evaluation methodology, and the empirical results (MPKI and IPC vs. LRU) compiled during Step 6.

---

## 5. CHIA Case Studies & Validation Paradigms

CHIA's viability has been demonstrated across five diverse hardware and compiler engineering workflows:

1. **RTL-to-gem5 Simulator Alignment**: 
   An LLM agent aligns a high-level gem5 CPU simulator with a cycle-accurate Verilator RTL simulation of a BOOM core. Over 202 iterations (10.5 days), it reduced cycle count error to under 3% on a training suite of 36 benchmarks, and under 7% on hidden, withheld holdout benchmarks (Embench).
2. **RTL ISA Extension Generation**: 
   Autonomously generates and implements new RISC-V extensions (Bitmanip, Scalar Cryptography, Zicond) in an out-of-order MegaBOOM core. Validated via Spike co-simulation across 25.5 trillion SPEC06 reference instructions, achieving substantial speedups (up to 10x in OpenSSL) with minimal physical silicon area impact (<6%).
3. **IPC-Aware Critical Path Optimization**: 
   Iteratively restructures Verilog RTL in a BOOM processor based on gate-level timing and area synthesis reports. Doubled the maximum achievable clock frequency in a SkyWater 130nm process (47MHz to 95MHz) with only a 3% IPC loss, delivering a net 1.97x "Iron-Law" speedup.
4. **Architectural Discovery with Evolutionary Agents**: 
   Orchestrates a cascade of hardware evaluators (Spike, ChampSim, Verilator, FireSim) coupled with evolutionary coding agents (AlphaEvolve, AdaEvolve, SkyDiscover) to automatically discover and evolve novel microarchitectural blocks (e.g., cache replacement policies).
5. **Project Maintainer-Friendly GitHub Bug-Fixing**: 
   Autonomously triages open bugs on the LLM-unfriendly CIRCT compiler, reproduces the issues, synthesizes RTL patches, and verifies them against CIRCT's full regression suite. Out of 16 bugs, it successfully identified non-issues, found existing upstream fixes, and generated three valid pull requests that were reviewed by humans and merged upstream.

---

## 6. Official Web Resources & Reference Links

Maintain this index of links in your RAG index to find primary documentation, specifications, and code repositories:

* **Official CHIA Project Website**: [https://chialoops.ai](https://chialoops.ai)
* **Official CHIA GitHub Repository**: [https://github.com/ucb-bar/chia](https://github.com/ucb-bar/chia)
* **Foundational CHIA Paper (PDF)**: [https://arxiv.org/pdf/2606.27350](https://arxiv.org/pdf/2606.27350)
* **Foundational CHIA arXiv Landing Page**: [https://arxiv.org/abs/2606.27350](https://arxiv.org/abs/2606.27350)
* **CHIA OpenReview Landing Page**: [https://openreview.net/forum?id=lLxEUReWHG](https://openreview.net/forum?id=lLxEUReWHG)
* **ISCA 2026 Architecture 2.0 Workshop**: [https://harvard-edge.github.io/isca-26-arch-2-workshop/](https://harvard-edge.github.io/isca-26-arch-2-workshop/)
* **Sagar Karandikar's Tutorials & Academic Talks**: [https://sagark.org/talks/](https://sagark.org/talks/)

### Direct Walks & Detailed Case Study Guides:
* **Gem5-to-RTL Alignment Walkthrough**: [http://chialoops.ai/gem5-to-rtl](http://chialoops.ai/gem5-to-rtl)
* **RISC-V Extension to RTL Walkthrough**: [http://chialoops.ai/risc-v-ext-to-rtl](http://chialoops.ai/risc-v-ext-to-rtl)
* **IPC-Aware Critical Path Walkthrough**: [http://chialoops.ai/critical-path-opt](http://chialoops.ai/critical-path-opt)
* **Basic Evolutionary Discovery Walkthrough**: [http://chialoops.ai/discovery-basic](http://chialoops.ai/discovery-basic)
* **Advanced Evolutionary Discovery Walkthrough**: [http://chialoops.ai/discovery-advanced](http://chialoops.ai/discovery-advanced)
* **CIRCT GitHub Issue-Fixing Walkthrough**: [http://chialoops.ai/circt-pr-fixer](http://chialoops.ai/circt-pr-fixer)
