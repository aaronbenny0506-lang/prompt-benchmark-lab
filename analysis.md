# Analysis: Basic vs. Few-Shot vs. Instruction-Heavy

**Task:** structured extraction of `order_number`, `product_name`,
`issue_type`, `refund_requested`, `sentiment` from customer order-complaint
emails. 8 test cases, 3 prompts, scored on Correctness / Format Compliance
/ Hallucination (all 8 cases) and Consistency (3 cases, original vs.
paraphrase). Full numbers in `results_table.md`.

## Headline result

| Prompt | Total /54 | % |
|---|---|---|
| A — Basic | 34 | 63.0% |
| B — Few-shot | 50 | 92.6% |
| C — Instruction-heavy | 53 | 98.1% |

Instruction-heavy performed best overall, few-shot was a large step up from
basic, and basic was the clear loser on every dimension except raw format
validity (it almost always produced *parseable* JSON, it just didn't
produce *correct* JSON).

## Pattern 1 - Basic hallucinates to fill gaps

Basic's hallucination score (11/16) was the worst of the three, and every
loss was a concrete fabrication rather than a subtle misread:
- **TC1**: invented `product_name: "phone"` when the email never named a
  product at all (only "the screen").
- **TC3**: invented `order_number: "12345"` out of thin air when no order
  number appeared anywhere in the text.

Few-shot and instruction-heavy never fabricated a concrete fact, both
scored a clean 16/16 on hallucination. This is the single biggest
practical risk of the basic prompt: it doesn't just get answers wrong, it
gets them wrong *confidently and silently*, which is worse for a
downstream system than an obvious failure would be.

## Pattern 2 - Few-shot generalizes only as far as its examples reach

Few-shot fixed every failure mode that one of its three worked examples
directly demonstrated:
- TC1/TC3 (missing fields → `null`): fixed, because example 3 showed a
  missing order number handled with `null`.
- TC6 (no real complaint → `no_issue`): fixed, because example 2 showed
  exactly that case.
- TC2 (replacement ≠ refund): fixed, because example 1 showed that
  distinction.

But on the two edge cases **no example touched**, few-shot performed
*identically* to basic:
- **TC5 (sarcasm)**: both basic and few-shot read "Oh great, ANOTHER late
  delivery... Just wonderful" as `sentiment: "positive"`.
- **TC7 (implicit refund)**: both missed "I just want my money back" as a
  refund request, since no example used indirect phrasing.

This is the clearest evidence in the whole benchmark: few-shot prompting
teaches pattern-matching to the *specific patterns shown*, not the
underlying rule. Three examples bought four fixed edge cases and left two
completely untouched.

## Pattern 3 - Explicit rules generalize where examples don't

Instruction-heavy was the only prompt to get TC5 (sarcasm) and TC7
(implicit refund) right and in both cases the fix traces directly to a
rule written into the prompt rather than an example: an explicit
sarcasm-detection instruction, and an explicit statement that "I want my
money back" counts as a refund request even without the word "refund." It
also correctly kept the `ORD-` prefix on TC4's order number and picked a
single valid `issue_type` from a genuinely multi-issue email, both because
the prompt spelled out an exact format rule and a tie-break rule, things
no amount of example-matching guarantees for a case that doesn't closely
resemble the examples.

## Pattern 4 - More instruction has a real, if small, cost

Instruction-heavy wasn't flawless: on TC8, the hardest case (slang, no
order number, no explicit refund verb), it got every field right but
still added a one-line explanatory sentence before the JSON object,
despite the prompt explicitly saying "respond with the JSON object and
nothing else." That's a real format-compliance failure (scored 1/2, not
2/2) and it's a known failure mode of long, rule-dense prompts: on the
hardest inputs, the model sometimes feels compelled to "show its work"
even when told not to. In a production pipeline this would still need the
same defensive stripping/parsing logic as basic or few-shot — a longer
prompt reduces how often you need it, but doesn't eliminate the need for
it.

## Pattern 5 - Consistency tracks correctness, but they aren't the same thing

The consistency check (original vs. a reworded paraphrase of TC1/TC3/TC5)
showed something worth calling out explicitly: basic was inconsistent
where it was *guessing* (TC1's invented product name changed from "phone"
to "screen" between runs; TC3's invented order number changed from
"12345" to a, coincidentally correct, `null`), but it was **perfectly
consistent** on TC5, where it confidently, repeatably got the sarcasm
wrong both times. Consistency alone would have scored basic's TC5
performance the same as instruction-heavy's (2/2 either way); only
correctness reveals that basic is consistently *wrong* there. This is why
the rubric scores these as separate dimensions, a prompt can be reliably
bad, and that's a different (and in some ways worse) problem than being
randomly bad.

## Conclusion

For this task, the instruction-heavy prompt is the strategy to ship: it
was the only one to handle sarcasm and implicit-refund phrasing correctly,
never hallucinated, and was consistent across reworded inputs. Few-shot is
a reasonable fallback if prompt length is constrained, but its
reliability is bounded by how well the chosen examples happen to cover the
input distribution, every edge case not represented by an example failed
exactly as often as it did under the basic prompt. The basic prompt should
not be used for this task in production: its hallucination rate (invented
order numbers and product names) is the kind of silent, plausible-looking
error that's most dangerous in an automated pipeline, since nothing about
the output looks obviously wrong.
