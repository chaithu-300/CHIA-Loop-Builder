# Argus: Agentic, Reference-Calibrated, Tree-Guided, System-Level Bottleneck Localization
### Presented at the Architecture 2.0 Workshop (ISCA 2026)

## 1. Overview and Core Challenge
In modern heterogeneous cloud and datacenter systems, locating system-level microarchitectural bottlenecks is extremely difficult. Traditional performance analysis requires deep expert domain knowledge to interpret hardware performance counters, and static heuristics often fail under dynamic, multi-tenant workloads. 

**Argus** addresses this by introducing an agentic, reference-calibrated, and tree-guided approach to automate system-level bottleneck localization.

## 2. Methodology & Architecture
Argus structures the bottleneck diagnostic space as a hierarchical tree:
* **Tree-Guided Diagnostic Search**: Rather than scanning millions of hardware metrics exhaustively, Argus uses a decision-tree reasoning pattern. It begins at top-level metrics (e.g., pipeline stalls, cache miss ratios) and branches down into specific functional units (e.g., load-store queues, execution port contention) based on performance symptoms.
* **Reference Calibration**: To avoid false positives under normal high-load execution, Argus calibrates incoming hardware counters against baseline reference traces run on similar functional hardware under optimal conditions.
* **Closed-Loop Verification**: Once a potential bottleneck is identified, Argus suggests microarchitectural adjustments or software pinning policies, executing a short validation run in a loop to verify if the diagnostic alignment resolves the latency.

## 3. Impact on HW/SW Co-Design
* Automated localization of complex, transient memory-hierarchy issues (e.g., speculative load-store queue issues).
* Simplifies cluster telemetry analysis for cloud providers, shifting the burden of microarchitectural bottleneck diagnosis from human system engineers to autonomous agents.