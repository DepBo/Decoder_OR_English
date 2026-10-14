// Balanced OR Tree with max_fan_in=4
// Inputs: 64, Logical Depth: 3, Internal Nodes: 21
module OR64_Balanced_FanIn4 (
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
    wire b_or_n1;
    wire b_or_n2;
    wire b_or_n3;
    wire b_or_n4;
    wire b_or_n5;
    wire b_or_n6;
    wire b_or_n7;
    wire b_or_n8;
    wire b_or_n9;
    wire b_or_n10;
    wire b_or_n11;
    wire b_or_n12;
    wire b_or_n13;
    wire b_or_n14;
    wire b_or_n15;
    wire b_or_n16;
    wire b_or_n17;
    wire b_or_n18;
    wire b_or_n19;
    wire b_or_n20;
    assign b_or_n1 = in_0 | in_1 | in_2 | in_3;
    assign b_or_n2 = in_4 | in_5 | in_6 | in_7;
    assign b_or_n3 = in_8 | in_9 | in_10 | in_11;
    assign b_or_n4 = in_12 | in_13 | in_14 | in_15;
    assign b_or_n5 = b_or_n1 | b_or_n2 | b_or_n3 | b_or_n4;
    assign b_or_n6 = in_16 | in_17 | in_18 | in_19;
    assign b_or_n7 = in_20 | in_21 | in_22 | in_23;
    assign b_or_n8 = in_24 | in_25 | in_26 | in_27;
    assign b_or_n9 = in_28 | in_29 | in_30 | in_31;
    assign b_or_n10 = b_or_n6 | b_or_n7 | b_or_n8 | b_or_n9;
    assign b_or_n11 = in_32 | in_33 | in_34 | in_35;
    assign b_or_n12 = in_36 | in_37 | in_38 | in_39;
    assign b_or_n13 = in_40 | in_41 | in_42 | in_43;
    assign b_or_n14 = in_44 | in_45 | in_46 | in_47;
    assign b_or_n15 = b_or_n11 | b_or_n12 | b_or_n13 | b_or_n14;
    assign b_or_n16 = in_48 | in_49 | in_50 | in_51;
    assign b_or_n17 = in_52 | in_53 | in_54 | in_55;
    assign b_or_n18 = in_56 | in_57 | in_58 | in_59;
    assign b_or_n19 = in_60 | in_61 | in_62 | in_63;
    assign b_or_n20 = b_or_n16 | b_or_n17 | b_or_n18 | b_or_n19;
    assign out = b_or_n5 | b_or_n10 | b_or_n15 | b_or_n20;
endmodule
