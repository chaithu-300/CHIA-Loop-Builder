# Architecture 2.0: Workshop on Agentic AI for Computing Systems Design
## Official Proceedings Directory · ISCA 2026 · Raleigh, NC

**Date**: Saturday, June 27, 2026  
**Location**: Room 306B, ISCA 2026, Raleigh, NC  
**Contact**: [zishenwan@seas.harvard.edu](mailto:zishenwan@seas.harvard.edu)  
**Organizing Team**: Zishen Wan, Chenyu Wang, Andy Cheng, Shvetank Prakash, Arya Tschand, Zander Ingare, Ankita Nayak, Vijay Janapa Reddi (Harvard University / Gimlet Labs)

---

### Workshop Overview
The **Architecture 2.0** workshop serves as a premier venue bringing together systems engineers, computer architects, and AI practitioners exploring the intersection of agentic artificial intelligence and hardware design. As autonomous agent workflows begin to replace manual scripting and heuristic optimization across the computing stack, the workshop focuses on novel methodologies, benchmarks, and runtime infrastructures designed to support agent-driven hardware/software co-design.

---

### Official Schedule & Research Abstracts

#### 08:00–08:15 | Welcome & Book Launch
* **Opening Remarks**: Featuring the launch of the landmark book:  
  *Architecture 2.0: Agentic Design Loops for Computing System Synthesis* ([https://arch2.mlsysbook.ai/](https://arch2.mlsysbook.ai/))

#### 08:15–09:15 | Session 1: Agentic EDA — RTL Optimization & Design-Space Exploration
1. **MAESTRO: A Multi-Agent EDA Orchestrator for Autonomous FPGA Design Closure**  
   *Presenter*: Saher Elsayed
2. **Intelligent Equality Saturation: From Hierarchical Prospection to a Minimal Implementation**  
   *Presenters*: Youwei Xiao, Chenyun Yin, Yun Liang
3. **AgenticDSE: A Multi-Agent Design Space Exploration Framework with Multi-Phase Bayesian Optimization for Chiplet Accelerators**  
   *Presenters*: Zhantong Zhu, Zhuolin Li, Kangbo Bai, Hongou Li, Tianyu Jia
4. **Dr. RTL: Autonomous Agentic RTL Optimization through Tool-Grounded Self-Improvement**  
   *Presenters*: Wenji Fang, Zhiyao Xie  
   *Focus*: An autonomous framework that performs RTL timing optimization by analyzing synthesis reports, proposing code changes, and running equivalence checks using sub-agents.

#### 09:15–10:00 | Session 2: Agentic Systems for Runtime Profiling, Serving, and Diagnosis
1. **Towards Agentic Offline Profiling for Speculative Load Micro-Op Fusion**  
   *Presenters*: Deepanjali Mishra, Tanvir Ahmed Khan, Gilles Pokam, Heiner Litz, Akshitha Sriraman
2. **Argus: Agentic, Reference-Calibrated, Tree-Guided, System-Level Bottleneck Localization**  
   *Presenters*: Vlad-Petru Nitu, Harsh Songara, Konstantinos Sgouras, Spiros Galanopoulos, Onur Mutlu  
   *Focus*: Employs a tree-guided agentic structure to autonomously pinpoint low-level bottlenecks in heterogeneous hardware systems.
3. **Dyserve: Dynamic Strategy Generation for Agent Serving**  
   *Presenters*: Jiayi Qian, Zishen Wan, Hanchen Yang, Souvik Kundu, Tushar Krishna  
   *Focus*: Details dynamic agent serving runtime logic that adaptively composes verification, routing, and retry loops to optimize processing efficiency.

#### 10:00–10:30 | Coffee Break & Poster Session I

#### 10:30–11:15 | Plenary Talk I
* **Speaker**: Saman Amarasinghe (MIT Commit Group, CSAIL)
* **Title**: *Compiler 2.0: Languages and Compilers in the Era of Machine Learning*
* **Abstract**: The genius of FORTRAN, introduced in 1957, was that it hid hardware complexity from programmers. Over time, multicores, vector units, and heterogeneous accelerators pushed that burden back. Today, achieving peak performance on platforms like NVIDIA GPUs or Apple's SME accelerator requires manual, architecture-specific CUDA or assembly kernels. Amarasinghe outlines a path forward to modernize compilers and hide architectural complexity by creating proper hardware abstractions and leveraging machine learning in compiling infrastructure.

#### 11:15–12:00 | Plenary Talk II (CHIA Keynote)
* **Speaker**: Sagar Karandikar (UC Berkeley)
* **Title**: *CHIA: An open-source framework for principled, agentic AI-driven hardware/software co-design research*
* **Abstract**: Karandikar introduces **CHIA** ([https://chialoops.ai](https://chialoops.ai)), an open-source framework designed to make complex AI-infused hardware development workflows easy to express, deploy, and study as Directed Acyclic Graphs ("CHIA loops"). The talk details several microarchitectural case studies, including **ArchAgent** (an evolutionary generative AI that autonomously designs cache replacement policies without human intervention), and reviews a decade of agile design infrastructure (Chipyard, FireSim, Hammer) that enables distributed scaling on heterogeneous physical and cloud clusters.

#### 12:00–13:30 | Lunch Break

#### 13:30–14:15 | Plenary Talk III
* **Speaker**: Dimitrios Skarlatos (CMU)
* **Title**: *Architecture & Systems in the Era of Agentic Co-Design*
* **Abstract**: With AI datacenters projected to draw over 1,000 TWh annually, renegotiating the hardware-software boundary is essential. Skarlatos outlines CMU's progress on agentic co-design, spanning **LithOS** (which rethinks the OS contract over GPUs for AI and agentic serving) and **Agentic Architect** (an LLM-driven architecture design space exploration and optimization framework). He calls on the computer architecture community to establish the benchmarks and simulator environments needed to close the agentic co-design loop.

#### 14:15–15:00 | Session 3: Benchmarking and Evaluation of Agentic Architecture
1. **Benchmarking Agentic HLS Design Tasks With HLS-Eval**  
   *Presenters*: Stefan Abi-Karam, Callie Hao
2. **Fail2Bench: Turning RTL Agent Failures into a Self-Curating Benchmark**  
   *Presenters*: Aryan Chhabra, Sumedh Narahari, Shritan Settipalli, Aadarsh Sivaraman
3. **Punctuated Stagnation**  
   *Presenter*: Mahesh Madhav

#### 15:00–15:30 | Tutorial
* **Title**: *ArchEval: Measuring AI Agents as Computer Architects*
* **Presenters**: Chenyu Wang, Zishen Wan, Jeffrey Ma, Shvetank Prakash, Zhenting Qi, Vijay Janapa Reddi, et al.

#### 15:30–16:00 | Coffee Break & Poster Session II

#### 16:00–16:45 | Plenary Talk IV
* **Speaker**: Qijing Jenny Huang (NVIDIA)
* **Title**: *Design Space Exploration in the Age of AI Architects*
* **Abstract**: Design Space Exploration (DSE) has traditionally been bounded by human-defined search criteria and manual modeling. Huang outlines the vision of "AI Architects": agentic systems that automate unstructured design stages, expand exploration parameters beyond human specifications, and perform knowledge-guided search. She presents **SOLAR**, an agentic framework that translates algorithms into performance-model-ready representations, and discusses benchmarks required to evaluate creative yet trustworthy AI design agents.

#### 16:45–17:30 | Session 4: Agentic Optimization for Kernels, Compilers, and Hardware Knowledge
1. **HDLxGraph: Bridging Large Language Models and HDL Repositories via HDL Graph Databases**  
   *Presenters*: Jiayin Qin, Pingqing Zheng, Fuqi Zhang, Zishen Wan, Yang Katie Zhao, et al.
2. **From Skills to Tracelets: Dependency-Guided Transfer for LLM Kernel Agents**  
   *Presenters*: Shuoming Zhang, Ruiyuan Xu, Huimin Cui, Jiacheng Zhao, et al.
3. **AccelOpt: A Self-Improving LLM Agentic System for AI Accelerator Kernel Optimization**  
   *Presenters*: Genghan Zhang, Shaowei Zhu, Anjiang Wei, Kunle Olukotun, Yida Wang, et al.

#### 17:30–18:00 | Poster Session III & Concluding Remarks
