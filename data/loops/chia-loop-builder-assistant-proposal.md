# CHIA Loop-Builder Assistant
## Hackathon Proposal — A³ Workshop, MICRO 2026

---

### 1. Task Overview
Building an AI-driven hardware/software co-design flow within the CHIA framework currently requires extensive manual work. Designers must read through the core documentation, study existing case studies (such as RTL implementation, simulator alignment, critical-path optimization, architectural discovery, or GitHub issue triage), and translate their research objectives into a specific graph of nodes and edges. This manual compilation acts as a steep barrier to entry for computer architects and system designers new to CHIA.

We propose the **CHIA Loop-Builder Assistant**: an autonomous agent that translates a natural language request (e.g., *"optimize cache hierarchy for a mobile-class workload"*) into a fully structured, runnable CHIA loop configuration. 

The generated output specifies:
* A complete node graph.
* Tool bindings (e.g., gem5, ChampSim, Verilator, Hammer, FireSim, or evolutionary/LLM nodes).
* Edge semantics (programmatic or agentic).
* A clear explanation of the design and architectural choices.

Unlike generic LLMs prompted cold, the Loop-Builder Assistant is grounded directly in CHIA's official documentation, example loops, and API references via a Retrieval-Augmented Generation (RAG) index. Furthermore, each generated configuration undergoes rigorous schema validation to guarantee that all output workflows use syntactically correct node definitions and parameter types.

---

### 2. Methodology & Phases
The development of the assistant is structured into four main phases:

#### Phase 1 — Knowledge Base Indexing
We ingest CHIA's documentation, the foundational research paper, and all published example loops into a structured, retrievable vector database. This indexing preserves node type definitions, edge behaviors, tool-binding constraints, and cluster configuration schemas as structured metadata.

#### Phase 2 — Loop-Builder Agent
An orchestrating agent, powered by the **Claude API**, parses the user's plain-English intent, retrieves the most structurally relevant existing CHIA loops as reference patterns, and synthesizes a new configuration tailored to the user's objective, providing a detailed design rationale for each decision.

#### Phase 3 — Structural Validation & Dry-Run
The generated JSON loop configurations are verified using schema checkers. To prove functionality, the assistant executes at least one compiled loop on a lightweight, simplified test scenario (e.g., a fast ChampSim or gem5 simulation run), showing that the generated loop can boot and run without errors.

#### Phase 4 — Empirical Iteration & Evaluation
We systematically compare agent-generated loops against established, hand-built baseline loops. Based on areas where the configurations diverge or throw errors, we refine prompting constraints and RAG retrieval parameters to maximize syntactic and semantic accuracy.

---

### 3. Expected Results
* **Functional Loop-Builder Assistant**: A working agent that turns a one-sentence natural language specification into a structurally valid, runnable CHIA loop configuration.
* **Worked Case Studies**: 2–3 end-to-end examples spanning different design domains (e.g., simulator alignment, ASIC physical synthesis), shown side-by-side with hand-built equivalents.
* **Execution Demonstration**: An end-to-end dry-run demo where an agent-generated loop successfully launches and executes on a lightweight simulation workload.
* **Technical Evaluation Report**: A short write-up identifying common failure modes, LLM reasoning limitations, and detailing where human-in-the-loop validation remains necessary.
