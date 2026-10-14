#!/usr/bin/env python3
"""
Step 3C & 3D Master Orchestration Runner
========================================

Executes the complete physical validation and electrical simulation suite:
  - Step 3C: Physical implementation, fan-out scaling, buffer insertion, and decoder audit
  - Step 3D: Transistor-level SPICE transient simulations and signal integrity analysis

Usage:
  python experiments/physical_validation/run_all.py [OPTIONS]

Options:
  --skip-large     Skip large designs/simulations exceeding WSL2 memory budget
  --skip-spice     Skip SPICE transient simulations
  --skip-route     Skip place & route flow script checks
  --fanout-max N   Maximum fanout value to evaluate (default: 64)
  --benchmark NAME Run audit on specific benchmark
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Master runner for Steps 3C and 3D.")
    parser.add_argument("--skip-large", action="store_true", help="Skip large design runs")
    parser.add_argument("--skip-spice", action="store_true", help="Skip SPICE simulations")
    parser.add_argument("--skip-route", action="store_true", help="Skip physical routing script generation")
    parser.add_argument("--fanout-max", type=int, default=64, help="Maximum fanout value (default: 64)")
    parser.add_argument("--benchmark", type=str, default=None, help="Specific benchmark to audit")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    run_3c_script = base_dir / "run_3c.py"
    run_3d_script = base_dir / "run_3d.py"

    print("=" * 80)
    print("STEP 3C & 3D: PHYSICAL & ELECTRICAL VALIDATION MASTER RUNNER")
    print("Paper: Realizing Arbitrary Logic Functions Using Decoders and OR Gates")
    print("=" * 80)
    print(f"Max Fan-out Target   : {args.fanout_max}")
    print(f"Skip Large Designs   : {args.skip_large}")
    print(f"Skip SPICE           : {args.skip_spice}")
    print(f"Skip Route Scripts   : {args.skip_route}")
    print("-" * 80)

    t_start = time.time()
    results_summary = {}

    # 1. Step 3C: Physical Implementation & Buffering
    print("\n>>> Launching Step 3C: Physical Implementation & Fan-out / Buffering Flow...")
    cmd_3c = [sys.executable, str(run_3c_script), "--fanout-max", str(args.fanout_max)]
    if args.skip_large:
        cmd_3c.append("--skip-large")

    t0 = time.time()
    p_3c = subprocess.run(cmd_3c, capture_output=True, text=True)
    t_3c = time.time() - t0
    print(p_3c.stdout)
    if p_3c.returncode != 0:
        print("[ERROR] Step 3C failed with stderr:")
        print(p_3c.stderr)
        results_summary["step_3c"] = "FAIL"
    else:
        results_summary["step_3c"] = f"PASS ({t_3c:.1f}s)"

    # 2. Step 3D: Transistor-Level SPICE Simulation
    if not args.skip_spice:
        print("\n>>> Launching Step 3D: Transistor-Level SPICE Electrical Validation...")
        cmd_3d = [sys.executable, str(run_3d_script), "--fanout-max", str(args.fanout_max)]
        t0 = time.time()
        p_3d = subprocess.run(cmd_3d, capture_output=True, text=True)
        t_3d = time.time() - t0
        print(p_3d.stdout)
        if p_3d.returncode != 0:
            print("[ERROR] Step 3D failed with stderr:")
            print(p_3d.stderr)
            results_summary["step_3d"] = "FAIL"
        else:
            results_summary["step_3d"] = f"PASS ({t_3d:.1f}s)"
    else:
        print("\n>>> Step 3D SPICE skipped per user flag (--skip-spice).")
        results_summary["step_3d"] = "SKIPPED"

    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print("MASTER EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Step 3C (Physical / Buffering) : {results_summary.get('step_3c', 'UNKNOWN')}")
    print(f"Step 3D (Transistor SPICE)     : {results_summary.get('step_3d', 'UNKNOWN')}")
    print(f"Total Execution Time           : {total_time:.2f} seconds")
    print("=" * 80)


if __name__ == "__main__":
    main()
