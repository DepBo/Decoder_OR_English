"""
experiments/technology_mapping/run_bcd_dc.py
--------------------------------------------
Part G: BCD to 7-Segment Don't-Care Experiment.
Evaluates the architectural and synthesis impact of don't-care states (10-15).
Compares:
1. Implementation A: Decoder + OR architecture (states 10-15 unrouted -> outputs 0).
2. Implementation B: Conventional minimized Boolean (states 10-15 as don't-care 'X').
3. Implementation C: Conventional Boolean with states 10-15 tied to zero ('0').

Verifies:
- All valid decimal digits 0-9 match the specification identically.
- States 10-15 behavior is explicitly recorded.
- Collects mapped cell count, standard-cell area (um^2), critical-path delay (ps),
  and separates decoder cost from OR-tree routing cost.
"""

import re
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

SKY130_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "sky130_fd_sc_hd__tt_025C_1v80.lib"
NANGATE45_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "NangateOpenCellLibrary_typical.lib"

# Ground truth 7-segment encoding for digits 0-9 (a, b, c, d, e, f, g)
SPEC_DIGITS = {
    0: (1, 1, 1, 1, 1, 1, 0),
    1: (0, 1, 1, 0, 0, 0, 0),
    2: (1, 1, 0, 1, 1, 0, 1),
    3: (1, 1, 1, 1, 0, 0, 1),
    4: (0, 1, 1, 0, 0, 1, 1),
    5: (1, 0, 1, 1, 0, 1, 1),
    6: (1, 0, 1, 1, 1, 1, 1),
    7: (1, 1, 1, 0, 0, 0, 0),
    8: (1, 1, 1, 1, 1, 1, 1),
    9: (1, 1, 1, 1, 0, 1, 1),
}


def to_wsl_path(p: Path) -> str:
    s = str(p.resolve()).replace('\\', '/')
    if len(s) >= 2 and s[1] == ':':
        drive = s[0].lower()
        return f"/mnt/{drive}{s[2:]}"
    return s


def run_functional_check(verilog_file: Path, top_module: str) -> Dict[str, Any]:
    """Runs Icarus Verilog testbench to verify outputs for all 16 input patterns (0-15)."""
    tb_code = f"""
`timescale 1ns/1ps
module tb_bcd;
    reg A, B, C, D;
    wire a, b, c, d, e, f, g;

    {top_module} dut (
        .A(A), .B(B), .C(C), .D(D),
        .a(a), .b(b), .c(c), .d(d), .e(e), .f(f), .g(g)
    );

    integer i;
    initial begin
        for (i = 0; i < 16; i = i + 1) begin
            {{A, B, C, D}} = i[3:0];
            #1;
            $display("VEC %0d: %b%b%b%b%b%b%b", i, a, b, c, d, e, f, g);
        end
        $finish;
    end
endmodule
"""
    tb_file = verilog_file.parent / f"tb_{top_module}.v"
    tb_file.write_text(tb_code, encoding="utf-8")
    
    w_tb = to_wsl_path(tb_file)
    w_v = to_wsl_path(verilog_file)
    vvp_file = f"/tmp/tb_{top_module}.vvp"

    compile_cmd = f"iverilog -g2012 -o {vvp_file} {w_tb} {w_v} && vvp {vvp_file}"
    proc = subprocess.run(["wsl", "-e", "bash", "-c", compile_cmd], capture_output=True, text=True)
    
    vectors = {}
    valid_correct = True
    for line in proc.stdout.splitlines():
        m = re.match(r"VEC\s+(\d+):\s+([01xXzZ]{7})", line)
        if m:
            idx = int(m.group(1))
            val_str = m.group(2)
            vectors[idx] = val_str
            if idx <= 9:
                expected_tuple = SPEC_DIGITS[idx]
                expected_str = "".join(str(b) for b in expected_tuple)
                if val_str != expected_str:
                    valid_correct = False

    return {
        "valid_0_to_9_pass": valid_correct,
        "vectors": vectors,
        "compile_ok": proc.returncode == 0
    }


def run_bcd_experiment(
    output_dir: Path = REPO_ROOT / "experiments" / "technology_mapping" / "results" / "bcd_dc"
) -> List[Dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    impl_configs = [
        {
            "implementation": "Impl_A_Decoder_OR_Unrouted_DC",
            "description": "Decoder + OR Architecture (Minterms 10-15 unrouted / evaluate to 0)",
            "verilog_file": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "BCD_to_7Segment.v",
            "top_module": "BCD_to_7Segment_Decoder_OR",
            "decoder_type": "4-to-16 Core Decoder",
            "or_routing_entries": 49, # 8+8+9+7+4+6+7 minterm connections
            "unrouted_minterms": [10, 11, 12, 13, 14, 15],
        },
        {
            "implementation": "Impl_B_Conventional_DC_Exploited",
            "description": "Conventional Boolean Case Statement (States 10-15 specified as 7'bxxxxxxx)",
            "verilog_file": REPO_ROOT / "experiments" / "technology_mapping" / "baselines" / "BCD_to_7Segment_Conventional.v",
            "top_module": "BCD_to_7Segment_Conventional",
            "decoder_type": "None (Multilevel Boolean logic)",
            "or_routing_entries": "N/A (Algebraic logic)",
            "unrouted_minterms": [10, 11, 12, 13, 14, 15],
        },
        {
            "implementation": "Impl_C_Conventional_Zero_DC",
            "description": "Conventional Boolean Case Statement (States 10-15 forced to 7'b0000000)",
            "verilog_file": REPO_ROOT / "experiments" / "technology_mapping" / "baselines" / "BCD_to_7Segment_ZeroDC_Conventional.v",
            "top_module": "BCD_to_7Segment_Conventional_ZeroDC",
            "decoder_type": "None (Multilevel Boolean logic)",
            "or_routing_entries": "N/A (Algebraic logic)",
            "unrouted_minterms": "None (Forced to 0)",
        },
    ]

    records = []
    print("=== Starting Part G: BCD to 7-Segment Don't-Care Experiment ===")

    for cfg in impl_configs:
        impl_name = cfg["implementation"]
        top = cfg["top_module"]
        vfile = cfg["verilog_file"]

        print(f"\nEvaluating: {impl_name}")
        # Functional check
        fn_res = run_functional_check(vfile, top)
        print(f"  Valid digits (0-9) pass: {fn_res['valid_0_to_9_pass']}")
        dc_vectors = {k: fn_res["vectors"].get(k) for k in range(10, 16)}
        print(f"  Don't care output vectors (10-15): {dc_vectors}")

        for lib_path in [SKY130_LIB, NANGATE45_LIB]:
            lib_name = lib_path.stem
            w_lib = to_wsl_path(lib_path)
            w_vfile = to_wsl_path(vfile)
            mapped_v = output_dir / f"{top}_mapped_{lib_name}.v"
            w_mapped = to_wsl_path(mapped_v)
            log_file = logs_dir / f"map_{top}_{lib_name}.log"

            ys_script = f"""
read_verilog -sv {w_vfile}
hierarchy -top {top}
proc
memory
opt
stat
techmap
opt
abc -liberty {w_lib}
opt_clean -purge
stat -liberty {w_lib}
write_verilog -noattr {w_mapped}
"""
            tmp_ys = f"/tmp/bcd_{top}_{lib_name}.ys"
            subprocess.run(["wsl", "-e", "bash", "-c", f"cat > {tmp_ys} << 'EOF'\n{ys_script}\nEOF\n"], check=True)

            t0 = time.time()
            proc = subprocess.run(["wsl", "-e", "yosys", "-s", tmp_ys], capture_output=True, text=True)
            elapsed = time.time() - t0
            log_file.write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")

            # Parse stats
            stats_blocks = re.findall(r"=== ([^\n=]+) ===\s*\n(.*?)(?=(?:===|\n\d+\. Printing statistics\.|\nEnd of script|\Z))", proc.stdout, re.DOTALL)
            pre_cells = 0
            post_cells = 0
            chip_area = 0.0
            if stats_blocks:
                pre_m = re.search(r"Number of cells:\s*(\d+)", stats_blocks[0][1])
                if pre_m:
                    pre_cells = int(pre_m.group(1))
                post_m = re.search(r"Number of cells:\s*(\d+)", stats_blocks[-1][1])
                if post_m:
                    post_cells = int(post_m.group(1))
                area_m = re.search(r"Chip area for module[^:]*:\s*([\d\.]+)", stats_blocks[-1][1])
                if area_m:
                    chip_area = float(area_m.group(1))

            # ABC STA
            abc_cmd = f"read_lib {w_lib}; read_verilog -m {w_mapped}; stime -p"
            sta_proc = subprocess.run(["wsl", "-e", "yosys-abc", "-c", abc_cmd], capture_output=True, text=True)
            delay_ps = None
            del_m = re.search(r"Delay\s*=\s*([\d\.]+)\s*([pnum]s)", sta_proc.stdout)
            if del_m:
                val = float(del_m.group(1))
                if del_m.group(2) == "ns":
                    val *= 1000.0
                delay_ps = val
            path_lines = re.findall(r"Path\s+\d+\s+--\s+\d+\s*:\s*\d+\s+\d+\s+(\S+)\s+.*", sta_proc.stdout)
            path_cells = [c for c in path_lines if c not in ["pi", "po"]]
            path_stages = len(path_cells)

            rec = {
                "implementation": impl_name,
                "library": lib_name,
                "valid_digits_pass": fn_res["valid_0_to_9_pass"],
                "decoder_hardware_cost": cfg["decoder_type"],
                "or_routing_cost": cfg["or_routing_entries"],
                "dc_states_10_15_output": json.dumps(dc_vectors),
                "pre_mapping_cells": pre_cells,
                "mapped_cell_count": post_cells,
                "chip_area_um2": chip_area,
                "delay_ps": delay_ps,
                "logic_stages": path_stages,
                "critical_path_cells": "; ".join(path_cells),
                "runtime_sec": elapsed
            }
            records.append(rec)
            delay_str = f"{delay_ps:.1f} ps" if delay_ps is not None else "N/A"
            print(f"  [{lib_name}]: mapped_cells={post_cells}, area={chip_area:.2f} um^2, delay={delay_str} (stages={path_stages})")

    # Save CSV
    csv_path = output_dir.parent / "bcd_dont_care_results.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        headers = [
            "implementation",
            "library",
            "valid_digits_pass",
            "decoder_hardware_cost",
            "or_routing_cost",
            "pre_mapping_cells",
            "mapped_cell_count",
            "chip_area_um2",
            "delay_ps",
            "logic_stages",
            "critical_path_cells",
            "dc_states_10_15_output"
        ]
        f.write(",".join(headers) + "\n")
        for r in records:
            row = [
                r["implementation"],
                r["library"],
                str(r["valid_digits_pass"]),
                f'"{r["decoder_hardware_cost"]}"',
                str(r["or_routing_cost"]),
                str(r["pre_mapping_cells"]),
                str(r["mapped_cell_count"]),
                f"{r['chip_area_um2']:.4f}",
                f"{r['delay_ps']:.2f}" if r["delay_ps"] is not None else "",
                str(r["logic_stages"]),
                f'"{r["critical_path_cells"]}"',
                f'"{r["dc_states_10_15_output"].replace("\"", "\"\"")}"'
            ]
            f.write(",".join(row) + "\n")
    print(f"\nWrote BCD don't-care CSV: {csv_path}")

    return records


def main():
    parser = argparse.ArgumentParser(description="Part G: BCD Don't-Care Experiment")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "experiments" / "technology_mapping" / "results" / "bcd_dc"))
    args = parser.parse_args()

    run_bcd_experiment(Path(args.output_dir))


if __name__ == "__main__":
    main()
