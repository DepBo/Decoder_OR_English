* Unbuffered Driver Fanout Test: N = 64
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

* Fan-out Load Stages: 64 identical inverters
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
Mload_p33 load_out33 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n33 load_out33 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p34 load_out34 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n34 load_out34 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p35 load_out35 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n35 load_out35 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p36 load_out36 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n36 load_out36 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p37 load_out37 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n37 load_out37 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p38 load_out38 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n38 load_out38 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p39 load_out39 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n39 load_out39 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p40 load_out40 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n40 load_out40 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p41 load_out41 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n41 load_out41 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p42 load_out42 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n42 load_out42 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p43 load_out43 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n43 load_out43 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p44 load_out44 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n44 load_out44 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p45 load_out45 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n45 load_out45 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p46 load_out46 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n46 load_out46 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p47 load_out47 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n47 load_out47 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p48 load_out48 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n48 load_out48 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p49 load_out49 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n49 load_out49 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p50 load_out50 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n50 load_out50 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p51 load_out51 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n51 load_out51 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p52 load_out52 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n52 load_out52 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p53 load_out53 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n53 load_out53 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p54 load_out54 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n54 load_out54 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p55 load_out55 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n55 load_out55 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p56 load_out56 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n56 load_out56 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p57 load_out57 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n57 load_out57 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p58 load_out58 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n58 load_out58 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p59 load_out59 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n59 load_out59 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p60 load_out60 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n60 load_out60 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p61 load_out61 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n61 load_out61 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p62 load_out62 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n62 load_out62 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p63 load_out63 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n63 load_out63 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p64 load_out64 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n64 load_out64 out gnd gnd nch.1 w=0.65 l=0.15

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
