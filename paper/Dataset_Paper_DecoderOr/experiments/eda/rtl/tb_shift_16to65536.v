
module tb_shift_16to65536;
    reg [15:0] in;
    wire [65535:0] Y;

    assign Y = 65536'b1 << in;

    integer errors = 0;

    initial begin
        // Test key edge cases: 0, 1, 255, 32767, 65535
        in = 16'd0; #1;
        if (Y[0] !== 1'b1) errors = errors + 1;
        
        in = 16'd1; #1;
        if (Y[1] !== 1'b1) errors = errors + 1;
        
        in = 16'd255; #1;
        if (Y[255] !== 1'b1) errors = errors + 1;

        in = 16'd32767; #1;
        if (Y[32767] !== 1'b1) errors = errors + 1;

        in = 16'd65535; #1;
        if (Y[65535] !== 1'b1) errors = errors + 1;

        $display("16-to-65536 Results: errors=%0d", errors);
        if (errors == 0) $display("PASS: 65536'b1 << in correctly decodes tested vectors.");
        $finish;
    end
endmodule
