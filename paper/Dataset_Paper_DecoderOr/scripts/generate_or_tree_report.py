"""
scripts/generate_or_tree_report.py
----------------------------------
Generates a structured report detailing the OR-tree decomposition metrics
for key fan-in sizes: 0, 1, 2, 3, 4, 5, 6, 8, 9, 16, 32, 64.
Saves to verification/or_tree_report.json.
"""

import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from compiler.or_tree import (
    decompose_or_tree,
    verify_or_tree_equivalence,
    emit_or_tree_verilog,
)


def generate_report():
    fan_in_cases = [0, 1, 2, 3, 4, 5, 6, 8, 9, 16, 32, 64]
    max_fan_in = 4
    report = []

    for k in fan_in_cases:
        leaves = [f"Y{i}" for i in range(k)]
        decomp = decompose_or_tree(leaves, max_fan_in=max_fan_in)
        equiv = verify_or_tree_equivalence(decomp)
        wire_decls, assign_stmts = emit_or_tree_verilog(decomp, output_signal=f"out_fanin_{k}")

        report.append({
            "original_fan_in": k,
            "max_fan_in": max_fan_in,
            "tree_depth": decomp.tree_depth,
            "number_of_internal_or_nodes": decomp.number_of_internal_or_nodes,
            "number_of_leaves": decomp.number_of_leaves,
            "intermediate_wires_count": len(wire_decls),
            "assign_statements_count": len(assign_stmts),
            "functional_equivalence_verified": equiv,
        })

    out_file = _REPO_ROOT / "verification" / "or_tree_report.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"benchmark_fan_ins": report}, f, indent=2)

    print(f"[OK] Saved OR-tree decomposition report: {out_file.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    generate_report()
