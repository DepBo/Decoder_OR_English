// ============================================================
// Module: OR64_FanIn_4
// 64-input OR reduction with max_fan_in = 4
// Logical Tree Depth: 3, Internal OR Nodes: 21
// ============================================================
module OR64_FanIn_4 (
    input  wire [63:0] in,
    output wire out
);

    wire or_n_n1;
    wire or_n_n2;
    wire or_n_n3;
    wire or_n_n4;
    wire or_n_n5;
    wire or_n_n6;
    wire or_n_n7;
    wire or_n_n8;
    wire or_n_n9;
    wire or_n_n10;
    wire or_n_n11;
    wire or_n_n12;
    wire or_n_n13;
    wire or_n_n14;
    wire or_n_n15;
    wire or_n_n16;
    wire or_n_n17;
    wire or_n_n18;
    wire or_n_n19;
    wire or_n_n20;
    assign or_n_n1 = in[0] | in[1] | in[2] | in[3];
    assign or_n_n2 = in[4] | in[5] | in[6] | in[7];
    assign or_n_n3 = in[8] | in[9] | in[10] | in[11];
    assign or_n_n4 = in[12] | in[13] | in[14] | in[15];
    assign or_n_n5 = or_n_n1 | or_n_n2 | or_n_n3 | or_n_n4;
    assign or_n_n6 = in[16] | in[17] | in[18] | in[19];
    assign or_n_n7 = in[20] | in[21] | in[22] | in[23];
    assign or_n_n8 = in[24] | in[25] | in[26] | in[27];
    assign or_n_n9 = in[28] | in[29] | in[30] | in[31];
    assign or_n_n10 = or_n_n6 | or_n_n7 | or_n_n8 | or_n_n9;
    assign or_n_n11 = in[32] | in[33] | in[34] | in[35];
    assign or_n_n12 = in[36] | in[37] | in[38] | in[39];
    assign or_n_n13 = in[40] | in[41] | in[42] | in[43];
    assign or_n_n14 = in[44] | in[45] | in[46] | in[47];
    assign or_n_n15 = or_n_n11 | or_n_n12 | or_n_n13 | or_n_n14;
    assign or_n_n16 = in[48] | in[49] | in[50] | in[51];
    assign or_n_n17 = in[52] | in[53] | in[54] | in[55];
    assign or_n_n18 = in[56] | in[57] | in[58] | in[59];
    assign or_n_n19 = in[60] | in[61] | in[62] | in[63];
    assign or_n_n20 = or_n_n16 | or_n_n17 | or_n_n18 | or_n_n19;
    assign out = or_n_n5 | or_n_n10 | or_n_n15 | or_n_n20;

endmodule
