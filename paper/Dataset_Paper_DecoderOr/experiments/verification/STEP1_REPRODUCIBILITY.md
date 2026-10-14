# Step 1 Reproducibility Guide — Decoder-OR Logic Synthesis

This document provides instructions and command-line recipes to reproduce all Step 1 results:
- Verification Oracle Mutation Testing (M01–M08, R01–R08)
- Decoder-OR Routing JSON Validation Layer
- Balanced OR-Tree Decomposition (Fan-in <= 4)
- Synthesizable Verilog RTL Generation

---

## 1. Environment Setup

Ensure Python 3.10+ is available. A local virtual environment with `pytest` is configured:

```bash
# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Or run directly via .venv:
.venv\Scripts\pytest -q
```

---

## 2. Regression Check: Existing Mathematical Oracle

Verify that all 5 canonical benchmark circuits pass the independent mathematical oracle:

```bash
python verify_dataset.py
```

Expected Output:
```text
  [PASS] Half_Adder  — all 4 minterms verified correctly.
  [PASS] Full_Adder  — all 8 minterms verified correctly.
  [PASS] 2_to_1_MUX  — all 8 minterms verified correctly.
  [PASS] BCD_to_7Segment  — all 16 minterms verified correctly.
  [PASS] 3bit_Comparator  — all 64 minterms verified correctly.
  [OK] ALL CIRCUITS PASSED — dataset is mathematically correct.
```

---

## 3. Step 1.1 — Mutation Testing Campaign

Run the comprehensive mutation testing campaign across all benchmark circuits:

```bash
python verification/mutation_test.py
```

Generated Artifacts:
- `verification/mutation_results.csv`: Per-specimen mutation log with original value, mutated value, expected result, observed result, killed status, and oracle error message.
- `verification/mutation_summary.json`: Aggregated summary statistics with kill rates by mutation type and by circuit.

Key Results:
- Total Mutations Injected: 78
- Killed Mutations: 78
- Survived Mutations: 0
- Mutation Kill Rate: 100.00%

---

## 4. Step 1.2 & 1.3 — Reference Routing Export & Verilog Synthesis

Export the 5 benchmark circuits to standardized Decoder-OR routing JSONs:

```bash
python scripts/export_benchmark_routing.py
```

Outputs stored in `benchmarks_routing/`:
- `benchmarks_routing/Half_Adder.json`
- `benchmarks_routing/Full_Adder.json`
- `benchmarks_routing/2_to_1_MUX.json`
- `benchmarks_routing/BCD_to_7Segment.json`
- `benchmarks_routing/3bit_Comparator.json`

Compile a routing JSON to synthesizable Verilog with OR-tree decomposition (max fan-in = 4):

```bash
python -m compiler.cli benchmarks_routing/BCD_to_7Segment.json -o output_bcd.v --max-fan-in 4
```

Generate OR-tree decomposition metrics across fan-in sizes [0, 1, 2, 3, 4, 5, 6, 8, 9, 16, 32, 64]:

```bash
python scripts/generate_or_tree_report.py
```

Generated Artifact:
- `verification/or_tree_report.json`

---

## 5. Automated Test Suite (pytest)

Run the full automated test suite covering validator, OR-tree decomposition, end-to-end compiler, and mutation campaign:

```bash
.venv\Scripts\pytest -v
```

Summary:
- Total Tests: 71
- Passed: 71
- Failed: 0
