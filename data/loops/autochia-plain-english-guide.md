# AutoCHIA: In Simple Terms
## A Beginner's Guide to Autonomous Cache Hierarchy Co-Design

AutoCHIA is an automated framework designed to optimize chip cache hierarchies using natural language objectives. 

### Core Concept
Normally, an engineer must manually wire together all the pieces of a hardware-software co-design loop:
* Picking which microarchitectural simulator to use.
* Defining the workload/benchmarks to run.
* Formulating what "success" or convergence looks like.
* Writing the heuristic logic that adjusts hardware parameters based on performance feedback.

AutoCHIA eliminates this manual bottleneck. By utilizing a high-level natural language prompt—such as *"optimize L2/L3 cache and prefetching for irregular memory-bound graph workloads on RISC-V"*—the system autonomously constructs, executes, and refines the entire design loop.

---

### The Two-Tier Architecture
AutoCHIA is divided into two primary logical layers:

#### 1. The Planner (The "Brain")
* **Powered by**: Gemini 1.5 Pro.
* **Role**: Interprets high-level natural language instructions and translates them into a machine-readable, structurally validated Directed Acyclic Graph (DAG) of execution nodes. It acts as a digital architect, deciding which simulation and profiling tools are required and how data should flow between them.

#### 2. The Executor + Feedback Loop (The "Hands and Eyes")
* **Role**: Carries out the scheduled tasks in the DAG using low-level microarchitectural simulators.
* **Mechanism**: Runs target benchmarks on simulators, collects and parses output performance counters, and feeds metrics back to a closed-loop optimizer. The optimizer modifies parameters and triggers a new simulation run, iterating until the design converges.

---

### The 8-Step Build Pipeline
To implement and build AutoCHIA, follow this structured, incremental timeline:

#### Step 1: Set up CHIA + Simulator Environment
* **CHIA Framework**: The core open-source execution substrate. It acts as an "operating system" for chip design agents, allowing the modular integration of simulators, build tools, and LLMs.
* **gem5**: A detailed, highly configurable, cycle-accurate architectural simulator. It simulates CPU and memory subsystem behavior at a low level, which is thorough but slow.
* **ChampSim**: A lightweight, fast simulator focused specifically on cache hierarchies and prefetchers. Excellent for rapid, high-volume iterations.
* **Spike**: The reference functional ISA simulator for RISC-V, used to verify program correctness rather than cycle performance.
* **GAPBS & CRONO**: Benchmark suites comprising graph-processing workloads (social network traversals, etc.). They feature irregular, unpredictable memory accesses that heavily stress cache structures.
* *Why it matters*: Run a single simulation manually first. Confirm you can execute a simulator, run a benchmark, and read the resulting `stats.txt` performance counter output. This provides the baseline "ground truth" to verify your automated environment behaves correctly.

#### Step 2: Study CHIA's DAG/Loop API Deeply
* **DAG (Directed Acyclic Graph)**: A flow of tasks (Nodes) connected by directional paths (Edges) without cyclic logic.
* **Node**: A discrete Python function wrapping a specific tool (e.g., simulator run, AI prompt, data parser).
* **CHIA Loop**: A runnable program mapping the DAG onto logical workers.
* *Why it matters*: The Meta-Planner must produce valid execution configurations that match CHIA's syntax. Studying existing example loop documentation prevents generating plausible-looking but broken graph definitions.

#### Step 3: Build the Meta-Planner Layer (NL to DAG)
* **Goal**: Translate natural language text into a structured DAG (typically JSON) specifying simulator nodes, benchmarks, and target parameters.
* **Schema Validation**: Explicitly validate LLM outputs against CHIA schemas to catch malformed structure or missing required keys before execution.
* *Why it matters*: Start narrow by hardcoding a template for a single objective. Prove the planner outputs a valid DAG, then generalize to broader requests.

#### Step 4: Wire up the Execution & Telemetry Layer
* **Execution**: Automatically launch simulators (gem5/ChampSim/Spike) specified in the compiled DAG.
* **Telemetry**: Capture live simulation logs, hardware performance counters, and the raw `stats.txt` file as simulations run.
* *Why it matters*: Focus on the plumbing. Ensure you can trigger a simulator programmatically and successfully capture output data without any optimization intelligence applied yet.

#### Step 5: Build the Closed-Loop Feedback Optimizer
* **Closed-loop System**: An iterative setup where output performance data directly informs the next input configuration (similar to a thermostat).
* **Target Metrics**:
  * **MPKI (Misses Per Kilo-Instruction)**: The number of cache misses per 1,000 instructions. Lower MPKI indicates a highly efficient memory hierarchy.
  * **IPC (Instructions Per Cycle)**: The number of instructions completed per cycle. Higher IPC represents better processing speed.
* **Target Parameters**:
  * **Cache Line Size**: The atomic unit block size moved in and out of the cache.
  * **Associativity**: The set-associative layout determining where data can be placed (ranges from direct-mapped to highly set-associative).
  * **Prefetch Throttle**: Regulates prefetch aggressiveness to prevent cache pollution and bandwidth waste.
* **Strategy**: Implement simple hill-climbing heuristics (testing small parameter changes and continuing in beneficial directions) before adding complex search algorithms.

#### Step 6: Run End-to-End and Tune for the 15% MPKI Target
* **LRU Baseline**: The default Least-Recently-Used replacement policy is the control baseline.
* **Optimization Goal**: Achieve a greater than 15% reduction in MPKI alongside improved IPC compared to the LRU baseline.
* *Why it matters*: This is the most time-consuming phase. Debug convergence issues, tune parameter scaling, and ensure the loop converges on stable, optimal configurations.

#### Step 7: Package the Open-Source Repo
* Clean up your project directory. 
* Write extensive installation guides, setup READMEs, example execution runs, and benchmark outcomes.
* Ensure the code is polished enough to serve as an upstream-ready extension that can be merged back into the core CHIA project.

#### Step 8: Write the 4-page A3 Paper
* Draft a short academic-style paper documenting:
  1. The two-tier architectural design (Planner + Execution/Telemetry).
  2. The precise feedback loop and optimization methodology.
  3. Experimental results showing the verified MPKI and IPC improvements relative to the LRU baseline.
