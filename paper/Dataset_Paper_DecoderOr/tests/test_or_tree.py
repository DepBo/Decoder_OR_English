"""
tests/test_or_tree.py
---------------------
Unit tests for balanced OR-tree decomposition, edge cases, metadata verification,
and functional Boolean equivalence.
"""

import math
import pytest
from compiler.or_tree import (
    decompose_or_tree,
    evaluate_or_tree,
    verify_or_tree_equivalence,
    emit_or_tree_verilog,
    ORTreeNode,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Edge Cases (Fan-in 0, 1)
# ─────────────────────────────────────────────────────────────────────────────

def test_fan_in_0():
    decomp = decompose_or_tree([], max_fan_in=4)
    assert decomp.original_fan_in == 0
    assert decomp.tree_depth == 0
    assert decomp.number_of_internal_or_nodes == 0
    assert decomp.number_of_leaves == 0
    assert decomp.root == "1'b0"

    # Evaluation
    assert evaluate_or_tree(decomp, {}) == 0
    assert verify_or_tree_equivalence(decomp)

    # Verilog emission
    wires, assigns = emit_or_tree_verilog(decomp, "out")
    assert wires == []
    assert assigns == ["assign out = 1'b0;"]


def test_fan_in_1():
    decomp = decompose_or_tree(["Y0"], max_fan_in=4)
    assert decomp.original_fan_in == 1
    assert decomp.tree_depth == 0
    assert decomp.number_of_internal_or_nodes == 0
    assert decomp.number_of_leaves == 1
    assert decomp.root == "Y0"

    # Evaluation
    assert evaluate_or_tree(decomp, {"Y0": 0}) == 0
    assert evaluate_or_tree(decomp, {"Y0": 1}) == 1
    assert verify_or_tree_equivalence(decomp)

    # Verilog emission
    wires, assigns = emit_or_tree_verilog(decomp, "out")
    assert wires == []
    assert assigns == ["assign out = Y[0];"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Monolithic Single OR Gate Cases (Fan-in 2, 3, 4 with max_fan_in=4)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("k", [2, 3, 4])
def test_monolithic_fan_in_up_to_max(k):
    inputs = [f"Y{i}" for i in range(k)]
    decomp = decompose_or_tree(inputs, max_fan_in=4)

    assert decomp.original_fan_in == k
    assert decomp.max_fan_in == 4
    assert decomp.tree_depth == 1
    assert decomp.number_of_internal_or_nodes == 1
    assert decomp.number_of_leaves == k
    assert len(decomp.all_nodes) == 1

    root_node = decomp.all_nodes[0]
    assert root_node.fan_in == k
    assert root_node.children == inputs

    # Functional Equivalence
    assert verify_or_tree_equivalence(decomp)

    # Verilog emission
    wires, assigns = emit_or_tree_verilog(decomp, "out")
    assert wires == []
    assert len(assigns) == 1
    expected_rhs = " | ".join(f"Y[{i}]" for i in range(k))
    assert assigns[0] == f"assign out = {expected_rhs};"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Decomposed Multi-level Trees (Fan-in 5, 6, 8, 9, 16, 32, 64)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("k, expected_depth", [
    (5, 2),
    (6, 2),
    (8, 2),
    (9, 2),
    (16, 2),
    (32, 3),
    (64, 3),
])
def test_decomposed_fan_in_structure_and_limits(k, expected_depth):
    inputs = [f"Y{i}" for i in range(k)]
    decomp = decompose_or_tree(inputs, max_fan_in=4)

    # Metadata assertions
    assert decomp.original_fan_in == k
    assert decomp.max_fan_in == 4
    assert decomp.number_of_leaves == k
    assert decomp.tree_depth == expected_depth
    assert decomp.number_of_internal_or_nodes == len(decomp.all_nodes)

    # Strict invariant: NO node may have fan_in > max_fan_in
    for node in decomp.all_nodes:
        assert node.fan_in <= 4, f"Node {node.node_id} violated max_fan_in: {node.fan_in} > 4"
        assert node.fan_in >= 2, f"Node {node.node_id} has invalid fan-in: {node.fan_in}"

    # Verilog emission test
    wires, assigns = emit_or_tree_verilog(decomp, "out")
    # Intermediate wires should equal internal_nodes - 1 (root drives target directly)
    assert len(wires) == decomp.number_of_internal_or_nodes - 1
    assert len(assigns) == decomp.number_of_internal_or_nodes

    # Check each emitted assign statement respects fan-in limit <= 4
    for stmt in assigns:
        # e.g. "assign wire_name = sig1 | sig2 | sig3;"
        rhs = stmt.split("=")[1].replace(";", "").strip()
        operands = [op.strip() for op in rhs.split("|")]
        assert len(operands) <= 4, f"Emitted statement exceeded max_fan_in: {stmt}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Functional Equivalence Verification
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("k", [2, 3, 4, 5, 6, 8, 9, 12, 16])
def test_exhaustive_functional_equivalence(k):
    """Exhaustively proves Boolean equivalence over all 2^k input combinations."""
    inputs = [f"Y{i}" for i in range(k)]
    decomp = decompose_or_tree(inputs, max_fan_in=4)
    assert verify_or_tree_equivalence(decomp, max_exhaustive_bits=16)


@pytest.mark.parametrize("k", [32, 64])
def test_large_scale_property_equivalence(k):
    """Proves Boolean equivalence for wide fan-in (32, 64) using structured + random vectors."""
    inputs = [f"Y{i}" for i in range(k)]
    decomp = decompose_or_tree(inputs, max_fan_in=4)
    assert verify_or_tree_equivalence(decomp, max_exhaustive_bits=16)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Configurable max_fan_in (e.g. Binary Tree with max_fan_in=2)
# ─────────────────────────────────────────────────────────────────────────────

def test_binary_or_tree_decomposition():
    inputs = [f"Y{i}" for i in range(8)]
    decomp = decompose_or_tree(inputs, max_fan_in=2)

    assert decomp.original_fan_in == 8
    assert decomp.max_fan_in == 2
    assert decomp.tree_depth == 3  # log2(8) = 3
    # A full binary tree with 8 leaves has 8 - 1 = 7 internal nodes
    assert decomp.number_of_internal_or_nodes == 7

    for node in decomp.all_nodes:
        assert node.fan_in == 2

    assert verify_or_tree_equivalence(decomp)


def test_invalid_max_fan_in():
    with pytest.raises(ValueError, match="max_fan_in must be >= 2"):
        decompose_or_tree(["Y0", "Y1"], max_fan_in=1)
