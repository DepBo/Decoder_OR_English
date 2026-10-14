
module fanout_test_16 (
    input in_a,
    input in_b,
    input [15:0] a_in,
    output [15:0] out
);
    (* keep *) wire dec_y;
    assign dec_y = in_a & in_b;
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : or_gates
            assign out[i] = dec_y | a_in[i];
        end
    endgenerate
endmodule
