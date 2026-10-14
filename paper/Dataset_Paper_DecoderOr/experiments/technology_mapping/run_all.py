"""
experiments/technology_mapping/run_all.py
-----------------------------------------
Master Orchestrator for Step 3B Hardware/EDA Research Validation.
Executes the full technology mapping, timing analysis, and decomposition scaling suite:
1. Technology Mapping (run_mapping.py) -> technology_mapping_results.csv, summary.json
2. Static Timing Analysis (run_sta.py) -> sta_results.csv
3. OR Fan-In Experiment (run_fan_in.py) -> fan_in_results.csv
4. OR-Tree Depth Scaling & Audit (run_or_depth.py) -> or_depth_scaling_results.csv, comparator_audit.json
5. BCD Don't-Care Experiment (run_bcd_dc.py) -> bcd_dont_care_results.csv
6. Conventional RTL Baseline Comparison (run_baseline.py) -> conventional_baseline_results.csv

Usage:
    python experiments/technology_mapping/run_all.py [--skip-large] [--library both|sky130|nangate45]
"""

import sys
import time
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from experiments.technology_mapping.run_mapping import run_all_mapping, save_mapping_reports, SKY130_LIB, NANGATE45_LIB
from experiments.technology_mapping.run_sta import run_all_sta
from experiments.technology_mapping.run_fan_in import run_fan_in_experiment
from experiments.technology_mapping.run_or_depth import run_depth_comparison, audit_8bit_comparator
from experiments.technology_mapping.run_bcd_dc import run_bcd_experiment
from experiments.technology_mapping.run_baseline import run_baseline_comparison


def main():
    parser = argparse.ArgumentParser(description="Step 3B EDA Validation Master Runner")
    parser.add_argument("--library", choices=["both", "sky130", "nangate45"], default="both", help="Standard cell library selection")
    parser.add_argument("--skip-large", action="store_true", default=True, help="Skip large 8-bit comparator mapping to protect memory")
    parser.add_argument("--include-large", action="store_true", help="Include large 8-bit comparator mapping")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "experiments" / "technology_mapping" / "results"), help="Results output directory")
    args = parser.parse_args()

    skip_large = not args.include_large if args.include_large else args.skip_large
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print("STEP 3B RESEARCH VALIDATION: TECHNOLOGY MAPPING, TIMING & DECOMPOSITION EVIDENCE")
    print(f"Target Directory : {out_dir}")
    print(f"Library Selection: {args.library}")
    print(f"Skip Large       : {skip_large}")
    print("================================================================================")

    total_start = time.time()

    # Determine libraries to run
    libs = []
    if args.library in ["sky130", "both"]:
        libs.append(SKY130_LIB)
    if args.library in ["nangate45", "both"]:
        libs.append(NANGATE45_LIB)

    # 1. Technology Mapping (Part B & C)
    print("\n>>> PHASE 1: BENCHMARK TECHNOLOGY MAPPING (Yosys + ABC)")
    all_mapping_res = []
    for lib in libs:
        m_res = run_all_mapping(lib_path=lib, output_dir=out_dir, skip_large=skip_large)
        all_mapping_res.extend(m_res)
    save_mapping_reports(all_mapping_res, out_dir)

    # 2. Static Timing Analysis (Part D)
    print("\n>>> PHASE 2: STATIC TIMING ANALYSIS (ABC stime -p)")
    sta_res = run_all_sta(results_dir=out_dir, output_csv=out_dir / "sta_results.csv")

    # 3. OR Fan-In Scaling Experiment (Part E)
    print("\n>>> PHASE 3: OR FAN-IN SCALING EXPERIMENT (k in [2, 4, 8, 16, 32, 64])")
    fanin_res = run_fan_in_experiment(output_dir=out_dir / "fan_in", num_inputs=64, fan_in_list=[2, 4, 8, 16, 32, 64], libraries=libs)

    # 4. OR-Tree Depth Scaling & Comparator Audit (Part F)
    print("\n>>> PHASE 4: OR-TREE DEPTH SCALING & 8-BIT COMPARATOR AUDIT")
    audit = audit_8bit_comparator()
    audit_file = out_dir / "comparator_audit.json"
    audit_file.write_text(__import__("json").dumps(audit, indent=2), encoding="utf-8")
    print(f"  Comparator Audit Match: {audit['reference_match']} (Total OR nodes: {audit['total_internal_or_nodes']})")
    depth_res = run_depth_comparison(output_dir=out_dir / "or_depth", input_sizes=[64, 256], libraries=libs)
    # Save CSV
    csv_depth = out_dir / "or_depth_scaling_results.csv"
    with open(csv_depth, "w", encoding="utf-8") as f:
        headers = ["num_inputs", "topology", "library", "logical_depth", "logical_gates", "pre_cells", "mapped_cells", "mapped_area_um2", "delay_ps", "critical_path_stages", "critical_path_cells"]
        f.write(",".join(headers) + "\n")
        for r in depth_res:
            row = [str(r["num_inputs"]), r["topology"], r["library"], str(r["logical_depth"]), str(r["logical_gates"]), str(r["pre_cells"]), str(r["mapped_cells"]), f"{r['mapped_area_um2']:.4f}", f"{r['delay_ps']:.2f}" if r["delay_ps"] is not None else "", str(r["critical_path_stages"]), f'"{r["critical_path_cells"]}"']
            f.write(",".join(row) + "\n")

    # 5. BCD Don't-Care Experiment (Part G)
    print("\n>>> PHASE 5: BCD TO 7-SEGMENT DON'T-CARE EXPERIMENT")
    bcd_res = run_bcd_experiment(output_dir=out_dir / "bcd_dc")

    # 6. Conventional Baseline Comparison (Part H)
    print("\n>>> PHASE 6: CONVENTIONAL RTL BASELINE COMPARISON")
    baseline_res = run_baseline_comparison(output_dir=out_dir / "baseline", skip_large_dec=skip_large)

    total_time = time.time() - total_start
    print("\n================================================================================")
    print(f"STEP 3B RESEARCH VALIDATION COMPLETED IN {total_time:.2f}s")
    print("Generated Reports:")
    print(f"  1. {out_dir / 'technology_mapping_results.csv'}")
    print(f"  2. {out_dir / 'technology_mapping_summary.json'}")
    print(f"  3. {out_dir / 'sta_results.csv'}")
    print(f"  4. {out_dir / 'fan_in_results.csv'}")
    print(f"  5. {out_dir / 'or_depth_scaling_results.csv'}")
    print(f"  6. {out_dir / 'comparator_audit.json'}")
    print(f"  7. {out_dir / 'bcd_dont_care_results.csv'}")
    print(f"  8. {out_dir / 'conventional_baseline_results.csv'}")
    print("================================================================================")


if __name__ == "__main__":
    main()
