# KEET: Explaining Performance of GPU Kernels Using LLM Agents

## Metadata
* **Authors/Organization**: Joshua H. Davis, Klaudiusz Rydzy, Srinivasan Ramesh, Aadit Nilay, Daniel Nichols, Swapna Raj, Nikhil Jain, and Abhinav Bhatele (University of Maryland)
* **Venue/Date**: arXiv:2605.04467, May 2026
* **Category**: 📄 Research / 💬 Opinion
* **Reference**: [CHIA Paper Reference [27]](https://arxiv.org/abs/2605.04467)

## Executive Summary
Optimizing high-performance GPU kernels (such as custom CUDA kernels for deep learning) requires deep expertise in memory hierarchies, coalescing, tensor core usage, and occupancy constraints. **KEET** is an agentic, trace-grounded framework that utilizes large language models to analyze execution trace metrics and explain performance bottlenecks to human developers, effectively acting as an automated performance engineering advisor.

## Key Technical Themes & Insights

### 1. Trace-Grounded Reasoning
* **Bridging the Raw Metric Gap**: Performance profilers (like NVIDIA Nsight Compute) produce thousands of raw hardware performance counters (e.g., DRAM throughput, warp issue efficiency, static vs. dynamic shared memory allocation). Humans find these difficult to synthesize quickly.
* **Automated Explanation Synthesis**: KEET uses an LLM agent to parse raw profiling outputs, map them to specific GPU hardware constraints, and generate clear, natural-language explanations of *why* a particular kernel is underperforming.

### 2. KEET Agent Framework Design
* **Closed-loop Diagnostics**: The framework runs the target kernel on physical GPUs, automatically captures execution traces, translates trace data into a structured token representation, and passes it to the agent.
* **Targeted Refactor Recommendations**: Beyond diagnosing issues (such as "shared memory bank conflicts in warp 4"), KEET provides direct code recommendations to refactor the CUDA/HIP source code to maximize tensor core utilization and avoid memory divergence.

### 3. Key Findings
* **Diagnostic Accuracy**: KEET achieves high accuracy in identifying performance-limiting bottlenecks on standard deep learning kernels (e.g., FlashAttention and layered MLP operators) compared to seasoned human performance architects.
* **API Efficiency**: Grounding model prompts in structured trace-to-text abstractions prevents model hallucination and significantly reduces prompt sizes, leading to cost-effective performance debugging.
