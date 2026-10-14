"""
Decoder-OR Compiler Package
----------------------------
Automated Logic Synthesis via Decoder and OR Gates.
Provides:
- validator: Validates Decoder-OR routing JSON against schema and dimensions
- or_tree: Balanced OR-tree decomposition for fan-in limits
- generator: Translates validated routing JSON into synthesizable Verilog RTL
"""

from .validator import (
    ValidationError,
    JSONSyntaxError,
    SchemaError,
    DecoderDimensionError,
    PinError,
    DuplicatePinError,
    UnknownOutputError,
    validate_routing_dict,
    validate_routing_json_string,
    validate_routing_file,
)
from .or_tree import (
    ORTreeNode,
    ORTreeDecomposition,
    decompose_or_tree,
    evaluate_or_tree,
    verify_or_tree_equivalence,
    emit_or_tree_verilog,
)
from .generator import (
    generate_verilog_from_data,
    compile_file,
)

__all__ = [
    "ValidationError",
    "JSONSyntaxError",
    "SchemaError",
    "DecoderDimensionError",
    "PinError",
    "DuplicatePinError",
    "UnknownOutputError",
    "validate_routing_dict",
    "validate_routing_json_string",
    "validate_routing_file",
    "ORTreeNode",
    "ORTreeDecomposition",
    "decompose_or_tree",
    "evaluate_or_tree",
    "verify_or_tree_equivalence",
    "emit_or_tree_verilog",
    "generate_verilog_from_data",
    "compile_file",
]
