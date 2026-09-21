# ArchAgent: Agentic AI-Driven Computer Architecture Discovery
## Paper Reference & Overview

### 1. Abstract and Core Concept
ArchAgent is the first agentic, evolutionary, generative AI system capable of automatically discovering novel, high-performing microarchitectural mechanisms without human bias. Rather than simply tuning continuous parameters (such as cache capacity or bus width), ArchAgent generates entirely new algorithms and code logic (such as cache replacement policies).

### 2. Evolutionary Methodology
*   **AlphaEvolve / SkyDiscover Integration**: Combines large language models with a distributed, massive-scale evaluation cluster.
*   **C++ Code Generation**: The agent acts as an architect, generating complete, compilable C++ classes representing microarchitectural controllers.
*   **Cascade of Evaluators**: Candidates are simulated across cycle-accurate simulators like ChampSim and gem5 running standard SPEC CPU2006 workloads.
*   **Reward Hacking Protection**: Implements strict assertion verification to prevent agents from exploiting simulator corner-cases (e.g., drop-traffic exploits to artificially inflate hit rates).

### 3. Key Achievements
*   Automatically discovers state-of-the-art cache replacement policies that outperform prior human-designed algorithms.
*   Enters and wins benchmark competitions (such as established cache replacement championships) completely autonomously.
*   Demonstrates how distributed AI-guided evolution can compress months of human architectural brainstorming into days of automated compute sweeps.
