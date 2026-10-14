# Step 2 Reproducibility Guide — Scalability & IWLS Benchmark Experiments

This document provides complete instructions, environment details, and execution commands to reproduce all Step 2 experimental results for the paper *"Realizing Arbitrary Logic Functions Using Decoders and OR Gates for Automated Logic Synthesis"*.

---

## 1. Experimental Environment & Specifications

All experiments were executed and recorded on the following physical host environment:

- **Operating System:** Windows 11 Home 64-bit (`Windows-11-10.0.26200-SP0`, AMD64)
- **Host Processor (CPU):** AMD Ryzen 5 7535HS with Radeon Graphics (6 physical cores, 12 logical threads @ 3.30 GHz base / 4.55 GHz boost)
- **Host Memory (RAM):** 8.0 GB Physical RAM (7.19 GB usable)
- **Python Version:** Python 3.12.3 (AMD64 64-bit MSC v.1938)
- **Repository Commit:** `25e4ec7cd94090f7a0534b513e847a5bf65fc100`
- **Dependencies:** Python standard library (`tracemalloc`, `time`, `json`, `math`, `pathlib`, `sys`, `typing`) + `pytest 9.1.1` (test runner). No external EDA binaries (Yosys, ABC, OpenROAD, etc.) are required for Step 2 data collection.

---

## 2. Directory Layout for Step 2 Artifacts

```
experiments/
├── scalability/
│   ├── run_scalability.py            # Automated generic & 8-bit comparator benchmark runner
│   ├── generate_8bit_comparator.py   # Independent 8-bit magnitude comparator generator
│   ├── scalability_results.csv       # Summary metrics CSV across all tested cases (N=2..21)
│   ├── scalability_summary.json      # Structured JSON metrics with mean/min/max statistics
│   ├── raw_runs/                     # Raw individual measurement iterations (3 runs/case)
│   ├── generated_json/               # Generated Decoder-OR routing JSONs (N=2..20, 8-bit)
│   ├── generated_verilog/            # Generated Verilog RTL modules (N=2..20, 8-bit)
│   └── logs/                         # Execution logs
├── iwls/
│   ├── pla_parser.py                 # Berkeley PLA format parser & independent evaluator
│   ├── run_iwls.py                   # Automated IWLS conversion, compilation, & verification runner
│   ├── benchmarks/                   # MCNC / LGSynth91 / IWLS93 PLA benchmark source files
│   ├── archive_pre_audit/            # Preserved pre-audit raw experimental outputs
│   ├── iwls_results.csv              # Summary metrics CSV across all 14 evaluated benchmarks
│   ├── iwls_summary.json             # Structured JSON metrics & verification logs
│   ├── generated_json/               # Synthesized routing JSONs for feasible circuits
│   ├── generated_verilog/            # Synthesized Verilog RTL modules for feasible circuits
│   ├── logs/                         # Execution logs
│   └── README.md                     # Provenance documentation & metric definitions
├── STEP2_REPRODUCIBILITY.md          # This reproducibility guide
└── STEP2_AUDIT_REPORT.md             # Comprehensive scientific audit report
```

---

## 3. Part A — Scalability Experiments (Reviewers #1.3 & #2.4)

### A.1 Standalone 8-Bit Magnitude Comparator

To independently generate, synthesize, and verify the 8-bit magnitude comparator ($N=16$ Boolean inputs, $2^{16} = 65,536$ decoder states, 3 outputs: `A_gt_B`, `A_eq_B`, `A_lt_B`):

```bash
# Generate routing JSON from independent mathematical ground truth
python experiments/scalability/generate_8bit_comparator.py
```

Outputs:
- **JSON:** `experiments/scalability/generated_json/8bit_Comparator.json` (1.052 MB, 65,536 routing connections)
- **Verilog:** `experiments/scalability/generated_verilog/8bit_Comparator.v` (2.224 MB, 21,931 internal OR gates, depth 8)

**Precise Structural Decomposition Breakdown:**
- `A_gt_B`: 32,640 active minterms ($A > B$), Tree Depth = 8, Internal OR Nodes = **10,923**, Intermediate Wires = 10,922
- `A_eq_B`: 256 active minterms ($A == B$), Tree Depth = 4, Internal OR Nodes = **85**, Intermediate Wires = 84
- `A_lt_B`: 32,640 active minterms ($A < B$), Tree Depth = 8, Internal OR Nodes = **10,923**, Intermediate Wires = 10,922
- **Module Totals:**
  - Total Internal OR Gates (continuous assigns): $10,923 + 85 + 10,923 = \mathbf{21,931}$
  - Total Intermediate Wires: $10,922 + 84 + 10,922 = 21,928$ (plus 1 decoder bus wire `wire [65535:0] Y;` = 21,929 wires)
  - Decoder Assignment: 1 statement (`assign Y = 65536'b1 << {A7, ..., B0};`)
  - Total Continuous Assignments: $21,931 + 1 = 21,932$

### A.2 Generic Scalability Suite ($N = 2 \dots 20$, and $N = 21$ Boundary)

To execute the automated scalability benchmark across input sizes $N=2$ to $N=21$ (with 3 repetitions per case):

```bash
python experiments/scalability/run_scalability.py --min-n 2 --max-n 21 --runs 3 --max-states 1048576
```

Configurable parameters:
- `--min-n`: Starting input size (default: 2)
- `--max-n`: Maximum input size to attempt (default: 21)
- `--runs`: Repetitions per data point for statistical variance (default: 3)
- `--max-states`: Safety threshold for decoder states (default: 1,048,576 = $2^{20}$)
- `--max-memory-mb`: Safety RAM threshold in MB (default: 2048 MB)
- `--timeout`: Maximum wall-clock time per circuit in seconds (default: 300 s)

Key Observed Findings:
- **$N = 2 \dots 16$:** All complete within milliseconds to seconds (e.g., $N=16$ completes full parse, validation, decomposition, and Verilog generation in ~5.88 seconds; peak RAM ~26.0 MB).
- **8-Bit Comparator ($N=16$ inputs, 65,536 states):** Completed in 4.87 s (total compiler time), 22.53 MB peak RAM, 1.05 MB JSON size, 2.22 MB Verilog size.
- **Maximum Observed Feasible Size:** $N = 20$ (1,048,576 decoder output states, 1,398,102 routing pins). JSON size: 24.0 MB; Peak RAM: 362.9 MB; Compilation: 101.3 seconds.
  - JSON Parsing fraction at $N=20$: $1,000.22\text{ ms} / 101,293.53\text{ ms} \approx 0.99\%$ of total compilation time.
  - Semantic Validation fraction: $36,200.89\text{ ms} / 101,293.53\text{ ms} \approx 35.74\%$.
  - Verilog String Emission fraction: $64,092.42\text{ ms} / 101,293.53\text{ ms} \approx 63.27\%$.
- **Controlled Boundary:** $N = 21$ ($2^{21} = 2,097,152$ states) cleanly triggers `MEMORY_LIMIT` under the configured safe threshold, recorded with exact reason in CSV and JSON summaries.

---

## 4. Part B — Benchmark Generalization (Reviewer #3.3)

### B.1 Benchmark Provenance & Citations

Benchmarks were sourced from the authoritative **MCNC / LGSynth91 Benchmark Collection** (curated for the 1991/1993 International Workshop on Logic Synthesis):
- **Technical Reference:** Saeyang Yang, *Logic Synthesis and Optimization Benchmarks User Guide: Version 3.0*, Microelectronics Center of North Carolina (MCNC), Research Triangle Park, NC, Jan. 1991.
- **Authoritative Archive:** Digital Design Group, Faculty of Information Technology, Czech Technical University in Prague ([https://ddd.fit.cvut.cz/prj/Benchmarks/](https://ddd.fit.cvut.cz/prj/Benchmarks/)) and ISPRAS benchmark repository ([https://github.com/ispras/hdl-benchmarks](https://github.com/ispras/hdl-benchmarks)).
- **Format:** Berkeley PLA (Programmable Logic Array format). Original source files are preserved in `experiments/iwls/benchmarks/`.

### B.2 Execution and Independent Verification

To run the complete benchmark conversion, compilation, and functional equivalence suite:

```bash
python experiments/iwls/run_iwls.py
```

Key Observed Findings:
- **Feasible Multi-Output Benchmarks (11 / 14):** `5xp1`, `alu4`, `clip`, `con1`, `ex1010`, `misex1`, `rd53`, `rd73`, `rd84`, `squar5`, and `table5`.
  - All 11 benchmarks are multi-output combinational circuits (2 to 15 outputs).
  - `table5` ($N=17$ inputs, 15 outputs, 158 PLA product terms, 131,072 theoretical states, 119,523 routing connections) successfully completed compilation in 10.05 seconds with 36.11 MB peak RAM.
  - **100% of tested input vectors** (including exhaustive evaluation across all 131,072 states for `table5` and 16,384 states for `alu4`) pass independent functional verification against the original Berkeley PLA representation.
- **Infeasible Large-Scale Benchmarks (3 / 14):** `duke2` ($N=22$), `cordic` ($N=23$), `e64` ($N=65$).
  - Correctly categorized as `INFEASIBLE_FOR_COMPLETE_MINTERM_REPRESENTATION`.
  - Their state spaces ($2^{22} = 4,194,304$, $2^{23} = 8,388,608$, $2^{65} \approx 3.69 \times 10^{19}$) exceed the single-decoder threshold ($2^{20} = 1,048,576$ states), empirically demonstrating the architectural boundary where hierarchical multi-level decomposition or sub-decoder factorization becomes necessary.

---

## 5. Automated Regression & Unit Tests (Step 1 + Step 2)

To run the unified test suite verifying both Step 1 baseline capabilities and all audited Step 2 experiment artifacts:

```bash
# Run pytest across all test modules
.venv\Scripts\pytest -v

# Run independent baseline oracle check for Step 1 circuits
.venv\Scripts\python verify_dataset.py
```

Expected Results:
- **Pytest:** 80 passed in ~11 seconds (71 Step 1 tests + 9 Step 2 regression tests).
- **verify_dataset.py:** 5/5 circuits PASS (Half_Adder, Full_Adder, 2_to_1_MUX, BCD_to_7Segment, 3bit_Comparator).
