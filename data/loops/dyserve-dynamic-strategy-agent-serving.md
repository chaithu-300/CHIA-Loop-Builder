# Dyserve: Dynamic Strategy Generation for Agent Serving
### Presented at the Architecture 2.0 Workshop (ISCA 2026)

## 1. Overview and Core Challenge
Agentic workflows heavily utilize optional operators (such as self-verifiers, routers, LLM retries, and escalation layers). However, current agent platforms typically commit to a fixed pipeline per task type. This is structurally suboptimal: different requests, varying models, and live cluster runtime conditions favor different subsets of operators.

**Dyserve** introduces a system designed to perform dynamic strategy generation to serve LLM agents efficiently.

## 2. Methodology & Architecture
Dyserve operates on three primary principles:
* **Dynamic Synthesis of Orchestration**: Instead of executing a static DAG, Dyserve dynamically decides which verification, routing, or code-generation sub-agents to invoke based on task difficulty, requested accuracy, and live server latency.
* **Pipelined Resource Optimization**: Schedules heavy reasoning agents (like full Verilog coders) only when lighter verification steps fail, protecting GPU/CPU serving capacity.
* **Feedback-Aware Strategy Mutator**: Observes execution times and correctness feedback in a closed loop to dynamically shift the system balance between high-effort planning models and rapid, low-latency execution routines.

## 3. Core Insights
By dynamically adjusting the serving layout per agent request, Dyserve maintains high reliability and task accuracy while significantly lowering serving costs and latency overheads compared to fixed-pipeline execution frameworks.