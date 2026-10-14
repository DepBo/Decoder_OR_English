// Controlled High-Fanout Test Case: N = 32
module fanout_test_32 (
    input  wire in_a,
    input  wire in_b,
    input  wire [31:0] a_in,
    output wire [31:0] out
);
    (* keep *) wire dec_y;
    assign dec_y = in_a & in_b;

    genvar i;
    generate
        for (i = 0; i < 32; i = i + 1) begin : or_gates
            assign out[i] = dec_y | a_in[i];
        end
    endgenerate
endmodule
