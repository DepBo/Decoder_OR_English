"""
compiler/or_tree.py
-------------------
Balanced OR-Tree Decomposition for Large Fan-In Logic Synthesis.

In physical standard cell libraries (e.g. CMOS), logic gates with large fan-in
(typically > 4) are restricted due to non-linear RC delay and parasitic capacitance.
This module decomposes wide OR operations into balanced hierarchical trees of
sub-OR gates, each with fan-in <= max_fan_in (default 4).
"""

import math
import itertools
from dataclasses import dataclass, field
from typing import List, Union, Dict, Tuple, Set


@dataclass
class ORTreeNode:
    """Represents an internal OR gate node in the decomposed tree."""
    node_id: str
    children: List[Union[str, "ORTreeNode"]] = field(default_factory=list)

    @property
    def fan_in(self) -> int:
        return len(self.children)


@dataclass
class ORTreeDecomposition:
    """Complete metadata and structural representation of an OR-tree decomposition."""
    root: Union[str, ORTreeNode]
    original_fan_in: int
    max_fan_in: int
    tree_depth: int
    number_of_internal_or_nodes: int
    number_of_leaves: int
    all_nodes: List[ORTreeNode] = field(default_factory=list)
    leaf_names: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "original_fan_in": self.original_fan_in,
            "max_fan_in": self.max_fan_in,
            "tree_depth": self.tree_depth,
            "number_of_internal_or_nodes": self.number_of_internal_or_nodes,
            "number_of_leaves": self.number_of_leaves,
        }


def _split_balanced(items: List[any], k: int) -> List[List[any]]:
    """Splits items into k contiguous slices with lengths differing by at most 1."""
    n = len(items)
    base = n // k
    rem = n % k
    slices = []
    idx = 0
    for i in range(k):
        size = base + (1 if i < rem else 0)
        slices.append(items[idx:idx + size])
        idx += size
    return slices


def decompose_or_tree(
    inputs: List[str],
    max_fan_in: int = 4,
    node_prefix: str = "or_tmp"
) -> ORTreeDecomposition:
    """
    Decomposes a list of input signals into a balanced OR tree where every OR gate
    satisfies fan_in <= max_fan_in.

    Parameters:
        inputs: List of input signal names (leaves).
        max_fan_in: Maximum fan-in per OR gate (default: 4, must be >= 2).
        node_prefix: Prefix used for naming intermediate wire nodes.

    Returns:
        ORTreeDecomposition object containing tree structure and detailed metadata.
    """
    if max_fan_in < 2:
        raise ValueError(f"max_fan_in must be >= 2, got {max_fan_in}")

    k_leaves = len(inputs)
    leaf_list = list(inputs)

    # Edge Case: Fan-in 0 (constant 0)
    if k_leaves == 0:
        return ORTreeDecomposition(
            root="1'b0",
            original_fan_in=0,
            max_fan_in=max_fan_in,
            tree_depth=0,
            number_of_internal_or_nodes=0,
            number_of_leaves=0,
            all_nodes=[],
            leaf_names=[],
        )

    # Edge Case: Fan-in 1 (direct pass-through wire)
    if k_leaves == 1:
        return ORTreeDecomposition(
            root=leaf_list[0],
            original_fan_in=1,
            max_fan_in=max_fan_in,
            tree_depth=0,
            number_of_internal_or_nodes=0,
            number_of_leaves=1,
            all_nodes=[],
            leaf_names=leaf_list,
        )

    # Base Case: Fan-in <= max_fan_in (single monolithic OR gate)
    if k_leaves <= max_fan_in:
        root_node = ORTreeNode(node_id=f"{node_prefix}_root", children=leaf_list)
        return ORTreeDecomposition(
            root=root_node,
            original_fan_in=k_leaves,
            max_fan_in=max_fan_in,
            tree_depth=1,
            number_of_internal_or_nodes=1,
            number_of_leaves=k_leaves,
            all_nodes=[root_node],
            leaf_names=leaf_list,
        )

    # General Case: Fan-in > max_fan_in -> Balanced Recursive Decomposition
    node_counter = 0
    all_internal_nodes: List[ORTreeNode] = []

    def _build_tree(leaves: List[str]) -> Tuple[Union[str, ORTreeNode], int]:
        nonlocal node_counter
        count = len(leaves)

        if count == 1:
            return leaves[0], 0

        if count <= max_fan_in:
            node_counter += 1
            node = ORTreeNode(node_id=f"{node_prefix}_n{node_counter}", children=leaves)
            all_internal_nodes.append(node)
            return node, 1

        # Determine target depth D and number of branches k
        # Capacity of height D-1 is max_fan_in^(D-1)
        depth = math.ceil(math.log(count, max_fan_in))
        sub_capacity = max_fan_in ** (depth - 1)
        num_branches = math.ceil(count / sub_capacity)
        # Guarantee num_branches <= max_fan_in
        num_branches = min(num_branches, max_fan_in)
        num_branches = max(num_branches, 2)

        groups = _split_balanced(leaves, num_branches)
        child_refs: List[Union[str, ORTreeNode]] = []
        max_sub_depth = 0

        for grp in groups:
            sub_root, sub_depth = _build_tree(grp)
            child_refs.append(sub_root)
            if sub_depth > max_sub_depth:
                max_sub_depth = sub_depth

        node_counter += 1
        curr_node = ORTreeNode(node_id=f"{node_prefix}_n{node_counter}", children=child_refs)
        all_internal_nodes.append(curr_node)
        return curr_node, max_sub_depth + 1

    root_node, actual_depth = _build_tree(leaf_list)

    return ORTreeDecomposition(
        root=root_node,
        original_fan_in=k_leaves,
        max_fan_in=max_fan_in,
        tree_depth=actual_depth,
        number_of_internal_or_nodes=len(all_internal_nodes),
        number_of_leaves=k_leaves,
        all_nodes=all_internal_nodes,
        leaf_names=leaf_list,
    )


def evaluate_or_tree(
    decomposition: ORTreeDecomposition,
    input_values: Union[Dict[str, int], Set[str]]
) -> int:
    """
    Simulates the Boolean behavior of the decomposed OR-tree.

    Parameters:
        decomposition: The ORTreeDecomposition instance.
        input_values: Dict mapping each leaf name to 0 or 1, or Set of active (1) leaf names.

    Returns:
        Evaluated Boolean output (0 or 1).
    """
    root = decomposition.root

    if isinstance(root, str):
        if root == "1'b0":
            return 0
        if isinstance(input_values, set):
            return 1 if root in input_values else 0
        return int(input_values.get(root, 0))

    is_set = isinstance(input_values, set)

    def _eval_node(node: Union[str, ORTreeNode]) -> int:
        if isinstance(node, str):
            if node == "1'b0":
                return 0
            if is_set:
                return 1 if node in input_values else 0
            return int(input_values.get(node, 0))
        # Internal node: bitwise OR of all children (short-circuit on 1)
        for ch in node.children:
            if _eval_node(ch) == 1:
                return 1
        return 0

    return _eval_node(root)


def verify_or_tree_equivalence(
    decomposition: ORTreeDecomposition,
    max_exhaustive_bits: int = 16
) -> bool:
    """
    Proves functional equivalence between the original Boolean OR function
    and the decomposed OR tree.

    - Exhaustive truth-table verification for fan-in <= max_exhaustive_bits.
    - Deterministic edge patterns + 1-hot + 2-hot + pseudo-random sampling for larger fan-in.

    Returns:
        True if all test vectors evaluate to identical Boolean outputs.
    Raises:
        AssertionError: If any discrepancy is found.
    """
    leaves = decomposition.leaf_names
    k = len(leaves)

    # Edge cases
    if k == 0:
        val = evaluate_or_tree(decomposition, set())
        assert val == 0, f"Fan-in 0 must evaluate to 0, got {val}"
        return True

    if k == 1:
        for bit in (0, 1):
            active = {leaves[0]} if bit == 1 else set()
            val = evaluate_or_tree(decomposition, active)
            assert val == bit, f"Fan-in 1 pass-through mismatch: expected {bit}, got {val}"
        return True

    # Exhaustive verification for practical sizes (<= 16 leaves)
    if k <= max_exhaustive_bits:
        total_vectors = 1 << k
        for pattern in range(total_vectors):
            active_set = {leaves[i] for i in range(k) if (pattern >> i) & 1}
            expected = 1 if len(active_set) > 0 else 0
            observed = evaluate_or_tree(decomposition, active_set)
            if observed != expected:
                raise AssertionError(
                    f"OR-tree functional equivalence failure for pattern {pattern:0{k}b}: "
                    f"expected {expected}, observed {observed}"
                )
        return True

    # Property-based + structured verification for large fan-in (e.g. 32, 64, 65536)
    # 1. All Zeros
    assert evaluate_or_tree(decomposition, set()) == 0, "All-zeros pattern must produce 0."

    # 2. All Ones
    all_ones_set = set(leaves)
    assert evaluate_or_tree(decomposition, all_ones_set) == 1, "All-ones pattern must produce 1."

    # 3. 1-Hot Vectors (each leaf asserted high individually)
    test_indices = range(k) if k <= 1024 else list(range(0, k, max(1, k // 256))) + [0, k - 1]
    for idx in test_indices:
        active_leaf = leaves[idx]
        obs = evaluate_or_tree(decomposition, {active_leaf})
        assert obs == 1, f"1-hot pattern at leaf '{active_leaf}' (index {idx}) must produce 1, got {obs}"

    # 4. 2-Hot Vectors (pairs of active leaves)
    sample_bound = min(k, 16)
    for i in range(sample_bound):
        for j in range(i + 1, sample_bound):
            obs = evaluate_or_tree(decomposition, {leaves[i], leaves[j]})
            assert obs == 1, f"2-hot pattern at ({i}, {j}) must produce 1"

    # 5. Deterministic pseudo-random vectors (Linear Congruential Generator)
    seed = 0x1337BEEF
    for _ in range(100):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        active_set = {leaves[i] for i in range(min(k, 31)) if (seed >> (i % 31)) & 1}
        expected = 1 if len(active_set) > 0 else 0
        observed = evaluate_or_tree(decomposition, active_set)
        assert observed == expected, f"Pseudo-random vector mismatch: expected {expected}, got {observed}"

    return True


def _format_verilog_signal(sig_name: str, bus_name: str = "Y") -> str:
    """Converts a pin name like 'Y5' into Verilog array indexing 'Y[5]' or 'dec_Y[5]'."""
    if sig_name.startswith("Y") and sig_name[1:].isdigit():
        return f"{bus_name}[{sig_name[1:]}]"
    return sig_name


def emit_or_tree_verilog(
    decomposition: ORTreeDecomposition,
    output_signal: str,
    decoder_bus_name: str = "Y"
) -> Tuple[List[str], List[str]]:
    """
    Emits intermediate wire declarations and assign statements for the decomposed OR tree.
    Guarantees that NO emitted OR expression has fan-in exceeding decomposition.max_fan_in.

    Parameters:
        decomposition: The ORTreeDecomposition object.
        output_signal: The final target wire or output port name (e.g. 'Sum', 'output_OR_a').
        decoder_bus_name: The name of the internal decoder bus (default: 'Y').

    Returns:
        (wire_declarations, assign_statements)
    """
    root = decomposition.root

    # Fan-in 0: drive constant 0
    if decomposition.original_fan_in == 0:
        return [], [f"assign {output_signal} = 1'b0;"]

    # Fan-in 1: direct pass-through
    if decomposition.original_fan_in == 1:
        rhs = _format_verilog_signal(str(root), bus_name=decoder_bus_name)
        return [], [f"assign {output_signal} = {rhs};"]

    # Single OR node (fan-in <= max_fan_in)
    if isinstance(root, ORTreeNode) and len(decomposition.all_nodes) == 1:
        expr = " | ".join(_format_verilog_signal(ch if isinstance(ch, str) else ch.node_id, bus_name=decoder_bus_name) for ch in root.children)
        return [], [f"assign {output_signal} = {expr};"]

    # Multi-level decomposed tree:
    # All nodes except root are intermediate wires.
    # Root node drives output_signal directly.
    wire_decls: List[str] = []
    assign_stmts: List[str] = []

    # Map node instances to their driving signal names
    root_node = decomposition.all_nodes[-1]

    for node in decomposition.all_nodes:
        # Determine target wire name
        is_root = (node == root_node)
        target_wire = output_signal if is_root else node.node_id

        if not is_root:
            wire_decls.append(f"wire {node.node_id};")

        # Build RHS expression
        child_signals: List[str] = []
        for ch in node.children:
            if isinstance(ch, str):
                child_signals.append(_format_verilog_signal(ch, bus_name=decoder_bus_name))
            elif isinstance(ch, ORTreeNode):
                child_signals.append(ch.node_id)
            else:
                child_signals.append(str(ch))

        rhs_expr = " | ".join(child_signals)
        assign_stmts.append(f"assign {target_wire} = {rhs_expr};")

    return wire_decls, assign_stmts
