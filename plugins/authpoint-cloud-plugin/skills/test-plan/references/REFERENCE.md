# Test Plan Writer Reference

Detailed reference for table formats, scenario rules, and coverage guidance.

---

## 1. Table Format

All test scenarios must use the standard table format.

The last column is for evidence or notes added during execution.

| Scenarios | Expected Behavior | Result | Notes |
|---|---|---|---|
| [description] | [outcome] | | |

---

## 2. Scenario Rules

1. **Never use `Positive` / `Negative` labels** — scenarios are described in plain English without such prefixes.
2. **Only generate a boundary scenario if the boundary is explicitly defined** in the Jira story, acceptance criteria, or linked specification. Never invent boundary values.
3. **Plain English, user perspective**: _"An MFA local user provides the correct password and the correct OTP"_
4. **Expected Behavior is always explicit**: _"Successfully authenticated"_ or _"The authentication has been denied"_
5. **Leave Result and Notes columns empty** — they are filled during test execution, not planning.
6. **Never generate a row for a scenario that cannot be tested.** If an entire group is untestable, document it as plain text above the table instead: _"Items that cannot be tested: 1 - X depends on Y (still under development)."_

---

## 3. Coverage Checklist

For every feature area, consider all of the following during investigation before writing scenarios. Apply only what is relevant to the feature in scope.

**User types**
- [ ] All user types that can interact with this feature (e.g. local, azure, ldap, non-mfa)
- [ ] Users with restricted or blocked access
- [ ] Users with different permission levels or roles

**Input validity**
- [ ] Correct inputs → success
- [ ] Incorrect inputs → expected failure
- [ ] Empty or missing required fields → rejection
- [ ] Wrong format or data type → rejection
- [ ] Boundary values (min, max, exact limits)
- [ ] Reused, expired, or already-consumed tokens/codes → rejection

**State & transitions**
- [ ] Happy path from initial state to final state
- [ ] Each valid state transition
- [ ] Invalid or out-of-order transitions
- [ ] Timeout or expiry behaviour
- [ ] Retry limits and auto-blocking

**Backend / data layer** (for data-layer stories)
- [ ] Record created correctly
- [ ] Record updated correctly
- [ ] Record deleted correctly
- [ ] Error response when payload is invalid or malformed
- [ ] No side effects on unrelated records

---

