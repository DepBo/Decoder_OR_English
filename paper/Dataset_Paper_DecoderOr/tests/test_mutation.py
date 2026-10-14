"""
tests/test_mutation.py
----------------------
Unit and regression tests for mutation testing framework.
Verifies that all injected mutations are reliably flagged as FAIL by the oracle.
"""

import csv
import json
import pytest
from pathlib import Path

from verification.mutation_test import (
    run_mutation_campaign,
    generate_benchmark_mutations,
    generate_routing_mutations,
    verify_routing_representation,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_full_mutation_campaign():
    """Runs the complete mutation campaign and checks kill rate is 100%."""
    results, summary = run_mutation_campaign(
        dataset_path=REPO_ROOT / "benchmark_dataset.json",
        output_dir=REPO_ROOT / "verification"
    )

    # Invariants
    assert summary.total_mutations >= 70, f"Expected >= 70 mutations, got {summary.total_mutations}"
    assert summary.killed_mutations == summary.total_mutations
    assert summary.survived_mutations == 0
    assert summary.mutation_kill_rate == 1.0

    # Verify CSV file existence and format
    csv_file = REPO_ROOT / "verification" / "mutation_results.csv"
    assert csv_file.is_file(), "mutation_results.csv must exist"

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        expected_header = [
            "circuit",
            "mutation_id",
            "mutation_type",
            "original_value",
            "mutated_value",
            "expected_result",
            "observed_result",
            "killed",
            "error_message",
        ]
        assert header == expected_header

        rows = list(reader)
        assert len(rows) == summary.total_mutations
        for row in rows:
            killed = (row[7] == "True")
            observed = row[6]
            assert observed == "FAIL", f"Mutant {row[1]} was not observed as FAIL"
            assert killed is True, f"Mutant {row[1]} was not killed"

    # Verify JSON summary file existence and format
    json_file = REPO_ROOT / "verification" / "mutation_summary.json"
    assert json_file.is_file(), "mutation_summary.json must exist"

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["total_mutations"] == summary.total_mutations
        assert data["killed_mutations"] == summary.killed_mutations
        assert data["survived_mutations"] == 0
        assert data["mutation_kill_rate"] == 1.0


def test_mutation_types_coverage():
    """Verifies that all 8 required mutation types M01-M08 are tested."""
    results, summary = run_mutation_campaign(
        dataset_path=REPO_ROOT / "benchmark_dataset.json",
        output_dir=REPO_ROOT / "verification"
    )

    required_m_types = [
        "M01_remove_valid_minterm",
        "M02_add_incorrect_minterm",
        "M03_replace_valid_minterm",
        "M04_remove_entire_output_mapping",
        "M05_inject_wrong_output_mapping",
        "M06_swap_output_mappings",
        "M07_duplicate_minterm",
        "M08_corrupt_multiple_entries",
    ]

    for req_m in required_m_types:
        assert req_m in summary.details_by_type, f"Missing mutation type: {req_m}"
        stats = summary.details_by_type[req_m]
        assert stats["total"] > 0
        assert stats["killed"] == stats["total"]
        assert stats["survived"] == 0


def test_routing_mutation_types_coverage():
    """Verifies that all 8 routing mutation types R01-R08 are tested."""
    results, summary = run_mutation_campaign(
        dataset_path=REPO_ROOT / "benchmark_dataset.json",
        output_dir=REPO_ROOT / "verification"
    )

    required_r_types = [
        "R01_routing_remove_pin",
        "R02_routing_add_incorrect_pin",
        "R03_routing_replace_pin",
        "R04_routing_clear_output",
        "R05_routing_swap_outputs",
        "R06_routing_duplicate_pin",
        "R07_routing_out_of_range_pin",
        "R08_routing_corrupt_multiple",
    ]

    for req_r in required_r_types:
        assert req_r in summary.details_by_type, f"Missing routing mutation type: {req_r}"
        stats = summary.details_by_type[req_r]
        assert stats["total"] > 0
        assert stats["killed"] == stats["total"]
        assert stats["survived"] == 0
