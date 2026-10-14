# ABC Logic Synthesis & Standard-Cell Verification Summary

This report documents all operations performed by **Berkeley ABC (v1.01)** in technology mapping, static timing analysis, and automated buffer insertion.

## 1. Distinct Synthesis Concepts
To maintain scientific precision, ABC operations are strictly partitioned:
- **Technology Mapping:** Transforming Boolean logic networks into concrete standard cells (`abc -liberty`).
- **Logic Optimization:** Restructuring Boolean networks prior to mapping (`resyn2`, `opt`).
- **Buffer Insertion:** Explicit addition of standard-cell buffer trees (`sky130_fd_sc_hd__buf_6`, etc.) to mitigate excessive fan-out load capacitance.
- **Timing & Slew Analysis:** Computing critical path delay and pin slews via Non-Linear Delay Model (NLDM) lookup tables (`stime -p`).

> **Scientific Audit Notice on Buffer Counts:**  
> For fan-out loads $N \in \{1, 2, 4, 8\}$, ABC inserted **0 buffers** because the driver gate drive strength was sufficient to meet slew constraints. Any delay or area adjustments at $N \le 8$ are strictly due to **gate sizing and cell selection**, NOT buffer tree insertion.

## 2. ABC Technology Mapping & Timing Summary Table

| Stage | Design / Case | Library | Cells | Area ($\mu\text{m}^2$) | Delay (ps) | Buffers Inserted | Mechanism / Repair Type | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| Step 3B (Technology Mapping & STA) | `2_to_1_MUX` | NangateOpenCellLibrary_typical |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `2_to_1_MUX` | sky130_fd_sc_hd__tt_025C_1v80 |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `3bit_Comparator` | NangateOpenCellLibrary_typical |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `3bit_Comparator` | sky130_fd_sc_hd__tt_025C_1v80 |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `BCD_to_7Segment` | NangateOpenCellLibrary_typical |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `BCD_to_7Segment` | sky130_fd_sc_hd__tt_025C_1v80 |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `Full_Adder` | NangateOpenCellLibrary_typical |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `Full_Adder` | sky130_fd_sc_hd__tt_025C_1v80 |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `Half_Adder` | NangateOpenCellLibrary_typical |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3B (Technology Mapping & STA) | `Half_Adder` | sky130_fd_sc_hd__tt_025C_1v80 |  |  |  | 0 (pure mapping) | None | **PASS** |
| Step 3C (Fan-out Buffer Repair) | `Fanout_N1` | sky130_fd_sc_hd | 2 | 15.0144 | 209.56 | 0 | Gate Sizing / Logic Restructuring | **PASS** |
| Step 3C (Fan-out Buffer Repair) | `Fanout_N2` | sky130_fd_sc_hd | 3 | 22.5216 | 221.45 | 0 | Gate Sizing / Logic Restructuring | **PASS** |
| Step 3C (Fan-out Buffer Repair) | `Fanout_N4` | sky130_fd_sc_hd | 5 | 37.536 | 245.37 | 0 | Gate Sizing / Logic Restructuring | **PASS** |
| Step 3C (Fan-out Buffer Repair) | `Fanout_N8` | sky130_fd_sc_hd | 9 | 68.816 | 314.7 | 0 | Gate Sizing / Logic Restructuring | **PASS** |
| Step 3C (Fan-out Buffer Repair) | `Fanout_N16` | sky130_fd_sc_hd | 19 | 167.6608 | 435.36 | 2 | Buffer Tree Insertion | **PASS** |
| Step 3C (Fan-out Buffer Repair) | `Fanout_N32` | sky130_fd_sc_hd | 39 | 342.8288 | 435.56 | 6 | Buffer Tree Insertion | **PASS** |
| Step 3C (Fan-out Buffer Repair) | `Fanout_N64` | sky130_fd_sc_hd | 79 | 628.1024 | 484.66 | 14 | Buffer Tree Insertion | **PASS** |

## 3. Logs and Artifacts
ABC execution logs and Liberty timing reports are preserved in:
- `results/logs/abc/`
- `experiments/technology_mapping/logs/`
- `experiments/physical_validation/results/`
