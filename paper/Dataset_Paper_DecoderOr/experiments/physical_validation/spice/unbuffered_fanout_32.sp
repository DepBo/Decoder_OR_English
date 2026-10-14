* Unbuffered Driver Fanout Test: N = 32
* BSIM4 130nm CMOS Transistor Models (Sky130-equivalent geometry)
.option scale = 1e-6
.model nch.1 nmos ( version=4.7 level=54 lmin=0.1u lmax=20u wmin=0.1u wmax=10u )
.model pch.1 pmos ( version=4.7 level=54 lmin=0.1u lmax=20u wmin=0.1u wmax=10u )
.param vdd_val = 1.80
.param temp_val = 27.0
.global vdd gnd

Vdd vdd gnd dc 'vdd_val'
Vin in gnd pulse(0 'vdd_val' 100ps 50ps 50ps 1.0ns 2.2ns)

* Primary Driver Inverter: Wp=1.0um, Wn=0.65um, L=0.15um
Mdrv_p out in vdd vdd pch.1 w=1.0 l=0.15
Mdrv_n out in gnd gnd nch.1 w=0.65 l=0.15

* Fan-out Load Stages: 32 identical inverters
Mload_p1 load_out1 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n1 load_out1 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p2 load_out2 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n2 load_out2 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p3 load_out3 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n3 load_out3 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p4 load_out4 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n4 load_out4 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p5 load_out5 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n5 load_out5 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p6 load_out6 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n6 load_out6 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p7 load_out7 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n7 load_out7 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p8 load_out8 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n8 load_out8 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p9 load_out9 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n9 load_out9 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p10 load_out10 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n10 load_out10 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p11 load_out11 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n11 load_out11 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p12 load_out12 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n12 load_out12 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p13 load_out13 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n13 load_out13 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p14 load_out14 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n14 load_out14 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p15 load_out15 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n15 load_out15 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p16 load_out16 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n16 load_out16 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p17 load_out17 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n17 load_out17 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p18 load_out18 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n18 load_out18 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p19 load_out19 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n19 load_out19 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p20 load_out20 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n20 load_out20 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p21 load_out21 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n21 load_out21 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p22 load_out22 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n22 load_out22 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p23 load_out23 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n23 load_out23 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p24 load_out24 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n24 load_out24 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p25 load_out25 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n25 load_out25 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p26 load_out26 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n26 load_out26 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p27 load_out27 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n27 load_out27 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p28 load_out28 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n28 load_out28 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p29 load_out29 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n29 load_out29 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p30 load_out30 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n30 load_out30 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p31 load_out31 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n31 load_out31 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p32 load_out32 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n32 load_out32 out gnd gnd nch.1 w=0.65 l=0.15

* Transient simulation and automated .measure statements
.tran 1ps 2.5ns
.meas tran tphl trig v(in) val=0.90 rise=1 targ v(out) val=0.90 fall=1
.meas tran tplh trig v(in) val=0.90 fall=1 targ v(out) val=0.90 rise=1
.meas tran trise trig v(out) val=0.18 rise=1 targ v(out) val=1.62 rise=1
.meas tran tfall trig v(out) val=1.62 fall=1 targ v(out) val=0.18 fall=1
.meas tran vmax max v(out) from=0 to=2.5n
.meas tran vmin min v(out) from=100p to=1.2n
.meas tran i_supply_min min i(Vdd) from=0 to=2.5n
.meas tran i_supply_avg avg i(Vdd) from=0 to=2.5n
.meas tran q_tot integ i(Vdd) from=0 to=2.5n
.end
