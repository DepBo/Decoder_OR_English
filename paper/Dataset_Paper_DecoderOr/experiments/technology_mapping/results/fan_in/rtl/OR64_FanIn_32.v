// ============================================================
// Module: OR64_FanIn_32
// 64-input OR reduction with max_fan_in = 32
// Logical Tree Depth: 2, Internal OR Nodes: 3
// ============================================================
module OR64_FanIn_32 (
    input  wire [63:0] in,
    output wire out
);

    wire or_n_n1;
    wire or_n_n2;
    assign or_n_n1 = in[0] | in[1] | in[2] | in[3] | in[4] | in[5] | in[6] | in[7] | in[8] | in[9] | in[10] | in[11] | in[12] | in[13] | in[14] | in[15] | in[16] | in[17] | in[18] | in[19] | in[20] | in[21] | in[22] | in[23] | in[24] | in[25] | in[26] | in[27] | in[28] | in[29] | in[30] | in[31];
    assign or_n_n2 = in[32] | in[33] | in[34] | in[35] | in[36] | in[37] | in[38] | in[39] | in[40] | in[41] | in[42] | in[43] | in[44] | in[45] | in[46] | in[47] | in[48] | in[49] | in[50] | in[51] | in[52] | in[53] | in[54] | in[55] | in[56] | in[57] | in[58] | in[59] | in[60] | in[61] | in[62] | in[63];
    assign out = or_n_n1 | or_n_n2;

endmodule
