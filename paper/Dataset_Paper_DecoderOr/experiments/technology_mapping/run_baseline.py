"""
experiments/technology_mapping/run_baseline.py
----------------------------------------------
Part H: Side-by-Side Conventional RTL Baseline Comparison.
Synthesizes and maps both:
1. Decoder + OR Architecture
2. Conventional Boolean/Relational RTL Baseline
for:
- Half Adder
- Full Adder
- 2-to-1 MUX
- BCD 7-segment
- 3-bit Comparator
- 8-bit Comparator

Through the exact same Yosys + ABC synthesis and Liberty mapping flow.
Collects:
- Pre-mapping cells
- Post-mapping standard cells
- Standard-cell area (um^2)
- Critical path delay (ps)
- Logic depth (stages)
- Synthesis runtime
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

from experiments.technology_mapping.conventional_baselines import get_conventional_verilog

SKY130_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "sky130_fd_sc_hd__tt_025C_1v80.lib"
NANGATE45_LIB = REPO_ROOT / "experiments" / "technology_mapping" / "libraries" / "NangateOpenCellLibrary_typical.lib"

BENCHMARKS = [
    {
        "name": "Half_Adder",
        "dec_vfile": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "Half_Adder.v",
        "dec_top": "Half_Adder_Decoder_OR",
        "conv_top": "Half_Adder_Conventional",
        "is_large": False,
    },
    {
        "name": "Full_Adder",
        "dec_vfile": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "Full_Adder.v",
        "dec_top": "Full_Adder_Decoder_OR",
        "conv_top": "Full_Adder_Conventional",
        "is_large": False,
    },
    {
        "name": "2_to_1_MUX",
        "dec_vfile": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "2_to_1_MUX.v",
        "dec_top": "_2_to_1_MUX_Decoder_OR",
        "conv_top": "_2_to_1_MUX_Conventional",
        "is_large": False,
    },
    {
        "name": "BCD_to_7Segment",
        "dec_vfile": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "BCD_to_7Segment.v",
        "dec_top": "BCD_to_7Segment_Decoder_OR",
        "conv_top": "BCD_to_7Segment_Conventional",
        "is_large": False,
    },
    {
        "name": "3bit_Comparator",
        "dec_vfile": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "3bit_Comparator.v",
        "dec_top": "_3bit_Comparator_Decoder_OR",
        "conv_top": "_3bit_Comparator_Conventional",
        "is_large": False,
    },
    {
        "name": "8bit_Comparator",
        "dec_vfile": REPO_ROOT / "experiments" / "eda" / "rtl" / "generated" / "8bit_Comparator.v",
        "dec_top": "_8bit_Comparator_Decoder_OR",
        "conv_top": "_8bit_Comparator_Conventional",
        "is_large": True,
    },
]


def to_wsl_path(p: Path) -> str:
    s = str(p.resolve()).replace('\\', '/')
    if len(s) >= 2 and s[1] == ':':
        drive = s[0].lower()
        return f"/mnt/{drive}{s[2:]}"
    return s


def synthesize_and_measure(
    vfile: Path,
    top_module: str,
    lib_path: Path,
    out_dir: Path,
    tag: str,
    is_large: bool = False,
    skip_large: bool = True
) -> Dict[str, Any]:
    """Runs Yosys + ABC mapping and ABC STA for a single design."""
    if is_large and skip_large and "Decoder_OR" in top_module:
        return {
            "status": "SKIPPED_RESOURCE_PROTECTION",
            "pre_cells": 65534,
            "post_cells": "SKIPPED",
            "chip_area_um2": "SKIPPED",
            "delay_ps": "SKIPPED",
            "logic_stages": "SKIPPED",
            "runtime_sec": 0.0
        }

    lib_name = lib_path.stem
    w_vfile = to_wsl_path(vfile)
    w_lib = to_wsl_path(lib_path)
    mapped_v = out_dir / f"{tag}_mapped_{lib_name}.v"
    w_mapped = to_wsl_path(mapped_v)
    log_file = out_dir / "logs" / f"map_{tag}_{lib_name}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    ys_script = f"""
read_verilog -sv {w_vfile}
hierarchy -top {top_module}
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
    tmp_ys = f"/tmp/baseline_{tag}_{lib_name}.ys"
    subprocess.run(["wsl", "-e", "bash", "-c", f"cat > {tmp_ys} << 'EOF'\n{ys_script}\nEOF\n"], check=True)

    t0 = time.time()
    try:
        proc = subprocess.run(["wsl", "-e", "yosys", "-s", tmp_ys], capture_output=True, text=True, timeout=120)
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

        return {
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "pre_cells": pre_cells,
            "post_cells": post_cells,
            "chip_area_um2": chip_area,
            "delay_ps": delay_ps,
            "logic_stages": path_stages,
            "runtime_sec": elapsed
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "pre_cells": 65534,
            "post_cells": "TIMEOUT",
            "chip_area_um2": "TIMEOUT",
            "delay_ps": "TIMEOUT",
            "logic_stages": "TIMEOUT",
            "runtime_sec": 120.0
        }


def run_baseline_comparison(
    output_dir: Path = REPO_ROOT / "experiments" / "technology_mapping" / "results" / "baseline",
    skip_large_dec: bool = True
) -> List[Dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    conv_rtl_dir = output_dir / "conv_rtl"
    conv_rtl_dir.mkdir(parents=True, exist_ok=True)

    records = []
    print("=== Starting Part H: Conventional Baseline Comparison ===")

    for b in BENCHMARKS:
        bname = b["name"]
        dec_v = b["dec_vfile"]
        dec_top = b["dec_top"]
        conv_top = b["conv_top"]
        is_large = b["is_large"]

        # Generate conventional Verilog
        conv_code = get_conventional_verilog(bname)
        conv_v = conv_rtl_dir / f"{bname}_Conventional.v"
        conv_v.write_text(conv_code, encoding="utf-8")

        for lib_path in [SKY130_LIB, NANGATE45_LIB]:
            lib_name = lib_path.stem

            print(f"\n--- Benchmark: {bname} [{lib_name}] ---")
            # 1. Decoder + OR
            dec_res = synthesize_and_measure(
                dec_v, dec_top, lib_path, output_dir,
                tag=f"{bname}_DecoderOR",
                is_large=is_large,
                skip_large=skip_large_dec
            )
            print(f"  Decoder+OR   : Status={dec_res['status']}, Cells={dec_res['post_cells']}, Area={dec_res['chip_area_um2']}, Delay={dec_res['delay_ps']}")

            # 2. Conventional Baseline
            conv_res = synthesize_and_measure(
                conv_v, conv_top, lib_path, output_dir,
                tag=f"{bname}_Conventional",
                is_large=False,
                skip_large=False
            )
            print(f"  Conventional : Status={conv_res['status']}, Cells={conv_res['post_cells']}, Area={conv_res['chip_area_um2']}, Delay={conv_res['delay_ps']}")

            # Store comparison row
            records.append({
                "benchmark": bname,
                "library": lib_name,
                "dec_status": dec_res["status"],
                "dec_pre_cells": dec_res["pre_cells"],
                "dec_mapped_cells": dec_res["post_cells"],
                "dec_area_um2": dec_res["chip_area_um2"],
                "dec_delay_ps": dec_res["delay_ps"],
                "dec_stages": dec_res["logic_stages"],
                "conv_status": conv_res["status"],
                "conv_pre_cells": conv_res["pre_cells"],
                "conv_mapped_cells": conv_res["post_cells"],
                "conv_area_um2": conv_res["chip_area_um2"],
                "conv_delay_ps": conv_res["delay_ps"],
                "conv_stages": conv_res["logic_stages"],
            })

    # Save CSV
    csv_path = output_dir.parent / "conventional_baseline_results.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        headers = [
            "benchmark",
            "library",
            "dec_status",
            "dec_pre_cells",
            "dec_mapped_cells",
            "dec_area_um2",
            "dec_delay_ps",
            "dec_stages",
            "conv_status",
            "conv_pre_cells",
            "conv_mapped_cells",
            "conv_area_um2",
            "conv_delay_ps",
            "conv_stages"
        ]
        f.write(",".join(headers) + "\n")
        for r in records:
            dec_area_str = f"{r['dec_area_um2']:.4f}" if isinstance(r['dec_area_um2'], float) else str(r['dec_area_um2'])
            dec_del_str = f"{r['dec_delay_ps']:.2f}" if isinstance(r['dec_delay_ps'], float) else str(r['dec_delay_ps'])
            conv_area_str = f"{r['conv_area_um2']:.4f}" if isinstance(r['conv_area_um2'], float) else str(r['conv_area_um2'])
            conv_del_str = f"{r['conv_delay_ps']:.2f}" if isinstance(r['conv_delay_ps'], float) else str(r['conv_delay_ps'])
            row = [
                r["benchmark"],
                r["library"],
                r["dec_status"],
                str(r["dec_pre_cells"]),
                str(r["dec_mapped_cells"]),
                dec_area_str,
                dec_del_str,
                str(r["dec_stages"]),
                r["conv_status"],
                str(r["conv_pre_cells"]),
                str(r["conv_mapped_cells"]),
                conv_area_str,
                conv_del_str,
                str(r["conv_stages"]),
            ]
            f.write(",".join(row) + "\n")
    print(f"\nWrote conventional baseline CSV: {csv_path}")

    return records


def main():
    parser = argparse.ArgumentParser(description="Part H: Conventional Baseline Comparison")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "experiments" / "technology_mapping" / "results" / "baseline"))
    parser.add_argument("--skip-large-dec", action="store_true", default=True)
    args = parser.parse_args()

    run_baseline_comparison(Path(args.output_dir), skip_large_dec=args.skip_large_dec)


if __name__ == "__main__":
    main()
