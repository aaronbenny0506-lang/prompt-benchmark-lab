# Prompt Versions

Task: extract structured data from a customer order-complaint email.
Target schema (identical across all three prompts):

```json
{
  "order_number": "string or null",
  "product_name": "string or null",
  "issue_type": "damaged | wrong_item | late_delivery | missing_item | billing_error | no_issue | other",
  "refund_requested": true,
  "sentiment": "positive | neutral | negative"
}
```

---

## Prompt A — Basic (minimal instruction)

```
Extract the order number, product name, issue type, whether a refund was
requested, and the sentiment from this customer email. Return the answer
as JSON.

Email: {input}
```

No field definitions, no enum list, no formatting rules, no examples.

---

## Prompt B — Few-shot (examples, light instruction)

```
Extract structured data from customer order-complaint emails. Return a
JSON object with these keys: order_number, product_name, issue_type,
refund_requested, sentiment.

Example 1
Email: "Order #1002 came with a broken zipper on the backpack. Send me a
new one please."
Output: {"order_number": "1002", "product_name": "backpack",
"issue_type": "damaged", "refund_requested": false, "sentiment": "negative"}

Example 2
Email: "Thanks for the fast delivery on order 884, the mug looks great!"
Output: {"order_number": "884", "product_name": "mug", "issue_type":
"no_issue", "refund_requested": false, "sentiment": "positive"}

Example 3
Email: "I ordered a desk lamp last week and it still hasn't shown up, no
order number handy. Kind of annoyed at this point."
Output: {"order_number": null, "product_name": "desk lamp", "issue_type":
"late_delivery", "refund_requested": false, "sentiment": "negative"}

Now do the same for this email:
Email: "{input}"
Output:
```

Three examples, chosen to demonstrate: a normal case, a positive/no-issue
case, and a missing-order-number case — but no example demonstrates
sarcasm, multi-issue emails, or implicit refund requests, so those edge
cases are unsupported by any example.

---

## Prompt C — Instruction-heavy (detailed, explicit guidance)

```
You are a support-ticket data extraction system. Read the customer email
below and return ONLY a single JSON object — no markdown fences, no
commentary before or after — with exactly these five keys:

- "order_number": the order number as a string, exactly as written
  (keep any prefix like "ORD-"). If no order number appears anywhere in
  the email, use null. Never invent or guess an order number.

- "product_name": the specific product the complaint is about, in lowercase,
  as named in the email. If no product is explicitly named, use null. Do
  not infer a product type from context (e.g. do not assume "phone" just
  because a "screen" is mentioned).

- "issue_type": exactly one of: "damaged", "wrong_item", "late_delivery",
  "missing_item", "billing_error", "no_issue", "other".
  - Use "no_issue" if the email contains no complaint (e.g. a thank-you
    or praise message).
  - If more than one issue is described, choose the issue that is stated
    first or that the customer emphasizes most, and pick a single value —
    never combine categories.

- "refund_requested": true or false. Set true if the customer explicitly
  asks for a refund, their money back, or reversal of a charge — including
  indirect phrasing like "I want my money back". Set false if they ask for
  a replacement, repair, or fix, or if no request is made at all. Do not
  default to true just because the customer is upset.

- "sentiment": "positive", "neutral", or "negative", based on the writer's
  actual underlying emotional state — not surface politeness or word
  choice. Watch for sarcasm (e.g. "great, ANOTHER late delivery" is
  negative, not positive).

Respond with the JSON object and nothing else.

Email: "{input}"
```

Full field definitions, explicit enum list, explicit null-handling rules,
an explicit sarcasm rule, an explicit multi-issue tie-break rule, and an
explicit refund-inference rule — but no worked examples.
