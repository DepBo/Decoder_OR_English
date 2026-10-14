// Conventional 2-to-1 MUX baseline
module _2_to_1_MUX_Conventional (
    input  wire D0,
    input  wire D1,
    input  wire S,
    output wire Y
);
    assign Y = S ? D1 : D0;
endmodule
