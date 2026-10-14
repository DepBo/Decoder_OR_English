"""
experiments/scalability/run_scalability.py
-----------------------------------------
Automated Scalability Experiment for Decoder-OR Logic Synthesis.
Evaluates algorithmic and computational scaling from n = 2 up to n = 16+ inputs.

Addresses:
- Reviewer #1 Comment 3 (Combinatorial scaling of JSON representation and compiler)
- Reviewer #2 Comment 4 (Performance scaling, compilation time, JSON file size, peak RAM)

Measures:
1. Boolean input count (n)
2. Decoder states (2^n)
3. Number of outputs
4. Total routing connections
5. JSON file size (bytes / KB / MB)
6. JSON generation time (ms)
7. JSON parse time (ms)
8. Routing validation time (ms)
9. OR-tree decomposition time (ms)
10. Verilog RTL generation time (ms)
11. Total compiler execution time (ms)
12. Peak memory allocated (MB via tracemalloc)
13. Verilog file size (bytes / KB / MB)
14. Max OR-tree depth
15. Internal OR gates synthesized
16. Execution status (PASS / TIMEOUT / MEMORY_LIMIT / ERROR)
"""

import sys
import os
import json
import time
import csv
import tracemalloc
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from compiler.validator import validate_routing_dict, ValidationError
from compiler.or_tree import decompose_or_tree
from compiler.generator import generate_verilog_from_data
from experiments.scalability.generate_8bit_comparator import generate_8bit_comparator_ground_truth

# Experiment Safety Limits
MAX_RUNTIME_SECONDS = 60.0    # 60s per individual repetition
MAX_MEMORY_MB = 1500.0         # 1.5 GB limit to safeguard 7.2 GB system RAM
NUM_REPETITIONS = 3            # 3 repetitions for stable statistics


def generate_generic_scaling_circuit(n: int) -> Dict[str, Any]:
    """
    Generates a deterministic 3-output Boolean benchmark for n inputs (2^n states):
    - f_parity: odd parity of input bits (50% minterms)
    - f_threshold: integer value >= 2^(n-1) (50% minterms)
    - f_mod3: integer value % 3 == 0 (~33% minterms)
    """
    inputs = [f"X{i}" for i in range(n - 1, -1, -1)]
    outputs = ["f_parity", "f_threshold", "f_mod3"]
    total_states = 1 << n
    half = 1 << (n - 1)

    parity_pins = []
    thresh_pins = []
    mod3_pins = []

    for idx in range(total_states):
        pin_name = f"Y{idx}"
        # Bit count / parity
        popcount = bin(idx).count("1")
        if popcount % 2 == 1:
            parity_pins.append(pin_name)
        if idx >= half:
            thresh_pins.append(pin_name)
        if idx % 3 == 0:
            mod3_pins.append(pin_name)

    return {
        "system": f"Generic_Scale_N{n}_Decoder_OR",
        "architecture": {
            "core_decoder": f"{n}-to-{total_states}_Active_High",
            "inputs": inputs,
            "outputs": outputs,
        },
        "automated_routing_matrix": {
            "output_OR_f_parity": parity_pins,
            "output_OR_f_threshold": thresh_pins,
            "output_OR_f_mod3": mod3_pins,
        },
    }


def execute_single_measurement(
    routing_data: Dict[str, Any],
    circuit_name: str,
    n_inputs: int,
    operand_width: int,
    output_dir_json: Path,
    output_dir_v: Path,
    max_fan_in: int = 4
) -> Dict[str, Any]:
    """
    Executes a single timed and memory-profiled compilation run.
    """
    json_path = output_dir_json / f"{circuit_name}.json"
    verilog_path = output_dir_v / f"{circuit_name}.v"

    # Pre-flight resource check
    total_states = 1 << n_inputs
    if total_states > (1 << 20):  # Over 1M states
        return {
            "circuit_name": circuit_name,
            "operand_width": operand_width,
            "input_count": n_inputs,
            "status": "MEMORY_LIMIT",
            "error_reason": f"Theoretical states 2^{n_inputs} = {total_states:,} exceeds safe scalability bound (1M states).",
        }

    tracemalloc.start()
    mem_start = tracemalloc.get_traced_memory()[0]
    t_start = time.perf_counter()

    try:
        # 1. JSON Serialization & File Size
        json_str = json.dumps(routing_data, indent=2)
        json_path.write_text(json_str, encoding="utf-8")
        json_size_bytes = json_path.stat().st_size

        if time.perf_counter() - t_start > MAX_RUNTIME_SECONDS:
            raise TimeoutError("Exceeded MAX_RUNTIME_SECONDS during JSON serialization.")

        # 2. JSON Parse Phase
        t_p0 = time.perf_counter()
        parsed_dict = json.loads(json_str)
        t_p1 = time.perf_counter()
        parse_time_ms = (t_p1 - t_p0) * 1000.0

        # 3. Validation Phase
        t_v0 = time.perf_counter()
        validated = validate_routing_dict(parsed_dict)
        t_v1 = time.perf_counter()
        validation_time_ms = (t_v1 - t_v0) * 1000.0

        if time.perf_counter() - t_start > MAX_RUNTIME_SECONDS:
            raise TimeoutError("Exceeded MAX_RUNTIME_SECONDS during validation.")

        # 4. OR-Tree Decomposition Phase
        t_d0 = time.perf_counter()
        max_depth = 0
        total_internal_nodes = 0
        for out_name in validated["outputs"]:
            pins = validated["routing"][out_name]
            decomp = decompose_or_tree(pins, max_fan_in=max_fan_in, node_prefix=f"{out_name}_or")
            if decomp.tree_depth > max_depth:
                max_depth = decomp.tree_depth
            total_internal_nodes += decomp.number_of_internal_or_nodes
        t_d1 = time.perf_counter()
        or_tree_time_ms = (t_d1 - t_d0) * 1000.0

        if time.perf_counter() - t_start > MAX_RUNTIME_SECONDS:
            raise TimeoutError("Exceeded MAX_RUNTIME_SECONDS during OR-tree decomposition.")

        # 5. Verilog Generation Phase
        t_vg0 = time.perf_counter()
        verilog_code = generate_verilog_from_data(validated["raw"], max_fan_in=max_fan_in, verify_equivalence=False)
        verilog_path.write_text(verilog_code, encoding="utf-8")
        t_vg1 = time.perf_counter()
        verilog_generation_time_ms = (t_vg1 - t_vg0) * 1000.0
        verilog_size_bytes = verilog_path.stat().st_size

        total_compiler_time_ms = parse_time_ms + validation_time_ms + verilog_generation_time_ms

        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_memory_mb = (peak_mem - mem_start) / (1024.0 * 1024.0)

        if peak_memory_mb > MAX_MEMORY_MB:
            return {
                "circuit_name": circuit_name,
                "operand_width": operand_width,
                "input_count": n_inputs,
                "status": "MEMORY_LIMIT",
                "error_reason": f"Peak memory {peak_memory_mb:.1f} MB exceeded safety threshold of {MAX_MEMORY_MB} MB.",
            }

        num_connections = sum(len(pins) for pins in routing_data["automated_routing_matrix"].values())

        return {
            "circuit_name": circuit_name,
            "operand_width": operand_width,
            "input_count": n_inputs,
            "num_outputs": len(validated["outputs"]),
            "num_minterms": total_states,
            "num_routing_connections": num_connections,
            "json_size_bytes": json_size_bytes,
            "parse_time_ms": parse_time_ms,
            "validation_time_ms": validation_time_ms,
            "or_tree_time_ms": or_tree_time_ms,
            "verilog_generation_time_ms": verilog_generation_time_ms,
            "total_time_ms": total_compiler_time_ms,
            "peak_memory_mb": peak_memory_mb,
            "verilog_size_bytes": verilog_size_bytes,
            "max_tree_depth": max_depth,
            "internal_or_nodes": total_internal_nodes,
            "status": "PASS",
            "error_reason": "",
        }

    except TimeoutError as te:
        tracemalloc.stop()
        return {
            "circuit_name": circuit_name,
            "operand_width": operand_width,
            "input_count": n_inputs,
            "status": "TIMEOUT",
            "error_reason": str(te),
        }
    except Exception as e:
        tracemalloc.stop()
        return {
            "circuit_name": circuit_name,
            "operand_width": operand_width,
            "input_count": n_inputs,
            "status": "ERROR",
            "error_reason": str(e),
        }


def run_scalability_suite() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Runs the full scalability experiment suite:
    - Generic scaling: n = 2 .. 16 (and safe exploratory n = 17, 18)
    - 8-bit Comparator: n = 16 (two 8-bit operands, 65,536 states)
    """
    exp_dir = _REPO_ROOT / "experiments" / "scalability"
    json_dir = exp_dir / "generated_json"
    verilog_dir = exp_dir / "generated_verilog"
    raw_dir = exp_dir / "raw_runs"
    json_dir.mkdir(parents=True, exist_ok=True)
    verilog_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    test_cases: List[Tuple[str, int, int, Any]] = []

    # 1. Generic Scaling Test Cases: n = 2..16
    for n in range(2, 17):
        test_cases.append((f"Generic_N{n}", n, n, lambda n=n: generate_generic_scaling_circuit(n)))

    # 2. Explicit 8-Bit Comparator (n = 16, 2x8-bit operands)
    test_cases.append(("8bit_Comparator", 16, 8, generate_8bit_comparator_ground_truth))

    # 3. Exploratory cases beyond 16: n = 17, 18, 19, 20, 21 (boundary)
    for n in (17, 18, 19, 20, 21):
        test_cases.append((f"Generic_N{n}", n, n, lambda n=n: generate_generic_scaling_circuit(n)))

    final_results: List[Dict[str, Any]] = []
    summary_data: Dict[str, Any] = {
        "benchmark_environment": {
            "python_version": sys.version.split()[0],
            "os": sys.platform,
            "max_runtime_limit_sec": MAX_RUNTIME_SECONDS,
            "max_memory_limit_mb": MAX_MEMORY_MB,
            "repetitions": NUM_REPETITIONS,
        },
        "circuits": {},
    }

    print("\n" + "=" * 80)
    print(f"{'Circuit':<18} | {'In':<3} | {'States':<8} | {'JSON (KB)':<10} | {'RAM (MB)':<9} | {'Time (ms)':<10} | {'Status'}")
    print("-" * 80)

    for c_name, n_in, op_w, gen_fn in test_cases:
        total_states = 1 << n_in
        if total_states > (1 << 20):  # Over 1M states boundary
            summary_row = {
                "circuit_name": c_name,
                "operand_width": op_w,
                "input_count": n_in,
                "num_outputs": 3,
                "num_minterms": total_states,
                "num_routing_connections": 0,
                "json_size_bytes": 0,
                "json_size_kb": 0.0,
                "generation_time_ms": 0.0,
                "parse_time_ms": 0.0,
                "validation_time_ms": 0.0,
                "or_tree_time_ms": 0.0,
                "verilog_generation_time_ms": 0.0,
                "total_time_ms": 0.0,
                "total_time_min_ms": 0.0,
                "total_time_max_ms": 0.0,
                "peak_memory_mb": 0.0,
                "verilog_size_bytes": 0,
                "verilog_size_kb": 0.0,
                "max_tree_depth": 0,
                "internal_or_nodes": 0,
                "status": "MEMORY_LIMIT",
                "error_reason": f"Theoretical states 2^{n_in} = {total_states:,} exceeds safe scalability bound (1,048,576 states).",
            }
            final_results.append(summary_row)
            summary_data["circuits"][c_name] = summary_row
            print(
                f"{c_name:<18} | {n_in:<3} | {total_states:<8} | "
                f"{'N/A':<10} | {'N/A':<9} | {'N/A':<10} | MEMORY_LIMIT"
            )
            print(f"  [STOP] Halting further generic scaling at N={n_in} due to MEMORY_LIMIT: {summary_row['error_reason']}")
            break

        # Generate circuit routing
        t_g0 = time.perf_counter()
        routing_obj = gen_fn()
        t_g1 = time.perf_counter()
        gen_time_ms = (t_g1 - t_g0) * 1000.0

        # Execute repetitions
        rep_runs = []
        aborted = False

        for rep in range(NUM_REPETITIONS):
            run_res = execute_single_measurement(
                routing_data=routing_obj,
                circuit_name=c_name,
                n_inputs=n_in,
                operand_width=op_w,
                output_dir_json=json_dir,
                output_dir_v=verilog_dir,
                max_fan_in=4
            )
            run_res["generation_time_ms"] = gen_time_ms
            run_res["repetition"] = rep + 1

            # Save raw run
            raw_path = raw_dir / f"{c_name}_rep{rep + 1}.json"
            raw_path.write_text(json.dumps(run_res, indent=2), encoding="utf-8")
            rep_runs.append(run_res)

            if run_res["status"] != "PASS":
                aborted = True
                break

        # Compute aggregate metrics
        if not aborted:
            mean_total = sum(r["total_time_ms"] for r in rep_runs) / len(rep_runs)
            min_total = min(r["total_time_ms"] for r in rep_runs)
            max_total = max(r["total_time_ms"] for r in rep_runs)
            mean_parse = sum(r["parse_time_ms"] for r in rep_runs) / len(rep_runs)
            mean_val = sum(r["validation_time_ms"] for r in rep_runs) / len(rep_runs)
            mean_or = sum(r["or_tree_time_ms"] for r in rep_runs) / len(rep_runs)
            mean_vgen = sum(r["verilog_generation_time_ms"] for r in rep_runs) / len(rep_runs)
            mean_mem = sum(r["peak_memory_mb"] for r in rep_runs) / len(rep_runs)

            base = rep_runs[0]
            summary_row = {
                "circuit_name": c_name,
                "operand_width": op_w,
                "input_count": n_in,
                "num_outputs": base["num_outputs"],
                "num_minterms": base["num_minterms"],
                "num_routing_connections": base["num_routing_connections"],
                "json_size_bytes": base["json_size_bytes"],
                "json_size_kb": round(base["json_size_bytes"] / 1024.0, 2),
                "generation_time_ms": round(gen_time_ms, 2),
                "parse_time_ms": round(mean_parse, 2),
                "validation_time_ms": round(mean_val, 2),
                "or_tree_time_ms": round(mean_or, 2),
                "verilog_generation_time_ms": round(mean_vgen, 2),
                "total_time_ms": round(mean_total, 2),
                "total_time_min_ms": round(min_total, 2),
                "total_time_max_ms": round(max_total, 2),
                "peak_memory_mb": round(mean_mem, 2),
                "verilog_size_bytes": base["verilog_size_bytes"],
                "verilog_size_kb": round(base["verilog_size_bytes"] / 1024.0, 2),
                "max_tree_depth": base["max_tree_depth"],
                "internal_or_nodes": base["internal_or_nodes"],
                "status": "PASS",
                "error_reason": "",
            }
        else:
            base = rep_runs[-1]
            summary_row = {
                "circuit_name": c_name,
                "operand_width": op_w,
                "input_count": n_in,
                "num_outputs": len(routing_obj["architecture"]["outputs"]),
                "num_minterms": 1 << n_in,
                "num_routing_connections": sum(len(pins) for pins in routing_obj["automated_routing_matrix"].values()),
                "json_size_bytes": 0,
                "json_size_kb": 0.0,
                "generation_time_ms": round(gen_time_ms, 2),
                "parse_time_ms": 0.0,
                "validation_time_ms": 0.0,
                "or_tree_time_ms": 0.0,
                "verilog_generation_time_ms": 0.0,
                "total_time_ms": 0.0,
                "total_time_min_ms": 0.0,
                "total_time_max_ms": 0.0,
                "peak_memory_mb": 0.0,
                "verilog_size_bytes": 0,
                "verilog_size_kb": 0.0,
                "max_tree_depth": 0,
                "internal_or_nodes": 0,
                "status": base["status"],
                "error_reason": base["error_reason"],
            }

        final_results.append(summary_row)
        summary_data["circuits"][c_name] = summary_row

        print(
            f"{c_name:<18} | {n_in:<3} | {1 << n_in:<8} | "
            f"{summary_row['json_size_kb']:<10.1f} | "
            f"{summary_row['peak_memory_mb']:<9.2f} | "
            f"{summary_row['total_time_ms']:<10.2f} | "
            f"{summary_row['status']}"
        )

        # If a generic case times out or hits memory limit, stop further generic escalations
        if aborted and c_name.startswith("Generic_N"):
            print(f"  [STOP] Halting further generic scaling at N={n_in} due to {base['status']}: {base['error_reason']}")
            break

    print("=" * 80)

    # Save summary JSON
    summary_path = exp_dir / "scalability_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # Save CSV
    csv_path = exp_dir / "scalability_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "input_count",
            "operand_width",
            "circuit_name",
            "num_outputs",
            "num_minterms",
            "num_routing_connections",
            "json_size_bytes",
            "generation_time_ms",
            "parse_time_ms",
            "validation_time_ms",
            "or_tree_time_ms",
            "verilog_generation_time_ms",
            "total_time_ms",
            "peak_memory_mb",
            "verilog_size_bytes",
            "max_tree_depth",
            "internal_or_nodes",
            "status",
            "error_reason",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in final_results:
            csv_row = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(csv_row)

    print(f"\n[OK] Scalability results saved to:")
    print(f"     - {csv_path.relative_to(_REPO_ROOT)}")
    print(f"     - {summary_path.relative_to(_REPO_ROOT)}")

    return final_results, summary_data


if __name__ == "__main__":
    run_scalability_suite()
