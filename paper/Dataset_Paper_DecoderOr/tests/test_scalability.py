"""
tests/test_scalability.py
-------------------------
Regression and validation tests for Step 2 Scalability Experiments.
"""

import csv
import json
import pytest
from pathlib import Path

from experiments.scalability.generate_8bit_comparator import (
    generate_8bit_comparator_ground_truth,
    benchmark_8bit_comparator,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_8bit_comparator_ground_truth_partition():
    """Verify that 8-bit comparator minterms form a complete, disjoint partition of 2^16."""
    routing = generate_8bit_comparator_ground_truth()
    matrix = routing["automated_routing_matrix"]

    gt_pins = matrix["output_OR_A_gt_B"]
    eq_pins = matrix["output_OR_A_eq_B"]
    lt_pins = matrix["output_OR_A_lt_B"]

    # Exact counts
    assert len(eq_pins) == 256
    assert len(gt_pins) == 32640
    assert len(lt_pins) == 32640

    # Total check
    assert len(gt_pins) + len(eq_pins) + len(lt_pins) == 65536

    # Disjointness check
    set_gt = set(gt_pins)
    set_eq = set(eq_pins)
    set_lt = set(lt_pins)
    assert len(set_gt.intersection(set_eq)) == 0
    assert len(set_gt.intersection(set_lt)) == 0
    assert len(set_eq.intersection(set_lt)) == 0


def test_scalability_results_file_exists():
    """Verify that scalability_results.csv exists and has all required columns and rows."""
    csv_path = REPO_ROOT / "experiments" / "scalability" / "scalability_results.csv"
    assert csv_path.is_file(), "scalability_results.csv must exist"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 16, f"Expected at least 16 test cases, got {len(reader)}"

    # Check 8bit_Comparator row
    comp_row = next((r for r in reader if r["circuit_name"] == "8bit_Comparator"), None)
    assert comp_row is not None, "8bit_Comparator must be explicitly present in CSV"
    assert comp_row["input_count"] == "16"
    assert comp_row["num_minterms"] == "65536"
    assert comp_row["status"] == "PASS"
    assert float(comp_row["total_time_ms"]) > 0

    # Check N=2..16 are all PASS
    for n in range(2, 17):
        n_row = next((r for r in reader if r["circuit_name"] == f"Generic_N{n}"), None)
        assert n_row is not None, f"Generic_N{n} must be present in CSV"
        assert n_row["status"] == "PASS"

    # Check N=21 boundary row
    bound_row = next((r for r in reader if r["circuit_name"] == "Generic_N21"), None)
    assert bound_row is not None, "Generic_N21 boundary row must be present in CSV"
    assert bound_row["status"] == "MEMORY_LIMIT"


def test_scalability_summary_json():
    """Verify that scalability_summary.json exists and has valid structure."""
    json_path = REPO_ROOT / "experiments" / "scalability" / "scalability_summary.json"
    assert json_path.is_file(), "scalability_summary.json must exist"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "circuits" in data
    assert "8bit_Comparator" in data["circuits"]
    assert data["circuits"]["8bit_Comparator"]["status"] == "PASS"


def test_8bit_comparator_exact_or_gate_counts():
    """Regression test ensuring exact decomposition OR-gate counts for 8-bit comparator."""
    from compiler.or_tree import decompose_or_tree
    routing = generate_8bit_comparator_ground_truth()
    matrix = routing["automated_routing_matrix"]

    d_gt = decompose_or_tree(matrix["output_OR_A_gt_B"], max_fan_in=4, node_prefix="A_gt_B_or")
    d_eq = decompose_or_tree(matrix["output_OR_A_eq_B"], max_fan_in=4, node_prefix="A_eq_B_or")
    d_lt = decompose_or_tree(matrix["output_OR_A_lt_B"], max_fan_in=4, node_prefix="A_lt_B_or")

    # Precise gate counts
    assert d_gt.number_of_internal_or_nodes == 10923
    assert d_eq.number_of_internal_or_nodes == 85
    assert d_lt.number_of_internal_or_nodes == 10923
    total_internal_nodes = d_gt.number_of_internal_or_nodes + d_eq.number_of_internal_or_nodes + d_lt.number_of_internal_or_nodes
    assert total_internal_nodes == 21931

    # Cross check against generated Verilog
    v_path = REPO_ROOT / "experiments" / "scalability" / "generated_verilog" / "8bit_Comparator.v"
    if v_path.is_file():
        v_lines = v_path.read_text(encoding="utf-8").splitlines()
        or_assigns = [l for l in v_lines if l.strip().startswith("assign ") and " | " in l]
        assert len(or_assigns) == 21931

