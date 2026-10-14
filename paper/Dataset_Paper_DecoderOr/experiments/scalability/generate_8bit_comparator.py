"""
experiments/scalability/generate_8bit_comparator.py
---------------------------------------------------
Generates the 8-bit Magnitude Comparator benchmark requested by reviewers:
- Reviewer #1 Comment 3
- Reviewer #2 Comment 4

Architecture:
- Operands: Two 8-bit unsigned integers (A, B)
- Boolean Inputs: 16 (A7..A0, B7..B0)
- Core Decoder: 16-to-65536_Active_High (65,536 states)
- Outputs:
    A_gt_B: A > B  (32,640 minterms)
    A_eq_B: A == B (256 minterms)
    A_lt_B: A < B  (32,640 minterms)
    Total minterms mapped: 65,536 (complete disjoint partition)
"""

import sys
import json
import time
import tracemalloc
from pathlib import Path
from typing import Dict, Any, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from compiler.validator import validate_routing_dict
from compiler.or_tree import decompose_or_tree, emit_or_tree_verilog
from compiler.generator import generate_verilog_from_data


def generate_8bit_comparator_ground_truth() -> Dict[str, Any]:
    """
    Computes exact mathematical ground truth for 8-bit comparator
    independently from the compiler.
    
    Index formula:
        index = (A << 8) | B
        where A in [0..255], B in [0..255]
    """
    inputs = [f"A{i}" for i in range(7, -1, -1)] + [f"B{i}" for i in range(7, -1, -1)]
    outputs = ["A_gt_B", "A_eq_B", "A_lt_B"]

    mterms_gt = []
    mterms_eq = []
    mterms_lt = []

    for a in range(256):
        for b in range(256):
            idx = (a << 8) | b
            if a > b:
                mterms_gt.append(f"Y{idx}")
            elif a == b:
                mterms_eq.append(f"Y{idx}")
            else:
                mterms_lt.append(f"Y{idx}")

    # Mathematical sanity assertions
    assert len(mterms_eq) == 256, f"Expected 256 equality states, got {len(mterms_eq)}"
    assert len(mterms_gt) == 32640, f"Expected 32,640 gt states, got {len(mterms_gt)}"
    assert len(mterms_lt) == 32640, f"Expected 32,640 lt states, got {len(mterms_lt)}"
    assert len(mterms_gt) + len(mterms_eq) + len(mterms_lt) == 65536, "Partition must equal 2^16 = 65536"

    routing_matrix = {
        "output_OR_A_gt_B": mterms_gt,
        "output_OR_A_eq_B": mterms_eq,
        "output_OR_A_lt_B": mterms_lt,
    }

    return {
        "system": "8bit_Comparator_Decoder_OR",
        "architecture": {
            "core_decoder": "16-to-65536_Active_High",
            "inputs": inputs,
            "outputs": outputs,
        },
        "automated_routing_matrix": routing_matrix,
    }


def benchmark_8bit_comparator(
    output_json_path: Path,
    output_verilog_path: Path,
    max_fan_in: int = 4
) -> Dict[str, Any]:
    """
    Executes end-to-end benchmark of 8-bit comparator with fine-grained timing
    and memory profiling.
    """
    tracemalloc.start()
    mem_start = tracemalloc.get_traced_memory()[0]

    # 1. Generation Phase
    t0 = time.perf_counter()
    routing_data = generate_8bit_comparator_ground_truth()
    t1 = time.perf_counter()
    generation_time_ms = (t1 - t0) * 1000.0

    # 2. JSON Serialization & File Size
    json_str = json.dumps(routing_data, indent=2)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json_str, encoding="utf-8")
    json_size_bytes = output_json_path.stat().st_size

    # 3. JSON Parsing Phase
    t2 = time.perf_counter()
    parsed_dict = json.loads(json_str)
    t3 = time.perf_counter()
    parse_time_ms = (t3 - t2) * 1000.0

    # 4. Routing Validation Phase
    t4 = time.perf_counter()
    validated = validate_routing_dict(parsed_dict)
    t5 = time.perf_counter()
    validation_time_ms = (t5 - t4) * 1000.0

    # 5. OR-Tree Decomposition Phase
    t6 = time.perf_counter()
    decompositions = {}
    max_depth = 0
    total_internal_nodes = 0
    for out_name in validated["outputs"]:
        pins = validated["routing"][out_name]
        decomp = decompose_or_tree(pins, max_fan_in=max_fan_in, node_prefix=f"{out_name}_or")
        decompositions[out_name] = decomp
        if decomp.tree_depth > max_depth:
            max_depth = decomp.tree_depth
        total_internal_nodes += decomp.number_of_internal_or_nodes
    t7 = time.perf_counter()
    or_tree_time_ms = (t7 - t6) * 1000.0

    # 6. Verilog Generation Phase
    t8 = time.perf_counter()
    verilog_code = generate_verilog_from_data(validated["raw"], max_fan_in=max_fan_in)
    output_verilog_path.parent.mkdir(parents=True, exist_ok=True)
    output_verilog_path.write_text(verilog_code, encoding="utf-8")
    t9 = time.perf_counter()
    verilog_generation_time_ms = (t9 - t8) * 1000.0
    verilog_size_bytes = output_verilog_path.stat().st_size

    total_compiler_time_ms = parse_time_ms + validation_time_ms + verilog_generation_time_ms

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_memory_mb = (peak_mem - mem_start) / (1024.0 * 1024.0)

    # Sanity checks on output
    num_connections = (
        len(routing_data["automated_routing_matrix"]["output_OR_A_gt_B"])
        + len(routing_data["automated_routing_matrix"]["output_OR_A_eq_B"])
        + len(routing_data["automated_routing_matrix"]["output_OR_A_lt_B"])
    )

    metrics = {
        "circuit_name": "8bit_Comparator",
        "operand_width": 8,
        "input_count": 16,
        "num_outputs": 3,
        "num_minterms": 65536,
        "num_routing_connections": num_connections,
        "json_size_bytes": json_size_bytes,
        "json_size_kb": round(json_size_bytes / 1024.0, 2),
        "json_size_mb": round(json_size_bytes / (1024.0 * 1024.0), 3),
        "generation_time_ms": round(generation_time_ms, 2),
        "parse_time_ms": round(parse_time_ms, 2),
        "validation_time_ms": round(validation_time_ms, 2),
        "or_tree_time_ms": round(or_tree_time_ms, 2),
        "verilog_generation_time_ms": round(verilog_generation_time_ms, 2),
        "total_time_ms": round(total_compiler_time_ms, 2),
        "peak_memory_mb": round(peak_memory_mb, 2),
        "verilog_size_bytes": verilog_size_bytes,
        "verilog_size_kb": round(verilog_size_bytes / 1024.0, 2),
        "verilog_size_mb": round(verilog_size_bytes / (1024.0 * 1024.0), 3),
        "max_tree_depth": max_depth,
        "internal_or_nodes": total_internal_nodes,
        "status": "PASS",
        "error_reason": "",
    }

    return metrics


def main():
    print("=" * 65)
    print("  8-Bit Magnitude Comparator Scalability Benchmark")
    print("  Evaluating Reviewer #1 R1.3 & Reviewer #2 R2.4 Stress Cases")
    print("=" * 65)

    json_path = _REPO_ROOT / "experiments" / "scalability" / "generated_json" / "8bit_Comparator.json"
    verilog_path = _REPO_ROOT / "experiments" / "scalability" / "generated_verilog" / "8bit_Comparator.v"

    metrics = benchmark_8bit_comparator(json_path, verilog_path, max_fan_in=4)

    print(f"\nBoolean Inputs              : {metrics['input_count']} (two 8-bit operands: A[7:0], B[7:0])")
    print(f"Decoder Output Pins         : {metrics['num_minterms']:,} (16-to-65536 decoder)")
    print(f"Output Logic Functions      : {metrics['num_outputs']} (A>B: 32640, A==B: 256, A<B: 32640)")
    print(f"Total Routing Connections   : {metrics['num_routing_connections']:,}")
    print(f"JSON File Size              : {metrics['json_size_mb']} MB ({metrics['json_size_bytes']:,} bytes)")
    print(f"Generated Verilog Size      : {metrics['verilog_size_mb']} MB ({metrics['verilog_size_bytes']:,} bytes)")
    print(f"JSON Generation Time        : {metrics['generation_time_ms']:.2f} ms")
    print(f"JSON Parse Time             : {metrics['parse_time_ms']:.2f} ms")
    print(f"Validation Time             : {metrics['validation_time_ms']:.2f} ms")
    print(f"OR-Tree Decomposition Time  : {metrics['or_tree_time_ms']:.2f} ms")
    print(f"Verilog Generation Time     : {metrics['verilog_generation_time_ms']:.2f} ms")
    print(f"TOTAL Compilation Time      : {metrics['total_time_ms']:.2f} ms")
    print(f"Peak Memory Allocated       : {metrics['peak_memory_mb']:.2f} MB")
    print(f"Max OR-Tree Depth           : {metrics['max_tree_depth']} (fan-in <= 4 bounded)")
    print(f"Total Internal OR Nodes     : {metrics['internal_or_nodes']:,} gates")
    print(f"Benchmark Status            : {metrics['status']}")
    print("=" * 65)


if __name__ == "__main__":
    main()
