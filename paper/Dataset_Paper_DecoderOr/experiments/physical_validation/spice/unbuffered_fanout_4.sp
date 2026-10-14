* Unbuffered Driver Fanout Test: N = 4
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

* Fan-out Load Stages: 4 identical inverters
Mload_p1 load_out1 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n1 load_out1 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p2 load_out2 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n2 load_out2 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p3 load_out3 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n3 load_out3 out gnd gnd nch.1 w=0.65 l=0.15
Mload_p4 load_out4 out vdd vdd pch.1 w=1.0 l=0.15
Mload_n4 load_out4 out gnd gnd nch.1 w=0.65 l=0.15

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
