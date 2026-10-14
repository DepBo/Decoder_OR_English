// Controlled High-Fanout Test Case: N = 1
module fanout_test_1 (
    input  wire in_a,
    input  wire in_b,
    input  wire [0:0] a_in,
    output wire [0:0] out
);
    (* keep *) wire dec_y;
    assign dec_y = in_a & in_b;

    genvar i;
    generate
        for (i = 0; i < 1; i = i + 1) begin : or_gates
            assign out[i] = dec_y | a_in[i];
        end
    endgenerate
endmodule
