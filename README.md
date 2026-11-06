# BA Toolkit by Prachit Parikh

Free, copy-ready templates for business analysts: acceptance criteria, UAT plans, data mapping, traceability, SQL data validation, and requirements that hold up when an AI agent is the one reading them.

I'm [Prachit Parikh](https://prachitparikh.github.io/), a business analyst. I built these because I kept rewriting the same documents from scratch on every project. They're plain Markdown, CSV and SQL, so they open anywhere, diff cleanly in Git, and paste straight into Confluence, Jira, Excel or Google Sheets.

## What's inside

| File | Use it for |
|---|---|
| [`templates/acceptance-criteria-template.md`](templates/acceptance-criteria-template.md) | Writing acceptance criteria testers can't misread: five checks, vague-word swaps, Given/When/Then with real data, unhappy paths, IDs linked to tests |
| [`templates/uat-plan-template.md`](templates/uat-plan-template.md) | Planning user acceptance testing: scope, entry and exit criteria, roles, schedule, defect rules, sign-off |
| [`templates/data-mapping-template.csv`](templates/data-mapping-template.csv) | Field-by-field source-to-target mapping for migrations and integrations |
| [`templates/traceability-matrix-template.csv`](templates/traceability-matrix-template.csv) | Linking every requirement to its design, test cases, defects and sign-off |
| [`sql/data-validation-checks.sql`](sql/data-validation-checks.sql) | Seven SQL checks to run before anyone trusts a report or signs UAT |
| [`checklists/agent-ready-requirements.md`](checklists/agent-ready-requirements.md) | Writing requirements precise enough for AI coding agents and spec-driven tools |
| [`examples/revenue-reconciliation/`](examples/revenue-reconciliation/) | A worked example you can run: data, SQL and tests that bridge a $48,300 gap between a revenue dashboard and the finance ledger |
| [`templates/ai-agent-test-plan.md`](templates/ai-agent-test-plan.md) | Testing an AI agent from dev to prod: golden set, buckets, pass marks set before the first run, three-run stability check, UAT weird cases and handoffs, one-page sign-off, prod reruns and weekly sampling |
| [`checklists/should-this-be-an-ai-agent.md`](checklists/should-this-be-an-ai-agent.md) | Deciding whether a process needs rules, AI that recommends, or an agent: five questions, three levels, the undo test |
| [`templates/ai-agent-job-description.md`](templates/ai-agent-job-description.md) | The one-page job description every AI agent needs: permission matrix (alone / ask first / never), blast radius, budget, handover triggers, log, off switch, one owner |

## PDF versions

Prefer something you can print or hand to a stakeholder? Formatted PDFs of the main templates:

- [Acceptance criteria template (PDF)](pdf/prachit-parikh-acceptance-criteria-template.pdf)
- [UAT plan template (PDF)](pdf/prachit-parikh-uat-plan-template.pdf)
- [7 SQL data validation checks (PDF)](pdf/prachit-parikh-sql-data-validation-checks.pdf)
- [Agent-ready requirements checklist (PDF)](pdf/prachit-parikh-agent-ready-requirements-checklist.pdf)

The same PDFs are on [my website](https://prachitparikh.github.io/#toolkit). New templates land here most weeks, each with a PDF.

## How to use it

1. Click **Code → Download ZIP**, or copy the single file you need.
2. Replace the example rows with your project's data. Every template ships with one realistic example row so you can see the expected format.
3. Keep the files in your project repo or wiki and update them as decisions change. A template that drifts from reality is worse than none.

## The thinking behind each template

- **Acceptance criteria:** vague words like "quickly" hide decisions nobody has made, and they surface in UAT when they're expensive to fix. The template runs five checks before a story goes to the team. Walkthrough: [How to Write Acceptance Criteria Testers Can't Misread](https://www.youtube.com/watch?v=puLtC-dnP1E) on YouTube.
- **UAT plan:** most UAT pain comes from unclear entry and exit criteria, not from testing itself. The template forces those decisions up front. Background: [What a good UAT plan actually looks like](https://prachitparikh.substack.com/p/what-a-good-uat-plan-actually-looks).
- **Data mapping:** the "example in / example out" columns catch more misunderstandings than any rule. Background: [Data mapping document template](https://prachitparikh.hashnode.dev/data-mapping-document-template).
- **SQL checks:** row counts, totals, duplicates, orphans, nulls, allowed values and record tracing. Background: [7 SQL checks I run before UAT sign-off](https://dev.to/prachitparikh/7-sql-checks-i-run-before-uat-sign-off-with-queries-you-can-copy-38h5).
- **Agent-ready requirements:** AI agents build whatever you specify, confidently and fast. Background: [AI agents can write the code now. The bottleneck is the requirements.](https://medium.com/@prachit.parikh/ai-agents-can-write-the-code-now-the-bottleneck-is-the-requirements-5f7a1ee86362)
- **AI agent test plan:** an agent doesn't pass a test, it passes a pass rate. Set the bar per bucket before the first run, and keep the golden set as the regression test in prod. Walkthrough: [How to Test an AI Agent Before It Goes Live (Dev to Prod)](https://www.youtube.com/watch?v=IBteCgiXc6Q).
- **Should this be an AI agent?:** many "agent" requests are an IF statement wearing a blazer. Five questions tell you the level a process actually needs. Walkthrough: [Should This Be an AI Agent? A 5-Question Test for BAs](https://www.youtube.com/watch?v=AZLoC-rGk6Y) on YouTube.
- **AI agent job description:** "never" is a test, not a wish. Write the never rules as acceptance criteria, then add the two requirements everyone forgets: a budget and an off switch with names. Walkthrough: [Write the "Never" Rules](https://www.youtube.com/@PrachitParikh1).

## Contributing

Spotted a gap, or have a template that saved a project? Open an issue or a pull request. Real-world examples (anonymized) are especially welcome.

## About the author

Prachit Parikh is a business analyst who turns what stakeholders ask for into requirements a team can test, checks the data with SQL, and sees changes through UAT. He writes about AI, data and the future of business analysis.

- Website: [prachitparikh.github.io](https://prachitparikh.github.io/)
- Videos: [YouTube](https://www.youtube.com/@PrachitParikh1)
- Writing: [Medium](https://medium.com/@prachit.parikh) · [Substack](https://prachitparikh.substack.com) · [Hashnode](https://prachitparikh.hashnode.dev) · [Dev.to](https://dev.to/prachitparikh) · [WordPress](https://prachitparikhblog.wordpress.com/) · [Blogger](https://prachitparikh-ba.blogspot.com)
- Elsewhere: [LinkedIn](https://www.linkedin.com/in/prachitp) · [Bluesky](https://bsky.app/profile/prachitparikh.bsky.social) · [Kaggle](https://www.kaggle.com/prachitparikh) · [Quora](https://www.quora.com/profile/Prachit-Parikh-2) · [Hub site](https://sites.google.com/view/prachit-parikh)

## License

MIT. Use these templates freely at work, in courses or in your own projects. A link back is appreciated but not required.
