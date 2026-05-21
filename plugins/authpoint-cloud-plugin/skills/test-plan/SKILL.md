---
name: test-plan
description: Generates manual QA test strategies and scenario tables. Use when creating test strategies, test scenario tables, or test plans for a feature, or when the user mentions test cases, QA strategy, test plan, or test scenarios.
---

# Test Plan Writer

Generates a test strategy document from a feature specification.

## Phase 1: Investigate Before Writing

**Complete all steps before producing any output. Final output is Markdown only — no commentary outside the document.**

The source is **specification material** the user provides (descriptions, acceptance criteria, attachments, linked docs). Do **not** read application source code in the repository to infer behavior; the test plan reflects the agreed spec, not the implementation.

### 1. Parse the input
- Extract all spec IDs (e.g., `AAAS-12345`)
- Note any explicit scope boundaries, integrations, or user types already mentioned

### 2. Read every specification
For each spec, extract:
- **Acceptance criteria** — these are your primary source of scenarios
- **Description** — surface any edge cases or constraints
- **Linked specs** — follow sub-tasks, related specs; they often add scope
- **Notes or comments** — these sometimes clarify untestable scenarios or integration constraints

### 3. Derive test signals from the spec only
From acceptance criteria, description, linked specs, and any attached specification docs, infer:
- Stated or implied validation rules → negative scenarios where the spec says what should happen on invalid input
- Branching by user type, channel, or configuration called out in the spec → separate scenario rows per branch
- Described state or lifecycle changes → state-change scenarios
- Documented errors, outcomes, or non-functional limits (retries, timeouts, expiry) → Expected Behavior wording and boundary rows **only where the spec defines them**

Do not invent boundary values or error details that are not stated or clearly implied in the specification.

### 4. Ask only what you cannot find
If after steps 1–3 you still cannot determine something critical — scope boundaries, whether a dependency is in scope — ask the user one targeted question per gap. Never ask about things already stated in the provided specification.

## Phase 2: Write the Output

Produce sections in this order:

```
## Test Strategies
### General Guidelines

## Test Plan
### Specs  (spec IDs and links)

## Test Scenarios
[one Markdown table per spec/feature area — NEVER prose or lists; see REFERENCE.md for the table format]
```

**Write the output to a Markdown file.** Use the Write tool to save the document. The file must be named `<SPEC-ID>-test-plan.md` (e.g., `AAAS-30123-test-plan.md`) and placed in the current working directory unless the user specifies otherwise.

**Every test scenario must be a row in a Markdown table. No exceptions.**
- Never write scenarios as bullet points, numbered lists, or prose paragraphs.
- If a scenario is not applicable, do not generate it at all.
- Scope exclusions are the only text allowed outside tables within the Test Scenarios section.
- **The Notes column must always be left empty in the output.** It is reserved for the QA engineer to fill in manually during test execution. Never pre-populate it with comments, reminders, or annotations.

## Phase 3: Verify Before Finishing

Check every scenario row against these standards before considering the task done:
- Describes **one specific condition** — not "valid input" but "An MFA local user provides the correct password and the correct OTP"
- Paired correctly: for every positive case, consider the inverse negative(s)
- Covers all user types in scope that can interact with the feature
- Includes boundary and limit cases (empty fields, wrong format, min/max values, expiry)
- Every acceptance criterion from the specification maps to at least one scenario row
- Any gaps or untestable items are documented above the relevant table

## Reference

- Table formats, scenario rules, coverage checklist → [references/REFERENCE.md](references/REFERENCE.md)
- Concrete example → [references/examples/otp-auth-test-strategy.md](references/examples/otp-auth-test-strategy.md)
