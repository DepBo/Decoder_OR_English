# ============================================================
# OpenROAD Physical Implementation Flow Script (SkyWater 130nm)
# Automatically generated for Decoder+OR Synthesis Validation
# ============================================================

set DESIGN_NAME     $::env(DESIGN_NAME)
set NETLIST_FILE    $::env(NETLIST_FILE)
set SDC_FILE        $::env(SDC_FILE)
set OUTPUT_DIR      $::env(OUTPUT_DIR)
set TECH_LEF        $::env(TECH_LEF)
set SC_LEF          $::env(SC_LEF)
set LIB_FILE        $::env(LIB_FILE)

# 1. Read Technology and Standard Cell Libraries
read_liberty $LIB_FILE
read_lef $TECH_LEF
read_lef $SC_LEF

# 2. Read Synthesized Gate-Level Netlist
read_verilog $NETLIST_FILE
link_design $DESIGN_NAME
read_sdc $SDC_FILE

# 3. Floorplan Initialization
# Core utilization = 40%, aspect ratio = 1.0, core margins = 10um
initialize_floorplan -site unithd \
                     -utilization 40 \
                     -aspect_ratio 1.0 \
                     -core_space 10.0

# 4. Standard Cell Placement
global_placement -density 0.5
detailed_placement

# 5. Buffer Repair & Fanout Optimization
# Inserts library buffer cells into nets exceeding fanout/slew/capacitance limits
repair_design -max_wire_length 800 \
              -buffer_cell sky130_fd_sc_hd__buf_1
repair_tie_fanout -max_fanout 8
repair_hold_violations -buffer_cell sky130_fd_sc_hd__buf_1
detailed_placement

# 6. Global & Detailed Routing (TritonRoute)
global_route -guide_file "$OUTPUT_DIR/${DESIGN_NAME}.guide" \
             -congestion_iterations 50
detailed_route -output_def "$OUTPUT_DIR/${DESIGN_NAME}_routed.def" \
               -output_drc "$OUTPUT_DIR/${DESIGN_NAME}_drc.rpt"

# 7. Parasitic Extraction & Static Timing Analysis
estimate_parasitics -global_routing
report_checks -path_delay max -fields {slew cap input nets fanout} > "$OUTPUT_DIR/${DESIGN_NAME}_timing.rpt"
report_tns > "$OUTPUT_DIR/${DESIGN_NAME}_tns.rpt"
report_wns > "$OUTPUT_DIR/${DESIGN_NAME}_wns.rpt"

# 8. Export Final Artifacts
write_def "$OUTPUT_DIR/${DESIGN_NAME}_final.def"
write_verilog "$OUTPUT_DIR/${DESIGN_NAME}_final.v"
exit
