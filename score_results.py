#!/usr/bin/env python3
"""
Scores every run in raw_outputs.json against test_cases.json using the
rubric in scoring_criteria.md, and writes:
  - scored_results.csv   (one row per prompt x test case)
  - results_table.md     (human-readable comparison table)

Correctness / Format / Hallucination scores below are the author's manual
judgment calls per the rubric (see scoring_criteria.md) - this script's
job is to aggregate them consistently and check the arithmetic, not to
auto-grade free text.
"""
import json
import csv
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent

# Manually-assigned rubric scores per (test_case, prompt), with a one-line
# rationale so every score is traceable back to the raw output.
SCORES = {
    ("TC1", "A_basic"):            dict(correctness=1, format=2, hallucination=0,
        note="Invented product_name 'phone' — never stated in the email."),
    ("TC1", "B_fewshot"):          dict(correctness=2, format=2, hallucination=2,
        note="All fields correct; product_name correctly left null."),
    ("TC1", "C_instruction_heavy"):dict(correctness=2, format=2, hallucination=2,
        note="All fields correct; explicit no-inference rule worked."),

    ("TC2", "A_basic"):            dict(correctness=1, format=2, hallucination=2,
        note="refund_requested=true, but customer asked for a replacement, not a refund."),
    ("TC2", "B_fewshot"):          dict(correctness=2, format=2, hallucination=2,
        note="Correctly matched the 'replacement not refund' example pattern."),
    ("TC2", "C_instruction_heavy"):dict(correctness=2, format=2, hallucination=2,
        note="Correct; explicit refund-vs-replacement rule worked."),

    ("TC3", "A_basic"):            dict(correctness=1, format=2, hallucination=0,
        note="Fabricated order_number '12345' though none was given anywhere in the text."),
    ("TC3", "B_fewshot"):          dict(correctness=2, format=2, hallucination=2,
        note="order_number correctly null; issue_type='late_delivery' is an accepted alternative."),
    ("TC3", "C_instruction_heavy"):dict(correctness=2, format=2, hallucination=2,
        note="order_number correctly null; issue_type='missing_item' is an accepted alternative."),

    ("TC4", "A_basic"):            dict(correctness=0, format=1, hallucination=2,
        note="Dropped the 'ORD-' prefix (order_number wrong) and returned a combined, invalid issue_type string."),
    ("TC4", "B_fewshot"):          dict(correctness=1, format=2, hallucination=2,
        note="Picked a single valid issue_type, but still dropped the 'ORD-' prefix."),
    ("TC4", "C_instruction_heavy"):dict(correctness=2, format=2, hallucination=2,
        note="Kept the 'ORD-' prefix and picked a single valid issue_type per the tie-break rule."),

    ("TC5", "A_basic"):            dict(correctness=1, format=2, hallucination=2,
        note="Misread sarcastic 'great'/'wonderful' as positive sentiment."),
    ("TC5", "B_fewshot"):          dict(correctness=1, format=2, hallucination=2,
        note="Same sarcasm miss as Basic — no example in the prompt covers sarcasm."),
    ("TC5", "C_instruction_heavy"):dict(correctness=2, format=2, hallucination=2,
        note="Correctly flagged sentiment negative per the explicit sarcasm rule."),

    ("TC6", "A_basic"):            dict(correctness=1, format=2, hallucination=1,
        note="Forced issue_type='other' onto an email with no actual complaint."),
    ("TC6", "B_fewshot"):          dict(correctness=2, format=2, hallucination=2,
        note="Matched the 'no_issue' example pattern correctly."),
    ("TC6", "C_instruction_heavy"):dict(correctness=2, format=2, hallucination=2,
        note="Correct; explicit no_issue rule worked."),

    ("TC7", "A_basic"):            dict(correctness=1, format=2, hallucination=2,
        note="Missed the implicit refund request ('I just want my money back')."),
    ("TC7", "B_fewshot"):          dict(correctness=1, format=2, hallucination=2,
        note="Same implicit-refund miss — no example covers indirect refund phrasing."),
    ("TC7", "C_instruction_heavy"):dict(correctness=2, format=2, hallucination=2,
        note="Correctly caught the indirect refund phrase per the explicit rule."),

    ("TC8", "A_basic"):            dict(correctness=0, format=1, hallucination=2,
        note="Wrapped output in a ```json fence; also missed product_name ('subscription' is explicitly stated) and wrongly set refund_requested=true."),
    ("TC8", "B_fewshot"):          dict(correctness=1, format=2, hallucination=2,
        note="Got product_name right, but still wrongly set refund_requested=true — 'sort this out' isn't an explicit refund ask."),
    ("TC8", "C_instruction_heavy"):dict(correctness=2, format=1, hallucination=2,
        note="All fields correct, but added a one-line explanation before the JSON despite 'respond with JSON and nothing else'."),
}

# Consistency scores (original vs. paraphrase), only run for TC1/TC3/TC5.
CONSISTENCY = {
    ("TC1", "A_basic"): dict(score=1, note="product_name differed: 'phone' vs 'screen' across the two runs."),
    ("TC1", "B_fewshot"): dict(score=2, note="Identical output on both runs."),
    ("TC1", "C_instruction_heavy"): dict(score=2, note="Identical output on both runs."),

    ("TC3", "A_basic"): dict(score=0, note="order_number differed (fabricated '12345' vs correct null) and issue_type differed."),
    ("TC3", "B_fewshot"): dict(score=2, note="Identical output on both runs."),
    ("TC3", "C_instruction_heavy"): dict(score=2, note="Identical output on both runs."),

    ("TC5", "A_basic"): dict(score=2, note="Consistently (wrongly) reads the sarcasm as positive both times."),
    ("TC5", "B_fewshot"): dict(score=2, note="Consistently (wrongly) reads the sarcasm as positive both times."),
    ("TC5", "C_instruction_heavy"): dict(score=2, note="Consistently (correctly) reads the sarcasm as negative both times."),
}

PROMPTS = ["A_basic", "B_fewshot", "C_instruction_heavy"]
TEST_CASES = [f"TC{i}" for i in range(1, 9)]
CONSISTENCY_CASES = ["TC1", "TC3", "TC5"]


def main():
    rows = []
    for tc in TEST_CASES:
        for p in PROMPTS:
            s = SCORES[(tc, p)]
            cons = CONSISTENCY.get((tc, p))
            total_partial = s["correctness"] + s["format"] + s["hallucination"]
            rows.append({
                "test_case": tc, "prompt": p,
                "correctness": s["correctness"], "format": s["format"],
                "hallucination": s["hallucination"],
                "consistency": cons["score"] if cons else "",
                "subtotal_(C+F+H)": total_partial,
                "note": s["note"],
                "consistency_note": cons["note"] if cons else "",
            })

    with open(HERE / "scored_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Per-prompt aggregates
    agg = defaultdict(lambda: defaultdict(int))
    for r in rows:
        p = r["prompt"]
        agg[p]["correctness"] += r["correctness"]
        agg[p]["format"] += r["format"]
        agg[p]["hallucination"] += r["hallucination"]
    for tc in CONSISTENCY_CASES:
        for p in PROMPTS:
            agg[p]["consistency"] += CONSISTENCY[(tc, p)]["score"]

    lines = ["# Results Table\n"]
    lines.append("## Per-test-case scores (Correctness / Format / Hallucination, each 0-2)\n")
    header = "| Test Case | " + " | ".join(f"{p} (C/F/H)" for p in PROMPTS) + " |"
    sep = "|---|" + "---|" * len(PROMPTS)
    lines.append(header)
    lines.append(sep)
    for tc in TEST_CASES:
        cells = []
        for p in PROMPTS:
            s = SCORES[(tc, p)]
            cells.append(f"{s['correctness']}/{s['format']}/{s['hallucination']}")
        lines.append(f"| {tc} | " + " | ".join(cells) + " |")

    lines.append("\n## Consistency check (original vs. paraphrased input, 0-2), n=3 test cases\n")
    lines.append("| Test Case | " + " | ".join(PROMPTS) + " |")
    lines.append(sep)
    for tc in CONSISTENCY_CASES:
        cells = [str(CONSISTENCY[(tc, p)]["score"]) for p in PROMPTS]
        lines.append(f"| {tc} | " + " | ".join(cells) + " |")

    lines.append("\n## Prompt totals\n")
    lines.append("| Prompt | Correctness /16 | Format /16 | Hallucination /16 | Consistency /6 | Total /54 | % |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in PROMPTS:
        c, f_, h, cons = agg[p]["correctness"], agg[p]["format"], agg[p]["hallucination"], agg[p]["consistency"]
        total = c + f_ + h + cons
        pct = round(100 * total / 54, 1)
        lines.append(f"| {p} | {c} | {f_} | {h} | {cons} | {total} | {pct}% |")

    (HERE / "results_table.md").write_text("\n".join(lines) + "\n")
    print("Wrote scored_results.csv and results_table.md")
    for p in PROMPTS:
        c, f_, h, cons = agg[p]["correctness"], agg[p]["format"], agg[p]["hallucination"], agg[p]["consistency"]
        print(p, "->", c + f_ + h + cons, "/54")


if __name__ == "__main__":
    main()
