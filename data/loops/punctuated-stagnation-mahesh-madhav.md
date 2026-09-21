# Research Presentation: Punctuated Stagnation
**Author:** Mahesh Madhav
**Venue:** Session 3 (Benchmarking and Evaluation of Agentic Architecture), ISCA 2026

## Key Concepts
In LLM-driven architectural discovery and optimization runs, the progress of evolutionary coding agents is rarely linear. This paper characterizes the phenomenon of **Punctuated Stagnation** in hardware co-design loops.

### The Stagnation Profile
* **Stagnation Plateaus**: AI agents often spend consecutive generations or iterations stuck at a specific performance ceiling (e.g., timing delays or cache MPKI limits). 
* **The "Punctuated" Leap**: Breakthroughs happen in sharp, non-linear jumps when the agent discovers a structurally distinct mechanism (e.g., shifting from linear-depth queues to log-depth reduction trees) rather than tweaking scalar parameters.
* **Implications for Exploration**: Standard search budget metrics (tokens spent vs. performance gained) mischaracterize these loops if evaluated in short windows. The paper argues for adaptive reasoning-effort steering to help agents exit plateaus without exhausting API budgets.