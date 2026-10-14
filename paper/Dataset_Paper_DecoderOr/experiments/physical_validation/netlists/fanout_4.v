// Controlled High-Fanout Test Case: N = 4
module fanout_test_4 (
    input  wire in_a,
    input  wire in_b,
    input  wire [3:0] a_in,
    output wire [3:0] out
);
    (* keep *) wire dec_y;
    assign dec_y = in_a & in_b;

    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin : or_gates
            assign out[i] = dec_y | a_in[i];
        end
    endgenerate
endmodule
