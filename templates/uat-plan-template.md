# UAT Plan: [Project name]

> Template from the [BA Toolkit by Prachit Parikh](https://github.com/prachitparikh/ba-toolkit). Replace everything in [brackets].

| Item | Detail |
|---|---|
| Project | [Name and release or wave] |
| Document owner | [BA name] |
| Business sign-off owner | [Name, role] |
| Version / date | [v0.1, YYYY-MM-DD] |
| Status | [Draft / In review / Approved] |

## 1. Purpose

[One paragraph: what business change is being tested and why UAT matters for this release. Example: "Confirm the new order-to-cash process lets the credit team hold, review and release orders correctly before go-live on 15 March."]

## 2. Scope

### In scope
| # | Business process / feature | Requirement IDs |
|---|---|---|
| 1 | [Create and submit sales order] | [REQ-001 to REQ-012] |

### Out of scope
- [Performance testing, done separately by IT]
- [Legacy report X, retired at go-live]

## 3. Entry criteria (UAT starts only when all are true)
- [ ] SIT complete with no open Critical or High defects
- [ ] UAT environment refreshed with masked production-like data on [date]
- [ ] Test scripts reviewed and approved by business owners
- [ ] Testers have access and have completed a 30-minute walkthrough
- [ ] Data validation checks run and passed (see `sql/data-validation-checks.sql`)

## 4. Exit criteria (UAT is done only when all are true)
- [ ] 100% of in-scope test cases executed
- [ ] At least [95]% passed; every failure has a logged defect
- [ ] No open Critical or High defects; Medium defects have an agreed workaround and fix date
- [ ] Traceability matrix updated: every requirement linked to a passed test
- [ ] Business sign-off obtained in writing

## 5. Roles

| Role | Name | Responsibility |
|---|---|---|
| UAT lead / BA | [Name] | Plan, scripts, daily status, defect triage |
| Business testers | [Names] | Execute scripts, log results and defects |
| Business owner | [Name] | Decide severity disputes, final sign-off |
| Dev / support | [Names] | Fix defects, redeploy, environment support |

## 6. Schedule

| Phase | Dates | Notes |
|---|---|---|
| Script review | [dates] | |
| Cycle 1 | [dates] | Full scope |
| Fix and retest | [dates] | |
| Cycle 2 (regression) | [dates] | Critical paths only |
| Sign-off | [date] | |

## 7. Test cases

| TC ID | Requirement | Scenario | Steps | Expected result | Tester | Status |
|---|---|---|---|---|---|---|
| TC-001 | REQ-004 | Order over credit limit is held | 1. Create order for customer C100 with $60,000 value. 2. Submit. | Order status = HOLD; credit team notified within 5 minutes | [Name] | [Not run] |

## 8. Defect management

| Severity | Definition | Target fix |
|---|---|---|
| Critical | Blocks a core business process, no workaround | Same day |
| High | Core process works only with a painful workaround | 2 business days |
| Medium | Non-core issue with a reasonable workaround | Before go-live or agreed date |
| Low | Cosmetic | Backlog |

- Daily triage at [time] with BA, business owner and dev lead.
- Every defect needs steps, expected vs actual result, screenshot or query, and the linked requirement.

## 9. Risks and assumptions

| Risk | Impact | Mitigation |
|---|---|---|
| [Testers pulled into month-end close] | [Cycle slips] | [Book testers now; backup tester per process] |

## 10. Sign-off

| Name | Role | Decision | Date |
|---|---|---|---|
| [Name] | Business owner | [Approved / Approved with conditions / Rejected] | [date] |
