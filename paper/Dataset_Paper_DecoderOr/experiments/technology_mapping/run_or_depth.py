"""
experiments/technology_mapping/run_or_depth.py
----------------------------------------------
Part F: OR-Tree Depth Scaling and Comparator Audit Experiment.
1. Audits the 8-bit comparator OR-tree output reductions:
   - A_gt_B: 32,640 minterms, 10,923 internal OR nodes, tree depth 8
   - A_eq_B: 256 minterms, 85 internal OR nodes, tree depth 4
   - A_lt_B: 32,640 minterms, 10,923 internal OR nodes, tree depth 8
   - Total internal OR nodes: 21,931
2. Compares Balanced OR Tree vs. Deliberately Unbalanced Linear Cascade
   on identical Boolean functions (N=64 and N=256 inputs, matching A_eq_B).
   Measures:
   - Logical depth
   - Pre-mapping cells
   - Mapped cell count (Sky130 & Nangate45)
   - Mapped area (um^2)
   - Critical path delay (ps)
   - Critical path logic stages
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


def audit_8bit_comparator() -> Dict[str, Any]:
    """Extracts and verifies the exact audited OR-tree statistics for the 8-bit comparator."""
    outputs_meta = {
        "A_gt_B": 32640,
        "A_eq_B": 256,
        "A_lt_B": 32640,
    }
    
    audit_results = {}
    total_internal_nodes = 0

    for out_name, count in outputs_meta.items():
        dummy_pins = [f"Y{i}" for i in range(count)]
        decomp = decompose_or_tree(dummy_pins, max_fan_in=4, node_prefix=f"{out_name}_or")
        audit_results[out_name] = {
            "active_routing_entries": count,
            "internal_or_nodes": decomp.number_of_internal_or_nodes,
            "tree_depth": decomp.tree_depth,
            "max_fan_in": decomp.max_fan_in,
        }
        total_internal_nodes += decomp.number_of_internal_or_nodes

    audit_results["total_internal_or_nodes"] = total_internal_nodes
    audit_results["reference_match"] = (
        audit_results["A_gt_B"]["internal_or_nodes"] == 10923 and
        audit_results["A_eq_B"]["internal_or_nodes"] == 85 and
        audit_results["A_lt_B"]["internal_or_nodes"] == 10923 and
        total_internal_nodes == 21931
    )
    return audit_results


def generate_unbalanced_linear_verilog(num_inputs: int) -> str:
    """Generates an unbalanced linear cascade OR reduction with scalar ports."""
    mod_name = f"OR{num_inputs}_Unbalanced_Linear"
    ports = ",\n    ".join(f"input wire in_{i}" for i in range(num_inputs))
    lines = [
        f"// Deliberately Unbalanced Linear Cascade OR reduction",
        f"// Inputs: {num_inputs}, Logical Depth: {num_inputs - 1}, Gates: {num_inputs - 1}",
        f"module {mod_name} (",
        f"    {ports},",
        f"    output wire out",
        f");",
    ]
    if num_inputs <= 1:
        lines.append("    assign out = in_0;")
    else:
        lines.append(f"    wire [{num_inputs - 2}:0] chain;")
        lines.append(f"    assign chain[0] = in_0 | in_1;")
        for i in range(1, num_inputs - 1):
            target = "out" if i == num_inputs - 2 else f"chain[{i}]"
            lines.append(f"    assign {target} = chain[{i - 1}] | in_{i + 1};")
    lines.append("endmodule\n")
    return "\n".join(lines)


def generate_balanced_tree_verilog(num_inputs: int, max_fan_in: int = 4) -> Tuple[str, ORTreeDecomposition]:
    """Generates balanced OR-tree Verilog with scalar ports."""
    mod_name = f"OR{num_inputs}_Balanced_FanIn{max_fan_in}"
    leaf_names = [f"in_{i}" for i in range(num_inputs)]
    decomp = decompose_or_tree(leaf_names, max_fan_in=max_fan_in, node_prefix="b_or")
    wire_decls, assign_stmts = emit_or_tree_verilog(decomp, output_signal="out")

    ports = ",\n    ".join(f"input wire in_{i}" for i in range(num_inputs))
    lines = [
        f"// Balanced OR Tree with max_fan_in={max_fan_in}",
        f"// Inputs: {num_inputs}, Logical Depth: {decomp.tree_depth}, Internal Nodes: {decomp.number_of_internal_or_nodes}",
        f"module {mod_name} (",
        f"    {ports},",
        f"    output wire out",
        f");",
    ]
    for w in wire_decls:
        lines.append(f"    {w}")
    for a in assign_stmts:
        lines.append(f"    {a}")
    lines.append("endmodule\n")
    return "\n".join(lines), decomp


def run_depth_comparison(
    output_dir: Path,
    input_sizes: List[int] = [64, 256],
    libraries: List[Path] = [SKY130_LIB, NANGATE45_LIB]
) -> List[Dict[str, Any]]:
    """Compares balanced vs unbalanced OR trees across input sizes and standard cell libraries."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    records = []

    for N in input_sizes:
        # 1. Balanced Tree (max_fan_in = 4)
        b_vcode, b_decomp = generate_balanced_tree_verilog(N, max_fan_in=4)
        b_mod = f"OR{N}_Balanced_FanIn4"
        b_vfile = output_dir / f"{b_mod}.v"
        b_vfile.write_text(b_vcode, encoding="utf-8")

        # 2. Unbalanced Linear Cascade
        u_vcode = generate_unbalanced_linear_verilog(N)
        u_mod = f"OR{N}_Unbalanced_Linear"
        u_vfile = output_dir / f"{u_mod}.v"
        u_vfile.write_text(u_vcode, encoding="utf-8")

        variants = [
            ("Balanced_Tree_k4", b_mod, b_vfile, b_decomp.tree_depth, b_decomp.number_of_internal_or_nodes),
            ("Unbalanced_Linear_Chain", u_mod, u_vfile, N - 1, N - 1),
        ]

        for topology, mod_name, v_file, log_depth, log_gates in variants:
            w_vfile = to_wsl_path(v_file)

            for lib_path in libraries:
                lib_name = lib_path.stem
                w_lib = to_wsl_path(lib_path)
                mapped_v = output_dir / f"{mod_name}_mapped_{lib_name}.v"
                w_mapped = to_wsl_path(mapped_v)
                log_file = logs_dir / f"depth_{mod_name}_{lib_name}.log"

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
                tmp_ys = f"/tmp/depth_{mod_name}_{lib_name}.ys"
                subprocess.run(["wsl", "-e", "bash", "-c", f"cat > {tmp_ys} << 'EOF'\n{ys_script}\nEOF\n"], check=True)

                t0 = time.time()
                proc = subprocess.run(["wsl", "-e", "yosys", "-s", tmp_ys], capture_output=True, text=True)
                elapsed = time.time() - t0
                log_file.write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")

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
                    "num_inputs": N,
                    "topology": topology,
                    "library": lib_name,
                    "logical_depth": log_depth,
                    "logical_gates": log_gates,
                    "pre_cells": pre_cells,
                    "mapped_cells": post_cells,
                    "mapped_area_um2": chip_area,
                    "delay_ps": delay_ps,
                    "critical_path_stages": path_stages,
                    "critical_path_cells": "; ".join(path_cells),
                    "runtime_sec": elapsed
                }
                records.append(rec)
                delay_str = f"{delay_ps:.1f} ps" if delay_ps is not None else "N/A"
                print(f"N={N:3d} [{topology}] [{lib_name}]: log_depth={log_depth}, log_gates={log_gates} -> mapped_cells={post_cells}, area={chip_area:.2f} um^2, delay={delay_str} (stages={path_stages})")

    return records


def main():
    parser = argparse.ArgumentParser(description="Part F: OR-Tree Depth Scaling & Comparator Audit")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "experiments" / "technology_mapping" / "results" / "or_depth"))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Step 3B Part F: 8-bit Comparator OR-Tree Audit ===")
    audit = audit_8bit_comparator()
    print(f"  A_gt_B (32,640 minterms): {audit['A_gt_B']['internal_or_nodes']} nodes, depth {audit['A_gt_B']['tree_depth']}")
    print(f"  A_eq_B (   256 minterms): {audit['A_eq_B']['internal_or_nodes']} nodes, depth {audit['A_eq_B']['tree_depth']}")
    print(f"  A_lt_B (32,640 minterms): {audit['A_lt_B']['internal_or_nodes']} nodes, depth {audit['A_lt_B']['tree_depth']}")
    print(f"  Total internal OR nodes : {audit['total_internal_or_nodes']}")
    print(f"  Exact reference match   : {audit['reference_match']}")

    # Save audit JSON
    audit_json = out_dir / "comparator_audit.json"
    audit_json.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"Wrote audit JSON: {audit_json}")

    print("\n=== Balanced vs Unbalanced OR-Tree Scaling Experiment ===")
    records = run_depth_comparison(out_dir)

    # Save CSV
    csv_path = out_dir.parent / "or_depth_scaling_results.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        headers = [
            "num_inputs",
            "topology",
            "library",
            "logical_depth",
            "logical_gates",
            "pre_cells",
            "mapped_cells",
            "mapped_area_um2",
            "delay_ps",
            "critical_path_stages",
            "critical_path_cells"
        ]
        f.write(",".join(headers) + "\n")
        for r in records:
            row = [
                str(r["num_inputs"]),
                r["topology"],
                r["library"],
                str(r["logical_depth"]),
                str(r["logical_gates"]),
                str(r["pre_cells"]),
                str(r["mapped_cells"]),
                f"{r['mapped_area_um2']:.4f}",
                f"{r['delay_ps']:.2f}" if r["delay_ps"] is not None else "",
                str(r["critical_path_stages"]),
                f'"{r["critical_path_cells"]}"'
            ]
            f.write(",".join(row) + "\n")
    print(f"Wrote OR-depth scaling CSV: {csv_path}")


if __name__ == "__main__":
    main()
