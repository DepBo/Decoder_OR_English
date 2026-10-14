* Buffered Driver Fanout Test: N = 1
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

* Fan-out Load Stages: 1 identical inverters driven by out_buf
Mload_p1 load_out1 out_buf vdd vdd pch.1 w=1.0 l=0.15
Mload_n1 load_out1 out_buf gnd gnd nch.1 w=0.65 l=0.15

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
