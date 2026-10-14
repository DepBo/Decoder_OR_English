"""
experiments/technology_mapping/run_sta.py
-----------------------------------------
Static Timing Analysis (STA) for technology-mapped netlists using:
1. ABC built-in Liberty STA engine (stime -p) with exact NLDM delay tables.
2. Yosys Longest Topological Path (ltp) for logic depth extraction.
"""

import re
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Default paths
MAPPED_DIR = REPO_ROOT / "experiments" / "technology_mapping" / "results"
SKY130_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "sky130_fd_sc_hd__tt_025C_1v80.lib"
NANGATE45_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "NangateOpenCellLibrary_typical.lib"


def to_wsl_path(p: Path) -> str:
    s = str(p.resolve()).replace('\\', '/')
    if len(s) >= 2 and s[1] == ':':
        drive = s[0].lower()
        return f"/mnt/{drive}{s[2:]}"
    return s


def parse_abc_stime(output: str) -> Dict[str, Any]:
    """Parses delay, gates, startpoint, endpoint, and critical path stages from ABC stime output."""
    res = {
        "delay_ps": None,
        "gates": None,
        "area": None,
        "startpoint": None,
        "endpoint": None,
        "path_stages": None,
        "critical_path_cells": [],
        "raw_path_lines": [],
    }

    # Summary line: WireLoad = "none"  Gates = 2 ... Area = 15.01 ... Delay = 119.34 ps
    delay_m = re.search(r"Delay\s*=\s*([\d\.]+)\s*([pnum]s)", output)
    if delay_m:
        val = float(delay_m.group(1))
        unit = delay_m.group(2)
        if unit == "ns":
            val *= 1000.0  # convert to ps
        elif unit == "us":
            val *= 1000000.0
        res["delay_ps"] = val

    gates_m = re.search(r"Gates\s*=\s*(\d+)", output)
    if gates_m:
        res["gates"] = int(gates_m.group(1))

    area_m = re.search(r"Area\s*=\s*([\d\.]+)", output)
    if area_m:
        res["area"] = float(area_m.group(1))

    # Startpoint and Endpoint
    sp_m = re.search(r"Start-point\s*=\s*([^\.]+)\.\s*End-point\s*=\s*([^\.]+)\.", output)
    if sp_m:
        res["startpoint"] = sp_m.group(1).strip()
        res["endpoint"] = sp_m.group(2).strip()

    # Path lines: Path  1 --       6 : 2    1 sky130_fd_sc_hd__xor2_1 ...
    path_lines = re.findall(r"Path\s+\d+\s+--\s+\d+\s*:\s*\d+\s+\d+\s+(\S+)\s+.*", output)
    cells = [c for c in path_lines if c not in ["pi", "po"]]
    res["critical_path_cells"] = cells
    res["path_stages"] = len(cells)

    return res


def run_yosys_ltp(verilog_path: Path, top_module: str) -> int:
    """Runs Yosys ltp to determine the longest topological path length."""
    w_verilog = to_wsl_path(verilog_path)
    ys = f"read_verilog -sv {w_verilog}; hierarchy -top {top_module}; opt_clean -purge; ltp"
    cmd = ["wsl", "-e", "yosys", "-p", ys]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        m = re.search(r"length=(\d+)", proc.stdout)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return -1


def run_sta_single(
    mapped_netlist: Path,
    lib_path: Path,
    top_module: str,
    log_path: Path
) -> Dict[str, Any]:
    """Runs ABC stime and Yosys ltp on a single mapped netlist."""
    w_netlist = to_wsl_path(mapped_netlist)
    w_lib = to_wsl_path(lib_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    abc_cmd = f"read_lib {w_lib}; read_verilog -m {w_netlist}; stime -p"
    proc = subprocess.run(
        ["wsl", "-e", "yosys-abc", "-c", abc_cmd],
        capture_output=True,
        text=True,
        timeout=60
    )
    full_log = proc.stdout + "\n" + proc.stderr
    log_path.write_text(full_log, encoding="utf-8")

    parsed = parse_abc_stime(proc.stdout)
    parsed["returncode"] = proc.returncode
    parsed["topological_depth"] = run_yosys_ltp(mapped_netlist, top_module)
    return parsed


def run_all_sta(
    results_dir: Path = MAPPED_DIR,
    output_csv: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Runs STA on all generated mapped netlists in results_dir."""
    output_csv = output_csv or results_dir / "sta_results.csv"
    logs_dir = results_dir / "logs" / "sta"
    logs_dir.mkdir(parents=True, exist_ok=True)

    sta_records = []
    
    # Check what mapped files exist
    mapped_files = list(results_dir.glob("*_mapped_*.v"))
    if not mapped_files:
        print("No mapped netlist files found in", results_dir)
        return []

    print(f"=== Running Static Timing Analysis on {len(mapped_files)} netlists ===")

    for vfile in sorted(mapped_files):
        # Extract design name and lib name from filename: {design}_mapped_{lib}.v
        m = re.match(r"^(.*)_mapped_(.*)\.v$", vfile.name)
        if not m:
            continue
        design_name = m.group(1)
        lib_name = m.group(2)

        # Determine library path
        lib_path = SKY130_LIB if "sky130" in lib_name else NANGATE45_LIB

        # Determine top module name
        top_module = f"{design_name}_Decoder_OR"
        if design_name in ["3bit_Comparator", "2_to_1_MUX", "8bit_Comparator"]:
            top_module = f"_{top_module}"

        log_path = logs_dir / f"abc_sta_{design_name}_{lib_name}.log"
        print(f"Timing analysis: {design_name} [{lib_name}]...")
        
        t0 = time.time()
        res = run_sta_single(vfile, lib_path, top_module, log_path)
        res["design"] = design_name
        res["library"] = lib_name
        res["netlist"] = vfile.name
        res["runtime_sec"] = time.time() - t0

        print(f"  Delay: {res['delay_ps']} ps, Path stages: {res['path_stages']}, Topo depth: {res['topological_depth']}")
        print(f"  Path: {res['startpoint']} -> {res['endpoint']}, Cells: {res['critical_path_cells']}")
        sta_records.append(res)

    # Save to CSV
    with open(output_csv, "w", encoding="utf-8") as f:
        headers = [
            "design",
            "library",
            "netlist",
            "worst_path_delay_ps",
            "logic_stages",
            "topological_depth",
            "total_gates",
            "estimated_area_um2",
            "startpoint",
            "endpoint",
            "critical_path_cells"
        ]
        f.write(",".join(headers) + "\n")
        for r in sta_records:
            cells_str = "; ".join(r.get("critical_path_cells", []))
            row = [
                r["design"],
                r["library"],
                r["netlist"],
                f"{r.get('delay_ps', 0.0):.2f}" if r.get('delay_ps') is not None else "",
                str(r.get("path_stages", "")),
                str(r.get("topological_depth", "")),
                str(r.get("gates", "")),
                f"{r.get('area', 0.0):.4f}" if r.get('area') is not None else "",
                str(r.get("startpoint", "")),
                str(r.get("endpoint", "")),
                f'"{cells_str}"'
            ]
            f.write(",".join(row) + "\n")
    print(f"\nWrote STA results CSV: {output_csv}")

    return sta_records


def main():
    parser = argparse.ArgumentParser(description="Step 3B Static Timing Analysis Runner")
    parser.add_argument("--results-dir", default=str(MAPPED_DIR), help="Directory containing mapped netlists")
    parser.add_argument("--output", default=None, help="Output CSV path")
    args = parser.parse_args()

    rdir = Path(args.results_dir)
    out_csv = Path(args.output) if args.output else rdir / "sta_results.csv"
    run_all_sta(rdir, out_csv)


if __name__ == "__main__":
    main()
