"""
experiments/generate_plots.py
-----------------------------
Generates publication-quality figures from actual CSV results for the paper:
'Realizing Arbitrary Logic Functions Using Decoders and OR Gates for Automated Logic Synthesis'

Rules:
- Python + matplotlib only (no seaborn)
- Each figure is a separate plot
- Standard matplotlib styling (no custom styles/themes)
- Clear axis labels, units, legends, and figure titles
- Saves both PNG and PDF formats
"""

import os
import sys
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional

# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_csv_data(filepath: Path) -> List[Dict[str, Any]]:
    """Load CSV into a list of row dicts."""
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def generate_all_figures(results_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
    if results_dir is None:
        results_dir = REPO_ROOT / "experiments" / "physical_validation" / "results"
    if output_dir is None:
        output_dir = REPO_ROOT / "results" / "figures"

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    timing_csv = results_dir / "physical_timing_results.csv"
    buffer_csv = results_dir / "buffer_insertion_results.csv"
    spice_fanout_csv = results_dir / "spice_fanout_results.csv"
    spice_buffer_csv = results_dir / "spice_buffer_results.csv"

    timing_data = load_csv_data(timing_csv)
    buffer_data = load_csv_data(buffer_csv)
    spice_fo_data = load_csv_data(spice_fanout_csv)
    spice_buf_data = load_csv_data(spice_buffer_csv)

    print(f"Generating publication-quality figures into: {output_dir}")

    # -----------------------------------------------------------------
    # Figure 1: Fan-out vs unbuffered delay (STA)
    # -----------------------------------------------------------------
    unbuf_timing = [r for r in timing_data if r.get("configuration") == "unbuffered"]
    buf_timing = [r for r in timing_data if r.get("configuration") == "buffered_repaired"]

    if unbuf_timing:
        plt.figure(figsize=(7, 5))
        fo = [int(r["fanout"]) for r in unbuf_timing]
        unbuf_d = [float(r["delay_ps"]) for r in unbuf_timing]
        plt.plot(fo, unbuf_d, marker='o', linewidth=2, label="Unbuffered Path Delay (STA)")
        plt.xlabel("Decoder Output Fan-out (N)")
        plt.ylabel("Propagation Delay (ps)")
        plt.title("Figure 1: Fan-out vs Unbuffered Delay (SkyWater 130nm HD)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig1_fanout_vs_unbuffered_delay.png", dpi=300)
        plt.savefig(output_dir / "fig1_fanout_vs_unbuffered_delay.pdf")
        plt.close()
        print("  [OK] Saved fig1_fanout_vs_unbuffered_delay (.png, .pdf)")

    # -----------------------------------------------------------------
    # Figure 2: Fan-out vs buffered delay (STA)
    # -----------------------------------------------------------------
    if buf_timing:
        plt.figure(figsize=(7, 5))
        fo = [int(r["fanout"]) for r in buf_timing]
        buf_d = [float(r["delay_ps"]) for r in buf_timing]
        plt.plot(fo, buf_d, marker='s', linewidth=2, label="Buffered / Repaired Delay (STA)")
        plt.xlabel("Decoder Output Fan-out (N)")
        plt.ylabel("Propagation Delay (ps)")
        plt.title("Figure 2: Fan-out vs Buffered Delay (SkyWater 130nm HD)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig2_fanout_vs_buffered_delay.png", dpi=300)
        plt.savefig(output_dir / "fig2_fanout_vs_buffered_delay.pdf")
        plt.close()
        print("  [OK] Saved fig2_fanout_vs_buffered_delay (.png, .pdf)")

    # -----------------------------------------------------------------
    # Figure 3: Fan-out vs number of inserted buffers
    # -----------------------------------------------------------------
    if buffer_data:
        plt.figure(figsize=(7, 5))
        fo = [int(r["fanout"]) for r in buffer_data]
        n_buf = [int(r["num_buffers_inserted"]) for r in buffer_data]
        plt.step(fo, n_buf, where='mid', marker='^', linewidth=2, label="Inserted Buffer Count")
        plt.xlabel("Decoder Output Fan-out (N)")
        plt.ylabel("Number of Inserted Standard-Cell Buffers")
        plt.title("Figure 3: Fan-out vs Number of Inserted Buffers (ABC Synthesis)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig3_fanout_vs_inserted_buffers.png", dpi=300)
        plt.savefig(output_dir / "fig3_fanout_vs_inserted_buffers.pdf")
        plt.close()
        print("  [OK] Saved fig3_fanout_vs_inserted_buffers (.png, .pdf)")

    # -----------------------------------------------------------------
    # Figure 4: Fan-out vs rise time (SPICE)
    # -----------------------------------------------------------------
    if spice_fo_data and spice_buf_data:
        plt.figure(figsize=(7, 5))
        # Note: Unbuffered N=64 has incomplete switching (trise undefined / 0)
        fo_u = [int(r["fanout"]) for r in spice_fo_data if float(r["trise_ps"]) > 0]
        trise_u = [float(r["trise_ps"]) for r in spice_fo_data if float(r["trise_ps"]) > 0]
        fo_b = [int(r["fanout"]) for r in spice_buf_data]
        trise_b = [float(r["trise_ps"]) for r in spice_buf_data]

        plt.plot(fo_u, trise_u, marker='o', linewidth=2, label="Unbuffered (N=64 Incomplete)")
        plt.plot(fo_b, trise_b, marker='s', linewidth=2, label="Buffered (2-Stage Driver)")
        plt.xlabel("Fan-out Load Count (N)")
        plt.ylabel("10% - 90% Rise Time (ps)")
        plt.title("Figure 4: Fan-out vs 10%-90% Rise Time (BSIM4 130nm SPICE)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig4_fanout_vs_rise_time.png", dpi=300)
        plt.savefig(output_dir / "fig4_fanout_vs_rise_time.pdf")
        plt.close()
        print("  [OK] Saved fig4_fanout_vs_rise_time (.png, .pdf)")

    # -----------------------------------------------------------------
    # Figure 5: Fan-out vs fall time (SPICE)
    # -----------------------------------------------------------------
    if spice_fo_data and spice_buf_data:
        plt.figure(figsize=(7, 5))
        fo_u = [int(r["fanout"]) for r in spice_fo_data if float(r["tfall_ps"]) > 0]
        tfall_u = [float(r["tfall_ps"]) for r in spice_fo_data if float(r["tfall_ps"]) > 0]
        fo_b = [int(r["fanout"]) for r in spice_buf_data]
        tfall_b = [float(r["tfall_ps"]) for r in spice_buf_data]

        plt.plot(fo_u, tfall_u, marker='o', linewidth=2, label="Unbuffered (N=64 Incomplete)")
        plt.plot(fo_b, tfall_b, marker='s', linewidth=2, label="Buffered (2-Stage Driver)")
        plt.xlabel("Fan-out Load Count (N)")
        plt.ylabel("90% - 10% Fall Time (ps)")
        plt.title("Figure 5: Fan-out vs 90%-10% Fall Time (BSIM4 130nm SPICE)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig5_fanout_vs_fall_time.png", dpi=300)
        plt.savefig(output_dir / "fig5_fanout_vs_fall_time.pdf")
        plt.close()
        print("  [OK] Saved fig5_fanout_vs_fall_time (.png, .pdf)")

    # -----------------------------------------------------------------
    # Figure 6: Fan-out vs SPICE propagation delay
    # -----------------------------------------------------------------
    if spice_fo_data:
        plt.figure(figsize=(7, 5))
        fo = [int(r["fanout"]) for r in spice_fo_data]
        tphl = [float(r["tphl_ps"]) for r in spice_fo_data]
        tplh = [float(r["tplh_ps"]) for r in spice_fo_data]
        tp_avg = [float(r["tp_avg_ps"]) for r in spice_fo_data]

        plt.plot(fo, tphl, marker='v', linestyle='--', label="tpHL (High-to-Low Delay)")
        plt.plot(fo, tplh, marker='^', linestyle='--', label="tpLH (Low-to-High Delay)")
        plt.plot(fo, tp_avg, marker='o', linewidth=2, label="tp,avg (Average Propagation Delay)")
        plt.xlabel("Fan-out Load Count (N)")
        plt.ylabel("Propagation Delay (ps)")
        plt.title("Figure 6: Fan-out vs SPICE Propagation Delay (Unbuffered)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig6_fanout_vs_spice_propagation_delay.png", dpi=300)
        plt.savefig(output_dir / "fig6_fanout_vs_spice_propagation_delay.pdf")
        plt.close()
        print("  [OK] Saved fig6_fanout_vs_spice_propagation_delay (.png, .pdf)")

    # -----------------------------------------------------------------
    # Figure 7: Buffered vs unbuffered SPICE delay
    # -----------------------------------------------------------------
    if spice_fo_data and spice_buf_data:
        plt.figure(figsize=(7, 5))
        fo_u = [int(r["fanout"]) for r in spice_fo_data]
        tp_u = [float(r["tp_avg_ps"]) for r in spice_fo_data]
        fo_b = [int(r["fanout"]) for r in spice_buf_data]
        tp_b = [float(r["tp_avg_ps"]) for r in spice_buf_data]

        plt.plot(fo_u, tp_u, marker='o', linewidth=2, label="Unbuffered tp,avg")
        plt.plot(fo_b, tp_b, marker='s', linewidth=2, label="Buffered tp,avg (2-Stage Driver)")
        plt.xlabel("Fan-out Load Count (N)")
        plt.ylabel("Average Propagation Delay (ps)")
        plt.title("Figure 7: Buffered vs Unbuffered SPICE Delay Comparison")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig7_buffered_vs_unbuffered_spice_delay.png", dpi=300)
        plt.savefig(output_dir / "fig7_buffered_vs_unbuffered_spice_delay.pdf")
        plt.close()
        print("  [OK] Saved fig7_buffered_vs_unbuffered_spice_delay (.png, .pdf)")

    # -----------------------------------------------------------------
    # Figure 8: Fan-out vs dynamic energy
    # -----------------------------------------------------------------
    if spice_fo_data and spice_buf_data:
        plt.figure(figsize=(7, 5))
        fo_u = [int(r["fanout"]) for r in spice_fo_data]
        e_u = [float(r["energy_fj"]) for r in spice_fo_data]
        fo_b = [int(r["fanout"]) for r in spice_buf_data]
        e_b = [float(r["energy_fj"]) for r in spice_buf_data]

        plt.plot(fo_u, e_u, marker='o', linewidth=2, label="Unbuffered Switching Energy")
        plt.plot(fo_b, e_b, marker='s', linewidth=2, label="Buffered Switching Energy")
        plt.xlabel("Fan-out Load Count (N)")
        plt.ylabel("Dynamic Switching Energy per Cycle (fJ)")
        plt.title("Figure 8: Fan-out vs Dynamic Switching Energy (SPICE)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "fig8_fanout_vs_dynamic_energy.png", dpi=300)
        plt.savefig(output_dir / "fig8_fanout_vs_dynamic_energy.pdf")
        plt.close()
        print("  [OK] Saved fig8_fanout_vs_dynamic_energy (.png, .pdf)")

    # Also copy figures to results/final/figures if output_dir is results/figures
    final_fig_dir = REPO_ROOT / "results" / "final" / "figures"
    if output_dir != final_fig_dir:
        final_fig_dir.mkdir(parents=True, exist_ok=True)
        for ext in ("*.png", "*.pdf"):
            for f in output_dir.glob(ext):
                dest = final_fig_dir / f.name
                dest.write_bytes(f.read_bytes())


if __name__ == "__main__":
    generate_all_figures()
