
module tb_shift_6to64;
    reg [5:0] in;
    wire [63:0] Y;

    assign Y = 64'b1 << in;

    integer i;
    integer errors = 0;

    initial begin
        for (i = 0; i < 64; i = i + 1) begin
            in = i[5:0];
            #1;
            if (Y[i] !== 1'b1 || $countones(Y) !== 1) begin
                errors = errors + 1;
            end
        end
        $display("6-to-64 Results: errors=%0d", errors);
        if (errors == 0) $display("PASS: 64'b1 << in is 100% correct one-hot for all 64 states.");
        $finish;
    end
endmodule
