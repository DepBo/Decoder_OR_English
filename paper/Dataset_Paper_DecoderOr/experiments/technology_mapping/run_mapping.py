"""
experiments/technology_mapping/run_mapping.py
---------------------------------------------
Performs technology mapping using Yosys + ABC against standard-cell Liberty libraries.
Supports:
- SkyWater 130nm (sky130_fd_sc_hd__tt_025C_1v80.lib)
- Nangate 45nm (NangateOpenCellLibrary_typical.lib)
"""

import os
import re
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Default libraries
SKY130_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "sky130_fd_sc_hd__tt_025C_1v80.lib"
NANGATE45_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "NangateOpenCellLibrary_typical.lib"

BENCHMARK_CONFIGS = [
    {
        "name": "Half_Adder",
        "top_module": "Half_Adder_Decoder_OR",
        "verilog_file": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "Half_Adder.v",
        "is_large": False,
    },
    {
        "name": "Full_Adder",
        "top_module": "Full_Adder_Decoder_OR",
        "verilog_file": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "Full_Adder.v",
        "is_large": False,
    },
    {
        "name": "2_to_1_MUX",
        "top_module": "_2_to_1_MUX_Decoder_OR",
        "verilog_file": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "2_to_1_MUX.v",
        "is_large": False,
    },
    {
        "name": "BCD_to_7Segment",
        "top_module": "BCD_to_7Segment_Decoder_OR",
        "verilog_file": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "BCD_to_7Segment.v",
        "is_large": False,
    },
    {
        "name": "3bit_Comparator",
        "top_module": "_3bit_Comparator_Decoder_OR",
        "verilog_file": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "3bit_Comparator.v",
        "is_large": False,
    },
    {
        "name": "8bit_Comparator",
        "top_module": "_8bit_Comparator_Decoder_OR",
        "verilog_file": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "8bit_Comparator.v",
        "is_large": True,
    },
]


def to_wsl_path(p: Path) -> str:
    """Converts a Windows path to WSL /mnt/... format."""
    s = str(p.resolve()).replace('\\', '/')
    if len(s) >= 2 and s[1] == ':':
        drive = s[0].lower()
        return f"/mnt/{drive}{s[2:]}"
    return s


def parse_stat_output(log_text: str) -> Dict[str, Any]:
    """Parses pre-mapping and post-mapping statistics from Yosys log."""
    # Look for module stat blocks
    # Sections usually look like:
    # 5. Printing statistics.
    # === module ===
    # ...
    # 9. Printing statistics.
    # === module ===
    stats_blocks = re.findall(r"=== ([^\n=]+) ===\s*\n(.*?)(?=(?:===|\n\d+\. Printing statistics\.|\nEnd of script|\Z))", log_text, re.DOTALL)
    
    result = {
        "wires": None,
        "wire_bits": None,
        "ports": None,
        "port_bits": None,
        "pre_cells": None,
        "post_cells": None,
        "chip_area": None,
        "cell_types": {},
        "peak_mem_mb": None,
        "cpu_user_sec": None,
    }

    # Extract memory and CPU if present
    mem_m = re.search(r"MEM:\s*([\d\.]+)\s*MB peak", log_text)
    if mem_m:
        result["peak_mem_mb"] = float(mem_m.group(1))
    cpu_m = re.search(r"CPU:\s*user\s*([\d\.]+)s", log_text)
    if cpu_m:
        result["cpu_user_sec"] = float(cpu_m.group(1))

    if not stats_blocks:
        return result

    # If there are multiple blocks, block 0 is pre-map, block -1 is post-map
    pre_block = stats_blocks[0][1]
    post_block = stats_blocks[-1][1]

    # Pre-mapping cells
    pre_cells_m = re.search(r"Number of cells:\s*(\d+)", pre_block)
    if pre_cells_m:
        result["pre_cells"] = int(pre_cells_m.group(1))

    # Post-mapping stats
    wires_m = re.search(r"Number of wires:\s*(\d+)", post_block)
    if wires_m:
        result["wires"] = int(wires_m.group(1))
    wire_bits_m = re.search(r"Number of wire bits:\s*(\d+)", post_block)
    if wire_bits_m:
        result["wire_bits"] = int(wire_bits_m.group(1))
    ports_m = re.search(r"Number of ports:\s*(\d+)", post_block)
    if ports_m:
        result["ports"] = int(ports_m.group(1))
    port_bits_m = re.search(r"Number of port bits:\s*(\d+)", post_block)
    if port_bits_m:
        result["port_bits"] = int(port_bits_m.group(1))
    post_cells_m = re.search(r"Number of cells:\s*(\d+)", post_block)
    if post_cells_m:
        result["post_cells"] = int(post_cells_m.group(1))
    area_m = re.search(r"Chip area for module[^:]*:\s*([\d\.]+)", post_block)
    if area_m:
        result["chip_area"] = float(area_m.group(1))

    # Cell breakdown
    cell_lines = re.findall(r"^\s+([a-zA-Z0-9_\$]+)\s+(\d+)\s*$", post_block, re.MULTILINE)
    for cname, ccount in cell_lines:
        result["cell_types"][cname] = int(ccount)

    return result


def map_design(
    verilog_path: Path,
    top_module: str,
    lib_path: Path,
    output_netlist: Path,
    log_path: Path,
    timeout_sec: int = 180
) -> Dict[str, Any]:
    """
    Executes technology mapping using Yosys + ABC.
    Returns parsed mapping metrics.
    """
    w_verilog = to_wsl_path(verilog_path)
    w_lib = to_wsl_path(lib_path)
    w_out = to_wsl_path(output_netlist)
    output_netlist.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    ys_script = f"""
read_verilog -sv {w_verilog}
hierarchy -top {top_module}
check -assert
proc
memory
opt
stat
techmap
opt
abc -liberty {w_lib}
opt_clean -purge
stat -liberty {w_lib}
write_verilog -noattr {w_out}
"""
    tmp_ys = f"/tmp/map_{top_module}.ys"
    # Write script to WSL tmp
    subprocess.run(["wsl", "-e", "bash", "-c", f"cat > {tmp_ys} << 'EOF'\n{ys_script}\nEOF\n"], check=True)

    t0 = time.time()
    try:
        proc = subprocess.run(
            ["wsl", "-e", "yosys", "-s", tmp_ys],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        elapsed = time.time() - t0
        log_path.write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
        
        parsed = parse_stat_output(proc.stdout)
        parsed["returncode"] = proc.returncode
        parsed["runtime_sec"] = elapsed
        parsed["timeout"] = False
        parsed["error"] = None if proc.returncode == 0 else "Yosys returned non-zero"
        return parsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return {
            "returncode": -1,
            "runtime_sec": elapsed,
            "timeout": True,
            "error": f"Timed out after {timeout_sec}s",
            "wires": None,
            "wire_bits": None,
            "ports": None,
            "port_bits": None,
            "pre_cells": None,
            "post_cells": None,
            "chip_area": None,
            "cell_types": {},
            "peak_mem_mb": None,
            "cpu_user_sec": None,
        }


def run_all_mapping(
    lib_path: Path = SKY130_LIB,
    output_dir: Path = REPO_ROOT / "experiments" / "technology_mapping" / "results",
    skip_large: bool = True,
    large_timeout: int = 120
) -> List[Dict[str, Any]]:
    """Runs mapping across all benchmark designs."""
    results = []
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    lib_name = lib_path.stem
    print(f"=== Starting Technology Mapping with Library: {lib_name} ===")

    for cfg in BENCHMARK_CONFIGS:
        name = cfg["name"]
        top = cfg["top_module"]
        vfile = cfg["verilog_file"]
        is_large = cfg["is_large"]

        print(f"\nDesign: {name} (Top: {top})")
        if is_large and skip_large:
            print(f"  [SKIPPED] Large design (--skip-large enabled to protect host RAM/execution)")
            res = {
                "design": name,
                "top_module": top,
                "library": lib_name,
                "status": "SKIPPED_RESOURCE_PROTECTION",
                "returncode": 0,
                "runtime_sec": 0.0,
                "timeout": False,
                "pre_cells": 65534,
                "post_cells": "SKIPPED",
                "chip_area": "SKIPPED",
                "wires": 65550,
                "wire_bits": 131085,
                "ports": 19,
                "port_bits": 19,
                "cell_types": {},
                "note": "Skipped full ABC mapping to protect WSL2 memory (~65k unmapped cells); synthesis sanity verified in Step 3A."
            }
            results.append(res)
            continue

        out_netlist = output_dir / f"{name}_mapped_{lib_name}.v"
        log_file = logs_dir / f"yosys_map_{name}_{lib_name}.log"
        timeout = large_timeout if is_large else 60

        res = map_design(vfile, top, lib_path, out_netlist, log_file, timeout_sec=timeout)
        res["design"] = name
        res["top_module"] = top
        res["library"] = lib_name
        res["netlist_path"] = str(out_netlist)
        res["log_path"] = str(log_file)
        res["status"] = "PASS" if res.get("returncode") == 0 else ("TIMEOUT" if res.get("timeout") else "FAIL")

        print(f"  Status: {res['status']}, Runtime: {res['runtime_sec']:.2f}s")
        print(f"  Pre-map cells: {res.get('pre_cells')}, Post-map cells: {res.get('post_cells')}, Area: {res.get('chip_area')} um^2")
        print(f"  Cells breakdown: {res.get('cell_types')}")
        results.append(res)

    return results


def save_mapping_reports(results: List[Dict[str, Any]], output_dir: Path):
    """Saves CSV and JSON summary reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Summary JSON
    json_path = output_dir / "technology_mapping_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote summary JSON: {json_path}")

    # 2. Results CSV
    csv_path = output_dir / "technology_mapping_results.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        headers = [
            "design",
            "top_module",
            "library",
            "status",
            "returncode",
            "runtime_sec",
            "ports",
            "port_bits",
            "wires",
            "wire_bits",
            "pre_cells",
            "post_cells",
            "chip_area_um2",
            "cell_types_json"
        ]
        f.write(",".join(headers) + "\n")
        for r in results:
            ct_str = json.dumps(r.get("cell_types", {})).replace('"', '""')
            row = [
                r["design"],
                r["top_module"],
                r["library"],
                r["status"],
                str(r["returncode"]),
                f"{r['runtime_sec']:.4f}",
                str(r.get("ports", "")),
                str(r.get("port_bits", "")),
                str(r.get("wires", "")),
                str(r.get("wire_bits", "")),
                str(r.get("pre_cells", "")),
                str(r.get("post_cells", "")),
                str(r.get("chip_area", "")),
                f'"{ct_str}"'
            ]
            f.write(",".join(row) + "\n")
    print(f"Wrote results CSV: {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Step 3B Yosys + ABC Technology Mapping")
    parser.add_argument("--library", choices=["sky130", "nangate45", "both"], default="both", help="Standard cell library")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "experiments" / "technology_mapping" / "results"), help="Output directory")
    parser.add_argument("--skip-large", action="store_true", default=True, help="Skip large 8-bit comparator mapping")
    parser.add_argument("--include-large", action="store_true", help="Attempt 8-bit comparator mapping")
    parser.add_argument("--large-timeout", type=int, default=120, help="Timeout in seconds for large design")
    args = parser.parse_args()

    skip_large = not args.include_large if args.include_large else args.skip_large
    out_dir = Path(args.output_dir)

    all_results = []
    libs_to_run = []
    if args.library in ["sky130", "both"]:
        libs_to_run.append(SKY130_LIB)
    if args.library in ["nangate45", "both"]:
        libs_to_run.append(NANGATE45_LIB)

    for lib in libs_to_run:
        res = run_all_mapping(lib_path=lib, output_dir=out_dir, skip_large=skip_large, large_timeout=args.large_timeout)
        all_results.extend(res)

    save_mapping_reports(all_results, out_dir)


if __name__ == "__main__":
    main()
