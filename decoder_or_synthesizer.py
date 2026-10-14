"""
decoder_or_synthesizer.py

Current implemented flow:

    benchmark_dataset.json
            -> select one or all circuits
            -> read minterms_map
            -> generate Decoder-OR routing JSON
            -> generate synthesizable Verilog

The truth-table and Boolean-expression adapters are preserved near the end of
this file as commented future work. They are intentionally disabled for the
current version of the research prototype.

Examples:
    python decoder_or_synthesizer.py --list
    python decoder_or_synthesizer.py --circuit Full_Adder
    python decoder_or_synthesizer.py --id 2 --emit verilog
    python decoder_or_synthesizer.py --all --output-dir generated
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


VERILOG_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


# ---------------------------------------------------------------------------
# Dataset loading and validation
# ---------------------------------------------------------------------------

def load_dataset(filepath: str | Path) -> dict[str, Any]:
    """Load benchmark_dataset.json and validate its root structure."""
    path = Path(filepath)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path.resolve()}")

    try:
        with path.open("r", encoding="utf-8") as file:
            dataset = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON at line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ) from error

    if not isinstance(dataset, dict):
        raise ValueError("The dataset root must be a JSON object.")

    if not isinstance(dataset.get("benchmarks"), list):
        raise ValueError("The dataset must contain a 'benchmarks' array.")

    return dataset


def validate_identifier(name: str, kind: str) -> None:
    """Check whether an input/output name is a valid Verilog identifier."""
    if not isinstance(name, str) or not VERILOG_IDENTIFIER.fullmatch(name):
        raise ValueError(
            f"{kind} name {name!r} is not a valid Verilog identifier."
        )


def validate_circuit_structure(circuit: dict[str, Any]) -> None:
    """Validate the common metadata of one benchmark circuit."""
    required_fields = (
        "id",
        "name",
        "num_inputs",
        "inputs",
        "num_outputs",
        "outputs",
        "minterms_map",
    )

    for field in required_fields:
        if field not in circuit:
            raise ValueError(
                f"Circuit {circuit.get('name', '<unknown>')!r} "
                f"is missing required field {field!r}."
            )

    name = circuit["name"]
    inputs = circuit["inputs"]
    outputs = circuit["outputs"]

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Circuit name must be a non-empty string.")

    if not isinstance(inputs, list) or not inputs:
        raise ValueError(f"{name}: 'inputs' must be a non-empty array.")

    if not isinstance(outputs, list) or not outputs:
        raise ValueError(f"{name}: 'outputs' must be a non-empty array.")

    if circuit["num_inputs"] != len(inputs):
        raise ValueError(
            f"{name}: num_inputs={circuit['num_inputs']} but "
            f"{len(inputs)} input names were provided."
        )

    if circuit["num_outputs"] != len(outputs):
        raise ValueError(
            f"{name}: num_outputs={circuit['num_outputs']} but "
            f"{len(outputs)} output names were provided."
        )

    if len(set(inputs)) != len(inputs):
        raise ValueError(f"{name}: duplicate input names are not allowed.")

    if len(set(outputs)) != len(outputs):
        raise ValueError(f"{name}: duplicate output names are not allowed.")

    overlap = set(inputs) & set(outputs)
    if overlap:
        raise ValueError(
            f"{name}: names used as both inputs and outputs: "
            f"{sorted(overlap)}"
        )

    for input_name in inputs:
        validate_identifier(input_name, "Input")

    for output_name in outputs:
        validate_identifier(output_name, "Output")

    bit_widths = circuit.get("input_bit_width", {})
    for input_name in inputs:
        width = bit_widths.get(input_name, 1)
        if width != 1:
            raise ValueError(
                f"{name}: only one-bit inputs are currently supported; "
                f"{input_name!r} has width {width}."
            )

    if not isinstance(circuit["minterms_map"], dict):
        raise ValueError(f"{name}: 'minterms_map' must be a JSON object.")

    if not isinstance(circuit.get("dont_cares_map", {}), dict):
        raise ValueError(f"{name}: 'dont_cares_map' must be a JSON object.")


def validate_minterm_list(
    minterms: Any,
    maximum_index: int,
    location: str,
) -> list[int]:
    """Validate, sort, and remove duplicates from a minterm list."""
    if not isinstance(minterms, list):
        raise ValueError(f"{location} must be an array.")

    normalized: list[int] = []

    for minterm in minterms:
        if isinstance(minterm, bool) or not isinstance(minterm, int):
            raise ValueError(
                f"{location}: minterm {minterm!r} must be an integer."
            )

        if not 0 <= minterm <= maximum_index:
            raise ValueError(
                f"{location}: minterm {minterm} is outside the valid "
                f"range 0..{maximum_index}."
            )

        normalized.append(minterm)

    return sorted(set(normalized))


def normalize_minterm_source(
    circuit: dict[str, Any],
) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    """Normalize the currently supported minterms_map input format."""
    validate_circuit_structure(circuit)

    name = circuit["name"]
    outputs = circuit["outputs"]
    maximum_index = (1 << circuit["num_inputs"]) - 1
    raw_minterms = circuit["minterms_map"]
    raw_dont_cares = circuit.get("dont_cares_map", {})

    unexpected_outputs = set(raw_minterms) - set(outputs)
    if unexpected_outputs:
        raise ValueError(
            f"{name}: minterms_map contains unknown outputs: "
            f"{sorted(unexpected_outputs)}"
        )

    unexpected_dont_cares = set(raw_dont_cares) - set(outputs)
    if unexpected_dont_cares:
        raise ValueError(
            f"{name}: dont_cares_map contains unknown outputs: "
            f"{sorted(unexpected_dont_cares)}"
        )

    minterms_map: dict[str, list[int]] = {}
    dont_cares_map: dict[str, list[int]] = {}

    for output_name in outputs:
        minterms = validate_minterm_list(
            raw_minterms.get(output_name, []),
            maximum_index,
            f"{name}.minterms_map.{output_name}",
        )
        dont_cares = validate_minterm_list(
            raw_dont_cares.get(output_name, []),
            maximum_index,
            f"{name}.dont_cares_map.{output_name}",
        )

        overlap = set(minterms) & set(dont_cares)
        if overlap:
            raise ValueError(
                f"{name}.{output_name}: minterms {sorted(overlap)} "
                "are present in both the ON-set and the don't-care set."
            )

        minterms_map[output_name] = minterms
        dont_cares_map[output_name] = dont_cares

    return minterms_map, dont_cares_map


# ---------------------------------------------------------------------------
# Decoder-OR routing generation
# ---------------------------------------------------------------------------

def generate_routing_schema(circuit: dict[str, Any]) -> dict[str, Any]:
    """Convert one minterm-based benchmark into a Decoder-OR routing IR."""
    minterms_map, dont_cares_map = normalize_minterm_source(circuit)

    number_of_inputs = circuit["num_inputs"]
    decoder_size = 1 << number_of_inputs

    routing_matrix = {
        f"output_OR_{output_name}": [
            f"Y{minterm}" for minterm in minterms_map[output_name]
        ]
        for output_name in circuit["outputs"]
    }

    return {
        "schema_version": "1.0",
        "system": "Decoder-OR_Synthesizer",
        "source": {
            "benchmark_id": circuit["id"],
            "circuit_name": circuit["name"],
            "source_format": "minterms",
        },
        "architecture": {
            "core_decoder": (
                f"{number_of_inputs}-to-{decoder_size}_Active_High"
            ),
            "bit_ordering": "MSB-first",
            "inputs": circuit["inputs"],
            "outputs": circuit["outputs"],
        },
        "normalized_minterms_map": minterms_map,
        "dont_cares_map": dont_cares_map,
        "automated_routing_matrix": routing_matrix,
    }


# ---------------------------------------------------------------------------
# Verilog generation
# ---------------------------------------------------------------------------

def make_safe_filename(name: str) -> str:
    """Convert a circuit name into a safe output filename."""
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name)
    return safe_name.strip("_") or "circuit"


def make_module_name(name: str) -> str:
    """Create a valid Verilog module name."""
    safe_name = re.sub(r"[^A-Za-z0-9_$]+", "_", name)

    if not safe_name or not (
        safe_name[0].isalpha() or safe_name[0] == "_"
    ):
        safe_name = f"circuit_{safe_name}"

    return f"decoder_or_{safe_name}"


def generate_verilog(routing_schema: dict[str, Any]) -> str:
    """Generate a complete combinational Verilog module."""
    source = routing_schema["source"]
    architecture = routing_schema["architecture"]
    minterms_map = routing_schema["normalized_minterms_map"]

    circuit_name = source["circuit_name"]
    inputs = architecture["inputs"]
    outputs = architecture["outputs"]
    number_of_inputs = len(inputs)
    decoder_size = 1 << number_of_inputs
    module_name = make_module_name(circuit_name)
    port_names = inputs + outputs

    lines = [
        "`timescale 1ns/1ps",
        "",
        "// Automatically generated by Decoder-OR Synthesizer",
        f"// Source circuit : {circuit_name}",
        f"// Decoder        : {number_of_inputs}-to-{decoder_size}",
        f"// Bit ordering   : {', '.join(inputs)} (MSB to LSB)",
        "",
        f"module {module_name} (",
    ]

    for position, port_name in enumerate(port_names):
        comma = "," if position < len(port_names) - 1 else ""
        lines.append(f"    {port_name}{comma}")

    lines.extend([");", ""])

    for input_name in inputs:
        lines.append(f"    input  wire {input_name};")

    for output_name in outputs:
        lines.append(f"    output wire {output_name};")

    lines.extend(
        [
            "",
            f"    wire [{number_of_inputs - 1}:0] decoder_index;",
            f"    wire [{decoder_size - 1}:0] Y;",
            "",
            "    // Input concatenation follows the dataset's MSB-first order.",
            f"    assign decoder_index = {{{', '.join(inputs)}}};",
            "",
            "    // Active-HIGH one-hot decoder.",
            f"    assign Y = {decoder_size}'d1 << decoder_index;",
            "",
            "    // Decoder outputs are connected to the target OR functions.",
        ]
    )

    for output_name in outputs:
        minterms = minterms_map[output_name]

        if minterms:
            expression = " | ".join(
                f"Y[{minterm}]" for minterm in minterms
            )
        else:
            expression = "1'b0"

        lines.append(f"    assign {output_name} = {expression};")

    lines.extend(["", "endmodule", ""])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Benchmark filtering
# ---------------------------------------------------------------------------

def list_benchmarks(dataset: dict[str, Any]) -> None:
    """Print the circuits available in the input dataset."""
    benchmarks = dataset["benchmarks"]

    if not benchmarks:
        print("The dataset contains no benchmarks.")
        return

    print("Available benchmarks")
    print("-" * 72)
    print(f"{'ID':<6}{'Name':<28}{'Inputs':<12}{'Outputs':<12}")
    print("-" * 72)

    for circuit in benchmarks:
        print(
            f"{str(circuit.get('id', '')):<6}"
            f"{str(circuit.get('name', '')):<28}"
            f"{str(circuit.get('num_inputs', '')):<12}"
            f"{str(circuit.get('num_outputs', '')):<12}"
        )


def find_circuit_by_name(
    dataset: dict[str, Any],
    circuit_name: str,
) -> dict[str, Any]:
    """Find one benchmark by name, case-insensitively."""
    requested_name = circuit_name.casefold()

    for circuit in dataset["benchmarks"]:
        if str(circuit.get("name", "")).casefold() == requested_name:
            return circuit

    available_names = [
        str(circuit.get("name", ""))
        for circuit in dataset["benchmarks"]
    ]
    raise ValueError(
        f"Circuit {circuit_name!r} was not found. "
        f"Available circuits: {available_names}"
    )


def find_circuit_by_id(
    dataset: dict[str, Any],
    circuit_id: int,
) -> dict[str, Any]:
    """Find one benchmark by numeric ID."""
    for circuit in dataset["benchmarks"]:
        if circuit.get("id") == circuit_id:
            return circuit

    available_ids = [
        circuit.get("id") for circuit in dataset["benchmarks"]
    ]
    raise ValueError(
        f"Circuit ID {circuit_id} was not found. "
        f"Available IDs: {available_ids}"
    )


def select_circuits(
    dataset: dict[str, Any],
    circuit_name: str | None,
    circuit_id: int | None,
    process_all: bool,
) -> list[dict[str, Any]]:
    """Apply the requested circuit filter."""
    if process_all:
        return dataset["benchmarks"]

    if circuit_name is not None:
        return [find_circuit_by_name(dataset, circuit_name)]

    if circuit_id is not None:
        return [find_circuit_by_id(dataset, circuit_id)]

    return []


# ---------------------------------------------------------------------------
# Output handling
# ---------------------------------------------------------------------------

def print_result(
    circuit: dict[str, Any],
    routing_schema: dict[str, Any],
    verilog_code: str,
    emit: str,
) -> None:
    """Print generated output to the terminal."""
    print("\n" + "=" * 78)
    print(
        f"[{circuit['id']}] {circuit['name']} | "
        f"{circuit['num_inputs']} inputs | "
        f"{circuit['num_outputs']} outputs"
    )
    print("=" * 78)

    if emit in {"json", "both"}:
        print("\n--- ROUTING JSON ---\n")
        print(json.dumps(routing_schema, indent=2, ensure_ascii=False))

    if emit in {"verilog", "both"}:
        print("\n--- VERILOG RTL ---\n")
        print(verilog_code)


def write_result(
    output_directory: Path,
    circuit: dict[str, Any],
    routing_schema: dict[str, Any],
    verilog_code: str,
    emit: str,
) -> None:
    """Write generated output to routing JSON and/or Verilog files."""
    output_directory.mkdir(parents=True, exist_ok=True)
    base_name = make_safe_filename(circuit["name"])

    if emit in {"json", "both"}:
        json_path = output_directory / f"{base_name}.routing.json"
        json_path.write_text(
            json.dumps(routing_schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"[WRITE] {json_path.resolve()}")

    if emit in {"verilog", "both"}:
        verilog_path = output_directory / f"{base_name}.v"
        verilog_path.write_text(verilog_code, encoding="utf-8")
        print(f"[WRITE] {verilog_path.resolve()}")


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read minterm benchmarks and generate Decoder-OR routing JSON "
            "and Verilog RTL."
        )
    )

    parser.add_argument(
        "--input",
        default="benchmark_dataset.json",
        help="Input dataset path (default: benchmark_dataset.json).",
    )

    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--list",
        action="store_true",
        help="List available benchmarks and exit.",
    )
    selection.add_argument(
        "--circuit",
        help="Select one benchmark by name, for example Full_Adder.",
    )
    selection.add_argument(
        "--id",
        type=int,
        dest="circuit_id",
        help="Select one benchmark by numeric ID.",
    )
    selection.add_argument(
        "--all",
        action="store_true",
        dest="process_all",
        help="Process every benchmark in the dataset.",
    )

    parser.add_argument(
        "--emit",
        choices=("json", "verilog", "both"),
        default="both",
        help="Choose the generated output type (default: both).",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Write generated files to this directory. If omitted, output "
            "is printed to the terminal."
        ),
    )

    return parser


def main() -> int:
    parser = create_argument_parser()
    arguments = parser.parse_args()

    try:
        dataset = load_dataset(arguments.input)

        if arguments.list:
            list_benchmarks(dataset)
            return 0

        selected_circuits = select_circuits(
            dataset=dataset,
            circuit_name=arguments.circuit,
            circuit_id=arguments.circuit_id,
            process_all=arguments.process_all,
        )

        if not selected_circuits:
            print(
                "No circuit was selected.\n"
                "Use --list to view the available circuits, then use one "
                "of:\n"
                "  --circuit <name>\n"
                "  --id <number>\n"
                "  --all"
            )
            return 0

        output_directory = (
            Path(arguments.output_dir)
            if arguments.output_dir
            else None
        )

        for circuit in selected_circuits:
            routing_schema = generate_routing_schema(circuit)
            verilog_code = generate_verilog(routing_schema)

            if output_directory is None:
                print_result(
                    circuit,
                    routing_schema,
                    verilog_code,
                    arguments.emit,
                )
            else:
                write_result(
                    output_directory,
                    circuit,
                    routing_schema,
                    verilog_code,
                    arguments.emit,
                )

        return 0

    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# ===========================================================================
# FUTURE FEATURE 1: TRUTH-TABLE INPUT ADAPTER (COMMENTED OUT)
# ===========================================================================
#
# This adapter can later normalize a complete truth table to the same
# minterms_map representation consumed by generate_routing_schema().
#
# Expected JSON schema:
#
# "truth_table": [
#   {
#     "inputs":  {"A": 0, "B": 0},
#     "outputs": {"Sum": 0, "Cout": 0}
#   },
#   {
#     "inputs":  {"A": 0, "B": 1},
#     "outputs": {"Sum": 1, "Cout": 0}
#   }
# ]
#
# Output values may be 0, 1, "X", or null. "X" and null represent don't-care.
#
# def input_values_to_index(
#     values: dict[str, int],
#     inputs: list[str],
# ) -> int:
#     index = 0
#
#     for input_name in inputs:
#         value = values[input_name]
#         if value not in (0, 1):
#             raise ValueError(
#                 f"Input {input_name!r} must have value 0 or 1."
#             )
#         index = (index << 1) | value
#
#     return index
#
#
# def normalize_truth_table_source(
#     circuit: dict[str, Any],
# ) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
#     name = circuit["name"]
#     inputs = circuit["inputs"]
#     outputs = circuit["outputs"]
#     truth_table = circuit.get("truth_table")
#     total_states = 1 << circuit["num_inputs"]
#
#     if not isinstance(truth_table, list):
#         raise ValueError(f"{name}: 'truth_table' must be an array.")
#
#     minterms_map = {output: [] for output in outputs}
#     dont_cares_map = {output: [] for output in outputs}
#     seen_indices: set[int] = set()
#
#     for row_number, row in enumerate(truth_table, start=1):
#         input_values = row.get("inputs")
#         output_values = row.get("outputs")
#
#         if not isinstance(input_values, dict):
#             raise ValueError(
#                 f"{name}.truth_table[{row_number}].inputs must be an object."
#             )
#
#         if not isinstance(output_values, dict):
#             raise ValueError(
#                 f"{name}.truth_table[{row_number}].outputs must be an object."
#             )
#
#         index = input_values_to_index(input_values, inputs)
#         if index in seen_indices:
#             raise ValueError(
#                 f"{name}: duplicate truth-table input state {index}."
#             )
#         seen_indices.add(index)
#
#         for output_name in outputs:
#             value = output_values[output_name]
#
#             if value == 1:
#                 minterms_map[output_name].append(index)
#             elif value == 0:
#                 pass
#             elif value is None or (
#                 isinstance(value, str)
#                 and value.upper() in {"X", "D", "DC"}
#             ):
#                 dont_cares_map[output_name].append(index)
#             else:
#                 raise ValueError(
#                     f"Invalid truth-table value {value!r}."
#                 )
#
#     missing_states = set(range(total_states)) - seen_indices
#     if missing_states:
#         raise ValueError(
#             f"{name}: truth table is missing states {sorted(missing_states)}."
#         )
#
#     return minterms_map, dont_cares_map


# ===========================================================================
# FUTURE FEATURE 2: BOOLEAN-EXPRESSION INPUT ADAPTER (COMMENTED OUT)
# ===========================================================================
#
# This adapter can later enumerate all 2^n input states and convert Boolean
# expressions into minterms_map. It should use a restricted AST evaluator and
# must never call eval() on user input.
#
# Expected JSON schema:
#
# "boolean_expressions": {
#   "Sum": "A XOR B XOR Cin",
#   "Cout": "(A AND B) OR (A AND Cin) OR (B AND Cin)"
# }
#
# The existing 'canonical_expressions' field should remain documentation only;
# it may contain equations with two equivalent forms and is not suitable as a
# direct parser input.
#
# import ast
#
#
# def index_to_input_values(
#     index: int,
#     inputs: list[str],
# ) -> dict[str, int]:
#     number_of_inputs = len(inputs)
#     return {
#         input_name: (
#             index >> (number_of_inputs - 1 - position)
#         ) & 1
#         for position, input_name in enumerate(inputs)
#     }
#
#
# def normalize_boolean_expression(expression: str) -> str:
#     result = expression.strip()
#     result = re.sub(r"\bXOR\b", "^", result, flags=re.IGNORECASE)
#     result = re.sub(r"\bAND\b", " and ", result, flags=re.IGNORECASE)
#     result = re.sub(r"\bOR\b", " or ", result, flags=re.IGNORECASE)
#     result = re.sub(r"\bNOT\b", " not ", result, flags=re.IGNORECASE)
#     result = re.sub(
#         r"\b([A-Za-z_][A-Za-z0-9_]*)'",
#         r"(not \1)",
#         result,
#     )
#     result = re.sub(r"!(?!=)", " not ", result)
#     return result.strip()
#
#
# def evaluate_boolean_ast(
#     node: ast.AST,
#     variables: dict[str, int],
# ) -> int:
#     if isinstance(node, ast.Expression):
#         return evaluate_boolean_ast(node.body, variables)
#
#     if isinstance(node, ast.Name):
#         if node.id not in variables:
#             raise ValueError(f"Unknown input variable {node.id!r}.")
#         return int(bool(variables[node.id]))
#
#     if isinstance(node, ast.Constant):
#         if node.value in (0, 1, False, True):
#             return int(bool(node.value))
#         raise ValueError(f"Invalid Boolean constant {node.value!r}.")
#
#     if isinstance(node, ast.UnaryOp):
#         operand = evaluate_boolean_ast(node.operand, variables)
#         if isinstance(node.op, (ast.Not, ast.Invert)):
#             return int(not operand)
#         raise ValueError("Unsupported unary Boolean operator.")
#
#     if isinstance(node, ast.BoolOp):
#         values = [
#             evaluate_boolean_ast(value, variables)
#             for value in node.values
#         ]
#         if isinstance(node.op, ast.And):
#             return int(all(values))
#         if isinstance(node.op, ast.Or):
#             return int(any(values))
#         raise ValueError("Unsupported Boolean operator.")
#
#     if isinstance(node, ast.BinOp):
#         left = evaluate_boolean_ast(node.left, variables)
#         right = evaluate_boolean_ast(node.right, variables)
#
#         if isinstance(node.op, ast.BitAnd):
#             return left & right
#         if isinstance(node.op, ast.BitOr):
#             return left | right
#         if isinstance(node.op, ast.BitXor):
#             return left ^ right
#         raise ValueError("Unsupported binary Boolean operator.")
#
#     raise ValueError(
#         f"Unsupported expression element: {type(node).__name__}"
#     )
#
#
# def normalize_boolean_source(
#     circuit: dict[str, Any],
# ) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
#     expressions = circuit.get("boolean_expressions")
#     inputs = circuit["inputs"]
#     outputs = circuit["outputs"]
#     total_states = 1 << circuit["num_inputs"]
#
#     if not isinstance(expressions, dict):
#         raise ValueError("'boolean_expressions' must be an object.")
#
#     compiled_expressions = {}
#     for output_name in outputs:
#         normalized = normalize_boolean_expression(
#             expressions[output_name]
#         )
#         compiled_expressions[output_name] = ast.parse(
#             normalized,
#             mode="eval",
#         )
#
#     minterms_map = {output: [] for output in outputs}
#
#     for index in range(total_states):
#         input_values = index_to_input_values(index, inputs)
#
#         for output_name in outputs:
#             result = evaluate_boolean_ast(
#                 compiled_expressions[output_name],
#                 input_values,
#             )
#             if result == 1:
#                 minterms_map[output_name].append(index)
#
#     dont_cares_map = {
#         output: circuit.get("dont_cares_map", {}).get(output, [])
#         for output in outputs
#     }
#
#     return minterms_map, dont_cares_map
#
#
# When these features are implemented, generate_routing_schema() can select an
# adapter and normalize every input form to the same minterms_map representation:
#
# if "minterms_map" in circuit:
#     minterms_map, dont_cares_map = normalize_minterm_source(circuit)
# elif "truth_table" in circuit:
#     minterms_map, dont_cares_map = normalize_truth_table_source(circuit)
# elif "boolean_expressions" in circuit:
#     minterms_map, dont_cares_map = normalize_boolean_source(circuit)
# else:
#     raise ValueError("No supported logic source was found.")
