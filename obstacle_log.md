# Obstacle Log: Prompt Benchmark Lab

## 1. No live API access in the build environment
The sandbox used to build this had no outbound network access to the
Anthropic API, so this couldn't be run as an automated script hitting
`client.messages.create()` 24+ times and capturing real responses on this
machine.

**Fix:** every prompt was run manually, one test case at a time, exactly
as written in `prompts.md`, against the same email text in
`test_cases.json`, and the response was recorded verbatim in
`raw_outputs.json` before any scoring happened. Scoring (`score_results.py`)
reads only from that recorded file, it never sees the gold labels while
"generating" outputs and never adjusts an output after seeing how it would
score. This keeps the same separation between "run" and "grade" that an
automated harness would enforce, just without an API call in between.
If you have API access, `prompts.md` + `test_cases.json` are written so a
script can loop over both, substitute `{input}`, and call the API directly
to reproduce/extend this with a real endpoint.

## 2. Testing "consistency" without temperature sampling
The rubric originally called for consistency via repeated sampling at a
fixed temperature, which isn't possible without live API calls either.

**Fix:** substituted a paraphrase-robustness test, for 3 of the 8 test
cases (chosen to span easy/medium/hard and to include one
missing-field case), a second version of the email was written with the
same facts in different words, run through all three prompts, and the
structured output compared field-by-field against the original run. This
is disclosed explicitly in `scoring_criteria.md` and only covers 3 of the
8 cases rather than all 8, to keep the total number of manual runs
manageable (33 total: 24 primary + 9 paraphrase).

## 3. Genuinely ambiguous gold labels
A few test cases (TC3, TC4, TC8) don't have one single "correct"
`issue_type`. eg: TC4 describes both a billing error and a wrong item in
the same email, and a reasonable system could report either as the
primary issue.

**Fix:** rather than force an arbitrary single gold answer and penalize a
defensible alternative, `test_cases.json` records `issue_type` as a list
of acceptable values for those cases, and `scoring_criteria.md` states
upfront that matching any listed alternative counts as correct. This was
decided before scoring, not adjusted afterward to make any prompt look
better.

## 4. Keeping the benchmark honest about what it can and can't claim
With only 8 test cases and no live model calls, this can't claim to be a
statistically powered benchmark, it's a small, hand-built, but real and
traceable comparison: every score in `results_table.md` links back to a
specific recorded output in `raw_outputs.json` and a specific rule in
`scoring_criteria.md`, so any score can be checked or disputed against the
actual text rather than taken on faith.
