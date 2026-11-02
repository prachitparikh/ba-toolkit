# Agent-ready requirements checklist

> From the [BA Toolkit by Prachit Parikh](https://github.com/prachitparikh/ba-toolkit). Background: [AI agents can write the code now. The bottleneck is the requirements.](https://medium.com/@prachit.parikh/ai-agents-can-write-the-code-now-the-bottleneck-is-the-requirements-5f7a1ee86362)

AI coding agents and spec-driven tools (GitHub Spec Kit, AWS Kiro and others) build exactly what you write, at machine speed, and they rarely stop to ask what you meant. Run every requirement through this list before it goes to an agent or an AI-assisted developer.

## The checklist

- [ ] **One behavior per requirement.** "Validate, save and notify" is three requirements.
- [ ] **Trigger, condition, outcome.** When X happens, if Y is true, the system does Z.
- [ ] **Numbers, not adjectives.** "Fast" becomes "under 2 seconds for 95% of requests."
- [ ] **Named data.** "Customer status" becomes "customer.status, one of Active, On Hold, Closed."
- [ ] **Unhappy paths written down.** Blank fields, timeouts, duplicates, permissions.
- [ ] **At least one concrete example.** Input in, output out.
- [ ] **A test you could run.** If you can't say how you'd prove it, it isn't finished.
- [ ] **Traceable.** Linked to its source (workshop, regulation, ticket) and to its test case.

## EARS patterns (Easy Approach to Requirements Syntax)

| Pattern | Template |
|---|---|
| Event-driven | WHEN [trigger], THE SYSTEM SHALL [response]. |
| State-driven | WHILE [state], THE SYSTEM SHALL [response]. |
| Unwanted behavior | IF [condition], THEN THE SYSTEM SHALL [response]. |
| Optional feature | WHERE [feature is included], THE SYSTEM SHALL [response]. |
| Ubiquitous | THE SYSTEM SHALL [response]. |

## Before and after

**Before:** "Flag suspicious transactions for review."

**After:** "WHEN a payment over $10,000 is created for a beneficiary added in the last 24 hours, THE SYSTEM SHALL set review_status to PENDING_REVIEW and block release until a user with the Reviewer role approves it.
Example: a $12,500 payment to a beneficiary added 3 hours ago is held; the same payment to a beneficiary added 30 days ago is released."

## Questions to ask before handing a spec to an agent

1. What should happen when the data is missing or wrong?
2. Who is allowed to do this, and who isn't?
3. What does "done" look like in numbers?
4. Which existing behavior must not change?
5. How will we know, with data, that the agent built what the business meant?
