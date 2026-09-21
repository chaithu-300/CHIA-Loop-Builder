# Dr. RTL: Autonomous Agentic RTL Optimization through Tool-Grounded Self-Improvement
## Paper Reference & Overview

### 1. Abstract and Core Concept
Dr. RTL is an autonomous agentic framework designed to optimize the timing, power, performance, and area (PPA) of Register-Transfer-Level (RTL) designs. While Large Language Models (LLMs) can generate Verilog code, optimizing that code for physical implementation remains a major bottleneck. Dr. RTL addresses this by keeping physical synthesis and verification tools directly in the optimization loop.

### 2. Closed-Loop Methodology
*   **Analysis Agent**: Parses raw synthesis and timing reports (from Yosys, OpenROAD, or commercial physical design suites) to identify the specific critical path and gate delays.
*   **Verilog Refactorer**: A specialized sub-agent (such as Claude Code) that receives the original Verilog code along with the critical path feedback to propose targeted architectural refactorings.
*   **Sequential Equivalence Checking (SEC)**: To prevent functional regressions, every proposed modification is formally verified against the original golden RTL using SEC tools before proceeding.
*   **Iterative Timing Optimization**: The loop runs up to 10 major optimization rounds, with 5 minor recovery attempts allowed per round to fix syntax errors or equivalence mismatches.

### 3. Key Findings
*   Automates high-effort timing closure tasks that normally consume days of physical design engineering time.
*   Discovers hardware optimization patterns (e.g., restructuring linear logic chains into log-depth trees) entirely through closed-loop tool feedback.
