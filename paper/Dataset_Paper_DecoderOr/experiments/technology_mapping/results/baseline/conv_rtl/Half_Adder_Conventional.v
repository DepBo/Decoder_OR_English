// Conventional Half Adder baseline
module Half_Adder_Conventional (
    input  wire A,
    input  wire B,
    output wire Sum,
    output wire Cout
);
    assign Sum  = A ^ B;
    assign Cout = A & B;
endmodule
