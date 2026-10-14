
module fanout_test_16 (
    input wire in,
    output wire [15:0] out
);
    wire drv_net;
    sky130_fd_sc_hd__inv_1 drv (.A(in), .Y(drv_net));
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : loads
            sky130_fd_sc_hd__inv_1 load (.A(drv_net), .Y(out[i]));
        end
    endgenerate
endmodule
