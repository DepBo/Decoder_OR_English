# NGSPICE Transistor-Level Electrical Simulation Summary

This report documents the BSIM4 (130nm CMOS, $V_{DD} = 1.80\text{ V}$, $T = 27^\circ\text{C}$) transient circuit simulations conducted with **ngspice (v45.2)**.

## 1. Electrical Simulation Methodology
- **Model:** BSIM4 level 54 (SkyWater 130nm geometry equivalent: $W_n=0.65\,\mu\text{m}, W_p=1.00\,\mu\text{m}, L=0.15\,\mu\text{m}$).
- **Stimulus:** $1.80\text{ V}$ pulse, $50\text{ ps}$ input rise/fall time, $1.0\text{ ns}$ pulse width, $2.2\text{ ns}$ period, $2.5\text{ ns}$ transient window.
- **Energy Definition:** Dynamic energy per switching cycle:
  $$E_{\text{cycle}} = \int_0^{2.5\,\text{ns}} V_{DD} \cdot I_{DD}(t)\,dt$$

## 2. Quantitative Electrical Results Table

| Topology | Fan-out ($N$) | $t_{p,rise}$ (ps) | $t_{p,fall}$ (ps) | $t_{rise}$ (ps) | $t_{fall}$ (ps) | $V_{OH}$ (V) | $V_{OL}$ (V) | Energy (fJ) | $I_{peak}$ (mA) | Electrical Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| unbuffered | 1 | 26.28 | 24.28 | 42.89 | 38.17 | 1.868 | -0.05 | 74.82 | 0.522 | **PASS** |
| unbuffered | 2 | 35.46 | 32.37 | 64.39 | 58.26 | 1.855 | -0.043 | 149.12 | 0.671 | **PASS** |
| unbuffered | 4 | 55.64 | 49.37 | 109.3 | 98.87 | 1.84 | -0.032 | 357.41 | 1.033 | **PASS** |
| unbuffered | 8 | 99.19 | 84.53 | 201.98 | 182.75 | 1.825 | -0.022 | 988.41 | 1.737 | **PASS** |
| unbuffered | 16 | 196.31 | 157.0 | 390.55 | 354.06 | 1.815 | -0.013 | 2634.95 | 3.151 | **PASS** |
| unbuffered | 32 | 394.91 | 306.13 | 767.4 | 696.96 | 1.808 | 0.005 | 8149.93 | 5.984 | **PASS** |
| unbuffered | 64 | 410.8 | 609.25 | INCOMPLETE | INCOMPLETE | 1.804 | 0.62 | 27631.98 | 11.653 | **INCOMPLETE_SWITCHING** |
| buffered_2stage | 1 | 74.45 | 76.18 | 44.22 | 45.42 | 1.85 | -0.036 | 419.37 | 1.222 | **PASS** |
| buffered_2stage | 2 | 77.7 | 79.43 | 49.34 | 50.62 | 1.848 | -0.035 | 470.31 | 1.407 | **PASS** |
| buffered_2stage | 4 | 83.55 | 85.25 | 59.46 | 60.41 | 1.845 | -0.033 | 591.16 | 1.778 | **PASS** |
| buffered_2stage | 8 | 94.35 | 95.56 | 79.5 | 79.22 | 1.838 | -0.029 | 896.07 | 2.596 | **PASS** |
| buffered_2stage | 16 | 114.9 | 114.32 | 121.0 | 116.89 | 1.83 | -0.024 | 1696.79 | 4.101 | **PASS** |
| buffered_2stage | 32 | 156.73 | 149.53 | 208.1 | 195.43 | 1.82 | -0.017 | 3678.23 | 6.962 | **PASS** |
| buffered_2stage | 64 | 250.09 | 220.09 | 387.63 | 358.21 | 1.812 | -0.01 | 9488.45 | 12.646 | **PASS** |

## 3. Scientific In-Depth Analysis

### A. Incomplete Switching at N=64 (Unbuffered)
- At $N=64$ with an unbuffered $1\times$ driver, the cumulative gate load capacitance ($64 \times C_{in} \approx 120\,\text{fF}$) causes the $RC$ discharge time constant to exceed the $1.0\,\text{ns}$ input pulse width.
- The output node reaches a minimum of only $V_{OL} = 0.620\,\text{V}$ before the next input transition begins.
- Because $V_{OL} > 10\%\,V_{DD}$ ($0.18\,\text{V}$), the $90\% \to 10\%$ fall transition is truncated.
- **Classification:** **`INCOMPLETE_SWITCHING`** (not marked PASS despite ngspice exit code 0).

### B. Voltage Overshoot & Undershoot Analysis
- At low fan-out ($N=1$), $V_{OH}$ peaks at $1.868\,\text{V}$ ($+68\,\text{mV}$ above $V_{DD}$) and $V_{OL}$ dips to $-0.050\,\text{V}$ ($-50\,\text{mV}$ below ground).
- **Physical Cause:** Capacitive feedthrough across gate-drain overlap capacitance ($C_{gd}$) during ultra-steep input voltage transients ($50\,\text{ps}$ edge rate, $dv/dt = 36\,\text{V/ns}$).
- As fan-out capacitance increases ($N=32, 64$), the load capacitance swamped the feedthrough, damping overshoot and undershoot completely.
- **Conclusion:** These transient excursions represent well-known capacitive feedthrough dynamics in fast CMOS switching, not static rail-to-rail degradation.

### C. Dynamic Energy & Crowbar Current Mitigation
- Buffered driver dynamic energy at $N=32$ ($3,678\,\text{fJ}$) is **55% lower** than unbuffered dynamic energy ($8,150\,\text{fJ}$).
- The sharper buffered transition ($208\,\text{ps}$ vs $767\,\text{ps}$) minimizes simultaneous conduction of NMOS and PMOS networks in downstream gates, eliminating prolonged crowbar current.
