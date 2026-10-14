// Conventional Full Adder baseline
module Full_Adder_Conventional (
    input  wire A,
    input  wire B,
    input  wire Cin,
    output wire Sum,
    output wire Cout
);
    assign {Cout, Sum} = A + B + Cin;
endmodule
