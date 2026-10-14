// Deliberately Unbalanced Linear Cascade OR reduction
// Inputs: 64, Logical Depth: 63, Gates: 63
module OR64_Unbalanced_Linear (
    input wire in_0,
    input wire in_1,
    input wire in_2,
    input wire in_3,
    input wire in_4,
    input wire in_5,
    input wire in_6,
    input wire in_7,
    input wire in_8,
    input wire in_9,
    input wire in_10,
    input wire in_11,
    input wire in_12,
    input wire in_13,
    input wire in_14,
    input wire in_15,
    input wire in_16,
    input wire in_17,
    input wire in_18,
    input wire in_19,
    input wire in_20,
    input wire in_21,
    input wire in_22,
    input wire in_23,
    input wire in_24,
    input wire in_25,
    input wire in_26,
    input wire in_27,
    input wire in_28,
    input wire in_29,
    input wire in_30,
    input wire in_31,
    input wire in_32,
    input wire in_33,
    input wire in_34,
    input wire in_35,
    input wire in_36,
    input wire in_37,
    input wire in_38,
    input wire in_39,
    input wire in_40,
    input wire in_41,
    input wire in_42,
    input wire in_43,
    input wire in_44,
    input wire in_45,
    input wire in_46,
    input wire in_47,
    input wire in_48,
    input wire in_49,
    input wire in_50,
    input wire in_51,
    input wire in_52,
    input wire in_53,
    input wire in_54,
    input wire in_55,
    input wire in_56,
    input wire in_57,
    input wire in_58,
    input wire in_59,
    input wire in_60,
    input wire in_61,
    input wire in_62,
    input wire in_63,
    output wire out
);
    wire [62:0] chain;
    assign chain[0] = in_0 | in_1;
    assign chain[1] = chain[0] | in_2;
    assign chain[2] = chain[1] | in_3;
    assign chain[3] = chain[2] | in_4;
    assign chain[4] = chain[3] | in_5;
    assign chain[5] = chain[4] | in_6;
    assign chain[6] = chain[5] | in_7;
    assign chain[7] = chain[6] | in_8;
    assign chain[8] = chain[7] | in_9;
    assign chain[9] = chain[8] | in_10;
    assign chain[10] = chain[9] | in_11;
    assign chain[11] = chain[10] | in_12;
    assign chain[12] = chain[11] | in_13;
    assign chain[13] = chain[12] | in_14;
    assign chain[14] = chain[13] | in_15;
    assign chain[15] = chain[14] | in_16;
    assign chain[16] = chain[15] | in_17;
    assign chain[17] = chain[16] | in_18;
    assign chain[18] = chain[17] | in_19;
    assign chain[19] = chain[18] | in_20;
    assign chain[20] = chain[19] | in_21;
    assign chain[21] = chain[20] | in_22;
    assign chain[22] = chain[21] | in_23;
    assign chain[23] = chain[22] | in_24;
    assign chain[24] = chain[23] | in_25;
    assign chain[25] = chain[24] | in_26;
    assign chain[26] = chain[25] | in_27;
    assign chain[27] = chain[26] | in_28;
    assign chain[28] = chain[27] | in_29;
    assign chain[29] = chain[28] | in_30;
    assign chain[30] = chain[29] | in_31;
    assign chain[31] = chain[30] | in_32;
    assign chain[32] = chain[31] | in_33;
    assign chain[33] = chain[32] | in_34;
    assign chain[34] = chain[33] | in_35;
    assign chain[35] = chain[34] | in_36;
    assign chain[36] = chain[35] | in_37;
    assign chain[37] = chain[36] | in_38;
    assign chain[38] = chain[37] | in_39;
    assign chain[39] = chain[38] | in_40;
    assign chain[40] = chain[39] | in_41;
    assign chain[41] = chain[40] | in_42;
    assign chain[42] = chain[41] | in_43;
    assign chain[43] = chain[42] | in_44;
    assign chain[44] = chain[43] | in_45;
    assign chain[45] = chain[44] | in_46;
    assign chain[46] = chain[45] | in_47;
    assign chain[47] = chain[46] | in_48;
    assign chain[48] = chain[47] | in_49;
    assign chain[49] = chain[48] | in_50;
    assign chain[50] = chain[49] | in_51;
    assign chain[51] = chain[50] | in_52;
    assign chain[52] = chain[51] | in_53;
    assign chain[53] = chain[52] | in_54;
    assign chain[54] = chain[53] | in_55;
    assign chain[55] = chain[54] | in_56;
    assign chain[56] = chain[55] | in_57;
    assign chain[57] = chain[56] | in_58;
    assign chain[58] = chain[57] | in_59;
    assign chain[59] = chain[58] | in_60;
    assign chain[60] = chain[59] | in_61;
    assign chain[61] = chain[60] | in_62;
    assign out = chain[61] | in_63;
endmodule
