# Decoder-OR paper and source package

Complete-project repository: <https://github.com/DepBo/Decoder_OR_English>. The earlier dataset release is preserved at <https://github.com/DepBo/Dataset_Paper_DecoderOr> for provenance.

[Read the paper (PDF)](Realizing_Arbitrary_Logic_Functions_Using_Decoders_and_OR_Gates_for_Automated_Logic_Synthesis.pdf)

This folder contains the manuscript and source used to study active-high Decoder-OR implementations of explicitly specified minterm functions. The current workflow has two separate Python stages: a benchmark front end creates routing JSON, then the compiler creates bounded-fan-in OR-tree Verilog. The front end can also emit a simpler flat-OR Verilog reference.

## Start here

| Path | Purpose |
| --- | --- |
| `Realizing_Arbitrary_Logic_Functions_Using_Decoders_and_OR_Gates_for_Automated_Logic_Synthesis.pdf` | Readable paper PDF. |
| `main.tex` | Paper source; this is the manuscript to compile and submit. |
| `benchmark_dataset.json` | Five minterm-based combinational benchmarks. |
| `decoder_or_synthesizer.py` | Selects a benchmark and emits routing JSON and/or flat-OR Verilog. |
| `verify_dataset.py` | Independent oracle for the original five benchmarks. |
| `paper/Dataset_Paper_DecoderOr/compiler/` | Routing JSON validation and OR-tree Verilog generation. |
| `paper/Dataset_Paper_DecoderOr/tests/`, `verification/` | Unit, equivalence, and mutation tests. |
| `paper/Dataset_Paper_DecoderOr/experiments/`, `results/` | Research scripts and saved measurements. |

The local `readme.txt` is Springer's LNCS template documentation, not this project's guide.

## Generate OR-tree Verilog for one circuit

Run these commands from this folder (the paths work with Python on Windows and Linux):

```sh
python decoder_or_synthesizer.py --list
python decoder_or_synthesizer.py --circuit Full_Adder --emit json --output-dir generated
cd paper/Dataset_Paper_DecoderOr
python -m compiler.cli ../../generated/Full_Adder.routing.json -o ../../generated/Full_Adder.tree.v --max-fan-in 4
```

The first stage writes `generated/Full_Adder.routing.json`; the second writes `generated/Full_Adder.tree.v`. Input order is MSB-first (`A, B, Cin` means `101` selects decoder output `Y5`). To select another circuit, use `--list`, then `--circuit NAME` or `--id NUMBER`. `--all` intentionally processes all five. To generate the front end's *flat-OR* reference Verilog instead, run `python decoder_or_synthesizer.py --circuit Full_Adder --emit both --output-dir generated` from this top-level folder. Flat-OR output is not the OR-tree compiler output.

## Tests and research results

From `paper/Dataset_Paper_DecoderOr`, install the Python test dependencies with `python -m pip install -r requirements.txt`, then run `python -m pytest -q`. The compiler itself uses Python's standard library; Python 3.10 or newer is required by the source syntax. The optional full research runner is `python run_research_validation.py --all`; its EDA/SPICE stages additionally require the external tools and libraries described in the experiment subdirectories. Installing only `requirements.txt` does not install Yosys, ABC, Icarus, Verilator, ngspice, or physical-design tools. Saved measurements are under `results/`; the scale experiments are under `experiments/scalability/`.

## Supported scope

The user-facing front end currently accepts explicit minterm lists in JSON. Boolean-expression and truth-table input modes are not implemented. The OR-tree compiler supports active-high decoder outputs and OR/SOP routing; it rejects explicit active-low requests and unsupported NAND/POS architecture settings. The number of decoder states grows as `2^n`, and the research scripts impose a configurable capacity bound. OR-tree generation and downstream buffer insertion are different steps: the Python compiler generates OR-tree RTL, while technology-aware EDA tools may insert buffers later. The results do not establish post-layout timing or DRC closure.

## Before publishing the full package

This project is maintained as one Git repository rooted at this folder. The root `.gitignore` excludes private conference emails, working notes, caches, third-party cell-library copies, and large generated intermediates while retaining source code and compact evidence tables. The experiment scripts can regenerate excluded intermediates when their external tools and libraries are available. Both copies of `benchmark_dataset.json` contain the same parsed benchmark data; the nested copy is kept so existing experiment scripts continue to work.
