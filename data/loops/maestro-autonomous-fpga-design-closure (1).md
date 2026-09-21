# MAESTRO: A Multi-Agent EDA Orchestrator for Autonomous FPGA Design Closure
### Presented at the Architecture 2.0 Workshop (ISCA 2026)

## 1. Overview and Core Challenge
Achieving physical design closure (meeting timing, area, and power constraints) in FPGA flows requires navigating a massive and high-dimensional space of synthesis and place-and-route parameters. This process historically requires extensive, iterative manual tuning by experienced hardware engineers.

**MAESTRO** is an agentic orchestrator designed to autonomously drive physical design tools toward design closure.

## 2. Methodology & Architecture
MAESTRO partitions the design-space search among a team of specialized cooperative agents:
* **Timing-Closure Agent**: Analyzes critical path routing logs from Vivado/Quartus, isolating specific logical nets causing setup/hold violations.
* **Area-Optimization Agent**: Evaluates look-up table (LUT) and block RAM utilization, suggesting register-retiming or resource-sharing options.
* **Synthesis Coordinator Agent**: Programmatically alters Vivado physical synthesis properties (e.g., fanout limits, placement heuristics) and schedules parallel synthesis sweeps.
* **Multi-Phase Optimization**: The agents interact via a shared whiteboard pattern, negotiating PPA trade-offs until constraints are fully closed and verified.

## 3. Key Findings
Autonomous multi-agent negotiation allows MAESTRO to achieve timing closure on complex, congested RTL designs with substantially fewer synthesis iterations than naive random searches or single-agent black-box optimization algorithms.