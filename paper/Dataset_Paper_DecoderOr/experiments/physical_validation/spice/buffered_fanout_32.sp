* Buffered Driver Fanout Test: N = 32
* BSIM4 130nm CMOS Transistor Models (Sky130-equivalent geometry)
.option scale = 1e-6
.model nch.1 nmos ( version=4.7 level=54 lmin=0.1u lmax=20u wmin=0.1u wmax=10u )
.model pch.1 pmos ( version=4.7 level=54 lmin=0.1u lmax=20u wmin=0.1u wmax=10u )
.param vdd_val = 1.80
.param temp_val = 27.0
.global vdd gnd

Vdd vdd gnd dc 'vdd_val'
Vin in gnd pulse(0 'vdd_val' 100ps 50ps 50ps 1.0ns 2.2ns)

* Buffer Stage 1: Inverter 1x (Wp=1.0um, Wn=0.65um)
Mbuf1_p buf_mid in vdd vdd pch.1 w=1.0 l=0.15
Mbuf1_n buf_mid in gnd gnd nch.1 w=0.65 l=0.15

* Buffer Stage 2: Sized Inverter 4x (Wp=4.0um, Wn=2.6um)
Mbuf2_p out_buf buf_mid vdd vdd pch.1 w=4.0 l=0.15
Mbuf2_n out_buf buf_mid gnd gnd nch.1 w=2.6 l=0.15

* Fan-out Load Stages: 32 identical inverters driven by out_buf
Mload_p1 load_out1 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n1 load_out1 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p2 load_out2 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n2 load_out2 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p3 load_out3 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n3 load_out3 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p4 load_out4 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n4 load_out4 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p5 load_out5 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n5 load_out5 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p6 load_out6 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n6 load_out6 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p7 load_out7 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n7 load_out7 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p8 load_out8 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n8 load_out8 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p9 load_out9 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n9 load_out9 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p10 load_out10 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n10 load_out10 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p11 load_out11 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n11 load_out11 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p12 load_out12 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n12 load_out12 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p13 load_out13 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n13 load_out13 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p14 load_out14 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n14 load_out14 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p15 load_out15 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n15 load_out15 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p16 load_out16 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n16 load_out16 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p17 load_out17 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n17 load_out17 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p18 load_out18 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n18 load_out18 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p19 load_out19 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n19 load_out19 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p20 load_out20 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n20 load_out20 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p21 load_out21 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n21 load_out21 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p22 load_out22 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n22 load_out22 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p23 load_out23 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n23 load_out23 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p24 load_out24 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n24 load_out24 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p25 load_out25 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n25 load_out25 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p26 load_out26 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n26 load_out26 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p27 load_out27 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n27 load_out27 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p28 load_out28 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n28 load_out28 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p29 load_out29 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n29 load_out29 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p30 load_out30 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n30 load_out30 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p31 load_out31 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n31 load_out31 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p32 load_out32 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n32 load_out32 out_buf gnd gnd nch.1 w=0.65 l=0.15

* Transient simulation and automated .measure statements
.tran 1ps 2.5ns
* Note: Buffer is non-inverting overall (in -> out_buf)
.meas tran tphl trig v(in) val=0.90 fall=1 targ v(out_buf) val=0.90 fall=1
.meas tran tplh trig v(in) val=0.90 rise=1 targ v(out_buf) val=0.90 rise=1
.meas tran trise trig v(out_buf) val=0.18 rise=1 targ v(out_buf) val=1.62 rise=1
.meas tran tfall trig v(out_buf) val=1.62 fall=1 targ v(out_buf) val=0.18 fall=1
.meas tran vmax max v(out_buf) from=0 to=2.5n
.meas tran vmin min v(out_buf) from=100p to=1.2n
.meas tran i_supply_min min i(Vdd) from=0 to=2.5n
.meas tran i_supply_avg avg i(Vdd) from=0 to=2.5n
.meas tran q_tot integ i(Vdd) from=0 to=2.5n
.end
