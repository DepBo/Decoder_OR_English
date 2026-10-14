* Buffered Driver Fanout Test: N = 64
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

* Fan-out Load Stages: 64 identical inverters driven by out_buf
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
Mload_p33 load_out33 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n33 load_out33 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p34 load_out34 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n34 load_out34 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p35 load_out35 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n35 load_out35 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p36 load_out36 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n36 load_out36 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p37 load_out37 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n37 load_out37 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p38 load_out38 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n38 load_out38 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p39 load_out39 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n39 load_out39 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p40 load_out40 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n40 load_out40 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p41 load_out41 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n41 load_out41 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p42 load_out42 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n42 load_out42 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p43 load_out43 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n43 load_out43 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p44 load_out44 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n44 load_out44 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p45 load_out45 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n45 load_out45 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p46 load_out46 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n46 load_out46 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p47 load_out47 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n47 load_out47 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p48 load_out48 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n48 load_out48 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p49 load_out49 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n49 load_out49 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p50 load_out50 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n50 load_out50 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p51 load_out51 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n51 load_out51 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p52 load_out52 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n52 load_out52 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p53 load_out53 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n53 load_out53 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p54 load_out54 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n54 load_out54 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p55 load_out55 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n55 load_out55 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p56 load_out56 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n56 load_out56 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p57 load_out57 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n57 load_out57 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p58 load_out58 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n58 load_out58 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p59 load_out59 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n59 load_out59 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p60 load_out60 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n60 load_out60 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p61 load_out61 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n61 load_out61 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p62 load_out62 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n62 load_out62 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p63 load_out63 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n63 load_out63 out_buf gnd gnd nch.1 w=0.65 l=0.15
Mload_p64 load_out64 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n64 load_out64 out_buf gnd gnd nch.1 w=0.65 l=0.15

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
