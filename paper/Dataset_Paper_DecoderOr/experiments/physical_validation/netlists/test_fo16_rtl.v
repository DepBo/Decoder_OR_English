
module fanout_test_16 (
    input in,
    output [15:0] out
);
    wire drv_net;
    assign drv_net = in;
    assign out[0] = ~drv_net;
    assign out[1] = ~drv_net;
    assign out[2] = ~drv_net;
    assign out[3] = ~drv_net;
    assign out[4] = ~drv_net;
    assign out[5] = ~drv_net;
    assign out[6] = ~drv_net;
    assign out[7] = ~drv_net;
    assign out[8] = ~drv_net;
    assign out[9] = ~drv_net;
    assign out[10] = ~drv_net;
    assign out[11] = ~drv_net;
    assign out[12] = ~drv_net;
    assign out[13] = ~drv_net;
    assign out[14] = ~drv_net;
    assign out[15] = ~drv_net;
endmodule
