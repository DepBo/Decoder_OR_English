"""
scripts/export_benchmark_routing.py
-----------------------------------
Converts all 5 canonical benchmark circuits from benchmark_dataset.json
into standard Decoder-OR routing JSON files under benchmarks_routing/.
"""

import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from compiler.generator import benchmark_to_routing_dict
from compiler.validator import validate_routing_dict


def export_all():
    in_file = _REPO_ROOT / "benchmark_dataset.json"
    out_dir = _REPO_ROOT / "benchmarks_routing"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(in_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    for circuit in dataset["benchmarks"]:
        routing_obj = benchmark_to_routing_dict(circuit)
        # Validate to ensure 100% schema compliance
        validate_routing_dict(routing_obj)

        out_path = out_dir / f"{circuit['name']}.json"
        with open(out_path, "w", encoding="utf-8") as out_f:
            json.dump(routing_obj, out_f, indent=2)

        print(f"[OK] Exported routing JSON: {out_path.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    export_all()
