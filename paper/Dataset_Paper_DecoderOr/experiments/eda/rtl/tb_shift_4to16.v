
module tb_shift_4to16;
    reg [3:0] in;
    wire [15:0] Y_unsafe;
    wire [15:0] Y_sized;

    assign Y_unsafe = 1'b1 << in;
    assign Y_sized  = 16'b1 << in;

    integer i;
    integer errors_unsafe = 0;
    integer errors_sized = 0;

    initial begin
        for (i = 0; i < 16; i = i + 1) begin
            in = i[3:0];
            #1;
            // Check one-hot for Y_unsafe
            if (Y_unsafe !== (16'b1 << i)) begin
                errors_unsafe = errors_unsafe + 1;
            end
            // Check one-hot for Y_sized
            if (Y_sized !== (16'b1 << i)) begin
                errors_sized = errors_sized + 1;
            end
        end
        $display("4-to-16 Results: errors_unsafe=%0d, errors_sized=%0d", errors_unsafe, errors_sized);
        $display("Sample in=1: Y_unsafe=%016b, Y_sized=%016b", (1'b1 << 4'd1), (16'b1 << 4'd1));
        if (errors_sized == 0) $display("PASS: 16'b1 << in is 100% correct one-hot.");
        else $display("FAIL: 16'b1 << in had errors.");
        $finish;
    end
endmodule
