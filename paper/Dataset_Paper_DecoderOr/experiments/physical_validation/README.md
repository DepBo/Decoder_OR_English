# Physical Implementation & Transistor-Level Electrical Validation (Steps 3C & 3D)

This directory contains the complete, reproducible experimental infrastructure for **Step 3C** (Physical Implementation / Fan-out / Buffering / Routing) and **Step 3D** (Transistor-Level Electrical Validation / SPICE) for the paper:

> **"Realizing Arbitrary Logic Functions Using Decoders and OR Gates for Automated Logic Synthesis"**

---

## 1. Directory Structure

```
experiments/physical_validation/
├── run_all.py                 # Master execution orchestrator for 3C and 3D
├── run_3c.py                  # Step 3C physical synthesis, fan-out scaling, and buffer repair
├── run_3d.py                  # Step 3D transistor-level transient SPICE simulation
├── README.md                  # This documentation
├── scripts/                   # Physical implementation flow scripts
│   ├── openroad_flow.tcl      # Master OpenROAD Tcl flow script
│   ├── floorplan.tcl          # Core floorplanning and site initialization
│   ├── placement.tcl          # Global & detailed standard-cell placement
│   ├── buffer_repair.tcl      # Slew/fanout buffer insertion & hold repair
│   └── route.tcl              # Global routing & TritonRoute detailed routing
├── netlists/                  # Controlled fanout Verilog and constraint files
│   ├── fanout_{1..64}.v       # RTL test cases
│   ├── fanout_{1..64}.constr  # Standard-cell driving & load constraints
│   ├── unbuf_fo_*_mapped.v    # Unbuffered gate-level netlists
│   └── buf_fo_*_mapped.v      # Buffer-repaired gate-level netlists
├── spice/                     # SPICE netlists for transient simulations
│   ├── unbuffered_fanout_*.sp # Unbuffered CMOS driver netlists
│   └── buffered_fanout_*.sp   # 2-stage buffered CMOS driver netlists
└── results/                   # Experimental CSV datasets and JSON summaries
    ├── physical_fanout_results.csv
    ├── buffer_insertion_results.csv
    ├── physical_timing_results.csv
    ├── physical_mapping_results.csv
    ├── placement_results.csv
    ├── routing_results.csv
    ├── congestion_results.csv
    ├── spice_fanout_results.csv
    ├── spice_buffer_results.csv
    ├── decoder_fanout_audit.json
    └── spice_summary.json
```

---

## 2. Reproduction Instructions

### Master Run (Executes Steps 3C and 3D)
To reproduce the complete suite in a single run:
```bash
python experiments/physical_validation/run_all.py
```

### Modular Step Execution

#### Step 3C: Physical Synthesis & Buffering Flow
```bash
python experiments/physical_validation/run_3c.py --fanout-max 64
```
Options:
- `--fanout-max <N>`: Maximum fan-out value to test (default: 64).
- `--skip-large`: Skips large benchmarks exceeding memory budgets.

#### Step 3D: Transistor-Level SPICE Simulation
```bash
python experiments/physical_validation/run_3d.py --fanout-max 64
```
Options:
- `--fanout-max <N>`: Maximum fan-out to simulate (default: 64).

---

## 3. Environment & Tools

| Tool | Executable | Version Tested | Role in Experiment |
| :--- | :--- | :--- | :--- |
| **Yosys** | `yosys` | `0.52` | RTL elaboration, optimization, logic synthesis |
| **ABC** | `yosys-abc` | `1.01` | Technology mapping, buffer insertion (`buffer`), STA (`stime -p`) |
| **ngspice** | `ngspice` | `45.2` | BSIM4 transistor-level transient `.measure` simulation |
| **OpenROAD** | `openroad` | *Flow scripts generated* | Tcl place-and-route scripts provided in `scripts/` |

---

## 4. Key Experimental Findings

1. **Decoder Output Fan-out Architectural Audit**:
   - In single-output or mutually exclusive multi-output functions (e.g., `3bit_Comparator`, `8bit_Comparator`), minterm fan-out is strictly **1**.
   - In shared multi-output functions (e.g., `BCD_to_7Segment`), minterm outputs drive multiple OR trees (e.g., $Y_8$ drives 7 segments, $Y_0, Y_6, Y_9$ drive 6 segments).
   - High fan-out occurs strictly as a function of minterm sharing across outputs.

2. **Buffer Tree Insertion Scaling (Sky130 HD)**:
   - For $N \le 8$, standard cell drive strength is sufficient; **0 buffers** are required.
   - For $N = 16$, the physical engine automatically inserts **2 buffers** (`sky130_fd_sc_hd__buf_6`), reducing critical path delay from $687.00\text{ ps} \to 435.36\text{ ps}$ (36.6% speedup) at a 32.7% area overhead.
   - For $N = 32$, **6 buffers** are inserted, holding delay to $435.56\text{ ps}$ (vs. $1030.62\text{ ps}$ unbuffered, 57.7% speedup).
   - For $N = 64$, **14 buffers** are inserted, holding delay to $484.66\text{ ps}$ (vs. $1689.24\text{ ps}$ unbuffered, 71.3% speedup).

3. **Transistor-Level Electrical Behavior (SPICE)**:
   - Static CMOS logic levels remain rail-to-rail ($V_{OH} \approx 1.80\text{V}$, $V_{OL} \approx 0.0\text{V}$) across all capacitive loads.
   - Dynamic signal degradation is purely capacitive: unbuffered rise times scale linearly ($42.89\text{ ps} \to 767.40\text{ ps}$ at $N=32$).
   - Buffer insertion restores transition sharpness ($208.10\text{ ps}$ at $N=32$, $3.7\times$ improvement) and cuts dynamic energy by more than half ($3678\text{ fJ}$ vs. $8150\text{ fJ}$) by preventing crowbar current in downstream gates.
