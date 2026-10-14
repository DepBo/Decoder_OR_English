# Verification Report — Benchmark Dataset (Decoder-OR)

> **Status: ✅ ALL 5 CIRCUITS MATHEMATICALLY VERIFIED**

---

## Circuit 1 — Half Adder
**Inputs**: `A`, `B` → 2 inputs, 2² = 4 minterms  
**Encoding**: index = A·2 + B

| idx | A | B | Sum | Cout |
|-----|---|---|-----|------|
|  0  | 0 | 0 |  0  |  0   |
|  1  | 0 | 1 |  1  |  0   | ← Sum
|  2  | 1 | 0 |  1  |  0   | ← Sum
|  3  | 1 | 1 |  0  |  1   | ← Cout

- **Sum** = {1, 2} = A'B + AB' = A ⊕ B ✅  
- **Cout** = {3} = AB ✅

---

## Circuit 2 — Full Adder
**Inputs**: `A`, `B`, `Cin` → 3 inputs, 2³ = 8 minterms  
**Encoding**: index = A·4 + B·2 + Cin

| idx | A | B | Cin | Sum | Cout |
|-----|---|---|-----|-----|------|
|  0  | 0 | 0 |  0  |  0  |  0   |
|  1  | 0 | 0 |  1  |  1  |  0   | ← Sum
|  2  | 0 | 1 |  0  |  1  |  0   | ← Sum
|  3  | 0 | 1 |  1  |  0  |  1   | ← Cout
|  4  | 1 | 0 |  0  |  1  |  0   | ← Sum
|  5  | 1 | 0 |  1  |  0  |  1   | ← Cout
|  6  | 1 | 1 |  0  |  0  |  1   | ← Cout
|  7  | 1 | 1 |  1  |  1  |  1   | ← Sum, Cout

- **Sum** = {1, 2, 4, 7} = A ⊕ B ⊕ Cin ✅  
- **Cout** = {3, 5, 6, 7} = AB + ACin + BCin ✅

---

## Circuit 3 — 2-to-1 MUX
**Inputs**: `S`, `I0`, `I1` → 3 inputs, 2³ = 8 minterms  
**Encoding**: index = S·4 + I0·2 + I1

| idx | S | I0 | I1 | Y  | Reason |
|-----|---|----|----|----|--------|
|  0  | 0 |  0 |  0 | 0  | S=0→pass I0=0 |
|  1  | 0 |  0 |  1 | 0  | S=0→pass I0=0 |
|  2  | 0 |  1 |  0 | 1  | S=0→pass I0=1 | ← Y
|  3  | 0 |  1 |  1 | 1  | S=0→pass I0=1 | ← Y
|  4  | 1 |  0 |  0 | 0  | S=1→pass I1=0 |
|  5  | 1 |  0 |  1 | 1  | S=1→pass I1=1 | ← Y
|  6  | 1 |  1 |  0 | 0  | S=1→pass I1=0 |
|  7  | 1 |  1 |  1 | 1  | S=1→pass I1=1 | ← Y

- **Y** = {2, 3, 5, 7} = S'I0 + SI1 ✅

---

## Circuit 4 — BCD to 7-Segment
**Inputs**: `A`, `B`, `C`, `D` → 4 inputs, 2⁴ = 16 states  
**Valid BCD range**: digits 0–9 (states 10–15 = don't-care ✓)  
**Convention**: Common-cathode, active HIGH

| Digit | a | b | c | d | e | f | g |
|-------|---|---|---|---|---|---|---|
|   0   | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
|   1   | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
|   2   | 1 | 1 | 0 | 1 | 1 | 0 | 1 |
|   3   | 1 | 1 | 1 | 1 | 0 | 0 | 1 |
|   4   | 0 | 1 | 1 | 0 | 0 | 1 | 1 |
|   5   | 1 | 0 | 1 | 1 | 0 | 1 | 1 |
|   6   | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
|   7   | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
|   8   | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
|   9   | 1 | 1 | 1 | 1 | 0 | 1 | 1 |

Derived minterms (collecting indices where output = 1):

| Output | Minterms (digits where segment is ON) |
|--------|---------------------------------------|
| **a**  | {0,2,3,5,6,7,8,9} ✅ |
| **b**  | {0,1,2,3,4,7,8,9} ✅ |
| **c**  | {0,1,3,4,5,6,7,8,9} ✅ |
| **d**  | {0,2,3,5,6,8,9} ✅ |
| **e**  | {0,2,6,8} ✅ |
| **f**  | {0,4,5,6,8,9} ✅ |
| **g**  | {2,3,4,5,6,8,9} ✅ |

Don't-cares for all outputs: {10,11,12,13,14,15} ✅

---

## Circuit 5 — 3-bit Magnitude Comparator
**Inputs**: `A2,A1,A0,B2,B1,B0` → 6 inputs, 2⁶ = 64 minterms  
**Encoding**: index = A2·32 + A1·16 + A0·8 + B2·4 + B1·2 + B0  
**Values**: A = A2·4+A1·2+A0 ∈ [0..7], B = B2·4+B1·2+B0 ∈ [0..7]

For each pair (A∈{0..7}, B∈{0..7}), minterm index = A×8 + B:

**A_gt_B** (A > B) — 28 minterms:
```
A=1 vs B=0:       { 8 }
A=2 vs B<2:       { 16,17 }
A=3 vs B<3:       { 24,25,26 }
A=4 vs B<4:       { 32,33,34,35 }
A=5 vs B<5:       { 40,41,42,43,44 }
A=6 vs B<6:       { 48,49,50,51,52,53 }
A=7 vs B<7:       { 56,57,58,59,60,61,62 }
Total: 1+2+3+4+5+6+7 = 28 ✅
```

**A_eq_B** (A = B) — 8 minterms:
```
(0,0)→0, (1,1)→9, (2,2)→18, (3,3)→27,
(4,4)→36, (5,5)→45, (6,6)→54, (7,7)→63
Total: 8 ✅
```

**A_lt_B** (A < B) — 28 minterms:
```
A=0 vs B>0:       { 1,2,3,4,5,6,7 }
A=1 vs B>1:       { 10,11,12,13,14,15 }
A=2 vs B>2:       { 19,20,21,22,23 }
A=3 vs B>3:       { 28,29,30,31 }
A=4 vs B>4:       { 37,38,39 }
A=5 vs B>5:       { 46,47 }
A=6 vs B>6:       { 55 }
Total: 7+6+5+4+3+2+1 = 28 ✅
```

**Cross-check**: 28 + 8 + 28 = **64 = 2⁶** — partition is complete and disjoint ✅  
No minterm index appears in more than one output ✅

---

## Summary

| # | Circuit | Inputs | Outputs | Total States | Don't-Cares | Status |
|---|---------|--------|---------|-------------|-------------|--------|
| 1 | Half Adder | 2 | 2 | 4 | 0 | ✅ PASS |
| 2 | Full Adder | 3 | 2 | 8 | 0 | ✅ PASS |
| 3 | 2-to-1 MUX | 3 | 1 | 8 | 0 | ✅ PASS |
| 4 | BCD→7-Seg | 4 | 7 | 16 | 6×7=42 | ✅ PASS |
| 5 | 3-bit Comparator | 6 | 3 | 64 | 0 | ✅ PASS |

> **All 5 benchmark circuits are mathematically verified and ready for use in the Decoder-OR synthesis algorithm.**
