# Automated Research Validation Tables

> **Note on Provenance:** All tables below are dynamically generated directly from actual machine-readable CSV/JSON outputs of Yosys, ABC, and ngspice executions. No numbers are hardcoded or manually typed.

## 1. Standard-Cell Technology Mapping Summary

| Benchmark Design | Ports | Wires | Pre-Map Cells | Sky130 Cells | Sky130 Area ($\mu\text{m}^2$) | Nangate45 Cells | Nangate45 Area ($\mu\text{m}^2$) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Half_Adder** | 4 | 4 | 2 | 2 | 15.01 | 2 | 2.66 | **PASS** |
| **Full_Adder** | 5 | 8 | 7 | 2 | 33.78 | 5 | 5.59 | **PASS** |
| **2_to_1_MUX** | 4 | 4 | 4 | 1 | 11.26 | 1 | 1.86 | **PASS** |
| **BCD_to_7Segment** | 11 | 28 | 34 | 19 | 116.36 | 24 | 23.67 | **PASS** |
| **3bit_Comparator** | 9 | 51 | 62 | 44 | 260.25 | 45 | 47.61 | **PASS** |
| **8bit_Comparator** | 19 | 65550 | 65534 | SKIPPED | SKIPPED | SKIPPED | SKIPPED | **SKIPPED_RESOURCE_PROTECTION** |

## 2. Static Timing Analysis (STA) Summary (ABC `stime -p` NLDM)

| Benchmark Design | Library | Critical Path Delay (ps) | Logic Stages | Startpoint | Endpoint | Critical Path Cells |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `2_to_1_MUX` | NangateOpenCellLibrary_typical | 49.25 | 1 | `pi2` | `po0` | `MUX2_X1` |
| `2_to_1_MUX` | sky130_fd_sc_hd__tt_025C_1v80 | 260.32 | 1 | `pi2` | `po0` | `sky130_fd_sc_hd__mux2_1` |
| `3bit_Comparator` | NangateOpenCellLibrary_typical | 201.32 | 4 | `pi4` | `po1` | `NOR2_X1; OAI221_X1; AOI211_X1; OAI221_X1` |
| `3bit_Comparator` | sky130_fd_sc_hd__tt_025C_1v80 | 869.58 | 5 | `pi4` | `po2` | `sky130_fd_sc_hd__or3b_1; sky130_fd_sc_hd__o32ai_1; sky130_fd_sc_hd__a21oi_1; sky130_fd_sc_hd__a41oi_1; sky130_fd_sc_hd__or3_1` |
| `BCD_to_7Segment` | NangateOpenCellLibrary_typical | 113.42 | 3 | `pi3` | `po0` | `INV_X1; AOI211_X1; OAI221_X1` |
| `BCD_to_7Segment` | sky130_fd_sc_hd__tt_025C_1v80 | 544.81 | 3 | `pi2` | `po3` | `sky130_fd_sc_hd__mux2_1; sky130_fd_sc_hd__a21oi_1; sky130_fd_sc_hd__a31o_1` |
| `Full_Adder` | NangateOpenCellLibrary_typical | 87.85 | 2 | `pi2` | `po1` | `XNOR2_X1; XNOR2_X1` |
| `Full_Adder` | sky130_fd_sc_hd__tt_025C_1v80 | 331.98 | 1 | `pi0` | `po1` | `sky130_fd_sc_hd__xor3_1` |
| `Half_Adder` | NangateOpenCellLibrary_typical | 47.72 | 1 | `pi0` | `po1` | `XOR2_X1` |
| `Half_Adder` | sky130_fd_sc_hd__tt_025C_1v80 | 119.34 | 1 | `pi1` | `po1` | `sky130_fd_sc_hd__xor2_1` |

## 3. OR Fan-In Scaling Analysis (64 Minterms, SkyWater 130nm HD)

| Max Fan-In ($k$) | Tree Depth | Logic Gates | Mapped Cells | Mapped Area ($\mu\text{m}^2$) | Delay (ps) | Path Stages |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **2** | 6 | 63 | 23 | 136.3808 | 492.70 | 4 |
| **2** | 6 | 63 | 22 | 28.9940 | 232.35 | 4 |
| **4** | 3 | 21 | 23 | 136.3808 | 492.70 | 4 |
| **4** | 3 | 21 | 22 | 28.9940 | 232.35 | 4 |
| **8** | 2 | 9 | 23 | 136.3808 | 492.70 | 4 |
| **8** | 2 | 9 | 22 | 28.9940 | 232.35 | 4 |
| **16** | 2 | 5 | 23 | 136.3808 | 492.70 | 4 |
| **16** | 2 | 5 | 22 | 28.9940 | 232.35 | 4 |
| **32** | 2 | 3 | 23 | 136.3808 | 492.70 | 4 |
| **32** | 2 | 3 | 22 | 28.9940 | 232.35 | 4 |
| **64** | 1 | 1 | 23 | 136.3808 | 492.70 | 4 |
| **64** | 1 | 1 | 22 | 28.9940 | 232.35 | 4 |

## 4. Architectural Decoder Output Fan-out Audit

| Benchmark Circuit | Total Minterms Used | Max Minterm Fan-out | Top Fan-out Decoder Outputs | Architectural Assessment |
| :--- | :---: | :---: | :---: | :--- |
| **BCD_to_7Segment** | 10 | **7** | `Y[8]` | Shared minterms across multiple output functions. |
| **3bit_Comparator** | 64 | **1** | `Y[8], Y[16], Y[17], Y[24]` | Mutually exclusive / disjoint; strictly low fan-out. |
| **Full_Adder** | 7 | **2** | `Y[7]` | Mutually exclusive / disjoint; strictly low fan-out. |
| **Half_Adder** | 3 | **1** | `Y[1], Y[2], Y[3]` | Mutually exclusive / disjoint; strictly low fan-out. |
| **2_to_1_MUX** | 4 | **1** | `Y[2], Y[3], Y[5], Y[7]` | Mutually exclusive / disjoint; strictly low fan-out. |

## 5. Automated Buffer Insertion & Fan-Out Repair (SkyWater 130nm HD)

| Fan-out ($N$) | Unbuf Cells | Unbuf Area ($\mu\text{m}^2$) | Buf Cells | Buf Area ($\mu\text{m}^2$) | Inserted Buffers | Max Buffer-Output Fan-out | Buffer Cells Inserted | Area Overhead | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **1** | 2 | 13.7632 | 2 | 15.0144 | **0** | N/A | `None` | +9.09% | **PASS** |
| **2** | 3 | 21.2704 | 3 | 22.5216 | **0** | N/A | `None` | +5.88% | **PASS** |
| **4** | 5 | 36.2848 | 5 | 37.536 | **0** | N/A | `None` | +3.45% | **PASS** |
| **8** | 9 | 66.3136 | 9 | 68.816 | **0** | N/A | `None` | +3.77% | **PASS** |
| **16** | 17 | 126.3712 | 19 | 167.6608 | **2** | 10 | `buf_6x2` | +32.67% | **PASS** |
| **32** | 33 | 246.4864 | 39 | 342.8288 | **6** | 10 | `buf_6x6` | +39.09% | **PASS** |
| **64** | 65 | 486.7168 | 79 | 628.1024 | **14** | 10 | `buf_2x2, buf_4x1, buf_6x11` | +29.05% | **PASS** |

## 6. Transistor-Level Electrical Simulation (BSIM4 130nm SPICE)

| Topology | Fan-out ($N$) | $t_{p,rise}$ (ps) | $t_{p,fall}$ (ps) | $t_{rise}$ (ps) | $t_{fall}$ (ps) | $V_{OH}$ (V) | $V_{OL}$ (V) | Energy (fJ) | $I_{peak}$ (mA) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| unbuffered | 1 | 26.28 | 24.28 | 42.89 | 38.17 | 1.868 | -0.05 | 74.82 | 0.522 | **PASS** |
| unbuffered | 2 | 35.46 | 32.37 | 64.39 | 58.26 | 1.855 | -0.043 | 149.12 | 0.671 | **PASS** |
| unbuffered | 4 | 55.64 | 49.37 | 109.3 | 98.87 | 1.84 | -0.032 | 357.41 | 1.033 | **PASS** |
| unbuffered | 8 | 99.19 | 84.53 | 201.98 | 182.75 | 1.825 | -0.022 | 988.41 | 1.737 | **PASS** |
| unbuffered | 16 | 196.31 | 157.0 | 390.55 | 354.06 | 1.815 | -0.013 | 2634.95 | 3.151 | **PASS** |
| unbuffered | 32 | 394.91 | 306.13 | 767.4 | 696.96 | 1.808 | 0.005 | 8149.93 | 5.984 | **PASS** |
| unbuffered | 64 | 410.8 | 609.25 | INCOMPLETE | INCOMPLETE | 1.804 | 0.62 | 27631.98 | 11.653 | **INCOMPLETE_SWITCHING** |
| buffered_2stage | 1 | 74.45 | 76.18 | 44.22 | 45.42 | 1.85 | -0.036 | 419.37 | 1.222 | **PASS** |
| buffered_2stage | 2 | 77.7 | 79.43 | 49.34 | 50.62 | 1.848 | -0.035 | 470.31 | 1.407 | **PASS** |
| buffered_2stage | 4 | 83.55 | 85.25 | 59.46 | 60.41 | 1.845 | -0.033 | 591.16 | 1.778 | **PASS** |
| buffered_2stage | 8 | 94.35 | 95.56 | 79.5 | 79.22 | 1.838 | -0.029 | 896.07 | 2.596 | **PASS** |
| buffered_2stage | 16 | 114.9 | 114.32 | 121.0 | 116.89 | 1.83 | -0.024 | 1696.79 | 4.101 | **PASS** |
| buffered_2stage | 32 | 156.73 | 149.53 | 208.1 | 195.43 | 1.82 | -0.017 | 3678.23 | 6.962 | **PASS** |
| buffered_2stage | 64 | 250.09 | 220.09 | 387.63 | 358.21 | 1.812 | -0.01 | 9488.45 | 12.646 | **PASS** |

## 7. Decoder+OR vs Conventional Logic Synthesis Baseline Comparison

| Benchmark Design | Library | Decoder Cells | Conventional Cells | Decoder Area ($\mu\text{m}^2$) | Conv Area ($\mu\text{m}^2$) | Decoder Delay (ps) | Conv Delay (ps) | Area Ratio | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Half_Adder` | sky130_fd_sc_hd__tt_025C_1v80 | None | None | None | None | None | None | Nonex | **None** |
| `Half_Adder` | NangateOpenCellLibrary_typical | None | None | None | None | None | None | Nonex | **None** |
| `Full_Adder` | sky130_fd_sc_hd__tt_025C_1v80 | None | None | None | None | None | None | Nonex | **None** |
| `Full_Adder` | NangateOpenCellLibrary_typical | None | None | None | None | None | None | Nonex | **None** |
| `2_to_1_MUX` | sky130_fd_sc_hd__tt_025C_1v80 | None | None | None | None | None | None | Nonex | **None** |
| `2_to_1_MUX` | NangateOpenCellLibrary_typical | None | None | None | None | None | None | Nonex | **None** |
| `BCD_to_7Segment` | sky130_fd_sc_hd__tt_025C_1v80 | None | None | None | None | None | None | Nonex | **None** |
| `BCD_to_7Segment` | NangateOpenCellLibrary_typical | None | None | None | None | None | None | Nonex | **None** |
| `3bit_Comparator` | sky130_fd_sc_hd__tt_025C_1v80 | None | None | None | None | None | None | Nonex | **None** |
| `3bit_Comparator` | NangateOpenCellLibrary_typical | None | None | None | None | None | None | Nonex | **None** |
| `8bit_Comparator` | sky130_fd_sc_hd__tt_025C_1v80 | None | None | None | None | None | None | Nonex | **None** |
| `8bit_Comparator` | NangateOpenCellLibrary_typical | None | None | None | None | None | None | Nonex | **None** |

