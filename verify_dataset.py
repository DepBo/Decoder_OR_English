"""
verify_dataset.py
-----------------
Tự động đọc benchmark_dataset.json và kiểm chứng tính đúng đắn của
bảng minterm cho từng mạch.  Chạy bằng:
    python verify_dataset.py
"""

import json
import itertools


# ─────────────────────────────────────────────
# Helper: tính giá trị bit của 1 minterm index
# ─────────────────────────────────────────────
def minterm_to_bits(index: int, num_inputs: int) -> dict:
    """Chuyển một minterm index thành dict {input_name: bit_value}."""
    bits = {}
    for i in range(num_inputs - 1, -1, -1):
        bits[i] = (index >> i) & 1
    return index


def index_to_input_vals(index: int, inputs: list[str]) -> dict:
    n = len(inputs)
    return {inputs[i]: (index >> (n - 1 - i)) & 1 for i in range(n)}


# ─────────────────────────────────────────────────────────────────────────────
# Các hàm Oracle (ground truth) cho từng mạch
# ─────────────────────────────────────────────────────────────────────────────

def oracle_half_adder(vals: dict) -> dict:
    A, B = vals["A"], vals["B"]
    return {"Sum": A ^ B, "Cout": A & B}


def oracle_full_adder(vals: dict) -> dict:
    A, B, C = vals["A"], vals["B"], vals["Cin"]
    s = A ^ B ^ C
    c = (A & B) | (A & C) | (B & C)
    return {"Sum": s, "Cout": c}


def oracle_mux_2to1(vals: dict) -> dict:
    S, I0, I1 = vals["S"], vals["I0"], vals["I1"]
    return {"Y": I0 if S == 0 else I1}


def oracle_bcd_7seg(vals: dict) -> dict:
    A, B, C, D = vals["A"], vals["B"], vals["C"], vals["D"]
    digit = A * 8 + B * 4 + C * 2 + D
    # Common-cathode, active HIGH  (segments: a b c d e f g)
    table = {
        0: (1, 1, 1, 1, 1, 1, 0),
        1: (0, 1, 1, 0, 0, 0, 0),
        2: (1, 1, 0, 1, 1, 0, 1),
        3: (1, 1, 1, 1, 0, 0, 1),
        4: (0, 1, 1, 0, 0, 1, 1),
        5: (1, 0, 1, 1, 0, 1, 1),
        6: (1, 0, 1, 1, 1, 1, 1),
        7: (1, 1, 1, 0, 0, 0, 0),
        8: (1, 1, 1, 1, 1, 1, 1),
        9: (1, 1, 1, 1, 0, 1, 1),
    }
    if digit not in table:
        return None  # don't-care
    segs = table[digit]
    names = ["a", "b", "c", "d", "e", "f", "g"]
    return dict(zip(names, segs))


def oracle_3bit_comparator(vals: dict) -> dict:
    A = vals["A2"] * 4 + vals["A1"] * 2 + vals["A0"]
    B = vals["B2"] * 4 + vals["B1"] * 2 + vals["B0"]
    return {
        "A_gt_B": 1 if A > B else 0,
        "A_eq_B": 1 if A == B else 0,
        "A_lt_B": 1 if A < B else 0,
    }


ORACLES = {
    "Half_Adder":        oracle_half_adder,
    "Full_Adder":        oracle_full_adder,
    "2_to_1_MUX":        oracle_mux_2to1,
    "BCD_to_7Segment":   oracle_bcd_7seg,
    "3bit_Comparator":   oracle_3bit_comparator,
}


# ─────────────────────────────────────────────────────────────────────────────
# Kiểm chứng tự động
# ─────────────────────────────────────────────────────────────────────────────

def verify_circuit(circuit: dict) -> bool:
    name     = circuit["name"]
    inputs   = circuit["inputs"]
    n        = circuit["num_inputs"]
    mterms   = circuit["minterms_map"]
    dontcare = circuit.get("dont_cares_map", {})
    oracle   = ORACLES.get(name)

    if oracle is None:
        print(f"  [SKIP] No oracle defined for {name}")
        return True

    errors = []
    total  = 2 ** n

    for idx in range(total):
        vals    = index_to_input_vals(idx, inputs)
        result  = oracle(vals)

        if result is None:   # don't-care row (e.g. BCD > 9)
            continue

        for out_name, expected_val in result.items():
            in_mterms   = idx in mterms.get(out_name, [])
            in_dontcare = idx in dontcare.get(out_name, [])

            if in_dontcare:
                continue   # don't-care – either value is acceptable

            predicted = 1 if in_mterms else 0
            if predicted != expected_val:
                errors.append(
                    f"    Minterm {idx:>3} ({vals}) → output '{out_name}': "
                    f"expected {expected_val}, got {predicted}"
                )

    if errors:
        print(f"  [FAIL] {name}  — {len(errors)} error(s):")
        for e in errors:
            print(e)
        return False
    else:
        print(f"  [PASS] {name}  — all {total} minterms verified correctly.")
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    dataset_path = "benchmark_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print("=" * 60)
    print("  Benchmark Dataset Verification")
    print("  Decoder-OR Logic Design – Automated Checker")
    print("=" * 60)

    all_pass = True
    for circuit in dataset["benchmarks"]:
        print(f"\n[{circuit['id']}] {circuit['name']}")
        print(f"     Inputs : {circuit['inputs']}")
        print(f"     Outputs: {circuit['outputs']}")
        ok = verify_circuit(circuit)
        all_pass = all_pass and ok

    print("\n" + "=" * 60)
    if all_pass:
        print("  ✓ ALL CIRCUITS PASSED — dataset is mathematically correct.")
    else:
        print("  ✗ SOME CIRCUITS FAILED — please review the errors above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
