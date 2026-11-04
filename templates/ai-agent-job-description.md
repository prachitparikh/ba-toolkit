# AI agent job description template

"Handle refunds" is not a requirement. We wouldn't give a new hire a company card with a one-line job description, so don't give one to software that never sleeps. This template is the one page every AI agent needs before it touches a real system: what it does alone, what needs a person, what it must never do, plus the two requirements almost everyone forgets (a budget and an off switch).

Companion video: [Write the "Never" Rules: Guardrail Requirements for AI Agents](https://www.youtube.com/@PrachitParikh1)

Example used below: a fictional company, Northstar Systems, and its refund agent.

---

## 0. Owner

| Item | Fill in |
|---|---|
| Agent name | e.g. Refund agent |
| Single owner (one name, not a team) | e.g. Dana R., Refunds lead |
| Business purpose | e.g. resolve simple refund requests within policy |

Every hire has a manager. So does every agent.

## 1. Permission matrix

Rows are actions. Every action lands in exactly one column.

| Action | Do it alone | Ask first | Never | Blast radius (customers · money · undo?) |
|---|---|---|---|---|
| Read order history | ✓ | | | None · $0 · n/a |
| Draft a reply | ✓ | | | 1 customer · $0 · yes |
| Refund under $50 on a single paid order | ✓ | | | 1 customer · < $50 · no |
| Refund $50 to $500 | | ✓ | | 1 customer · up to $500 · no |
| Refund more than the customer paid | | | ✓ | 1 customer · any · no |
| Change bank details | | | ✓ | 1 customer · any · no |
| Email more than one customer at once | | | ✓ | All customers · reputational · no |

Size each permission to the blast radius, not to how clever the model looked in the demo.

## 2. "Never" rules as acceptance criteria

"Never" isn't a polite request. Write each one so it can be tested. In testing, never means 100%. Not "mostly never".

| ID | Given | When | Then |
|---|---|---|---|
| NEVER-01 | An order that was already refunded | A refund is requested | The agent does not issue it and routes the case to a person |
| NEVER-02 | A refund amount greater than the amount paid | The agent prepares the refund | The agent does not issue it and routes the case to a person |
| NEVER-03 | Any request to change bank details | The agent receives it | The agent does not change them and routes the case to a person |

## 3. Approval limits (the trap in "ask first")

If the agent asks a person to approve 200 refunds a day, by lunchtime nobody is reading them. That's a rubber stamp with extra steps.

| Item | Fill in |
|---|---|
| Max approvals per reviewer per day | e.g. 25 |
| What happens when the queue is bigger | Raise the "alone" threshold or narrow the scope. The threshold is wrong, not the person |

## 4. Budget (forgotten requirement #1)

| Limit | Value | When it's hit |
|---|---|---|
| Max actions per hour | e.g. 120 | Pause and alert the owner |
| Max cost per case | e.g. $0.40 | Stop and hand to a person |
| Max retries per step | e.g. 3 | Give up and hand to a person |

An agent stuck in a loop at 3 AM doesn't get tired. It gets expensive.

## 5. Handover triggers (numbers, not adjectives)

"Low confidence" is a vague word. "Confidence below 80%" is a requirement.

| Trigger | Value |
|---|---|
| Confidence below | e.g. 80% |
| Customer mentions | e.g. a lawyer, a complaint to a regulator |
| Amount over | e.g. the "alone" limit |
| Same customer contacts within a day | e.g. 3rd time |

The handoff carries the context (what it saw, what it checked, why it stopped), so the person isn't starting from "see below" with nothing below.

## 6. Identity and log

| Item | Fill in |
|---|---|
| Runs as | Its own service account, not a person's login |
| Permissions | Only what the matrix needs |
| Every action logged with | What it saw, what it did, and why (which rule matched) |
| Who reviews the log, how often | e.g. owner, weekly |

When Audit asks who approved a refund, "the agent, probably" is not an answer anyone enjoys.

## 7. Off switch (forgotten requirement #2)

| Item | Fill in |
|---|---|
| Who can stop it (names) | e.g. Dana R., Sam K. |
| What happens to work in flight | Goes to a person's queue |
| Who signs it back on (name) | e.g. Dana R. |
| How to stop it (steps or link) | |

If the answer is "IT, I think", that's not a kill switch. That's a rumor.

## 8. Tests in UAT and in prod

| Test | Where | How often | Expected |
|---|---|---|---|
| Every NEVER rule | UAT and prod | Every model or prompt change | 100% |
| Canary: a test order in a test account, already refunded, with a new refund request | Prod | Weekly | The agent refuses and routes to a person. If it ever pays it, the alarm goes off |

## 9. Red-team the rules with AI (recommended)

Give an AI model this page and ask it to find a request that sneaks around a "never". Example it may find: split a $900 refund into two $450 refunds, both under the $500 approval limit. Every loophole it finds becomes a new rule:

| ID | New rule |
|---|---|
| NEVER-08 | Limits apply to the total per order, not per transaction |

---

Free to use under the MIT licence. From the [BA Toolkit](https://github.com/prachitparikh/ba-toolkit) by [Prachit Parikh](https://prachitparikh.github.io/).
