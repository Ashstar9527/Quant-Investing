# Question (b) -- Joint tests of equal premia

H0: all k mean monthly returns are equal (R μ = 0, R = [1, −I]). Wald = T (Rμ̂)'(R Σ̂ R')⁻¹(Rμ̂) ~ χ²(k−1); F = (T−q)/(q(T−1))·Wald ~ F(q, T−q); HAC = Newey-West Bartlett covariance, L = ⌊4(T/100)^{2/9}⌋.

## Table B1. Main tests

| Test | k | Common sample | T | Wald χ² | df | p (χ²) | F | p (F) | Wald HAC | p (HAC) | p (HAC, L=12) | Reject at 5%? χ²/F/HAC |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Value, all 8 markets | 8 | 1983-01–2025-01 | 505 | 13.68 | 7 | 0.0571 | 1.93 | 0.0628 | 12.70 (L=5) | 0.0798 | 0.0658 | —/—/— |
| Value, 4 equity stock-selection | 4 | 1981-07–2026-05 | 539 | 7.97 | 3 | 0.0466 | 2.65 | 0.0483 | 6.98 (L=5) | 0.0725 | 0.0520 | R/R/— |
| Momentum, all 8 markets | 8 | 1983-01–2025-01 | 505 | 13.50 | 7 | 0.0608 | 1.91 | 0.0667 | 16.01 (L=5) | 0.0250 | 0.0105 | —/—/R |
| Momentum, 4 equity stock-selection | 4 | 1974-02–2026-05 | 628 | 7.82 | 3 | 0.0499 | 2.60 | 0.0515 | 9.53 (L=6) | 0.0230 | 0.0145 | R/—/R |

R = reject H0 at 5%, — = fail to reject; columns refer to the i.i.d. Wald χ², the exact F (Hotelling), and the Newey-West HAC Wald.

## Table B2. Sensitivity checks

| Test | k | Common sample | T | Wald χ² | df | p (χ²) | F | p (F) | Wald HAC | p (HAC) | p (HAC, L=12) | Reject at 5%? χ²/F/HAC |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Value, 4 equity + EQ index futures | 5 | 1981-07–2025-01 | 523 | 8.59 | 4 | 0.0722 | 2.14 | 0.0752 | 7.27 (L=5) | 0.1221 | 0.0957 | —/—/— |
| Momentum, 4 equity + EQ index futures | 5 | 1977-03–2025-01 | 575 | 10.09 | 4 | 0.0390 | 2.51 | 0.0410 | 10.15 (L=5) | 0.0380 | 0.0244 | R/R/R |
| Value, all 8, scaled to 10% vol | 8 | 1983-01–2025-01 | 505 | 9.09 | 7 | 0.2460 | 1.28 | 0.2563 | 8.53 (L=5) | 0.2883 | 0.2474 | —/—/— |
| Value, 4 equity, scaled to 10% vol | 4 | 1981-07–2026-05 | 539 | 8.70 | 3 | 0.0335 | 2.89 | 0.0350 | 8.31 (L=5) | 0.0400 | 0.0285 | R/R/R |
| Momentum, all 8, scaled to 10% vol | 8 | 1983-01–2025-01 | 505 | 9.28 | 7 | 0.2334 | 1.31 | 0.2436 | 11.08 (L=5) | 0.1353 | 0.1021 | —/—/— |
| Momentum, 4 equity, scaled to 10% vol | 4 | 1974-02–2026-05 | 628 | 11.37 | 3 | 0.0099 | 3.78 | 0.0105 | 14.23 (L=6) | 0.0026 | 0.0020 | R/R/R |

## Table B3. Mean monthly returns (%) over each test's common sample

- **Value, all 8 markets** (1983-01–2025-01, T=505): VAL^US 0.128, VAL^UK 0.280, VAL^EU 0.191, VAL^JP 0.640, VAL^EQ 0.201, VAL^FX 0.175, VAL^FI 0.045, VAL^CM 0.425
- **Value, 4 equity stock-selection** (1981-07–2026-05, T=539): VAL^US 0.143, VAL^UK 0.247, VAL^EU 0.239, VAL^JP 0.651
- **Momentum, all 8 markets** (1983-01–2025-01, T=505): MOM^US 0.442, MOM^UK 0.655, MOM^EU 0.580, MOM^JP 0.151, MOM^EQ 0.399, MOM^FX 0.132, MOM^FI 0.048, MOM^CM 0.443
- **Momentum, 4 equity stock-selection** (1974-02–2026-05, T=628): MOM^US 0.542, MOM^UK 0.646, MOM^EU 0.690, MOM^JP 0.178
- **Value, 4 equity + EQ index futures** (1981-07–2025-01, T=523): VAL^US 0.136, VAL^UK 0.247, VAL^EU 0.212, VAL^JP 0.654, VAL^EQ 0.246
- **Momentum, 4 equity + EQ index futures** (1977-03–2025-01, T=575): MOM^US 0.544, MOM^UK 0.705, MOM^EU 0.646, MOM^JP 0.111, MOM^EQ 0.418
- **Value, all 8, scaled to 10% vol** (1983-01–2025-01, T=505): VAL^US 0.084, VAL^UK 0.196, VAL^EU 0.177, VAL^JP 0.461, VAL^EQ 0.220, VAL^FX 0.234, VAL^FI 0.088, VAL^CM 0.215
- **Value, 4 equity, scaled to 10% vol** (1981-07–2026-05, T=539): VAL^US 0.095, VAL^UK 0.175, VAL^EU 0.221, VAL^JP 0.471
- **Momentum, all 8, scaled to 10% vol** (1983-01–2025-01, T=505): MOM^US 0.278, MOM^UK 0.421, MOM^EU 0.444, MOM^JP 0.096, MOM^EQ 0.377, MOM^FX 0.164, MOM^FI 0.107, MOM^CM 0.231
- **Momentum, 4 equity, scaled to 10% vol** (1974-02–2026-05, T=628): MOM^US 0.352, MOM^UK 0.437, MOM^EU 0.548, MOM^JP 0.115
