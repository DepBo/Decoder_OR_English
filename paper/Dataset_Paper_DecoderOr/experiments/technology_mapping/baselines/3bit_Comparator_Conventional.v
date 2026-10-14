// Conventional 3-bit Comparator baseline
module _3bit_Comparator_Conventional (
    input  wire A2, A1, A0,
    input  wire B2, B1, B0,
    output wire A_gt_B,
    output wire A_eq_B,
    output wire A_lt_B
);
    wire [2:0] A = {A2, A1, A0};
    wire [2:0] B = {B2, B1, B0};
    assign A_gt_B = (A > B);
    assign A_eq_B = (A == B);
    assign A_lt_B = (A < B);
endmodule
