"""
compiler/generator.py
---------------------
Translates validated Decoder-OR routing JSON into synthesizable Verilog RTL.
Integrates the validation layer and balanced OR-tree decomposition.
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

from .validator import (
    validate_routing_dict,
    validate_routing_file,
    validate_routing_json_string,
    ValidationError,
)
from .or_tree import (
    decompose_or_tree,
    emit_or_tree_verilog,
    verify_or_tree_equivalence,
    ORTreeDecomposition,
)


def benchmark_to_routing_dict(benchmark_circuit: dict) -> Dict[str, Any]:
    """
    Converts a benchmark circuit specification from benchmark_dataset.json
    into a standardized Decoder-OR routing representation.

    Parameters:
        benchmark_circuit: A circuit dict from benchmark_dataset.json

    Returns:
        Decoder-OR routing configuration dictionary.
    """
    name = benchmark_circuit["name"]
    inputs = list(benchmark_circuit["inputs"])
    outputs = list(benchmark_circuit["outputs"])
    n_in = benchmark_circuit["num_inputs"]
    n_out = 1 << n_in

    routing_matrix = {}
    minterms_map = benchmark_circuit.get("minterms_map", {})

    for out_name in outputs:
        mterms = minterms_map.get(out_name, [])
        # Sort minterm indices for deterministic routing
        pins = [f"Y{m}" for m in sorted(mterms)]
        routing_matrix[f"output_OR_{out_name}"] = pins

    return {
        "system": f"{name}_Decoder_OR",
        "architecture": {
            "core_decoder": f"{n_in}-to-{n_out}_Active_High",
            "inputs": inputs,
            "outputs": outputs,
        },
        "automated_routing_matrix": routing_matrix,
    }


def generate_verilog_from_data(
    routing_data: Dict[str, Any],
    max_fan_in: int = 4,
    module_name: Optional[str] = None,
    verify_equivalence: bool = False
) -> str:
    """
    Compiles a routing configuration dictionary into synthesizable Verilog RTL.

    Validates the data first. If invalid, raises ValidationError and aborts.

    Parameters:
        routing_data: Parsed routing configuration dictionary.
        max_fan_in: Maximum permitted fan-in per OR gate (default: 4).
        module_name: Custom module name (defaults to system name).
        verify_equivalence: Whether to execute software verification during synthesis (default: False).

    Returns:
        Complete Verilog module as a string.
    """
    # 1. Validation Layer (Strict rejection of malformed or invalid inputs)
    validated = validate_routing_dict(routing_data)

    sys_name = module_name or validated["system"]
    # Sanitize module name for Verilog (replace hyphens/spaces with underscores)
    verilog_mod_name = sys_name.replace("-", "_").replace(" ", "_").replace(".", "_")
    # Verilog identifiers cannot begin with a decimal digit (IEEE 1364-2005 Section 2.7.1)
    if verilog_mod_name and verilog_mod_name[0].isdigit():
        verilog_mod_name = f"_{verilog_mod_name}"

    inputs: List[str] = validated["inputs"]
    outputs: List[str] = validated["outputs"]
    routing: Dict[str, List[str]] = validated["routing"]
    num_inputs: int = validated["num_inputs"]
    num_decoder_outputs: int = validated["num_decoder_outputs"]

    lines: List[str] = []
    lines.append("// ============================================================")
    lines.append(f"// Module: {verilog_mod_name}")
    lines.append("// Automatically synthesized by Decoder-OR Logic Compiler")
    lines.append(f"// Architecture: {validated['core_decoder']}, Max OR Fan-in: {max_fan_in}")
    lines.append("// ============================================================")
    lines.append(f"module {verilog_mod_name} (")

    # Port declarations
    port_decls: List[str] = []
    for inp in inputs:
        port_decls.append(f"    input  wire {inp}")
    for out in outputs:
        port_decls.append(f"    output wire {out}")
    lines.append(",\n".join(port_decls))
    lines.append(");")
    lines.append("")

    # Disambiguate internal decoder bus name if 'Y' collides with a port name
    bus_name = "dec_Y" if ("Y" in inputs or "Y" in outputs) else "Y"

    # Decoder output bus
    lines.append(f"    // Internal active-high core decoder ({num_inputs}-to-{num_decoder_outputs})")
    lines.append(f"    wire [{num_decoder_outputs - 1}:0] {bus_name};")
    
    # Decoder logic realization
    # Bit-vector concatenation of inputs: {A, B, Cin}
    input_concat = ", ".join(inputs)
    lines.append(f"    assign {bus_name} = {num_decoder_outputs}'b1 << {{{input_concat}}};")
    lines.append("")

    # OR-Tree decomposition for each output
    lines.append(f"    // Automated OR-tree Routing Matrix (Decomposed with max_fan_in <= {max_fan_in})")
    
    for out_name in outputs:
        pins = routing.get(out_name, [])
        prefix = f"{out_name}_or"
        
        # Perform OR-tree decomposition
        decomp = decompose_or_tree(pins, max_fan_in=max_fan_in, node_prefix=prefix)
        
        # Optional functional equivalence verification
        if verify_equivalence:
            verify_or_tree_equivalence(decomp)

        wire_decls, assign_stmts = emit_or_tree_verilog(decomp, output_signal=out_name, decoder_bus_name=bus_name)
        
        lines.append(f"    // Output: {out_name} (Fan-in: {decomp.original_fan_in}, Tree Depth: {decomp.tree_depth}, Gates: {decomp.number_of_internal_or_nodes})")
        for wd in wire_decls:
            lines.append(f"    {wd}")
        for ast in assign_stmts:
            lines.append(f"    {ast}")
        lines.append("")

    lines.append("endmodule")
    lines.append("")

    return "\n".join(lines)


def compile_file(
    input_json_path: str | Path,
    output_v_path: Optional[str | Path] = None,
    max_fan_in: int = 4
) -> str:
    """
    Compiles a Decoder-OR routing JSON file to Verilog RTL.

    Parameters:
        input_json_path: Path to routing JSON file.
        output_v_path: Optional output path for the .v file.
        max_fan_in: Maximum fan-in per OR gate (default: 4).

    Returns:
        Generated Verilog string.
    """
    validated = validate_routing_file(input_json_path)
    verilog_code = generate_verilog_from_data(validated["raw"], max_fan_in=max_fan_in)

    if output_v_path:
        out_p = Path(output_v_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(verilog_code, encoding="utf-8")

    return verilog_code


def main():
    """Command Line Interface for the Decoder-OR Compiler."""
    parser = argparse.ArgumentParser(
        description="Decoder-OR Logic Synthesizer & Verilog Generator"
    )
    parser.add_argument("input_json", help="Path to input Decoder-OR routing JSON file")
    parser.add_argument("-o", "--output", help="Path to output Verilog (.v) file")
    parser.add_argument(
        "--max-fan-in",
        type=int,
        default=4,
        help="Maximum permitted fan-in per OR gate (default: 4)"
    )

    args = parser.parse_args()

    try:
        verilog_text = compile_file(
            input_json_path=args.input_json,
            output_v_path=args.output,
            max_fan_in=args.max_fan_in,
        )
        if not args.output:
            print(verilog_text)
        else:
            print(f"[OK] Successfully synthesized Verilog to: {args.output}")
        sys.exit(0)

    except ValidationError as e:
        print(f"[ERROR] Validation failed: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Compilation error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
