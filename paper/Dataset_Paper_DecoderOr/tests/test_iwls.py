"""
tests/test_iwls.py
------------------
Regression and validation tests for Step 2 IWLS Benchmark Generalization.
"""

import csv
import json
import pytest
from pathlib import Path

from experiments.iwls.pla_parser import (
    parse_pla_file,
    pla_to_routing_dict,
    verify_functional_equivalence,
    evaluate_pla,
)
from compiler.validator import validate_routing_dict

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_parse_rd53():
    pla_path = REPO_ROOT / "experiments" / "iwls" / "benchmarks" / "rd53.pla"
    pla = parse_pla_file(pla_path)
    assert pla.name == "rd53"
    assert pla.num_inputs == 5
    assert pla.num_outputs == 3
    assert pla.num_product_terms == 32


def test_rd53_functional_equivalence():
    pla_path = REPO_ROOT / "experiments" / "iwls" / "benchmarks" / "rd53.pla"
    pla = parse_pla_file(pla_path)
    routing = pla_to_routing_dict(pla)

    # Validate routing dictionary
    validated = validate_routing_dict(routing)
    assert validated["num_inputs"] == 5
    assert validated["num_decoder_outputs"] == 32

    # Verify equivalence against PLA
    ok, msg = verify_functional_equivalence(pla, routing)
    assert ok is True
    assert "Exhaustive" in msg


def test_squar5_multi_output():
    pla_path = REPO_ROOT / "experiments" / "iwls" / "benchmarks" / "squar5.pla"
    pla = parse_pla_file(pla_path)
    assert pla.num_inputs == 5
    assert pla.num_outputs == 8  # 8 outputs (squaring)

    routing = pla_to_routing_dict(pla)
    validated = validate_routing_dict(routing)
    assert len(validated["outputs"]) == 8

    ok, msg = verify_functional_equivalence(pla, routing)
    assert ok is True


def test_table5_execution_and_verification():
    """Regression test ensuring table5 (N=17, 15 outputs) is feasible and passes functional verification."""
    pla_path = REPO_ROOT / "experiments" / "iwls" / "benchmarks" / "table5.pla"
    pla = parse_pla_file(pla_path)
    assert pla.num_inputs == 17
    assert pla.num_outputs == 15
    assert pla.num_product_terms == 158

    routing = pla_to_routing_dict(pla, max_inputs_feasible=20)
    validated = validate_routing_dict(routing)
    assert validated["num_inputs"] == 17
    assert validated["num_decoder_outputs"] == 131072
    assert len(validated["outputs"]) == 15

    # Check that sample-based or exhaustive verification succeeds
    ok, msg = verify_functional_equivalence(pla, routing, max_exhaustive_bits=17)
    assert ok is True
    assert "Exhaustive" in msg or "Sample" in msg


def test_product_terms_vs_minterms_distinction():
    """Verify that original PLA product terms are distinguished from expanded active minterm routing entries."""
    csv_path = REPO_ROOT / "experiments" / "iwls" / "iwls_results.csv"
    assert csv_path.is_file(), "iwls_results.csv must exist"

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Check required distinct column names
    assert "original_pla_product_terms" in rows[0]
    assert "expanded_active_minterm_entries" in rows[0]
    assert "routing_connections" in rows[0]

    # Verify that for 5xp1, PLA product terms (75) != expanded active entries (576)
    row_5xp1 = next(r for r in rows if r["benchmark"] == "5xp1")
    assert int(row_5xp1["original_pla_product_terms"]) == 75
    assert int(row_5xp1["expanded_active_minterm_entries"]) == 576

    # Verify that table5 is present and PASS
    row_table5 = next(r for r in rows if r["benchmark"] == "table5")
    assert int(row_table5["original_pla_product_terms"]) == 158
    assert int(row_table5["expanded_active_minterm_entries"]) == 119523
    assert row_table5["status"] == "PASS"

    # Verify that large boundary circuits (cordic, duke2, e64) are INFEASIBLE
    for b_name in ["cordic", "duke2", "e64"]:
        row = next(r for r in rows if r["benchmark"] == b_name)
        assert row["status"] == "INFEASIBLE_FOR_COMPLETE_MINTERM_REPRESENTATION"
        assert int(row["theoretical_states"]) > 1048576

