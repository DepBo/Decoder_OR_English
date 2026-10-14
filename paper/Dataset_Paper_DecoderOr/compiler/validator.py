"""
compiler/validator.py
---------------------
Validation layer for Decoder-OR routing JSON / compiler input.
Ensures semantic correctness, schema compliance, decoder dimension consistency,
and pin range validity before downstream RTL synthesis.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set


class ValidationError(Exception):
    """Base class for all validation errors."""
    pass


class JSONSyntaxError(ValidationError):
    """Raised when the routing input cannot be parsed as valid JSON."""
    pass


class SchemaError(ValidationError):
    """Raised when required schema fields are missing or have incorrect types."""
    pass


class DecoderDimensionError(ValidationError):
    """Raised when decoder dimensions mismatch input signals or standard 2^n scaling."""
    pass


class PinError(ValidationError):
    """Raised when an invalid, malformed, or out-of-range decoder output pin is referenced."""
    pass


class DuplicatePinError(ValidationError):
    """Raised when duplicate decoder pins are routed to the same OR gate."""
    pass


class UnknownOutputError(ValidationError):
    """Raised when the routing matrix defines an output not declared in architecture."""
    pass


# Recognize Active_Low so it can be rejected with an explicit error instead of
# silently compiling it as Active_High.
DECODER_PATTERN = re.compile(
    r"^(\d+)-to-(\d+)(?:_(Active_High|Active_Low))?$", re.IGNORECASE
)

# Regex pattern for valid decoder output pin, e.g. "Y0", "Y15"
PIN_PATTERN = re.compile(r"^Y(\d+)$")


def parse_decoder_spec(core_decoder: str) -> Tuple[int, int, str]:
    """
    Parses a decoder specification string.
    
    Returns:
        (num_inputs, num_outputs, polarity)
        Example: "4-to-16_Active_High" -> (4, 16, "Active_High")
    
    Raises:
        SchemaError: If the format or decoder polarity is unsupported.
        DecoderDimensionError: If num_outputs != 2^num_inputs.
    """
    if not isinstance(core_decoder, str) or not core_decoder.strip():
        raise SchemaError("[ERROR] 'core_decoder' must be a non-empty string.")

    match = DECODER_PATTERN.match(core_decoder.strip())
    if not match:
        raise SchemaError(
            f"[ERROR] Invalid decoder specification format: '{core_decoder}'. "
            f"Expected format '<N>-to-<M>' or '<N>-to-<M>_Active_High'."
        )

    n_inputs = int(match.group(1))
    n_outputs = int(match.group(2))
    requested_polarity = match.group(3)
    if requested_polarity and requested_polarity.lower() != "active_high":
        raise SchemaError(
            f"[ERROR] Unsupported decoder polarity '{requested_polarity}'. "
            "This compiler only supports Active_High Decoder-OR; Active_Low is not implemented."
        )
    # The suffix is optional for existing JSON files and defaults to Active_High.
    polarity = "Active_High"

    if n_inputs <= 0 or n_outputs <= 0:
        raise DecoderDimensionError(
            f"[ERROR] Decoder dimensions must be positive integers: got {n_inputs}-to-{n_outputs}."
        )

    expected_outputs = 1 << n_inputs  # 2^n
    if n_outputs != expected_outputs:
        raise DecoderDimensionError(
            f"[ERROR] Invalid decoder specification: {n_inputs}-to-{n_outputs} for {n_inputs} inputs. "
            f"Expected 2^{n_inputs} = {expected_outputs} decoder outputs."
        )

    return n_inputs, n_outputs, polarity


def validate_routing_dict(data: Any) -> Dict[str, Any]:
    """
    Validates a Decoder-OR routing dictionary against the specification.
    
    Returns:
        Normalized dictionary with verified structure and metadata.
        
    Raises:
        ValidationError (or subclasses) with explicit error messages.
    """
    if not isinstance(data, dict):
        raise SchemaError("[ERROR] Root routing configuration must be a JSON object (dictionary).")

    # 1. Required top-level fields
    for field in ("system", "architecture", "automated_routing_matrix"):
        if field not in data:
            raise SchemaError(f"[ERROR] Missing required field: '{field}'")

    system_name = data["system"]
    if not isinstance(system_name, str) or not system_name.strip():
        raise SchemaError("[ERROR] 'system' must be a non-empty string identifier.")

    arch = data["architecture"]
    if not isinstance(arch, dict):
        raise SchemaError("[ERROR] 'architecture' must be a JSON object (dictionary).")

    # 2. Required architecture fields
    for field in ("core_decoder", "inputs", "outputs"):
        if field not in arch:
            raise SchemaError(f"[ERROR] Missing required architecture field: '{field}'")

    # Unknown architecture modes must not be silently ignored by the OR-only
    # generator (e.g. a requested NAND/POS mode would otherwise emit OR RTL).
    supported_arch_fields = {"core_decoder", "inputs", "outputs", "bit_ordering"}
    unsupported_fields = set(arch) - supported_arch_fields
    if unsupported_fields:
        raise SchemaError(
            f"[ERROR] Unsupported architecture field(s): {sorted(unsupported_fields)}. "
            "This compiler only supports active-high Decoder-OR routing."
        )
    if "bit_ordering" in arch and arch["bit_ordering"] != "MSB-first":
        raise SchemaError(
            "[ERROR] Unsupported bit_ordering. This compiler only supports 'MSB-first'."
        )

    inputs = arch["inputs"]
    outputs = arch["outputs"]

    if not isinstance(inputs, list) or len(inputs) == 0:
        raise SchemaError("[ERROR] 'inputs' must be a non-empty list of signal names.")
    if not isinstance(outputs, list) or len(outputs) == 0:
        raise SchemaError("[ERROR] 'outputs' must be a non-empty list of signal names.")

    # Validate signal name uniqueness and format
    input_set = set()
    for sig in inputs:
        if not isinstance(sig, str) or not sig.strip():
            raise SchemaError(f"[ERROR] Invalid input signal name: {repr(sig)}. Must be a non-empty string.")
        if sig in input_set:
            raise SchemaError(f"[ERROR] Duplicate input signal declared: '{sig}'")
        input_set.add(sig)

    output_set = set()
    for sig in outputs:
        if not isinstance(sig, str) or not sig.strip():
            raise SchemaError(f"[ERROR] Invalid output signal name: {repr(sig)}. Must be a non-empty string.")
        if sig in output_set:
            raise SchemaError(f"[ERROR] Duplicate output signal declared: '{sig}'")
        output_set.add(sig)

    overlap = input_set.intersection(output_set)
    if overlap:
        raise SchemaError(f"[ERROR] Signal name conflict between inputs and outputs: {sorted(overlap)}")

    # 3. Validate Decoder dimensions
    core_decoder_str = arch["core_decoder"]
    n_inputs, n_outputs, polarity = parse_decoder_spec(core_decoder_str)

    if len(inputs) != n_inputs:
        raise DecoderDimensionError(
            f"[ERROR] Decoder input count mismatch: decoder '{core_decoder_str}' specifies "
            f"{n_inputs} inputs, but 'inputs' list has {len(inputs)} pins ({inputs})."
        )

    # 4. Validate routing matrix
    matrix = data["automated_routing_matrix"]
    if not isinstance(matrix, dict):
        raise SchemaError("[ERROR] 'automated_routing_matrix' must be a JSON object (dictionary).")

    normalized_routing: Dict[str, List[str]] = {}
    valid_pins = {f"Y{i}" for i in range(n_outputs)}

    # Map each routing key to the declared output
    for port_key, pins in matrix.items():
        if not isinstance(port_key, str):
            raise SchemaError(f"[ERROR] Routing matrix port name must be a string: {repr(port_key)}")

        # Normalize port key: e.g. "output_OR_Sum" -> "Sum", or "Sum" -> "Sum"
        if port_key.startswith("output_OR_"):
            target_out = port_key[len("output_OR_"):]
        else:
            target_out = port_key

        if target_out not in output_set:
            raise UnknownOutputError(
                f"[ERROR] Unknown routing output: '{port_key}'. "
                f"Does not match any declared output in {list(outputs)}."
            )

        if not isinstance(pins, list):
            raise SchemaError(f"[ERROR] Routing entry for '{port_key}' must be a list of Y-pin strings.")

        seen_pins: Set[str] = set()
        normalized_pins: List[str] = []

        for pin in pins:
            if not isinstance(pin, str):
                raise PinError(f"[ERROR] Invalid pin type in '{port_key}': {repr(pin)}. Expected string (e.g. 'Y0').")

            pin_clean = pin.strip()
            pin_match = PIN_PATTERN.match(pin_clean)
            if not pin_match:
                raise PinError(
                    f"[ERROR] Invalid decoder output pin format: '{pin}'. "
                    f"Must match format 'Y<index>' where 0 <= index < {n_outputs}."
                )

            pin_idx = int(pin_match.group(1))
            if pin_idx < 0 or pin_idx >= n_outputs:
                raise PinError(
                    f"[ERROR] Invalid decoder output pin: '{pin}'. "
                    f"Pin index {pin_idx} is out of range for {n_inputs}-to-{n_outputs} decoder (valid: Y0..Y{n_outputs - 1})."
                )

            if pin_clean in seen_pins:
                raise DuplicatePinError(
                    f"[ERROR] Duplicate pin '{pin_clean}' in routing for '{port_key}'. "
                    f"Redundant decoder connection is not permitted."
                )

            seen_pins.add(pin_clean)
            normalized_pins.append(pin_clean)

        normalized_routing[target_out] = normalized_pins

    # Ensure all declared outputs have routing entries (if omitted, default to empty list)
    for out_name in outputs:
        if out_name not in normalized_routing:
            normalized_routing[out_name] = []

    return {
        "system": system_name,
        "core_decoder": core_decoder_str,
        "num_inputs": n_inputs,
        "num_decoder_outputs": n_outputs,
        "polarity": polarity,
        "inputs": inputs,
        "outputs": outputs,
        "routing": normalized_routing,
        "raw": data,
    }


def validate_routing_json_string(json_str: str) -> Dict[str, Any]:
    """
    Validates a JSON string as a Decoder-OR routing configuration.
    
    Raises:
        JSONSyntaxError: If JSON syntax is invalid or string is empty.
        ValidationError: If schema / dimension rules fail.
    """
    if not isinstance(json_str, str) or not json_str.strip():
        raise JSONSyntaxError("[ERROR] Empty JSON content provided.")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise JSONSyntaxError(f"[ERROR] Malformed JSON syntax: {e.msg} (line {e.lineno}, col {e.colno})") from e

    return validate_routing_dict(data)


def validate_routing_file(filepath: Path | str) -> Dict[str, Any]:
    """
    Reads a file and validates it as a Decoder-OR routing configuration.
    
    Raises:
        FileNotFoundError: If file does not exist.
        JSONSyntaxError: If file is empty or malformed.
        ValidationError: If validation rules fail.
    """
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(f"[ERROR] Routing configuration file not found: {p}")

    content = p.read_text(encoding="utf-8")
    return validate_routing_json_string(content)
