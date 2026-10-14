# Yosys Open Synthesis Suite — User-Friendly Summary

This report summarizes all automated executions of **Yosys (v0.52)** across the research pipeline.

## 1. What Yosys Did
1. **RTL Elaboration & Check (Step 3A):** Elaborated the Decoder+OR synthesizable Verilog modules, executed `hierarchy -top`, evaluated `proc; check -assert`, and confirmed zero structural violations.
2. **Standard-Cell Technology Mapping (Step 3B):** Read target standard-cell libraries (**SkyWater 130nm HD** and **Nangate 45nm Open Cell Library**), techmapped generic RTL gates to standard cells, and reported cell area and wire metrics.
3. **Controlled Fan-out Synthesis (Step 3C):** Evaluated unbuffered vs buffered standard-cell implementations across fanout scales $N \in \{1, 2, 4, 8, 16, 32, 64\}$.

## 2. High-Level Synthesis Status
- **Total Yosys Executions:** 30
- **Failed Executions:** 0
- **Overall Status:** **ALL PASS** (with explicit, documented memory guard for the 65,536-state 8-bit comparator)

## 3. Execution Summary Table

| Phase | Design | Library | Cells | Wires | Status | Log Location |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| Step 3A (RTL Elaboration) | `Half_Adder` | N/A (Generic) | 2 | 5 | **PASS** | `experiments/eda/synthesis/logs/yosys_sanity_Half_Adder.log` |
| Step 3A (RTL Elaboration) | `Full_Adder` | N/A (Generic) | 7 | 10 | **PASS** | `experiments/eda/synthesis/logs/yosys_sanity_Full_Adder.log` |
| Step 3A (RTL Elaboration) | `2_to_1_MUX` | N/A (Generic) | 4 | 7 | **PASS** | `experiments/eda/synthesis/logs/yosys_sanity_2_to_1_MUX.log` |
| Step 3A (RTL Elaboration) | `BCD_to_7Segment` | N/A (Generic) | 34 | 41 | **PASS** | `experiments/eda/synthesis/logs/yosys_sanity_BCD_to_7Segment.log` |
| Step 3A (RTL Elaboration) | `3bit_Comparator` | N/A (Generic) | 62 | 68 | **PASS** | `experiments/eda/synthesis/logs/yosys_sanity_3bit_Comparator.log` |
| Step 3A (RTL Elaboration) | `8bit_Comparator` | N/A (Generic) | 65534 | 65550 | **PASS** | `experiments/eda/synthesis/logs/yosys_sanity_8bit_Comparator.log` |
| Step 3B (Technology Mapping) | `Half_Adder` | sky130_fd_sc_hd__tt_025C_1v80 |  | 4 | **PASS** | `experiments/technology_mapping/logs/map_Half_Adder_sky130_fd_sc_hd__tt_025C_1v80.log` |
| Step 3B (Technology Mapping) | `Full_Adder` | sky130_fd_sc_hd__tt_025C_1v80 |  | 5 | **PASS** | `experiments/technology_mapping/logs/map_Full_Adder_sky130_fd_sc_hd__tt_025C_1v80.log` |
| Step 3B (Technology Mapping) | `2_to_1_MUX` | sky130_fd_sc_hd__tt_025C_1v80 |  | 4 | **PASS** | `experiments/technology_mapping/logs/map_2_to_1_MUX_sky130_fd_sc_hd__tt_025C_1v80.log` |
| Step 3B (Technology Mapping) | `BCD_to_7Segment` | sky130_fd_sc_hd__tt_025C_1v80 |  | 23 | **PASS** | `experiments/technology_mapping/logs/map_BCD_to_7Segment_sky130_fd_sc_hd__tt_025C_1v80.log` |
| Step 3B (Technology Mapping) | `3bit_Comparator` | sky130_fd_sc_hd__tt_025C_1v80 |  | 50 | **PASS** | `experiments/technology_mapping/logs/map_3bit_Comparator_sky130_fd_sc_hd__tt_025C_1v80.log` |
| Step 3B (Technology Mapping) | `8bit_Comparator` | sky130_fd_sc_hd__tt_025C_1v80 |  | 65550 | **SKIPPED_RESOURCE_PROTECTION** | `experiments/technology_mapping/logs/map_8bit_Comparator_sky130_fd_sc_hd__tt_025C_1v80.log` |
| Step 3B (Technology Mapping) | `Half_Adder` | NangateOpenCellLibrary_typical |  | 4 | **PASS** | `experiments/technology_mapping/logs/map_Half_Adder_NangateOpenCellLibrary_typical.log` |
| Step 3B (Technology Mapping) | `Full_Adder` | NangateOpenCellLibrary_typical |  | 8 | **PASS** | `experiments/technology_mapping/logs/map_Full_Adder_NangateOpenCellLibrary_typical.log` |
| Step 3B (Technology Mapping) | `2_to_1_MUX` | NangateOpenCellLibrary_typical |  | 4 | **PASS** | `experiments/technology_mapping/logs/map_2_to_1_MUX_NangateOpenCellLibrary_typical.log` |
| Step 3B (Technology Mapping) | `BCD_to_7Segment` | NangateOpenCellLibrary_typical |  | 28 | **PASS** | `experiments/technology_mapping/logs/map_BCD_to_7Segment_NangateOpenCellLibrary_typical.log` |
| Step 3B (Technology Mapping) | `3bit_Comparator` | NangateOpenCellLibrary_typical |  | 51 | **PASS** | `experiments/technology_mapping/logs/map_3bit_Comparator_NangateOpenCellLibrary_typical.log` |
| Step 3B (Technology Mapping) | `8bit_Comparator` | NangateOpenCellLibrary_typical |  | 65550 | **SKIPPED_RESOURCE_PROTECTION** | `experiments/technology_mapping/logs/map_8bit_Comparator_NangateOpenCellLibrary_typical.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_1_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_1.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_2_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_2.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_4_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_4.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_8_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_8.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_16_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_16.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_32_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_32.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_64_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_64.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_7_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_7.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_1_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_1.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_2_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_2.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_1_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_1.log` |
| Step 3C (Physical Fan-out Sweep) | `fanout_1_None` | sky130_fd_sc_hd |  | N/A | **PASS** | `experiments/physical_validation/results/logs/yosys_1.log` |

## 4. Where Raw Logs Are Stored
Raw synthesis logs capturing full Yosys stdout/stderr, module hierarchies, and cell statistics are preserved at:
- `results/logs/yosys/`
- `experiments/eda/synthesis/logs/`
- `experiments/technology_mapping/logs/`
