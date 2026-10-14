# Step 3B: Technology Mapping, Timing, and OR-Tree Decomposition Validation

This directory contains the reproducible scripts, standard-cell libraries, and experimental outputs for **Step 3B** of the research validation for the paper:

> *"Realizing Arbitrary Logic Functions Using Decoders and OR Gates for Automated Logic Synthesis"*

---

## Directory Structure

```
experiments/technology_mapping/
├── libraries/
│   ├── sky130_fd_sc_hd__tt_025C_1v80.lib    # SkyWater 130nm High-Density, Typical-Typical, 1.8V, 25°C
│   └── NangateOpenCellLibrary_typical.lib    # Nangate 45nm Open Cell Library, Typical, 1.1V, 25°C
├── results/
│   ├── logs/                                 # Detailed Yosys and ABC synthesis & timing logs
│   ├── fan_in/                               # OR Fan-in experiment artifacts and netlists
│   ├── or_depth/                             # OR-tree depth comparison netlists and audit JSON
│   ├── bcd_dc/                               # BCD don't-care netlists and testbench logs
│   ├── baseline/                             # Conventional baseline RTL netlists and comparisons
│   ├── technology_mapping_results.csv        # Master mapped cell and area results
│   ├── technology_mapping_summary.json       # JSON summary of mapping statistics
│   ├── sta_results.csv                       # Static timing analysis critical-path results
│   ├── fan_in_results.csv                    # Fan-in scaling experiment results (k in 2..64)
│   ├── or_depth_scaling_results.csv          # Balanced vs unbalanced depth results
│   ├── bcd_dont_care_results.csv             # BCD don't-care comparison results
│   └── conventional_baseline_results.csv     # Side-by-side conventional baseline comparison
├── conventional_baselines.py                 # Conventional RTL baseline generator
├── run_mapping.py                            # Yosys + ABC benchmark mapping runner
├── run_sta.py                                # ABC stime + Yosys ltp static timing analyzer
├── run_fan_in.py                             # Controlled OR fan-in scaling experiment
├── run_or_depth.py                           # 8-bit comparator audit and depth comparison
├── run_bcd_dc.py                             # BCD don't-care verification and mapping
├── run_all.py                                # Master orchestrator for all Step 3B experiments
└── README.md                                 # This documentation file
```

---

## Reproducibility Commands

To execute the entire Step 3B suite in one command:

```bash
# From workspace root
python experiments/technology_mapping/run_all.py
```

### CLI Options

- `--skip-large`: (Default: `True`) Skips full ABC standard-cell technology mapping of the 65,534-cell 8-bit comparator to protect host WSL2 RAM.
- `--include-large`: Attempts mapping of the large 8-bit comparator.
- `--library {both,sky130,nangate45}`: Selects which standard-cell library to evaluate (default: `both`).
- `--output-dir <path>`: Custom destination directory for result CSVs and JSONs.

### Running Individual Sub-Experiments

```bash
# 1. Technology Mapping only
python experiments/technology_mapping/run_mapping.py --library both

# 2. Static Timing Analysis only
python experiments/technology_mapping/run_sta.py

# 3. OR Fan-in scaling experiment
python experiments/technology_mapping/run_fan_in.py

# 4. OR-tree depth scaling & 8-bit comparator audit
python experiments/technology_mapping/run_or_depth.py

# 5. BCD don't-care experiment
python experiments/technology_mapping/run_bcd_dc.py

# 6. Conventional baseline comparison
python experiments/technology_mapping/run_baseline.py
```
