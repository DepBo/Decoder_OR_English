"""
tests/test_compiler.py
----------------------
End-to-end compiler integration tests:
Routing JSON -> Validation -> OR-tree Decomposition -> Synthesizable Verilog RTL.
"""

import re
import pytest
from pathlib import Path

from compiler.generator import (
    generate_verilog_from_data,
    compile_file,
    benchmark_to_routing_dict,
)
from compiler.validator import ValidationError

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_compile_half_adder():
    routing_path = REPO_ROOT / "benchmarks_routing" / "Half_Adder.json"
    verilog = compile_file(routing_path, max_fan_in=4)

    assert "module Half_Adder_Decoder_OR (" in verilog
    assert "input  wire A" in verilog
    assert "input  wire B" in verilog
    assert "output wire Sum" in verilog
    assert "output wire Cout" in verilog
    assert "wire [3:0] Y;" in verilog
    assert "assign Y = 4'b1 << {A, B};" in verilog
    assert "assign Sum = Y[1] | Y[2];" in verilog
    assert "assign Cout = Y[3];" in verilog
    assert "endmodule" in verilog


def test_compile_full_adder():
    routing_path = REPO_ROOT / "benchmarks_routing" / "Full_Adder.json"
    verilog = compile_file(routing_path, max_fan_in=4)

    assert "module Full_Adder_Decoder_OR (" in verilog
    assert "wire [7:0] Y;" in verilog
    assert "assign Y = 8'b1 << {A, B, Cin};" in verilog
    assert "assign Sum = Y[1] | Y[2] | Y[4] | Y[7];" in verilog
    assert "assign Cout = Y[3] | Y[5] | Y[6] | Y[7];" in verilog
    assert "endmodule" in verilog


def test_compile_bcd_7segment_or_tree_decomposition():
    """
    BCD to 7-segment has outputs requiring up to 9 inputs (segment 'c'),
    which MUST be decomposed into OR-trees when max_fan_in=4.
    """
    routing_path = REPO_ROOT / "benchmarks_routing" / "BCD_to_7Segment.json"
    verilog = compile_file(routing_path, max_fan_in=4)

    assert "module BCD_to_7Segment_Decoder_OR (" in verilog
    assert "wire [15:0] Y;" in verilog

    # Segment 'c' has 9 minterms: Y0, Y1, Y3, Y4, Y5, Y6, Y7, Y8, Y9
    # Must have intermediate wire declarations: c_or_n1, c_or_n2, c_or_n3
    assert "wire c_or_n1;" in verilog
    assert "wire c_or_n2;" in verilog
    assert "wire c_or_n3;" in verilog
    assert "assign c = c_or_n1 | c_or_n2 | c_or_n3;" in verilog

    # Segment 'e' has 4 minterms: kept as single monolithic OR gate
    assert "assign e = Y[0] | Y[2] | Y[6] | Y[8];" in verilog

    # Check that NO assign statement in the entire module has > 4 operands
    for line in verilog.splitlines():
        line = line.strip()
        if line.startswith("assign ") and "|" in line:
            rhs = line.split("=")[1].replace(";", "").strip()
            operands = rhs.split("|")
            assert len(operands) <= 4, f"Line exceeded max fan-in of 4: {line}"


def test_compile_3bit_comparator_wide_decomposition():
    """
    3-bit comparator has 28 minterms for A_gt_B,
    requiring 3-level tree decomposition with max_fan_in=4.
    """
    routing_path = REPO_ROOT / "benchmarks_routing" / "3bit_Comparator.json"
    verilog = compile_file(routing_path, max_fan_in=4)

    assert "module _3bit_Comparator_Decoder_OR (" in verilog
    assert "wire [63:0] Y;" in verilog

    # Ensure every single emitted OR assign has <= 4 operands
    assign_count = 0
    for line in verilog.splitlines():
        line = line.strip()
        if line.startswith("assign ") and "|" in line:
            assign_count += 1
            rhs = line.split("=")[1].replace(";", "").strip()
            operands = rhs.split("|")
            assert len(operands) <= 4, f"Line exceeded max fan-in of 4: {line}"

    assert assign_count > 10, "Expected decomposed assign statements for 3bit_Comparator"


def test_invalid_routing_aborts_without_verilog():
    """Invalid input must raise ValidationError and NEVER emit Verilog code."""
    invalid_data = {
        "system": "Corrupted_System",
        "architecture": {
            "core_decoder": "3-to-8_Active_High",
            "inputs": ["A", "B"],  # 2 inputs for 3-to-8 decoder -> mismatch
            "outputs": ["Y"],
        },
        "automated_routing_matrix": {"output_OR_Y": ["Y0"]},
    }

    with pytest.raises(ValidationError):
        generate_verilog_from_data(invalid_data)


def test_active_low_routing_aborts_without_verilog():
    """Unsupported polarity must fail before the active-high RTL is emitted."""
    invalid_data = {
        "system": "Unsupported_Active_Low",
        "architecture": {
            "core_decoder": "2-to-4_Active_Low",
            "inputs": ["A", "B"],
            "outputs": ["F"],
        },
        "automated_routing_matrix": {"output_OR_F": ["Y1"]},
    }

    with pytest.raises(ValidationError, match="Active_Low is not implemented"):
        generate_verilog_from_data(invalid_data)


def test_custom_module_name():
    routing_path = REPO_ROOT / "benchmarks_routing" / "Half_Adder.json"
    import json
    data = json.loads(routing_path.read_text(encoding="utf-8"))
    verilog = generate_verilog_from_data(data, module_name="MyCustomAdder")
    assert "module MyCustomAdder (" in verilog
