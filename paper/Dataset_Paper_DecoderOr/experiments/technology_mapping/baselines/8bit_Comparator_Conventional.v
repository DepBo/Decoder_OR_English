// Conventional 8-bit Comparator baseline
module _8bit_Comparator_Conventional (
    input  wire A7, A6, A5, A4, A3, A2, A1, A0,
    input  wire B7, B6, B5, B4, B3, B2, B1, B0,
    output wire A_gt_B,
    output wire A_eq_B,
    output wire A_lt_B
);
    wire [7:0] A = {A7, A6, A5, A4, A3, A2, A1, A0};
    wire [7:0] B = {B7, B6, B5, B4, B3, B2, B1, B0};
    assign A_gt_B = (A > B);
    assign A_eq_B = (A == B);
    assign A_lt_B = (A < B);
endmodule
