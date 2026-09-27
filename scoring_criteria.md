# Scoring Criteria

Defined before scoring any output, so grading is repeatable rather than a
post-hoc gut call. Every output is scored on four dimensions, each 0–2,
for a max of 8 points per (prompt, test case).

## 1. Correctness (0-2)
How well the extracted fields match the gold label.
- **2** : All 5 fields match gold, or match one of the pre-declared
  acceptable alternatives for genuinely ambiguous fields (TC3, TC4, TC8
  each have a documented acceptable-alternative field).
- **1** : Exactly one field is wrong and it is not an acceptable
  alternative (eg: wrong sentiment, wrong refund_requested, or an
  invented value for a field that should be null).
- **0** : Two or more fields wrong.

## 2. Format Compliance (0-2)
Whether the output is a clean, parseable JSON object matching the schema.
- **2** : Valid JSON, exactly the 5 expected keys, no markdown fences, no
  extra commentary, correct types (string/null, boolean, enum string).
- **1** : Valid JSON with a recoverable issue: wrapped in a ```json fence,
  one extra/missing key, or an enum value outside the allowed list (eg:
  "Billing Issue" instead of "billing_error").
- **0** : Not parseable as JSON at all, or missing more than one required
  key.

## 3. Hallucination (0-2, higher = less hallucination)
Whether the model invented information not present in, or not reasonably
inferable from, the email.
- **2** : No fabrication; correctly returns null for anything not stated.
- **1** : One minor unsupported inference stated as fact (eg: guessing a
  product category from a vague clue).
- **0** : Fabricates a concrete, checkable fact that isn't in the text at
  all (eg: invents an order number, invents a product name out of thin
  air, invents a refund request that was never made).

## 4. Consistency (0-2)
Whether the prompt produces the same structured result for the same
underlying facts when the wording changes but the facts don't. Measured
by writing a paraphrased variant of a subset of test cases (same facts,
different phrasing) and comparing the two outputs field-by-field.
- **2** : All 5 fields identical between original and paraphrase.
- **1** : 1 field differs.
- **0** : 2+ fields differ.

Consistency was checked on 3 of the 8 test cases (TC1 easy, TC3 medium/
missing-field, TC5 hard/sarcasm), chosen to span the difficulty range,
rather than all 8, to keep the number of completions manageable; this
subset and the reasoning is disclosed here and in `obstacle_log.md` rather
than left implicit.

## Aggregation
Per (prompt, test case): sum of the 4 dimension scores (0–8).
Per prompt: mean score across the 8 test cases, plus the sum of each
dimension separately, reported in `results_table.md`.
