"""
scripts/test_yosys_decoders.py
------------------------------
Tests Yosys synthesis sanity on 4-to-16, 6-to-64, and 16-to-65536 decoders.
"""

import subprocess
from pathlib import Path

def test_decoder(bits_in: int, name: str):
    num_out = 1 << bits_in
    verilog = f"""
module dec_{name} (
    input  wire [{bits_in-1}:0] in,
    output wire [{num_out-1}:0] Y
);
    assign Y = {num_out}'b1 << in;
endmodule
"""
    v_path = Path(f"/tmp/dec_{name}.v")
    ys_script = Path(f"/tmp/dec_{name}.ys")
    
    cmd_write = f"cat > {v_path} << 'EOF'\n{verilog}\nEOF\n"
    subprocess.run(["wsl", "-e", "bash", "-c", cmd_write], check=True)
    
    ys_content = f"""
read_verilog -sv {v_path}
hierarchy -top dec_{name}
proc
check
opt
stat
"""
    cmd_ys_write = f"cat > {ys_script} << 'EOF'\n{ys_content}\nEOF\n"
    subprocess.run(["wsl", "-e", "bash", "-c", cmd_ys_write], check=True)
    
    print(f"\n--- Testing dec_{name} ({bits_in}-to-{num_out}) in Yosys ---")
    res = subprocess.run(["wsl", "-e", "bash", "-c", f"yosys -s {ys_script}"], capture_output=True, text=True)
    print(f"Exit code: {res.returncode}")
    lines = res.stdout.splitlines()
    for l in lines:
        if any(k in l for k in ["Warning", "ERROR", "Checking module", "Number of cells", "Chip area", "hierarchy"]):
            print(f"  {l}")
    if res.returncode != 0:
        print("STDERR:\n" + res.stderr[:1000])

if __name__ == "__main__":
    test_decoder(4, "4to16")
    test_decoder(6, "6to64")
    # For 16-to-65536, let's see how Yosys handles it
    test_decoder(16, "16to65536")
