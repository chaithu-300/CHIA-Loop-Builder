# Agent Factories for High Level Synthesis: How Far Can General-Purpose Coding Agents Go in Hardware Optimization?

## Metadata
* **Authors/Organization**: Abhishek Bhandwaldar, Mihir Choudhury, Ruchir Puri, and Akash Srivastava (IBM / MIT)
* **Venue/Date**: arXiv:2603.25719, March 2026
* **Category**: 📄 Research / 🔧 Technical
* **Reference**: [CHIA Paper Reference [14]](https://arxiv.org/abs/2603.25719)

## Executive Summary
This paper investigates the boundaries and capabilities of general-purpose software coding agents (such as Claude Code and Gemini-based agents) when applied directly to hardware compilation and optimization tasks, specifically targeting **High-Level Synthesis (HLS)**. The study explores whether an autonomous, LLM-based agent factory can effectively optimize C/C++ representations of hardware to yield better post-synthesis performance, power, and area (PPA) metrics.

## Key Technical Themes & Insights

### 1. The Challenge of Hardware Context for Software Agents
* **Amdahl's Abstraction Gap**: Software agents are highly proficient at optimizing algorithmic complexity (e.g., standard big-O speedups). However, they frequently struggle to comprehend the physical, parallel-execution hardware structures implied by sequential C/C++ code.
* **Over-reliance on Pragmas**: The paper demonstrates that general coding agents initially rely almost exclusively on standard loop unrolling (`#pragma HLS unroll`) or pipelining (`#pragma HLS pipeline`) without understanding memory port constraints or array partitioning, leading to severe resource congestion and synthesis failures.

### 2. The "Agent Factory" Architecture
* **Structural Scaffold**: To counter these limitations, the authors introduce a structured "factory" that wraps the general-purpose agent. 
* **Tool-Grounded Self-Correction**: The agent is bound directly to an HLS compiler. Rather than proposing changes in a single shot, the agent iteratively:
  1. Rewrites C/C++ code structures.
  2. Synthesizes the design using a commercial HLS tool.
  3. Parses the synthesis warnings, resource utilization tables, and estimated clock latency.
  4. Automatically corrects pragmas and memory partition arrays based on compiler feedback.

### 3. Key Findings & Performance Boundaries
* **The Optimization Ceiling**: While general-purpose agents can successfully optimize small, standard compute kernels (e.g., matrix-vector multiply or convolutional layers), their effectiveness decays on large, complex nested-loop designs where memory bandwidth (non-sequential memory access) limits performance.
* **Co-design Potential**: The paper concludes that while software agents are not "hardware-native," grounding them in closed-loop compiler telemetry allows them to reach or exceed human-baseline PPA results on 70% of standard HLS benchmark suites.
