"""
scripts/test_decoder_width.py
-----------------------------
Investigates Verilog expression sizing rules and decoder width semantics
for 4-to-16, 6-to-64, and 16-to-65536 decoders under:
1. IEEE 1364-2005 standard expression sizing rules (theoretical analysis)
2. Icarus Verilog (iverilog) simulation
3. Verilator lint and compilation
4. Yosys synthesis

Checks:
- Left-operand width: 1'b1 vs sized literal (N'b1) vs parameterized/array/indexed logic.
- Verifies one-hot property: exactly one Y[i] = 1, all other Y[j] = 0.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_wsl(cmd: str) -> subprocess.CompletedProcess:
    # Use bash -c in WSL
    return subprocess.run(["wsl", "-e", "bash", "-c", cmd], capture_output=True, text=True)

def test_verilog_snippet(verilog_code: str, top_module: str, test_name: str):
    print(f"\n{'='*60}\nRunning test: {test_name}\n{'='*60}")
    tmp_v = Path(f"experiments/eda/rtl/{top_module}.v")
    tmp_v.parent.mkdir(parents=True, exist_ok=True)
    tmp_v.write_text(verilog_code, encoding="utf-8")
    
    # WSL path
    # d:\Git\... -> /mnt/d/Git/...
    wsl_path = str(tmp_v.resolve()).replace('\\', '/').replace('d:', '/mnt/d').replace('D:', '/mnt/d')
    
    # 1. Test with iverilog
    vvp_out = str(tmp_v.with_suffix('.vvp')).replace('\\', '/').replace('d:', '/mnt/d').replace('D:', '/mnt/d')
    iv_cmd = f"iverilog -g2012 -s {top_module} {wsl_path} -o {vvp_out} && vvp {vvp_out}"
    res_iv = run_wsl(iv_cmd)
    print("--- Icarus Verilog Result ---")
    print(f"Exit code: {res_iv.returncode}")
    if res_iv.stdout:
        print("STDOUT:\n" + res_iv.stdout[:2000])
    if res_iv.stderr:
        print("STDERR:\n" + res_iv.stderr[:2000])

    # 2. Test with verilator --lint-only
    lint_cmd = f"verilator --lint-only -Wall -Wno-DECLFILENAME {wsl_path} --top-module {top_module}"
    res_vl = run_wsl(lint_cmd)
    print("--- Verilator Lint Result ---")
    print(f"Exit code: {res_vl.returncode}")
    if res_vl.stdout:
        print("STDOUT:\n" + res_vl.stdout[:2000])
    if res_vl.stderr:
        print("STDERR:\n" + res_vl.stderr[:2000])

    # 3. Test with yosys
    ys_cmd = f"yosys -p 'read_verilog -sv {wsl_path}; hierarchy -top {top_module}; proc; check'"
    res_ys = run_wsl(ys_cmd)
    print("--- Yosys Sanity Result ---")
    print(f"Exit code: {res_ys.returncode}")
    if res_ys.stdout:
        lines = [l for l in res_ys.stdout.splitlines() if "Warning" in l or "ERROR" in l or "Checking module" in l or "hierarchy" in l]
        print("Summary lines:\n" + "\n".join(lines[-15:]))
    if res_ys.stderr:
        print("STDERR:\n" + res_ys.stderr[:2000])

if __name__ == "__main__":
    # Test 1: 4-to-16 Unsafe 1'b1 shift vs Sized 16'b1 shift
    t1_code = """
module tb_shift_4to16;
    reg [3:0] in;
    wire [15:0] Y_unsafe;
    wire [15:0] Y_sized;

    assign Y_unsafe = 1'b1 << in;
    assign Y_sized  = 16'b1 << in;

    integer i;
    integer errors_unsafe = 0;
    integer errors_sized = 0;

    initial begin
        for (i = 0; i < 16; i = i + 1) begin
            in = i[3:0];
            #1;
            // Check one-hot for Y_unsafe
            if (Y_unsafe !== (16'b1 << i)) begin
                errors_unsafe = errors_unsafe + 1;
            end
            // Check one-hot for Y_sized
            if (Y_sized !== (16'b1 << i)) begin
                errors_sized = errors_sized + 1;
            end
        end
        $display("4-to-16 Results: errors_unsafe=%0d, errors_sized=%0d", errors_unsafe, errors_sized);
        $display("Sample in=1: Y_unsafe=%016b, Y_sized=%016b", (1'b1 << 4'd1), (16'b1 << 4'd1));
        if (errors_sized == 0) $display("PASS: 16'b1 << in is 100% correct one-hot.");
        else $display("FAIL: 16'b1 << in had errors.");
        $finish;
    end
endmodule
"""
    test_verilog_snippet(t1_code, "tb_shift_4to16", "4-to-16 Unsafe vs Sized")

    # Test 2: 6-to-64 Sized shift
    t2_code = """
module tb_shift_6to64;
    reg [5:0] in;
    wire [63:0] Y;

    assign Y = 64'b1 << in;

    integer i;
    integer errors = 0;

    initial begin
        for (i = 0; i < 64; i = i + 1) begin
            in = i[5:0];
            #1;
            if (Y[i] !== 1'b1 || $countones(Y) !== 1) begin
                errors = errors + 1;
            end
        end
        $display("6-to-64 Results: errors=%0d", errors);
        if (errors == 0) $display("PASS: 64'b1 << in is 100% correct one-hot for all 64 states.");
        $finish;
    end
endmodule
"""
    test_verilog_snippet(t2_code, "tb_shift_6to64", "6-to-64 Sized Shift")

    # Test 3: 16-to-65536 Sized shift
    t3_code = """
module tb_shift_16to65536;
    reg [15:0] in;
    wire [65535:0] Y;

    assign Y = 65536'b1 << in;

    integer errors = 0;

    initial begin
        // Test key edge cases: 0, 1, 255, 32767, 65535
        in = 16'd0; #1;
        if (Y[0] !== 1'b1) errors = errors + 1;
        
        in = 16'd1; #1;
        if (Y[1] !== 1'b1) errors = errors + 1;
        
        in = 16'd255; #1;
        if (Y[255] !== 1'b1) errors = errors + 1;

        in = 16'd32767; #1;
        if (Y[32767] !== 1'b1) errors = errors + 1;

        in = 16'd65535; #1;
        if (Y[65535] !== 1'b1) errors = errors + 1;

        $display("16-to-65536 Results: errors=%0d", errors);
        if (errors == 0) $display("PASS: 65536'b1 << in correctly decodes tested vectors.");
        $finish;
    end
endmodule
"""
    test_verilog_snippet(t3_code, "tb_shift_16to65536", "16-to-65536 Sized Shift")
