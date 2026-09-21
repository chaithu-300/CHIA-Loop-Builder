# ACE-RTL: When Agentic Context Evolution Meets RTL-Specialized LLMs

## Metadata
* **Authors/Organization**: Chenhui Deng, Zhongzhi Yu, Guan-Ting Liu, Nathaniel Pinckney, Brucek Khailany, and Haoxing Ren (NVIDIA)
* **Venue/Date**: arXiv:2602.10218, February 2026
* **Category**: 📄 Research / 🔧 Technical
* **Reference**: [CHIA Paper Reference [28]](https://arxiv.org/abs/2602.10218)

## Executive Summary
Generating and debugging Register-Transfer-Level (RTL) code using LLMs is severely bottlenecked by context limitations. Real-world RTL modules operate within deep file hierarchies and are highly coupled with other submodules and verification scripts. **ACE-RTL** introduces a dynamic, agentic method for context evolution that selectively retrieves, abstracts, and updates module dependencies to help hardware-specialized LLMs generate functionally correct Verilog.

## Key Technical Themes & Insights

### 1. The Context Bottleneck in RTL Design
* **Flat vs. Hierarchical Code**: Simple code generators treat RTL as isolated text blocks. Real physical silicon, however, has complex signal propagation and clock/reset relationships across deep module hierarchies.
* **Context Dilution**: Flooding an LLM's prompt window with thousands of lines of dependent modules degrades reasoning quality, causing model distraction and syntax regressions.

### 2. Context Evolution Mechanism (ACE)
* **Dynamic Abstract Representation**: ACE-RTL does not feed raw Verilog submodules to the LLM. Instead, it compiles submodules into compact Abstract Syntax Trees (ASTs) and interface-only summaries (showing only module ports, parameters, and timing expectations).
* **Stateful Updating**: As the LLM agent modifies a module, an orchestration loop updates the dependency graph in real time, shifting the context window to focus on the immediate signals, variables, or clock domains affected by the change.

### 3. Key Findings & QoR
* **Improved Synthesis Success**: ACE-RTL paired with RTL-specialized models increases compilation and synthesis success rates on industrial-scale SoC microarchitectures by over 34% compared to standard static RAG systems.
* **Functional Correctness**: The system ensures zero timing loops and eliminates dead-lock states in generated finite state machines (FSMs) through structural and timing validation feedback loops.
