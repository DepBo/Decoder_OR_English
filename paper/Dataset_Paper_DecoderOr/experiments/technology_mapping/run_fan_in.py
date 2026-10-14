"""
experiments/technology_mapping/run_fan_in.py
--------------------------------------------
Controlled OR Fan-In Experiment (Part E).
Investigates the impact of OR gate fan-in and tree decomposition on:
- Logical tree depth
- Pre-mapping cell count
- Mapped cell count
- Mapped standard-cell area
- Critical-path delay (ps)
- Logic depth (stages)

Uses a controlled 64-input synthetic OR reduction function across:
max_fan_in in {2, 4, 8, 16, 32, 64}.
"""

import re
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from compiler.or_tree import (
    decompose_or_tree,
    emit_or_tree_verilog,
    verify_or_tree_equivalence,
    ORTreeDecomposition,
)

SKY130_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "sky130_fd_sc_hd__tt_025C_1v80.lib"
NANGATE45_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "NangateOpenCellLibrary_typical.lib"


def to_wsl_path(p: Path) -> str:
    s = str(p.resolve()).replace('\\', '/')
    if len(s) >= 2 and s[1] == ':':
        drive = s[0].lower()
        return f"/mnt/{drive}{s[2:]}"
    return s


def generate_fanin_verilog(num_inputs: int = 64, max_fan_in: int = 4) -> str:
    """Generates Verilog RTL for a controlled N-input OR tree with max_fan_in constraint."""
    mod_name = f"OR{num_inputs}_FanIn_{max_fan_in}"
    leaf_names = [f"in[{i}]" for i in range(num_inputs)]
    
    decomp = decompose_or_tree(leaf_names, max_fan_in=max_fan_in, node_prefix="or_n")
    # Verify Boolean equivalence
    verify_or_tree_equivalence(decomp)

    wire_decls, assign_stmts = emit_or_tree_verilog(decomp, output_signal="out")

    lines = [
        f"// ============================================================",
        f"// Module: {mod_name}",
        f"// 64-input OR reduction with max_fan_in = {max_fan_in}",
        f"// Logical Tree Depth: {decomp.tree_depth}, Internal OR Nodes: {decomp.number_of_internal_or_nodes}",
        f"// ============================================================",
        f"module {mod_name} (",
        f"    input  wire [{num_inputs - 1}:0] in,",
        f"    output wire out",
        f");",
        "",
    ]
    for wd in wire_decls:
        lines.append(f"    {wd}")
    for ast in assign_stmts:
        lines.append(f"    {ast}")
    lines.append("")
    lines.append("endmodule")
    lines.append("")
    return "\n".join(lines), decomp


def run_fan_in_experiment(
    output_dir: Path = REPO_ROOT / "experiments" / "technology_mapping" / "results" / "fan_in",
    num_inputs: int = 64,
    fan_in_list: List[int] = [2, 4, 8, 16, 32, 64],
    libraries: List[Path] = [SKY130_LIB, NANGATE45_LIB]
) -> List[Dict[str, Any]]:
    """Runs the controlled OR fan-in experiment across all specified fan-ins and libraries."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rtl_dir = output_dir / "rtl"
    rtl_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    records = []

    print(f"=== Starting OR Fan-In Experiment (Inputs: {num_inputs}, Fan-ins: {fan_in_list}) ===")

    for k in fan_in_list:
        v_code, decomp = generate_fanin_verilog(num_inputs=num_inputs, max_fan_in=k)
        v_file = rtl_dir / f"OR{num_inputs}_FanIn_{k}.v"
        v_file.write_text(v_code, encoding="utf-8")
        v_size_bytes = len(v_code.encode("utf-8"))
        v_lines = len(v_code.splitlines())

        w_vfile = to_wsl_path(v_file)
        mod_name = f"OR{num_inputs}_FanIn_{k}"

        for lib_path in libraries:
            lib_name = lib_path.stem
            w_lib = to_wsl_path(lib_path)
            mapped_v = output_dir / f"{mod_name}_mapped_{lib_name}.v"
            w_mapped = to_wsl_path(mapped_v)
            log_file = logs_dir / f"map_{mod_name}_{lib_name}.log"

            ys_script = f"""
read_verilog -sv {w_vfile}
hierarchy -top {mod_name}
proc
opt
stat
techmap
opt
abc -liberty {w_lib}
opt_clean -purge
stat -liberty {w_lib}
write_verilog -noattr {w_mapped}
"""
            tmp_ys = f"/tmp/fanin_{k}_{lib_name}.ys"
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

            # Run ABC STA for timing
            abc_cmd = f"read_lib {w_lib}; read_verilog -m {w_mapped}; stime -p"
            sta_proc = subprocess.run(["wsl", "-e", "yosys-abc", "-c", abc_cmd], capture_output=True, text=True)
            
            delay_ps = None
            path_stages = 0
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
                "max_fan_in": k,
                "library": lib_name,
                "logical_tree_depth": decomp.tree_depth,
                "internal_or_nodes": decomp.number_of_internal_or_nodes,
                "verilog_bytes": v_size_bytes,
                "verilog_lines": v_lines,
                "yosys_pre_cells": pre_cells,
                "mapped_cells": post_cells,
                "mapped_area_um2": chip_area,
                "delay_ps": delay_ps,
                "critical_path_stages": path_stages,
                "critical_path_cells": "; ".join(path_cells),
                "runtime_sec": elapsed,
            }
            records.append(rec)
            print(f"k={k:2d} [{lib_name}]: depth={decomp.tree_depth}, nodes={decomp.number_of_internal_or_nodes} -> mapped_cells={post_cells}, area={chip_area:.2f} um^2, delay={delay_ps:.1f} ps (stages={path_stages})")

    # Write CSV
    csv_path = output_dir.parent / "fan_in_results.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        headers = [
            "max_fan_in",
            "library",
            "logical_tree_depth",
            "internal_or_nodes",
            "verilog_bytes",
            "verilog_lines",
            "yosys_pre_cells",
            "mapped_cells",
            "mapped_area_um2",
            "delay_ps",
            "critical_path_stages",
            "critical_path_cells"
        ]
        f.write(",".join(headers) + "\n")
        for r in records:
            row = [
                str(r["max_fan_in"]),
                r["library"],
                str(r["logical_tree_depth"]),
                str(r["internal_or_nodes"]),
                str(r["verilog_bytes"]),
                str(r["verilog_lines"]),
                str(r["yosys_pre_cells"]),
                str(r["mapped_cells"]),
                f"{r['mapped_area_um2']:.4f}",
                f"{r['delay_ps']:.2f}" if r["delay_ps"] is not None else "",
                str(r["critical_path_stages"]),
                f'"{r["critical_path_cells"]}"'
            ]
            f.write(",".join(row) + "\n")
    print(f"\nWrote fan-in experiment CSV: {csv_path}")
    return records


def main():
    parser = argparse.ArgumentParser(description="OR Fan-In Technology Mapping Experiment")
    parser.add_argument("--inputs", type=int, default=64, help="Number of OR inputs (default: 64)")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "experiments" / "technology_mapping" / "results" / "fan_in"))
    args = parser.parse_args()

    run_fan_in_experiment(output_dir=Path(args.output_dir), num_inputs=args.inputs)


if __name__ == "__main__":
    main()
