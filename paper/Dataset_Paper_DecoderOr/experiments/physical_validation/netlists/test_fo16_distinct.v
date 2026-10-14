
module fanout_test_16 (
    input in_dec,
    input [15:0] a_in,
    output [15:0] out
);
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : or_gates
            assign out[i] = in_dec | a_in[i];
        end
    endgenerate
endmodule
