"""
verification/mutation_test.py
------------------------------
Mutation testing framework for validating the correctness and fault sensitivity
of the Decoder-OR mathematical verification oracle and JSON routing matrices.

Addresses Reviewer Comment:
"How did you validate the correctness of the verification oracle itself?
Did you perform mutation testing or inject intentional errors into the JSON routing
matrices to verify that the oracle reliably flags these mismatches as [FAIL]?"

Workflow:
1. Load valid benchmark dataset (and generate reference Decoder-OR routing matrices).
2. Create deep copies to ensure zero corruption of original benchmarks.
3. Systematically inject semantic mutations (M01 to M08) into both benchmark minterms
   and Decoder-OR routing matrices.
4. Execute the independent mathematical verification oracle against each mutated specimen.
5. Record detection status: killed if oracle detects the fault and reports FAIL.
6. Generate verification/mutation_results.csv and verification/mutation_summary.json.
"""

import sys
import json
import copy
import csv
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to sys.path to ensure imports work from any CWD
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from verify_dataset import (
    ORACLES,
    index_to_input_vals,
    check_circuit_errors,
)
from compiler.validator import (
    validate_routing_dict,
    ValidationError,
)
from compiler.generator import benchmark_to_routing_dict


@dataclass
class MutationResult:
    circuit: str
    mutation_id: str
    mutation_type: str
    original_value: str
    mutated_value: str
    expected_result: str    # "FAIL"
    observed_result: str    # "FAIL" or "PASS"
    killed: bool            # True if observed_result == "FAIL"
    error_message: str


@dataclass
class MutationSummary:
    total_mutations: int
    killed_mutations: int
    survived_mutations: int
    mutation_kill_rate: float
    details_by_type: Dict[str, Dict[str, int]]
    details_by_circuit: Dict[str, Dict[str, int]]


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Verify a Decoder-OR routing matrix against the independent Oracle
# ─────────────────────────────────────────────────────────────────────────────

def verify_routing_representation(
    routing_data: Dict[str, Any],
    circuit_name: str,
    dont_cares_map: Optional[Dict[str, List[int]]] = None
) -> List[str]:
    """
    Independently verifies a Decoder-OR routing JSON against the mathematical oracle.
    Maps Y-pins back to minterm indices and computes exact output matching.
    """
    errors: List[str] = []

    # First, validate syntax, pin bounds, and schema
    try:
        validated = validate_routing_dict(routing_data)
    except ValidationError as val_err:
        errors.append(f"Routing schema validation rejected mutated JSON: {val_err}")
        return errors

    oracle = ORACLES.get(circuit_name)
    if oracle is None:
        return [f"No oracle defined for {circuit_name}"]

    inputs = validated["inputs"]
    n_in = validated["num_inputs"]
    total_states = 1 << n_in
    routing = validated["routing"]
    dontcare = dont_cares_map or {}

    # Extract minterm sets from Y-pins
    minterm_map: Dict[str, Set[int]] = {}
    for out_name, pins in routing.items():
        m_set = set()
        for p in pins:
            # pin format guaranteed to be Y<idx> by validator
            idx = int(p[1:])
            m_set.add(idx)
        minterm_map[out_name] = m_set

    # Verify against independent oracle
    for idx in range(total_states):
        vals = index_to_input_vals(idx, inputs)
        result = oracle(vals)
        if result is None:
            continue  # don't-care row

        for out_name, expected_val in result.items():
            in_mterms = idx in minterm_map.get(out_name, set())
            in_dontcare = idx in dontcare.get(out_name, [])

            if in_dontcare:
                continue

            predicted = 1 if in_mterms else 0
            if predicted != expected_val:
                errors.append(
                    f"Minterm {idx} ({vals}) -> output '{out_name}': "
                    f"expected {expected_val}, got {predicted}"
                )

    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark-Level Mutation Operators (M01 - M08)
# ─────────────────────────────────────────────────────────────────────────────

def _find_false_minterm(circuit: dict, out_name: str) -> Optional[int]:
    """Finds a minterm index where expected output is 0 and NOT a don't-care."""
    name = circuit["name"]
    inputs = circuit["inputs"]
    n = circuit["num_inputs"]
    oracle = ORACLES.get(name)
    dontcare = circuit.get("dont_cares_map", {}).get(out_name, [])

    for idx in range(1 << n):
        vals = index_to_input_vals(idx, inputs)
        res = oracle(vals)
        if res is not None and res.get(out_name) == 0 and idx not in dontcare:
            return idx
    return None


def generate_benchmark_mutations(circuit: dict) -> List[Tuple[str, str, str, str, dict]]:
    """
    Generates mutations M01 to M08 for a benchmark circuit.
    
    Returns list of tuples:
        (mutation_id, mutation_type, original_repr, mutated_repr, mutated_circuit_dict)
    """
    c_name = circuit["name"]
    mutations = []
    mterms_orig = circuit["minterms_map"]
    outputs = circuit["outputs"]

    # Pick primary output to mutate (one that has at least one minterm)
    primary_out = None
    for out in outputs:
        if len(mterms_orig.get(out, [])) > 0:
            primary_out = out
            break
    if not primary_out:
        primary_out = outputs[0]

    orig_list = list(mterms_orig.get(primary_out, []))

    # M01 — Remove one valid minterm
    if len(orig_list) >= 1:
        mut_c = copy.deepcopy(circuit)
        removed_m = orig_list[0]
        mut_c["minterms_map"][primary_out] = orig_list[1:]
        mutations.append((
            f"{c_name}_M01",
            "M01_remove_valid_minterm",
            f"{primary_out}: {orig_list}",
            f"{primary_out}: {mut_c['minterms_map'][primary_out]} (removed {removed_m})",
            mut_c,
        ))

    # M02 — Add an incorrect minterm
    false_m = _find_false_minterm(circuit, primary_out)
    if false_m is not None:
        mut_c = copy.deepcopy(circuit)
        new_list = sorted(orig_list + [false_m])
        mut_c["minterms_map"][primary_out] = new_list
        mutations.append((
            f"{c_name}_M02",
            "M02_add_incorrect_minterm",
            f"{primary_out}: {orig_list}",
            f"{primary_out}: {new_list} (added {false_m})",
            mut_c,
        ))

    # M03 — Replace a valid minterm with another wrong minterm
    if len(orig_list) >= 1 and false_m is not None:
        mut_c = copy.deepcopy(circuit)
        replaced_m = orig_list[0]
        new_list = sorted(orig_list[1:] + [false_m])
        mut_c["minterms_map"][primary_out] = new_list
        mutations.append((
            f"{c_name}_M03",
            "M03_replace_valid_minterm",
            f"{primary_out}: {orig_list}",
            f"{primary_out}: {new_list} (replaced {replaced_m} with {false_m})",
            mut_c,
        ))

    # M04 — Remove an entire output's routing/minterm mapping
    mut_c = copy.deepcopy(circuit)
    mut_c["minterms_map"][primary_out] = []
    mutations.append((
        f"{c_name}_M04",
        "M04_remove_entire_output_mapping",
        f"{primary_out}: {orig_list}",
        f"{primary_out}: []",
        mut_c,
    ))

    # M05 — Inject a wrong output mapping (inverted/complement valid minterms)
    mut_c = copy.deepcopy(circuit)
    total_states = 1 << circuit["num_inputs"]
    dontcare = circuit.get("dont_cares_map", {}).get(primary_out, [])
    inverted_list = [
        i for i in range(total_states)
        if i not in orig_list and i not in dontcare
    ]
    mut_c["minterms_map"][primary_out] = inverted_list
    mutations.append((
        f"{c_name}_M05",
        "M05_inject_wrong_output_mapping",
        f"{primary_out}: {orig_list}",
        f"{primary_out}: {inverted_list[:6]}... (inverted minterms)",
        mut_c,
    ))

    # M06 — Swap mappings between two outputs (if circuit has >= 2 outputs)
    if len(outputs) >= 2:
        out1, out2 = outputs[0], outputs[1]
        mut_c = copy.deepcopy(circuit)
        mut_c["minterms_map"][out1] = list(mterms_orig.get(out2, []))
        mut_c["minterms_map"][out2] = list(mterms_orig.get(out1, []))
        mutations.append((
            f"{c_name}_M06",
            "M06_swap_output_mappings",
            f"{out1}<->{out2}",
            f"swapped({out1}, {out2})",
            mut_c,
        ))

    # M07 — Duplicate a minterm
    if len(orig_list) >= 1:
        mut_c = copy.deepcopy(circuit)
        dup_list = list(orig_list) + [orig_list[0]]
        mut_c["minterms_map"][primary_out] = dup_list
        mutations.append((
            f"{c_name}_M07",
            "M07_duplicate_minterm",
            f"{primary_out}: {orig_list}",
            f"{primary_out}: {dup_list} (duplicated {orig_list[0]})",
            mut_c,
        ))

    # M08 — Corrupt multiple minterm entries simultaneously
    mut_c = copy.deepcopy(circuit)
    if len(outputs) >= 2:
        out1, out2 = outputs[0], outputs[1]
        if len(mut_c["minterms_map"].get(out1, [])) > 0:
            mut_c["minterms_map"][out1] = mut_c["minterms_map"][out1][1:]
        f_m2 = _find_false_minterm(circuit, out2)
        if f_m2 is not None:
            mut_c["minterms_map"][out2] = sorted(mut_c["minterms_map"].get(out2, []) + [f_m2])
    else:
        # Single output: remove one and add another
        if len(orig_list) >= 2 and false_m is not None:
            mut_c["minterms_map"][primary_out] = [false_m]
        else:
            mut_c["minterms_map"][primary_out] = [9999]  # out of range
    mutations.append((
        f"{c_name}_M08",
        "M08_corrupt_multiple_entries",
        f"{c_name} minterms",
        "simultaneous multi-output corruptions",
        mut_c,
    ))

    return mutations


# ─────────────────────────────────────────────────────────────────────────────
# Routing-Matrix-Level Mutation Operators (R01 - R08)
# ─────────────────────────────────────────────────────────────────────────────

def generate_routing_mutations(circuit: dict) -> List[Tuple[str, str, str, str, dict]]:
    """
    Generates mutations R01 to R08 directly on the Decoder-OR routing JSON structure.
    """
    c_name = circuit["name"]
    base_routing = benchmark_to_routing_dict(circuit)
    outputs = circuit["outputs"]
    matrix = base_routing["automated_routing_matrix"]

    primary_out = outputs[0]
    primary_key = f"output_OR_{primary_out}"
    orig_pins = list(matrix.get(primary_key, []))

    mutations = []

    # R01 — Remove valid Y pin
    if len(orig_pins) >= 1:
        mut_r = copy.deepcopy(base_routing)
        mut_r["automated_routing_matrix"][primary_key] = orig_pins[1:]
        mutations.append((
            f"{c_name}_R01",
            "R01_routing_remove_pin",
            f"{primary_key}: {orig_pins}",
            f"{primary_key}: {orig_pins[1:]}",
            mut_r,
        ))

    # R02 — Add wrong Y pin
    false_m = _find_false_minterm(circuit, primary_out)
    if false_m is not None:
        mut_r = copy.deepcopy(base_routing)
        wrong_pin = f"Y{false_m}"
        mut_r["automated_routing_matrix"][primary_key] = sorted(orig_pins + [wrong_pin])
        mutations.append((
            f"{c_name}_R02",
            "R02_routing_add_incorrect_pin",
            f"{primary_key}: {orig_pins}",
            f"added {wrong_pin}",
            mut_r,
        ))

    # R03 — Replace valid Y pin with wrong pin
    if len(orig_pins) >= 1 and false_m is not None:
        mut_r = copy.deepcopy(base_routing)
        wrong_pin = f"Y{false_m}"
        mut_r["automated_routing_matrix"][primary_key] = sorted(orig_pins[1:] + [wrong_pin])
        mutations.append((
            f"{c_name}_R03",
            "R03_routing_replace_pin",
            f"{primary_key}: {orig_pins}",
            f"replaced {orig_pins[0]} with {wrong_pin}",
            mut_r,
        ))

    # R04 — Remove entire output routing
    mut_r = copy.deepcopy(base_routing)
    mut_r["automated_routing_matrix"][primary_key] = []
    mutations.append((
        f"{c_name}_R04",
        "R04_routing_clear_output",
        f"{primary_key}: {orig_pins}",
        f"{primary_key}: []",
        mut_r,
    ))

    # R05 — Swap Y pins between two outputs
    if len(outputs) >= 2:
        k1, k2 = f"output_OR_{outputs[0]}", f"output_OR_{outputs[1]}"
        mut_r = copy.deepcopy(base_routing)
        mut_r["automated_routing_matrix"][k1] = list(matrix[k2])
        mut_r["automated_routing_matrix"][k2] = list(matrix[k1])
        mutations.append((
            f"{c_name}_R05",
            "R05_routing_swap_outputs",
            f"{k1} <-> {k2}",
            f"swapped({k1}, {k2})",
            mut_r,
        ))

    # R06 — Duplicate Y pin in routing matrix
    if len(orig_pins) >= 1:
        mut_r = copy.deepcopy(base_routing)
        mut_r["automated_routing_matrix"][primary_key] = list(orig_pins) + [orig_pins[0]]
        mutations.append((
            f"{c_name}_R06",
            "R06_routing_duplicate_pin",
            f"{primary_key}: {orig_pins}",
            f"duplicated {orig_pins[0]}",
            mut_r,
        ))

    # R07 — Out-of-range Y pin (e.g. Y999)
    mut_r = copy.deepcopy(base_routing)
    mut_r["automated_routing_matrix"][primary_key] = list(orig_pins) + ["Y999"]
    mutations.append((
        f"{c_name}_R07",
        "R07_routing_out_of_range_pin",
        f"{primary_key}: {orig_pins}",
        f"injected Y999",
        mut_r,
    ))

    # R08 — Multi-pin simultaneous corruption
    mut_r = copy.deepcopy(base_routing)
    if len(outputs) >= 2:
        k1, k2 = f"output_OR_{outputs[0]}", f"output_OR_{outputs[1]}"
        if len(mut_r["automated_routing_matrix"][k1]) > 0:
            mut_r["automated_routing_matrix"][k1] = mut_r["automated_routing_matrix"][k1][1:]
        if false_m is not None:
            mut_r["automated_routing_matrix"][k2] = list(mut_r["automated_routing_matrix"][k2]) + [f"Y{false_m}"]
    else:
        mut_r["automated_routing_matrix"][primary_key] = ["Y0", "Y999"]
    mutations.append((
        f"{c_name}_R08",
        "R08_routing_corrupt_multiple",
        f"{c_name} routing",
        "simultaneous multi-output Y-pin corruptions",
        mut_r,
    ))

    return mutations


# ─────────────────────────────────────────────────────────────────────────────
# Execution Engine
# ─────────────────────────────────────────────────────────────────────────────

def run_mutation_campaign(
    dataset_path: Path | str = "benchmark_dataset.json",
    output_dir: Path | str = "verification"
) -> Tuple[List[MutationResult], MutationSummary]:
    """
    Executes a comprehensive mutation campaign across all benchmark circuits
    at both benchmark minterm and Decoder-OR routing matrix levels.
    """
    p_data = Path(dataset_path)
    if not p_data.is_absolute():
        p_data = _REPO_ROOT / dataset_path

    p_out = Path(output_dir)
    if not p_out.is_absolute():
        p_out = _REPO_ROOT / output_dir
    p_out.mkdir(parents=True, exist_ok=True)

    with open(p_data, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    results: List[MutationResult] = []
    type_counts: Dict[str, Dict[str, int]] = {}
    circ_counts: Dict[str, Dict[str, int]] = {}

    for circuit in dataset["benchmarks"]:
        c_name = circuit["name"]
        circ_counts.setdefault(c_name, {"total": 0, "killed": 0, "survived": 0})

        # 1. Benchmark-level mutations
        bm_mutations = generate_benchmark_mutations(circuit)
        for m_id, m_type, orig_val, mut_val, mut_spec in bm_mutations:
            type_counts.setdefault(m_type, {"total": 0, "killed": 0, "survived": 0})
            circ_counts[c_name]["total"] += 1
            type_counts[m_type]["total"] += 1

            errors = check_circuit_errors(mut_spec)
            observed = "FAIL" if len(errors) > 0 else "PASS"
            killed = (observed == "FAIL")

            if killed:
                circ_counts[c_name]["killed"] += 1
                type_counts[m_type]["killed"] += 1
            else:
                circ_counts[c_name]["survived"] += 1
                type_counts[m_type]["survived"] += 1

            err_msg = "; ".join(errors[:2]) if errors else "No mismatch detected (mutant survived)"
            results.append(MutationResult(
                circuit=c_name,
                mutation_id=m_id,
                mutation_type=m_type,
                original_value=str(orig_val),
                mutated_value=str(mut_val),
                expected_result="FAIL",
                observed_result=observed,
                killed=killed,
                error_message=err_msg,
            ))

        # 2. Routing-matrix-level mutations
        rt_mutations = generate_routing_mutations(circuit)
        for m_id, m_type, orig_val, mut_val, mut_routing in rt_mutations:
            type_counts.setdefault(m_type, {"total": 0, "killed": 0, "survived": 0})
            circ_counts[c_name]["total"] += 1
            type_counts[m_type]["total"] += 1

            errors = verify_routing_representation(
                mut_routing,
                circuit_name=c_name,
                dont_cares_map=circuit.get("dont_cares_map")
            )
            observed = "FAIL" if len(errors) > 0 else "PASS"
            killed = (observed == "FAIL")

            if killed:
                circ_counts[c_name]["killed"] += 1
                type_counts[m_type]["killed"] += 1
            else:
                circ_counts[c_name]["survived"] += 1
                type_counts[m_type]["survived"] += 1

            err_msg = "; ".join(errors[:2]) if errors else "No mismatch detected (mutant survived)"
            results.append(MutationResult(
                circuit=c_name,
                mutation_id=m_id,
                mutation_type=m_type,
                original_value=str(orig_val),
                mutated_value=str(mut_val),
                expected_result="FAIL",
                observed_result=observed,
                killed=killed,
                error_message=err_msg,
            ))

    total = len(results)
    killed_cnt = sum(1 for r in results if r.killed)
    survived_cnt = total - killed_cnt
    kill_rate = (killed_cnt / total) if total > 0 else 0.0

    summary = MutationSummary(
        total_mutations=total,
        killed_mutations=killed_cnt,
        survived_mutations=survived_cnt,
        mutation_kill_rate=kill_rate,
        details_by_type=type_counts,
        details_by_circuit=circ_counts,
    )

    # Save CSV
    csv_path = p_out / "mutation_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "circuit",
            "mutation_id",
            "mutation_type",
            "original_value",
            "mutated_value",
            "expected_result",
            "observed_result",
            "killed",
            "error_message",
        ])
        for r in results:
            writer.writerow([
                r.circuit,
                r.mutation_id,
                r.mutation_type,
                r.original_value,
                r.mutated_value,
                r.expected_result,
                r.observed_result,
                r.killed,
                r.error_message,
            ])

    # Save JSON summary
    json_path = p_out / "mutation_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(summary), f, indent=2)

    return results, summary


def main():
    print("=" * 65)
    print("  Decoder-OR Oracle & Routing Mutation Testing Campaign")
    print("  Mathematical Ground-Truth Sensitivity Verification")
    print("=" * 65)

    results, summary = run_mutation_campaign()

    print(f"\nTotal Mutations Injected : {summary.total_mutations}")
    print(f"Killed Mutations [FAIL]  : {summary.killed_mutations}")
    print(f"Survived Mutations [PASS]: {summary.survived_mutations}")
    print(f"Mutation Kill Rate       : {summary.mutation_kill_rate * 100:.2f}%")

    print("\n--- Results by Circuit ---")
    for c_name, stats in summary.details_by_circuit.items():
        rate = (stats["killed"] / stats["total"]) * 100 if stats["total"] > 0 else 0.0
        print(f"  {c_name:<18}: {stats['killed']:>2}/{stats['total']:>2} killed ({rate:.1f}%)")

    print("\n--- Results by Mutation Type ---")
    for m_type, stats in summary.details_by_type.items():
        rate = (stats["killed"] / stats["total"]) * 100 if stats["total"] > 0 else 0.0
        print(f"  {m_type:<32}: {stats['killed']:>2}/{stats['total']:>2} killed ({rate:.1f}%)")

    print("\n" + "=" * 65)
    if summary.survived_mutations == 0:
        print("  [SUCCESS] All injected mutations were reliably killed by the oracle.")
        print("  Verification results recorded to:")
        print("    - verification/mutation_results.csv")
        print("    - verification/mutation_summary.json")
    else:
        print(f"  [WARNING] {summary.survived_mutations} mutant(s) survived! Review mutation_results.csv.")
    print("=" * 65)


if __name__ == "__main__":
    main()
