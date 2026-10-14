
`timescale 1ns/1ps
module tb_bcd;
    reg A, B, C, D;
    wire a, b, c, d, e, f, g;

    BCD_to_7Segment_Conventional_ZeroDC dut (
        .A(A), .B(B), .C(C), .D(D),
        .a(a), .b(b), .c(c), .d(d), .e(e), .f(f), .g(g)
    );

    integer i;
    initial begin
        for (i = 0; i < 16; i = i + 1) begin
            {A, B, C, D} = i[3:0];
            #1;
            $display("VEC %0d: %b%b%b%b%b%b%b", i, a, b, c, d, e, f, g);
        end
        $finish;
    end
endmodule
