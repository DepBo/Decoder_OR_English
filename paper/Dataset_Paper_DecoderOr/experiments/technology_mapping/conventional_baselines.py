"""
experiments/technology_mapping/conventional_baselines.py
--------------------------------------------------------
Generates clean, conventional behavioral/Boolean RTL baselines for:
1. Half Adder
2. Full Adder
3. 2-to-1 MUX
4. BCD 7-segment (both don't-care variants)
5. 3-bit Comparator
6. 8-bit Comparator
"""

from pathlib import Path

def get_conventional_verilog(benchmark_name: str) -> str:
    """Returns synthesizable conventional RTL for the given benchmark."""
    if benchmark_name == "Half_Adder":
        return """\
// Conventional Half Adder baseline
module Half_Adder_Conventional (
    input  wire A,
    input  wire B,
    output wire Sum,
    output wire Cout
);
    assign Sum  = A ^ B;
    assign Cout = A & B;
endmodule
"""
    elif benchmark_name == "Full_Adder":
        return """\
// Conventional Full Adder baseline
module Full_Adder_Conventional (
    input  wire A,
    input  wire B,
    input  wire Cin,
    output wire Sum,
    output wire Cout
);
    assign {Cout, Sum} = A + B + Cin;
endmodule
"""
    elif benchmark_name == "2_to_1_MUX":
        return """\
// Conventional 2-to-1 MUX baseline
module _2_to_1_MUX_Conventional (
    input  wire D0,
    input  wire D1,
    input  wire S,
    output wire Y
);
    assign Y = S ? D1 : D0;
endmodule
"""
    elif benchmark_name == "BCD_to_7Segment":
        return """\
// Conventional BCD to 7-Segment baseline (don't cares unspecified/X)
module BCD_to_7Segment_Conventional (
    input  wire A,
    input  wire B,
    input  wire C,
    input  wire D,
    output reg  a,
    output reg  b,
    output reg  c,
    output reg  d,
    output reg  e,
    output reg  f,
    output reg  g
);
    always @(*) begin
        case ({A, B, C, D})
            4'd0: {a, b, c, d, e, f, g} = 7'b1111110;
            4'd1: {a, b, c, d, e, f, g} = 7'b0110000;
            4'd2: {a, b, c, d, e, f, g} = 7'b1101101;
            4'd3: {a, b, c, d, e, f, g} = 7'b1111001;
            4'd4: {a, b, c, d, e, f, g} = 7'b0110011;
            4'd5: {a, b, c, d, e, f, g} = 7'b1011011;
            4'd6: {a, b, c, d, e, f, g} = 7'b1011111;
            4'd7: {a, b, c, d, e, f, g} = 7'b1110000;
            4'd8: {a, b, c, d, e, f, g} = 7'b1111111;
            4'd9: {a, b, c, d, e, f, g} = 7'b1111011;
            default: {a, b, c, d, e, f, g} = 7'bxxxxxxx;
        endcase
    end
endmodule
"""
    elif benchmark_name == "BCD_to_7Segment_ZeroDC":
        return """\
// Conventional BCD to 7-Segment baseline (don't cares tied to zero)
module BCD_to_7Segment_Conventional_ZeroDC (
    input  wire A,
    input  wire B,
    input  wire C,
    input  wire D,
    output reg  a,
    output reg  b,
    output reg  c,
    output reg  d,
    output reg  e,
    output reg  f,
    output reg  g
);
    always @(*) begin
        case ({A, B, C, D})
            4'd0: {a, b, c, d, e, f, g} = 7'b1111110;
            4'd1: {a, b, c, d, e, f, g} = 7'b0110000;
            4'd2: {a, b, c, d, e, f, g} = 7'b1101101;
            4'd3: {a, b, c, d, e, f, g} = 7'b1111001;
            4'd4: {a, b, c, d, e, f, g} = 7'b0110011;
            4'd5: {a, b, c, d, e, f, g} = 7'b1011011;
            4'd6: {a, b, c, d, e, f, g} = 7'b1011111;
            4'd7: {a, b, c, d, e, f, g} = 7'b1110000;
            4'd8: {a, b, c, d, e, f, g} = 7'b1111111;
            4'd9: {a, b, c, d, e, f, g} = 7'b1111011;
            default: {a, b, c, d, e, f, g} = 7'b0000000;
        endcase
    end
endmodule
"""
    elif benchmark_name == "3bit_Comparator":
        return """\
// Conventional 3-bit Comparator baseline
module _3bit_Comparator_Conventional (
    input  wire A2, A1, A0,
    input  wire B2, B1, B0,
    output wire A_gt_B,
    output wire A_eq_B,
    output wire A_lt_B
);
    wire [2:0] A = {A2, A1, A0};
    wire [2:0] B = {B2, B1, B0};
    assign A_gt_B = (A > B);
    assign A_eq_B = (A == B);
    assign A_lt_B = (A < B);
endmodule
"""
    elif benchmark_name == "8bit_Comparator":
        return """\
// Conventional 8-bit Comparator baseline
module _8bit_Comparator_Conventional (
    input  wire A7, A6, A5, A4, A3, A2, A1, A0,
    input  wire B7, B6, B5, B4, B3, B2, B1, B0,
    output wire A_gt_B,
    output wire A_eq_B,
    output wire A_lt_B
);
    wire [7:0] A = {A7, A6, A5, A4, A3, A2, A1, A0};
    wire [7:0] B = {B7, B6, B5, B4, B3, B2, B1, B0};
    assign A_gt_B = (A > B);
    assign A_eq_B = (A == B);
    assign A_lt_B = (A < B);
endmodule
"""
    else:
        raise ValueError(f"Unknown benchmark name: {benchmark_name}")


def write_all_baselines(target_dir: Path) -> dict:
    """Writes all conventional baseline Verilog files to target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    names = [
        "Half_Adder",
        "Full_Adder",
        "2_to_1_MUX",
        "BCD_to_7Segment",
        "BCD_to_7Segment_ZeroDC",
        "3bit_Comparator",
        "8bit_Comparator"
    ]
    for name in names:
        code = get_conventional_verilog(name)
        out_path = target_dir / f"{name}_Conventional.v"
        out_path.write_text(code, encoding="utf-8")
        files[name] = out_path
    return files
