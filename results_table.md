# Results Table

## Per-test-case scores (Correctness / Format / Hallucination, each 0-2)

| Test Case | A_basic (C/F/H) | B_fewshot (C/F/H) | C_instruction_heavy (C/F/H) |
|---|---|---|---|
| TC1 | 1/2/0 | 2/2/2 | 2/2/2 |
| TC2 | 1/2/2 | 2/2/2 | 2/2/2 |
| TC3 | 1/2/0 | 2/2/2 | 2/2/2 |
| TC4 | 0/1/2 | 1/2/2 | 2/2/2 |
| TC5 | 1/2/2 | 1/2/2 | 2/2/2 |
| TC6 | 1/2/1 | 2/2/2 | 2/2/2 |
| TC7 | 1/2/2 | 1/2/2 | 2/2/2 |
| TC8 | 0/1/2 | 1/2/2 | 2/1/2 |

## Consistency check (original vs. paraphrased input, 0-2), n=3 test cases

| Test Case | A_basic | B_fewshot | C_instruction_heavy |
|---|---|---|---|
| TC1 | 1 | 2 | 2 |
| TC3 | 0 | 2 | 2 |
| TC5 | 2 | 2 | 2 |

## Prompt totals

| Prompt | Correctness /16 | Format /16 | Hallucination /16 | Consistency /6 | Total /54 | % |
|---|---|---|---|---|---|---|
| A_basic | 6 | 14 | 11 | 3 | 34 | 63.0% |
| B_fewshot | 12 | 16 | 16 | 6 | 50 | 92.6% |
| C_instruction_heavy | 16 | 15 | 16 | 6 | 53 | 98.1% |
