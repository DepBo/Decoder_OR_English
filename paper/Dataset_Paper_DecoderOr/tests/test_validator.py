"""
tests/test_validator.py
-----------------------
Unit and integration tests for Decoder-OR routing JSON validation layer.
Tests ACCEPT and REJECT conditions for syntax, schema, dimensions, and pins.
"""

import pytest
from pathlib import Path

from compiler.validator import (
    validate_routing_dict,
    validate_routing_json_string,
    validate_routing_file,
    parse_decoder_spec,
    ValidationError,
    JSONSyntaxError,
    SchemaError,
    DecoderDimensionError,
    PinError,
    DuplicatePinError,
    UnknownOutputError,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# Test Fixtures & Valid Specifications
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def valid_half_adder_routing():
    return {
        "system": "Half_Adder_Decoder_OR",
        "architecture": {
            "core_decoder": "2-to-4_Active_High",
            "inputs": ["A", "B"],
            "outputs": ["Sum", "Cout"],
        },
        "automated_routing_matrix": {
            "output_OR_Sum": ["Y1", "Y2"],
            "output_OR_Cout": ["Y3"],
        },
    }


@pytest.fixture
def valid_full_adder_routing():
    return {
        "system": "Full_Adder_Decoder_OR",
        "architecture": {
            "core_decoder": "3-to-8_Active_High",
            "inputs": ["A", "B", "Cin"],
            "outputs": ["Sum", "Cout"],
        },
        "automated_routing_matrix": {
            "output_OR_Sum": ["Y1", "Y2", "Y4", "Y7"],
            "output_OR_Cout": ["Y3", "Y5", "Y6", "Y7"],
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. Valid Input Acceptance Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_valid_routing_dict_accepted(valid_half_adder_routing):
    res = validate_routing_dict(valid_half_adder_routing)
    assert res["system"] == "Half_Adder_Decoder_OR"
    assert res["num_inputs"] == 2
    assert res["num_decoder_outputs"] == 4
    assert res["inputs"] == ["A", "B"]
    assert res["outputs"] == ["Sum", "Cout"]
    assert res["routing"]["Sum"] == ["Y1", "Y2"]
    assert res["routing"]["Cout"] == ["Y3"]


def test_valid_benchmark_routing_files():
    """All 5 exported benchmark routing files must pass validation."""
    routing_dir = REPO_ROOT / "benchmarks_routing"
    for json_file in routing_dir.glob("*.json"):
        res = validate_routing_file(json_file)
        assert res["num_inputs"] > 0
        assert res["num_decoder_outputs"] == (1 << res["num_inputs"])


def test_valid_decoder_spec_parsing():
    n_in, n_out, pol = parse_decoder_spec("2-to-4")
    assert (n_in, n_out, pol) == (2, 4, "Active_High")

    n_in, n_out, pol = parse_decoder_spec("3-to-8_Active_High")
    assert (n_in, n_out, pol) == (3, 8, "Active_High")

    n_in, n_out, pol = parse_decoder_spec("6-to-64")
    assert (n_in, n_out, pol) == (6, 64, "Active_High")


def test_reject_active_low_decoder_spec():
    with pytest.raises(SchemaError, match="only supports Active_High Decoder-OR"):
        parse_decoder_spec("4-to-16_Active_Low")


def test_reject_active_low_routing(valid_half_adder_routing):
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"]["core_decoder"] = "2-to-4_Active_Low"
    with pytest.raises(SchemaError, match="Active_Low is not implemented"):
        validate_routing_dict(corrupted)


@pytest.mark.parametrize("unsupported_field, value", [
    ("polarity", "Active_Low"),
    ("gate_type", "NAND"),
    ("logic_form", "POS"),
])
def test_reject_unsupported_architecture_modes(valid_half_adder_routing, unsupported_field, value):
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"][unsupported_field] = value
    with pytest.raises(SchemaError, match="Unsupported architecture field"):
        validate_routing_dict(corrupted)


def test_reject_unsupported_bit_ordering(valid_half_adder_routing):
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"]["bit_ordering"] = "LSB-first"
    with pytest.raises(SchemaError, match="only supports 'MSB-first'"):
        validate_routing_dict(corrupted)


def test_accept_explicit_msb_first_bit_ordering(valid_half_adder_routing):
    valid_half_adder_routing["architecture"]["bit_ordering"] = "MSB-first"
    assert validate_routing_dict(valid_half_adder_routing)["polarity"] == "Active_High"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Syntax & Parsing Errors (Expected REJECT)
# ─────────────────────────────────────────────────────────────────────────────

def test_reject_empty_string():
    with pytest.raises(JSONSyntaxError, match="Empty JSON content"):
        validate_routing_json_string("")


def test_reject_whitespace_only():
    with pytest.raises(JSONSyntaxError, match="Empty JSON content"):
        validate_routing_json_string("    \n\t  ")


def test_reject_malformed_json_unclosed_brace():
    with pytest.raises(JSONSyntaxError, match="Malformed JSON syntax"):
        validate_routing_json_string('{"system": "Test"')


def test_reject_malformed_json_trailing_comma():
    with pytest.raises(JSONSyntaxError, match="Malformed JSON syntax"):
        validate_routing_json_string('{"system": "Test",}')


def test_reject_non_dict_root():
    with pytest.raises(SchemaError, match="must be a JSON object"):
        validate_routing_dict(["not", "a", "dict"])


def test_reject_missing_file():
    with pytest.raises(FileNotFoundError):
        validate_routing_file(REPO_ROOT / "non_existent_routing.json")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Schema & Required Field Errors (Expected REJECT)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("missing_field", ["system", "architecture", "automated_routing_matrix"])
def test_reject_missing_top_level_field(valid_half_adder_routing, missing_field):
    corrupted = dict(valid_half_adder_routing)
    del corrupted[missing_field]
    with pytest.raises(SchemaError, match=f"Missing required field: '{missing_field}'"):
        validate_routing_dict(corrupted)


@pytest.mark.parametrize("missing_arch_field", ["core_decoder", "inputs", "outputs"])
def test_reject_missing_architecture_field(valid_half_adder_routing, missing_arch_field):
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    del corrupted["architecture"][missing_arch_field]
    with pytest.raises(SchemaError, match=f"Missing required architecture field: '{missing_arch_field}'"):
        validate_routing_dict(corrupted)


def test_reject_empty_inputs_list(valid_half_adder_routing):
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"]["inputs"] = []
    with pytest.raises(SchemaError, match="'inputs' must be a non-empty list"):
        validate_routing_dict(corrupted)


def test_reject_duplicate_inputs(valid_half_adder_routing):
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"]["inputs"] = ["A", "A"]
    with pytest.raises(SchemaError, match="Duplicate input signal"):
        validate_routing_dict(corrupted)


def test_reject_input_output_overlap(valid_half_adder_routing):
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"]["outputs"] = ["Sum", "A"]  # 'A' is already an input
    with pytest.raises(SchemaError, match="Signal name conflict between inputs and outputs"):
        validate_routing_dict(corrupted)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Decoder Dimension Errors (Expected REJECT)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("bad_spec", ["invalid", "4_to_16", "abc-to-def", "4-to-"])
def test_reject_invalid_decoder_format(bad_spec):
    with pytest.raises(SchemaError, match="Invalid decoder specification format"):
        parse_decoder_spec(bad_spec)


def test_reject_decoder_dimension_zero():
    with pytest.raises(DecoderDimensionError, match="Decoder dimensions must be positive integers"):
        parse_decoder_spec("0-to-0")


def test_reject_decoder_dimension_power_of_two_mismatch():
    """Decoder 4-to-32 for 4 inputs is mathematically impossible."""
    with pytest.raises(DecoderDimensionError, match="Invalid decoder specification: 4-to-32 for 4 inputs"):
        parse_decoder_spec("4-to-32")


def test_reject_decoder_dimension_input_count_mismatch(valid_half_adder_routing):
    """Declared 2 inputs (A, B) but core_decoder specifies 3-to-8."""
    corrupted = dict(valid_half_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"]["core_decoder"] = "3-to-8_Active_High"
    with pytest.raises(DecoderDimensionError, match="Decoder input count mismatch"):
        validate_routing_dict(corrupted)


def test_reject_decoder_dimension_too_many_inputs(valid_full_adder_routing):
    """Declared 3 inputs but core_decoder specifies 2-to-4."""
    corrupted = dict(valid_full_adder_routing)
    corrupted["architecture"] = dict(corrupted["architecture"])
    corrupted["architecture"]["core_decoder"] = "2-to-4_Active_High"
    with pytest.raises(DecoderDimensionError, match="Decoder input count mismatch"):
        validate_routing_dict(corrupted)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Output Port & Pin Range Errors (Expected REJECT)
# ─────────────────────────────────────────────────────────────────────────────

def test_reject_unknown_routing_output(valid_half_adder_routing):
    corrupted = dict(valid_half_adder_routing)
    corrupted["automated_routing_matrix"] = {
        "output_OR_Sum": ["Y1", "Y2"],
        "output_OR_NonExistent": ["Y0"],
    }
    with pytest.raises(UnknownOutputError, match="Unknown routing output: 'output_OR_NonExistent'"):
        validate_routing_dict(corrupted)


@pytest.mark.parametrize("bad_pin", ["Y4", "Y16", "Y999", "Y100", "Y-1", "Yabc", "Z0", 123])
def test_reject_invalid_or_out_of_range_pin(valid_half_adder_routing, bad_pin):
    """In a 2-to-4 decoder, valid pins are strictly Y0..Y3."""
    corrupted = dict(valid_half_adder_routing)
    corrupted["automated_routing_matrix"] = {
        "output_OR_Sum": ["Y1", bad_pin],
        "output_OR_Cout": ["Y3"],
    }
    with pytest.raises(PinError):
        validate_routing_dict(corrupted)


def test_reject_duplicate_pin(valid_half_adder_routing):
    """Redundant wiring of Y1 twice to the same OR gate must be rejected."""
    corrupted = dict(valid_half_adder_routing)
    corrupted["automated_routing_matrix"] = {
        "output_OR_Sum": ["Y1", "Y2", "Y1"],
        "output_OR_Cout": ["Y3"],
    }
    with pytest.raises(DuplicatePinError, match="Duplicate pin 'Y1' in routing"):
        validate_routing_dict(corrupted)


def test_reject_non_list_routing_entry(valid_half_adder_routing):
    corrupted = dict(valid_half_adder_routing)
    corrupted["automated_routing_matrix"] = {
        "output_OR_Sum": "Y1 | Y2",  # Should be a list
        "output_OR_Cout": ["Y3"],
    }
    with pytest.raises(SchemaError, match="must be a list of Y-pin strings"):
        validate_routing_dict(corrupted)
