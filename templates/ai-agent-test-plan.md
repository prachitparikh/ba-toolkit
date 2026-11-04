# AI agent test plan (dev, UAT, prod)

A test plan for an AI agent that makes decisions or takes actions: refunds, approvals, routing, replies. Normal testing assumes the same input gives the same output. An agent doesn't promise that, so this plan tests pass rates per bucket, stability across runs, and behavior after go-live, not just "all test cases passed".

Companion video: [How to Test an AI Agent Before It Goes Live (Dev to Prod)](https://www.youtube.com/watch?v=IBteCgiXc6Q)

Example used below: a fictional company, Northstar Systems, with an agent that reads refund emails and decides to approve, reject, or hand the case to a person.

---

## 1. Scope

| Item | Fill in |
|---|---|
| Agent name and version | e.g. Refund agent v0.3, model + prompt version |
| What it decides or does | e.g. approve / reject / hand to a person |
| Systems it can touch | e.g. order system (read), refund API (write), email (send) |
| Out of scope | e.g. chargebacks, fraud cases |
| Owner of this plan | Name |

## 2. Gate 1, dev: the golden set

A golden set is real cases with the right answer written next to each one. Not demo questions.

- Source: real cases from the last 3 to 6 months (anonymized).
- Size: enough to cover every bucket. Northstar used 200 refund emails.
- The right answer: the call a senior person would make, written down before the agent sees the case.
- Who labels: the BA with the people who do the work today.

| Case ID | Input (or link) | Bucket | Right answer | Labelled by |
|---|---|---|---|---|
| GS-001 | "Refund please, order 10482, jacket too small" | Easy | Approve | Senior refunds rep |
| GS-002 | Angry email, two questions, typo in the order number | Messy | Hand to a person | Senior refunds rep |
| GS-003 | Refund request for an order that was already refunded | Must-never | Reject + hand to a person | Senior refunds rep |

### Buckets (mistakes don't cost the same)

| Bucket | What goes in it | Example |
|---|---|---|
| Easy | Clear cases where the answer is obvious | The refund that's obviously fine |
| Messy | Real-world noise: anger, typos, two requests in one | The angry email with a typo in the order number |
| Must-never | Mistakes that become incidents | Refunding an order twice, refunding more than the payment |

### Pass marks, written BEFORE the first run

Set the bar first. Set it after you see the score and you're grading on a curve.

| Bucket | Pass mark | What happens to misses |
|---|---|---|
| Easy | 98% | Logged, fixed before UAT |
| Messy | 90% | Every miss must go to a person, not out the door |
| Must-never | 100% | Anything less is a no-go |

### The three-run stability check

Run the whole golden set three times with the same agent and the same cases. Any case whose answer changes between runs is unstable. Log it as a defect.

| Case ID | Run 1 | Run 2 | Run 3 | Stable? | Defect |
|---|---|---|---|---|---|
| GS-047 | Approve | Approve | Reject | No | BUG-47 |

### Harder cases with AI (optional, recommended)

Give a model 10 real cases and ask for 20 nasty variations: typos, two requests in one message, furious, overly polite, the wrong order number. A person writes the right answer for each variation before it joins the golden set. AI writes the hard questions. Humans write the right answers.

## 3. Gate 2, UAT: the weird cases and the handoffs

### Weird cases from the business

Ask the people who do the work today: "What's the weirdest request you got this year?" Add each one to the golden set with its right answer.

| Case ID | Weird case | Right answer | Added by |
|---|---|---|---|
| UAT-001 | Refund requested by replying to a newsletter | Hand to a person | Refunds team |
| UAT-002 | Photo of a receipt instead of an order number | Hand to a person | Refunds team |

### Handoff tests

When the agent isn't sure, it should pass the case to a person with the context attached, not guess.

| Check | Pass? |
|---|---|
| Unsure cases go to a person, not out the door | |
| The handoff carries the context (order, history, why it's unsure) | |
| The person can act without re-reading the whole thread | |

### One-page sign-off scorecard

| Bucket | Result | Pass mark | Met? |
|---|---|---|---|
| Easy | | 98% | |
| Messy | | 90% | |
| Must-never | | 100% | |
| Unstable cases (three-run check) | | 0 open | |
| Misses with a named owner | __ / __ | All | |

Decision: Go / No-go. Must-never under 100% means no-go. Not "we'll fix it in hypercare".

Signed off by: ______________________ Date: __________

## 4. Gate 3, prod: the world moves

An AI agent can change while nobody touches the code: the vendor updates the model, customers write differently, a new product brings new questions.

### Rerun on every change

The golden set becomes the regression test.

| Trigger | Action | Ship rule |
|---|---|---|
| Model update (vendor or internal) | Rerun the full golden set | Must-never at 100% or it doesn't ship |
| Prompt or instruction change | Rerun the full golden set | Same |
| New product or policy | Add cases, then rerun | Same |

### Weekly sample of real traffic

Every week, a person scores a sample of cases the agent handled (Northstar used 50).

| Week | Cases scored | Human overrule rate | Escalation rate | Cost per case | Notes |
|---|---|---|---|---|---|
| W1 | 50 | | | | |

Watch the trend. A drift on a Monday chart beats a call from a customer on Friday.

### Off switch

| Item | Fill in |
|---|---|
| What triggers it | e.g. one must-never mistake in production |
| What happens | The agent stops acting; all cases route to people |
| Named owner who switches it back on | Name |

If nobody knows who that is, that's your next ticket.

---

Free to use under the MIT licence. From the [BA Toolkit](https://github.com/prachitparikh/ba-toolkit) by [Prachit Parikh](https://prachitparikh.github.io/).
