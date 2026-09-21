# LongRTL: Graph-Similarity-Guided LLM-Driven Long Context RTL Optimization
## Paper Reference & Overview

### 1. Abstract and Core Challenge
Large Language Models excel at generating and refactoring small, self-contained Verilog modules, but fail on large, flat, and highly coupled industrial RTL codebases. In these files, control paths, datalaths, and state machines are heavily interleaved, causing the model to lose structural focus, exhaust context windows, and generate syntactically or functionally invalid code. LongRTL solves this via structural AST-guided decomposition.

### 2. The Three-Step Optimization Workflow
1.  **Decomposition (AST Extraction)**: Parses flat, long Verilog modules into an Abstract Syntax Tree (AST) graph. It automatically identifies and extracts independent functional blocks (e.g., arithmetic units, priority encoders, barrel shifters, state machines) by comparing AST sub-graphs against a library of 55 standard hardware design templates.
2.  **Specialized Agentic Optimization**: Passes each segmented sub-module to dedicated, specialized LLM sub-agents. Because the sub-agents operate on small, clean code blocks with clear PPA targets, they can perform highly effective optimizations without losing context.
3.  **Reconstruction**: A specialized reconstruction agent takes the optimized sub-modules and joins them back together according to the original AST dependency graph, ensuring that top-level port interfaces, clock domains, and logic relations remain intact and functionally identical.

### 3. Key Findings
*   Moves past the naive "long-context window" approach to mimic the hierarchical decomposition methodology used by real human chip designers.
*   Allows large codebases (thousands of lines of Verilog) to be safely refactored and optimized for PPA without risking functional breakage.
