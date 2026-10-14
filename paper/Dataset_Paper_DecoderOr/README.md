# Decoder-OR compiler and experiments

This subdirectory contains the validated Decoder-OR routing compiler, tests, and research experiments. It compiles routing JSON for an active-high decoder into synthesizable Verilog with a configurable maximum OR-node fan-in (default: four). The manuscript `main.tex` and the separate benchmark-selection front end `decoder_or_synthesizer.py` live two directories above (`../../`) in the same complete-project package.

## Directory map

| Path | Contents |
| --- | --- |
| `benchmark_dataset.json` | Five original minterm benchmarks. |
| `benchmarks_routing/` | Example routing JSON inputs for the compiler. |
| `compiler/validator.py` | JSON, decoder-dimension, polarity, output, and pin checks. |
| `compiler/or_tree.py` | Balanced OR-tree construction and equivalence checks. |
| `compiler/generator.py`, `compiler/cli.py` | Verilog generation and command-line entry point. |
| `tests/`, `verification/` | Unit tests, oracle-related checks, and mutation evidence. |
| `experiments/`, `results/` | Scalability, EDA, fan-out, SPICE experiments, and saved outputs. |
| `run_research_validation.py` | Optional research-validation runner. |

## Quick compiler example

From this directory:

```sh
python -m compiler.cli benchmarks_routing/Full_Adder.json -o Full_Adder.tree.v --max-fan-in 4
```

The input is routing JSON, **not** the five-circuit `benchmark_dataset.json`. Without `-o`, the generated Verilog is printed to the terminal. The compiler validates its input before emitting RTL. For an end-to-end benchmark selection and routing-JSON generation example, see `../../README.md` at the complete-project root.

## Tests and optional EDA runs

Python 3.10+ is required. Install test dependencies and run the suite:

```sh
python -m pip install -r requirements.txt
python -m pytest -q
```

`python run_research_validation.py --all` additionally attempts the research experiments. Yosys/ABC, Icarus, Verilator, ngspice, and physical-design tools are separate external dependencies; `requirements.txt` does not install them. Individual experiment READMEs give more detail. Recorded evidence is kept under `results/` and `verification/`; a saved CSV or report is not a substitute for rerunning an experiment in a documented environment.

## Scope and caveats

Only active-high Decoder-OR/SOP routing is supported. Explicit active-low and unsupported NAND/POS settings are rejected; Boolean-expression and truth-table input modes are not part of this compiler. A balanced RTL OR-tree does not guarantee lower post-synthesis delay. Buffer insertion is handled by downstream mapping, not by this Python compiler. The single-decoder representation grows exponentially with input width, and no post-layout timing or DRC closure is claimed.
