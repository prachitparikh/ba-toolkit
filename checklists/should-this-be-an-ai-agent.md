# "Should this be an AI agent?" scoring sheet

Five questions to run before anyone builds an agent. Most requests don't need one. Some need rules, some need AI that recommends, and a few need an agent that acts. This sheet tells you which level a process needs, so the conversation in the meeting is about the process, not the buzzword.

Companion video: [Should This Be an AI Agent? A 5-Question Test for BAs](https://www.youtube.com/watch?v=AZLoC-rGk6Y)

---

## The three levels

| Level | What it is | Think of it as | Examples |
|---|---|---|---|
| 1. Rules | Same input, same output. A workflow, a formula, a bot that clicks the same buttons | A vending machine | Approve invoices under $500 that match a PO |
| 2. AI judgment | AI reads messy input and makes a call. A person acts on it | A translator | Label this email, pull the total off this PDF |
| 3. Agent | AI takes actions across systems, several steps, on its own | A new hire with a company card | Chase vendors by email and update the tracker |

## The five questions

Answer each one for a single process. Write the evidence, not just yes or no.

| # | Question | Answer | Evidence | What it means |
|---|---|---|---|---|
| 1 | Can you write the decision as rules on one page? | Yes / No | | Yes: build the rules (Level 1). Rules are cheaper, easier to test, and they never hallucinate. If nobody can write them because they change every week, the policy isn't decided yet. No model fixes an undecided policy |
| 2 | Is the input messy? (free-text emails, scanned PDFs, voicemails) | Yes / No | | Messy input is where AI earns its keep. If the input is a clean form, the best AI project might be fixing the form. Sometimes the right AI is a dropdown |
| 3 | Does it need to act, or just recommend? | Act / Recommend | | Reading and suggesting is Level 2. Clicking "approve" in several systems is Level 3. Every action you add is one more thing that can go wrong in production at 2 AM |
| 4 | The undo test: if it gets it wrong, can you undo it? | Easy undo / No undo | | A draft a person reviews: easy undo. A refund, a deleted record, an email to 10,000 customers: no undo. No undo means a person approves the action. Every time |
| 5 | Can you measure "better" today? | Yes / No | Baseline: time per case ___ · error rate ___ · cost per case ___ | Measure before anything gets built. No baseline, no business case |

## Result

| Process | Q1 | Q2 | Q3 | Q4 | Q5 | Level | Guardrail |
|---|---|---|---|---|---|---|---|
| Invoice matching (example) | Rules fit on one page | Clean | n/a | n/a | Baseline taken | 1 · Rules, no agent | None needed |
| Refund emails (example) | No | Messy | Recommend | Refund = no undo | Baseline taken | 2 · AI recommends | A person approves |
| Chasing vendors for missing invoices (example) | No | Messy replies | Acts (emails + tracker) | Emails = no undo | Baseline taken | 3 · Agent | A person approves the first message to each vendor |

Examples use a fictional company, Northstar Systems.

## The bonus check: make the AI argue against it

Paste the process into an AI model and ask it to argue AGAINST using an agent. Not for it. Models are good at building whatever case you ask for, so ask for the one you need to hear. If its best argument holds up, you just saved a budget line.

## What to say in the meeting

Don't walk in with a flat "no". Say: "Let's start one level down and earn the next one." Rules first. Then AI that recommends. Then an agent that acts, once the Level 2 numbers say it's ready.

## What changes in your requirements

- Level 2: acceptance criteria become pass rates (for example, 98% on easy cases, 90% on messy ones).
- Level 3: you also need the "never" rules, what the agent must never do on its own. See the [AI agent job description template](../templates/ai-agent-job-description.md).

---

Free to use under the MIT licence. From the [BA Toolkit](https://github.com/prachitparikh/ba-toolkit) by [Prachit Parikh](https://prachitparikh.github.io/).
