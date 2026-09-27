# Prompt Benchmark Lab

Comparing three prompt strategies — basic, few-shot, and instruction-heavy
— on the same structured-extraction task, scored against a rubric defined
before any test was run.

**Task:** extract `order_number`, `product_name`, `issue_type`,
`refund_requested`, and `sentiment` from customer order-complaint emails.

## Files

| File | Purpose |
|---|---|
| `test_cases.json` | 8 test cases (easy → very hard) with gold labels and an `edge_case_note` explaining what each one stress-tests. |
| `prompts.md` | The three full prompt texts: Basic, Few-shot, Instruction-heavy. Same schema/task in all three. |
| `scoring_criteria.md` | The rubric — Correctness / Format Compliance / Hallucination / Consistency, each 0–2 — defined **before** scoring. |
| `raw_outputs.json` | Every recorded model output: 24 primary runs (8 cases × 3 prompts) + 9 paraphrase runs used for the consistency check. |
| `score_results.py` | Applies the rubric scores to `raw_outputs.json`, checks the arithmetic, and writes `scored_results.csv` + `results_table.md`. |
| `scored_results.csv` | Generated: one row per (test case, prompt) with all 4 scores and a rationale note. |
| `results_table.md` | Generated: the comparison table, per-test-case and aggregated per-prompt. |
| `analysis.md` | Final write-up: which strategy won, and the specific failure/success patterns behind the numbers. |
| `obstacle_log.md` | What got in the way while building this and how it was handled. |

## Headline result

| Prompt | Total /54 | % |
|---|---|---|
| A — Basic | 34 | 63.0% |
| B — Few-shot | 50 | 92.6% |
| C — Instruction-heavy | 53 | 98.1% |

See `analysis.md` for the reasoning behind the numbers — in short:
basic hallucinated to fill in missing fields, few-shot generalized only to
patterns its examples covered (and failed identically to basic outside
them), and instruction-heavy's explicit rules were the only thing that
generalized to genuinely novel edge cases like sarcasm and implicit refund
requests.

## Reproducing / extending this

```bash
python3 score_results.py
```

regenerates `scored_results.csv` and `results_table.md` from
`raw_outputs.json`. To extend the benchmark with a live model: loop over
`test_cases.json`, substitute each email into the `{input}` slot of each
prompt in `prompts.md`, call the API, and append results to
`raw_outputs.json` in the same shape before re-scoring. See
`obstacle_log.md` item 1 for why this run was done manually rather than
through a live API call.
