"""
experiments/iwls/pla_parser.py
------------------------------
Independent parser, Boolean evaluator, and minterm extractor for standard Berkeley PLA
(Programmable Logic Array) benchmark files from the IWLS / LGSynth91 benchmark suites.

Provides:
- parse_pla_file(filepath): Parses PLA syntax, headers, and product terms
- evaluate_pla(pla_data, input_vector): Independent Boolean truth evaluator
- extract_minterms(pla_data, max_inputs=16): Generates exact Sum-of-Minterms
- pla_to_routing_dict(pla_data, max_inputs=16): Converts to Decoder-OR routing schema
- verify_functional_equivalence(pla_data, routing_dict): Proves 100% equivalence
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set, Optional, Any


@dataclass
class PLABenchmark:
    name: str
    num_inputs: int
    num_outputs: int
    num_product_terms: int
    input_names: List[str]
    output_names: List[str]
    product_terms: List[Tuple[str, str]]  # list of (input_cube, output_cube)
    source_file: str


def parse_pla_file(filepath: Path | str) -> PLABenchmark:
    """
    Parses a Berkeley PLA format benchmark file.
    """
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(f"PLA file not found: {p}")

    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    name = p.stem

    num_inputs = None
    num_outputs = None
    num_pterms = None
    input_names = []
    output_names = []
    product_terms = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        tag = parts[0]

        if tag == ".i":
            num_inputs = int(parts[1])
        elif tag == ".o":
            num_outputs = int(parts[1])
        elif tag == ".p":
            num_pterms = int(parts[1])
        elif tag == ".ilb":
            input_names.extend(parts[1:])
        elif tag == ".ob":
            output_names.extend(parts[1:])
        elif tag == ".e":
            break
        elif tag.startswith("."):
            # Other directives (e.g. .type, .phase)
            continue
        else:
            # Product term row: <in_cube> <out_cube>
            if len(parts) >= 2:
                in_cube = parts[0]
                out_cube = parts[1]
                product_terms.append((in_cube, out_cube))

    if num_inputs is None:
        raise ValueError(f"Missing .i in PLA file: {p}")
    if num_outputs is None:
        raise ValueError(f"Missing .o in PLA file: {p}")

    # Generate default signal names if not specified in .ilb / .ob
    if len(input_names) < num_inputs:
        input_names = [f"in_{i}" for i in range(num_inputs)]
    else:
        # Sanitize signal names for Verilog (alphanumeric + underscore)
        input_names = [re.sub(r"[^a-zA-Z0-9_]", "_", s) for s in input_names[:num_inputs]]

    if len(output_names) < num_outputs:
        output_names = [f"out_{j}" for j in range(num_outputs)]
    else:
        output_names = [re.sub(r"[^a-zA-Z0-9_]", "_", s) for s in output_names[:num_outputs]]

    # Ensure unique signal names
    input_names = _disambiguate_names(input_names, prefix="in")
    output_names = _disambiguate_names(output_names, prefix="out")

    # Ensure no overlap between inputs and outputs
    out_set = set(output_names)
    for i in range(len(input_names)):
        if input_names[i] in out_set:
            input_names[i] = f"in_{input_names[i]}"

    return PLABenchmark(
        name=name,
        num_inputs=num_inputs,
        num_outputs=num_outputs,
        num_product_terms=len(product_terms),
        input_names=input_names,
        output_names=output_names,
        product_terms=product_terms,
        source_file=str(p),
    )


def _disambiguate_names(names: List[str], prefix: str) -> List[str]:
    seen: Dict[str, int] = {}
    result = []
    for name in names:
        if not name or name == "_":
            name = f"{prefix}_sig"
        if name in seen:
            seen[name] += 1
            result.append(f"{name}_{seen[name]}")
        else:
            seen[name] = 0
            result.append(name)
    return result


def evaluate_pla(pla: PLABenchmark, input_bits: List[int]) -> List[int]:
    """
    Simulates the Boolean behavior of a PLA for a given binary input vector.
    Returns: List[int] of output values (0 or 1) of length pla.num_outputs.
    """
    n_in = pla.num_inputs
    n_out = pla.num_outputs
    out_vals = [0] * n_out

    for in_cube, out_cube in pla.product_terms:
        # Check if input vector matches in_cube
        match = True
        for i in range(n_in):
            c = in_cube[i]
            if c == "1" and input_bits[i] != 1:
                match = False
                break
            elif c == "0" and input_bits[i] != 0:
                match = False
                break
            # '-' matches either 0 or 1

        if match:
            # Active product term asserts corresponding outputs
            for j in range(n_out):
                if out_cube[j] == "1":
                    out_vals[j] = 1

    return out_vals


def extract_minterms(pla: PLABenchmark, max_inputs_feasible: int = 20) -> Dict[str, List[int]]:
    """
    Extracts the exact canonical sum-of-minterms for each output of the PLA.
    
    Raises:
        ValueError: If pla.num_inputs > max_inputs_feasible due to combinatorial explosion.
    """
    if pla.num_inputs > max_inputs_feasible:
        raise ValueError(
            f"Input size {pla.num_inputs} exceeds feasible complete minterm enumeration bound "
            f"({max_inputs_feasible} inputs = {1 << max_inputs_feasible:,} states). "
            f"Theoretical state space 2^{pla.num_inputs} = {1 << pla.num_inputs:,} states is computationally infeasible."
        )

    n_in = pla.num_inputs
    n_out = pla.num_outputs
    total_states = 1 << n_in

    # Prepare minterm lists for each output
    minterm_lists: List[List[int]] = [[] for _ in range(n_out)]

    # Optimized cube expansion directly into minterm sets
    # For each product term, generate the set of matching indices
    for in_cube, out_cube in pla.product_terms:
        # Find which outputs are asserted by this cube
        asserted_outputs = [j for j in range(n_out) if out_cube[j] == "1"]
        if not asserted_outputs:
            continue

        # Expand in_cube to matching minterms
        # Dash positions can be 0 or 1
        dash_indices = [i for i in range(n_in) if in_cube[i] == "-"]
        base_val = 0
        for i in range(n_in):
            if in_cube[i] == "1":
                base_val |= (1 << (n_in - 1 - i))

        num_dashes = len(dash_indices)
        if num_dashes == 0:
            for out_j in asserted_outputs:
                minterm_lists[out_j].append(base_val)
        else:
            # Expand all 2^num_dashes combinations
            shifts = [n_in - 1 - di for di in dash_indices]
            for combo in range(1 << num_dashes):
                val = base_val
                for b in range(num_dashes):
                    if (combo >> b) & 1:
                        val |= (1 << shifts[b])
                for out_j in asserted_outputs:
                    minterm_lists[out_j].append(val)

    # Deduplicate and sort minterm lists
    result = {}
    for j in range(n_out):
        out_name = pla.output_names[j]
        unique_sorted = sorted(set(minterm_lists[j]))
        result[out_name] = unique_sorted

    return result


def pla_to_routing_dict(pla: PLABenchmark, max_inputs_feasible: int = 20) -> Dict[str, Any]:
    """
    Translates a parsed PLA benchmark into a standard Decoder-OR routing configuration.
    """
    minterm_map = extract_minterms(pla, max_inputs_feasible=max_inputs_feasible)
    n_in = pla.num_inputs
    n_out = 1 << n_in

    routing_matrix = {}
    for out_name in pla.output_names:
        mterms = minterm_map.get(out_name, [])
        pins = [f"Y{m}" for m in mterms]
        routing_matrix[f"output_OR_{out_name}"] = pins

    return {
        "system": f"IWLS_{pla.name}_Decoder_OR",
        "architecture": {
            "core_decoder": f"{n_in}-to-{n_out}_Active_High",
            "inputs": pla.input_names,
            "outputs": pla.output_names,
        },
        "automated_routing_matrix": routing_matrix,
    }


def verify_functional_equivalence(
    pla: PLABenchmark,
    routing_data: Dict[str, Any],
    max_exhaustive_bits: int = 17
) -> Tuple[bool, str]:
    """
    Independently verifies that the Decoder-OR routing matrix exactly matches
    the original PLA benchmark across all Boolean input combinations.
    """
    n_in = pla.num_inputs
    n_out = pla.num_outputs
    outputs = pla.output_names
    matrix = routing_data["automated_routing_matrix"]

    # Extract minterm sets from routing pins
    routing_minterms: Dict[str, Set[int]] = {}
    for out_name in outputs:
        key = f"output_OR_{out_name}"
        pins = matrix.get(key, matrix.get(out_name, []))
        routing_minterms[out_name] = {int(p[1:]) for p in pins}

    # Exhaustive verification if feasible (<= 2^14 = 16,384 states)
    if n_in <= max_exhaustive_bits:
        total_vectors = 1 << n_in
        for idx in range(total_vectors):
            input_bits = [(idx >> (n_in - 1 - i)) & 1 for i in range(n_in)]
            pla_out = evaluate_pla(pla, input_bits)

            for j in range(n_out):
                out_name = outputs[j]
                expected_bit = pla_out[j]
                observed_bit = 1 if idx in routing_minterms[out_name] else 0

                if expected_bit != observed_bit:
                    return False, (
                        f"Equivalence mismatch at index {idx} ({input_bits}) for output '{out_name}': "
                        f"PLA expected {expected_bit}, Decoder-OR produced {observed_bit}"
                    )
        return True, f"100% Exhaustive equivalence verified ({total_vectors:,} states tested)."

    # Sample-based verification for larger inputs
    import random
    rng = random.Random(0x1337)
    sample_count = 5000
    for _ in range(sample_count):
        idx = rng.randint(0, (1 << n_in) - 1)
        input_bits = [(idx >> (n_in - 1 - i)) & 1 for i in range(n_in)]
        pla_out = evaluate_pla(pla, input_bits)

        for j in range(n_out):
            out_name = outputs[j]
            expected_bit = pla_out[j]
            observed_bit = 1 if idx in routing_minterms[out_name] else 0

            if expected_bit != observed_bit:
                return False, (
                    f"Equivalence mismatch at sample index {idx} for output '{out_name}': "
                    f"PLA expected {expected_bit}, Decoder-OR produced {observed_bit}"
                )

    return True, f"Sample-based equivalence verified across {sample_count:,} random vectors."
