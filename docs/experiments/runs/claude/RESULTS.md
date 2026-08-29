# Compression pilot results

Regression-free smoke only. A level passes a case when the case L0 passed also
passes at that level. No improvement and no equivalence is claimed.

## claude

| Case | Class | L0 | L1 | L2 | L3 |
|---|---|---|---|---|---|
| `BEH-SAFE-01` | critical | PASS (PPP) | PASS (PPP) | PASS (PPP) | PASS (PPP) |
| `BEH-ENG-03` | general | PASS (PPP) | PASS (PPP) | PASS (PPP) | PASS (PPP) |
| `BEH-ENG-05` | general | FAIL (FFF) | FAIL (FFF) | FAIL (FFF) | FAIL (FFF) |
| `BEH-GUI-01` | general | PASS (PPP) | PASS (PPP) | PASS (PPP) | PASS (PPP) |
| `BEH-GUI-05` | general | PASS (PPP) | PASS (PPP) | PASS (PPP) | PASS (PPP) |
| `BEH-GUI-07` | general | FAIL (FFF) | FAIL (FFF) | FAIL (FFF) | FAIL (FFF) |

Excluded because L0 did not pass: BEH-ENG-05 (L0 FAIL), BEH-GUI-07 (L0 FAIL).

- L1: no regression
- L2: no regression
- L3: no regression

Most compressed level with no regression on claude: **L3**

Only ['claude'] ran. Both hosts are required.

## Verdict

Per host: {'claude': 'L3'}.

The pilot's winner is the most compressed level that held on **both** hosts: **incomplete**.

`none` means compression is abandoned and candidate `1.0.1` stands, which is the
pre-committed outcome when L1 regresses.
