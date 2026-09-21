# CHIA: An Open-Source Framework for Principled, Agentic AI-Driven Hardware/Software Co-Design Research

**Authors:** Angela Cui*, Ferran Hermida-Rivera*, Jack Toubes*, Raghav Gupta, Jim Fang, Chengyi Lux Zhang, Ella Schwarz, Junha Kim, Yakun Sophia Shao, Borivoje Nikolić, Christopher W. Fletcher, Sagar Karandikar  
*University of California, Berkeley*  
*(Equal Contribution)*  
**License:** Creative Commons Attribution 4.0 International License

---

## Abstract
Agentic artificial intelligence shows great promise for radically improving the pace of innovation in hardware/software co-design research across computer architecture, systems, compilers, and VLSI. Thus far, however, applications of AI in these contexts have generally been demonstrated in isolated settings on small-scale problems, due to the difficulty of designing and deploying complex AI-infused hardware and software development workflows. 

This paper introduces **CHIA**, an open-source hardware/software co-design framework for agile and principled research on the application of AI to co-design. CHIA treats the productive construction and scalable deployment of the co-design flow itself as a first-class objective. In CHIA, agentic AI-driven hardware and software design flows are expressed as **CHIA loops**: directed cyclic graphs whose nodes execute various system-on-chip design tools, microarchitectural simulators, software build systems, AI models, evolutionary coding agents, and more. 

The CHIA library provides node implementations for many popular tools, including Chipyard, gem5, ChampSim, FireSim, Hammer (supporting several commercial ASIC CAD tools), Vivado, AlphaEvolve, AdaEvolve, and many others. CHIA also provides a broad set of features to conduct principled science around these flows. These include isolation between AI models and hardware tools, profiling mechanisms, fault-tolerant execution, and reliability at scale across hundreds of heterogeneous systems (CPUs, FPGAs, GPUs, etc., across public cloud/on-prem.).

To showcase CHIA, we present five CHIA loops as case studies:
1. Automatic RTL-to-gem5 simulator alignment
2. LLM-driven implementation of microarchitectural features in RTL
3. Agentic, IPC-aware critical path optimization
4. Evolutionary architectural discovery
5. Maintainer-friendly agentic GitHub issue fixing

---

## 1. Introduction
The design of modern computing systems is a challenging and labor-intensive endeavor. Architects, system designers, compiler engineers, and VLSI specialists must navigate enormous design spaces while reasoning across several abstraction layers, including software, architecture, microarchitecture, and physical implementation. Pushing the limits of co-design across these layers remains an important challenge and opportunity.

Recent advances in agentic artificial intelligence offer an opportunity to accelerate the pace of innovation in both hardware design and at the hardware/software boundary. For example, in November 2025, Gupta et. al. demonstrated the ability to harness AI to automatically generate new state-of-the-art microarchitectural components (cache replacement policies) using the context of established design championships. As another case-in-point, Krishna, et. al. recently demonstrated the generation of a 5-stage RISC-V microprocessor design from scratch using agentic AI. Computer architecture has clearly entered a new era, wherein humans, agents, and existing hardware design tools must all smoothly operate together.

Naively deploying existing hardware design workflows is not sufficient to tackle this question. Writing bespoke scripts that glue together the output of one tool into the input of the next tool (or AI model) breaks easily and does not scale well to large AI-driven design flows on hundreds of heterogeneous machines. Shifting from script writing to building a distributed and scalable implementation of each bespoke AI-driven design flow is error-prone and imposes immense engineering cost, even with AI-assistance. 

Relying strictly on agents to orchestrate the entire design flow (e.g., letting a coding agent "run wild" inside system-on-chip design frameworks or microarchitectural simulators) makes it challenging to enforce verification and validation requirements that are critical to successful hardware design while minimizing human review overhead. 

We built **CHIA** to address this problem. CHIA enables agile and principled research on the application of AI to co-design by making complex AI-infused workflows easy to express, deploy, and study. In CHIA, the expression of a design flow is called a **CHIA loop**, which is a directed cyclic graph whose nodes execute various SoC design tools, microarchitectural simulators, software build systems, AI models, evolutionary coding agents, and more.

---

## 2. CHIA Design Goals
To enable users to build productive, agile, AI-driven design workflows, CHIA meets the following key design goals:
*   **Massive Parallelism Support:** Agentic loops can perform tasks at a huge scale, implementing tens or hundreds of designs in parallel. CHIA's graph-based loop abstraction allows users to build parameterized, massive-scale design pipelines simply.
*   **Resource-Aware & Fault-Tolerant Scheduling:** Tasks in hardware design loops occupy a wide range of latencies (milliseconds to days) and have diverse and strict resource requirements (e.g., FPGAs for simulation, GPUs for model serving, or ASIC CAD tools). CHIA schedule resource requests onto heterogeneous substrates.
*   **Modularity & Tool Portability:** CHIA provides plug-and-play support for many different co-design tools with various input/output formats.
*   **Programmatic & Agentic Orchestration:** Control flow in a design loop is not always static. CHIA supports both programmatic edges and agentic decision-making, where the AI agent is given tool-using capability to adapt a workflow on the fly.
*   **Built-in Telemetry & Profiling:** CHIA features first-class support for data collection and profiling of both loop results and loop execution behaviors to enable principled evaluation.

---

## 3. The CHIA Workflow Abstraction
A CHIA project is called a **workflow**, and is composed of a **CHIA cluster** and a **CHIA loop**.

### 3.1 Clusters & Logical Workers
*   **Logical Workers:** A cluster starts with a collection of physical machines. On top of these, users specify logical workers—virtualized representations of the hardware and software environment. Nodes in the CHIA loop specify the types and quantities of resources they need, and the CHIA runtime schedules these using **Ray**.
*   **Containerization:** Placing logical workers inside Docker containers isolates unverified or potentially erroneous LLM agents from accessing sensitive proprietary PDKs, while simultaneously automating and speeding up environment setup (e.g., spinning up a fresh Chipyard environment in seconds rather than an hour).
*   **Public Cloud Machines:** CHIA clusters can be split across on-premises/owned computing resources and remote/rented computing resources from the public cloud (like AWS c5.9xlarge instances), allowing cost-effective scaling of heavy simulations (like Verilator or FireSim).

### 3.2 CHIA Loops (Nodes & Edges)
*   **Nodes:** A CHIA node is a Python function (annotated with `@ChiaFunction`) that performs a step in a hardware/software design pipeline, often by invoking some underlying hardware/software design tool. Nodes are scheduled and dispatched asynchronously, returning a future that can be blocked on or passed downstream.
*   **Programmatic Edges:** Represent explicit data/control flow statically defined in the Python orchestration program (e.g., connecting a build node's output directly to a simulator node).
*   **Agentic Edges:** Arise when an AI agent uses tool-calling (via the **Model Context Protocol**) to run nodes dynamically on the fly. By supporting both programmatic and agentic edges, CHIA generalizes across a broad spectrum of design patterns, giving users fine-grained control over how much autonomy is delegated to the AI.

---

## 4. Design & Interfaces

### 4.1 Cluster Configuration (YAML)
CHIA clusters are configured using a YAML schema that mapping physical machines, cloud instances, and logical workers. For example:
```yaml
aws_nodes:
  verilator_aws:
    InstanceType: c5.9xlarge
    count: 2
    ImageId: ami-0ec10929233384c7f
provider:
  head_ip: CPU1
available_node_types:
  Verilator_Runner:
    docker:
      image: "chia-verilator-run:latest"
    resources: {"verilator": 1}
    min_workers: 3
    max_workers: 3
    compatible_ips: [CPU3, verilator_aws:0, verilator_aws:1]
```
Clusters are managed using a Command Line Interface (CLI):
*   `chia up <config>.yaml` starts the cluster, spawns cloud nodes, and constructs containerized workers.
*   `chia down <config>.yaml` brings the cluster down.
*   `chia up <config>.yaml --add` dynamically scales resources or restarts dead workers.

### 4.2 Loop Interface (Python)
Programmatic nodes are declared with `@ChiaFunction`. An asynchronous remote task is scheduled using `fn_name.chia_remote(args)`, returning a future that can be collected via `get()`.
```python
@ChiaFunction(resources={"verilator": 1.0})
def verilate(sim_binary, test_binaries):
    ...
```

Agentic nodes are bound as MCP tools and managed by `ChiaTool` subclasses, overriding `setup()`:
```python
class rw_src_tool(ChiaTool):
    def setup(self):
        self.mcp.add_tool(read_chisel_src)
        self.mcp.add_tool(write_chisel_src)
```

---

## 5. Runtime Features
*   **Fault Tolerance:** CHIA leverages Ray's distributed scheduling to reschedule tasks automatically if a worker or machine crashes during a long-running execution.
*   **Subprocess Tracking:** CHIA tracks all processes spawned by nodes. If a node or loop is cancelled, CHIA stops all spawned subprocesses, preventing resources from leaking (e.g., avoiding stray Vivado compile runs).
*   **Profiling:** All functions annotated with `@ChiaFunction` are automatically profiled. Results (start time, wall-clock time, worker ID, reconstructed task graph) are automatically logged and can be viewed in TensorBoard or Weights & Biases.
*   **Caching & Bypassing:** Nodes can be bypassed by injecting mock data to stand in for long-running node outputs. Caching persists results on disk, enabling fast restarts or deterministic reproduction of LLM API behaviors.

---

## 6. The CHIA Library & Integrations
CHIA pieces together a diverse set of platforms out of the box:
*   **LLM Providers:** Vertex AI/Gemini Enterprise, AWS Bedrock, Claude Code, Codex, Ollama, vLLM, FireworksAI, Groq, OpenRouter.
*   **SoC Design:** Chipyard (RISC-V SoC framework).
*   **Hardware Compilation:** CIRCT, Scala FIRRTL Compiler.
*   **Simulators:** Verilator, FireSim, gem5, ChampSim.
*   **Verification:** RISC-V torture, Spike co-simulation.
*   **VLSI:** Hammer (supporting commercial CAD tools).
*   **Orchestration Core:** Built on **Ray** for high-performance distributed execution, surpassing standard orchestration frameworks in handling complex cyclic workflows and resource-aware scheduling.

---

## 7. Case Studies

### 7.1 Automatic RTL-to-gem5 Simulator Alignment
*   **Goal:** Keep high-level simulators (gem5) aligned with actual RTL processor core models (Berkeley Out-of-Order Machine - BOOM).
*   **Workflow:** An agent (Claude Code with Opus 4.6) is given access to gem5 C++ source files and configuration scripts. In each iteration, it is asked to modify microarchitectural structures in gem5. The updated simulator is run and compared to Verilator RTL reference cycles across 36 training benchmarks.
*   **Results:** Over 202 iterations (10.5 days), the CHIA loop aligned gem5 to within 3% cycle count error relative to BOOM RTL. It successfully generalized to withheld Embench benchmarks (under 7% misalignment error).
*   **Cost:** Average cost of $11.72 per iteration.

### 7.2 Automatically Implementing RISC-V ISA Extensions in RTL
*   **Goal:** Implement new instruction extensions (RISC-V Bitmanip, Crypto, Zicond) in an out-of-order processor RTL (4-wide MegaBOOM).
*   **Workflow:** A 3-stage loop:
    1.  *Stage 1:* LLM designs RTL, evaluated by a small verification test suite.
    2.  *Stage 2:* Verifies no regression of the base ISA using upstream RISC-V ISA tests.
    3.  *Stage 3:* Subjects the RTL to massive random instruction mixes (riscv-dv) and triggers ASIC synthesis.
*   **Results:** Successfully implemented and verified extensions. Bitmanip and Zicond survived all 25+ trillion instructions of the SPEC06 reference suite in a full Linux-booting FireSim simulation. Bitmanip achieved a 5.6% speedup; Zicond achieved a 3.5% speedup. Scalar Crypto achieved a 10x throughput improvement on OpenSSL benchmarks. Area impact was negligible (<5% in SkyWater 130nm and 16nm).

### 7.3 IPC-Aware Automated Critical Path Optimization in RTL
*   **Goal:** Optimize processor clock frequency by restructuring critical timing paths in RTL without degrading IPC.
*   **Workflow:** The loop parses synthesis reports from a commercial gate-level synthesis tool using the open Skywater 130nm PDK. An agent modifies BOOM Chisel code to break long timing paths, while Verilator/FireSim nodes measure and enforce IPC.
*   **Results:** Frequency more than doubled from 47 MHz to 95 MHz in the best iteration. IPC loss was limited to 3.28% on SPEC06 reference benchmarks, resulting in a net Iron-Law speedup of 1.97x (nearly doubling overall performance).
*   **Cost:** Only $202 in total API credits across 14 iterations.

### 7.4 Agentic Architectural Discovery with Evolutionary Coding Agents
*   **Goal:** Express evolutionary discovery loops (like ArchAgent) inside CHIA.
*   **Workflow:** CHIA couples SkyDiscover and evolutionary algorithms (such as AdaEvolve, EvoX, GEPA, and OpenEvolve) with a multi-level cascade of evaluators (Spike, gem5, ChampSim, Verilator, FireSim, Hammer).
*   **Power of CHIA:** Cache-and-bypass allows developers to easily pause, correct bugs, and fast-forward through days-long evolutionary runs without restarting the cluster.

### 7.5 Automatically Addressing GitHub Issues in the CIRCT Compiler
*   **Goal:** Autonomously find, reproduce, and fix verified bugs in compiler repositories to reduce maintainer burden.
*   **Workflow:** Programmatic triage filters out issues without code blocks or with existing PRs. LLM nodes assess if the issue is a bug with an unambiguous solution, write a reproduction script, and modify C++ source. A programmatic verification stage tests the fix against CIRCT's full regression suite with zero AI involvement.
*   **Results:** Out of 16 randomly selected GitHub issues, the loop correctly triaged and bug-fixed 5 real issues. Three non-trivial pull requests were generated and successfully merged into the official CIRCT upstream master branch.

---

## 8. Discussion, Related Work & Future Work
*   **Bottleneck Shift:** With agentic AI making implementation virtually instantaneous, the new primary bottleneck in chip design is evaluation and verification. Shorter representative benchmarks, faster cycle-accurate simulators, and high-fidelity PPA estimation tools are critical.
*   **Privileged Information:** PDK data is often highly confidential and cannot be sent to public models. Solutions include developing techniques to abstract PPA metrics or optimizing small, locally hosted open hardware LLMs inside secure CHIA logical workers.
*   **Conclusion:** CHIA reframes hardware co-design by shifting focus from bespoke, one-off AI scripts to building, scaling, and rigorously evaluating design flows as first-class citizens.
