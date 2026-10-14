# MCNC / LGSynth91 / IWLS93 Benchmark Generalization Experiment

This directory contains the experimental setup and results evaluating the Decoder-OR
compiler on established industry benchmarks from the **MCNC / LGSynth91 / IWLS93 Benchmark Collection**.

## Source and Provenance of Benchmarks
- **Suite**: MCNC Logic Synthesis Benchmarks (curated for LGSynth91 and IWLS93)
- **Reference Document**: Saeyang Yang, *Logic Synthesis and Optimization Benchmarks User Guide: Version 3.0*, Microelectronics Center of North Carolina (MCNC), Research Triangle Park, NC, Jan. 1991.
- **Authoritative Archive**: Digital Design Group, Faculty of Information Technology, Czech Technical University in Prague ([https://ddd.fit.cvut.cz/prj/Benchmarks/](https://ddd.fit.cvut.cz/prj/Benchmarks/)) and ISPRAS benchmark repository ([https://github.com/ispras/hdl-benchmarks](https://github.com/ispras/hdl-benchmarks)).
- **Format**: Berkeley PLA (Programmable Logic Array format).

## Conceptual Distinction: PLA Product Terms vs. Active Minterm Entries
- **Original PLA Product Terms**: The count of input-output cube lines specified in the original `.pla` file.
- **Expanded Active Minterm Entries**: The total number of minterm assignments asserting individual outputs ($\sum_j |M_j|$), mapping directly to routing connections in the Decoder-OR architecture.
- **Theoretical States**: $2^N$, representing the total output bus width of an unpartitioned $N$-input decoder.

## Evaluated Benchmarks Summary

| Benchmark | Inputs ($N$) | Outputs ($M$) | PLA Product Terms | Expanded Routing Pins | Theoretical States ($2^N$) | Status | Verification Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **5xp1** | 7 | 10 | 75 | 576 | 128 | ✅ PASS | 100% Exhaustive |
| **alu4** | 14 | 8 | 1,028 | 62,256 | 16,384 | ✅ PASS | 100% Exhaustive |
| **clip** | 9 | 5 | 167 | 1,280 | 512 | ✅ PASS | 100% Exhaustive |
| **con1** | 7 | 2 | 9 | 156 | 128 | ✅ PASS | 100% Exhaustive |
| **cordic** | 23 | 2 | 1,206 | N/A | 8,388,608 | ⚠️ INFEASIBLE | N/A |
| **duke2** | 22 | 29 | 87 | N/A | 4,194,304 | ⚠️ INFEASIBLE | N/A |
| **e64** | 65 | 65 | 65 | N/A | 36,893,488,147,419,103,232 | ⚠️ INFEASIBLE | N/A |
| **ex1010** | 10 | 10 | 1,024 | 1,471 | 1,024 | ✅ PASS | 100% Exhaustive |
| **misex1** | 8 | 7 | 32 | 548 | 256 | ✅ PASS | 100% Exhaustive |
| **rd53** | 5 | 3 | 32 | 42 | 32 | ✅ PASS | 100% Exhaustive |
| **rd73** | 7 | 3 | 141 | 192 | 128 | ✅ PASS | 100% Exhaustive |
| **rd84** | 8 | 4 | 256 | 411 | 256 | ✅ PASS | 100% Exhaustive |
| **squar5** | 5 | 8 | 32 | 85 | 32 | ✅ PASS | 100% Exhaustive |
| **table5** | 17 | 15 | 158 | 119,523 | 131,072 | ✅ PASS | 100% Exhaustive |

## Key Findings & Architectural Boundary
1. **Generalizability to Multi-Output Industrial Circuits**:
   - The Decoder-OR compiler successfully synthesized **11 multi-output benchmarks** (`rd53`, `squar5`, `con1`, `rd73`, `5xp1`, `misex1`, `rd84`, `clip`, `ex1010`, `alu4`, `table5`).
   - All 11 designs possess multiple primary outputs (ranging from 2 to 15 outputs).
   - 100% of synthesized circuits achieved bit-for-bit functional equivalence when independently simulated against the original PLA definitions (exhaustive across all $2^N$ states up to $N=17$).

2. **Representation Boundary (Combinatorial State-Space Explosion)**:
   - Circuits with $N \le 20$ inputs (such as `table5` at $N=17$, with 131,072 states and 119,523 routing connections) synthesize and verify cleanly.
   - Benchmarks with $N > 20$ inputs (`duke2` at $N=22$, `cordic` at $N=23$, and `e64` at $N=65$) exceed the single-decoder threshold ($2^{20} = 1,048,576$ states).
   - For these large circuits, a monolithic flat decoder is computationally impractical, defining the exact architectural boundary where hierarchical multi-level decomposition or sub-decoder factorization becomes necessary.