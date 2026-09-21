# Plenary Talk: Compiler 2.0 — Languages and Compilers in the Era of Machine Learning
**Speaker:** Saman Amarasinghe (Thomas and Gerd Perkins Professor, EECS Department, MIT; Commit compiler research group lead, CSAIL)
**Venue:** Architecture 2.0 Workshop, ISCA 2026

## Abstract
The genius of FORTRAN, introduced in 1957, was not just that it was the first high-level language, but that it made hardware disappear. The same FORTRAN program could run on an IBM System/360, a DEC PDP-8, a CDC 6600, or even a Cray-1 with enough performance that most programmers never had to touch assembly or write architecture-specific code.

Over time, as hardware and software grew more complex, compilers quietly lost the ability to maintain this abstraction. Multicores, complex vector instructions, and specialized accelerators have all pushed more of the performance burden back onto the programmer. Today we have, in many ways, come a full circle.

For example:
* Getting peak performance from NVIDIA's V100, A100, H100, and B100 families often requires different, architecture-specific CUDA kernels and, on the latest parts, even hand-written PTX assembly to fully exploit tensor cores and the Tensor Memory Accelerator.
* To the best of our knowledge, the Apple/Arm SME accelerator does not even have a high-level compiler, and most high-performance code must be written using intrinsics or assembly.

This raises a fundamental question: can the next generation of compilers restore the original promise of the high-level programming languages—hiding architectural complexity while still delivering near-peak performance?

In this talk, I argue that the answer is **yes**, and outline a path forward to modernize compilers:
1. Create proper, scalable abstractions.
2. Leverage machine learning and modern generative techniques to optimize down to the physical silicon layers.
3. Radically simplify compiler building workflows.