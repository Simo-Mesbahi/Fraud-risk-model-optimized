# UI/UX improvements — 17 November 2026

This checklist keeps the identifiers from the design audit. The reference model,
training data and published performance are unchanged. Validation is recorded in
GitHub Actions and its `browser-verification` artifact.

| ID | Area | Implementation | Acceptance evidence |
|---|---|---|---|
| 1 | Scoring and errors | Co-located loopback inference; bounded, readable proxy errors | Actual scoring/TreeSHAP, HTML error regression, container workflow |
| 2 | Initial loading | Model readiness gates interface startup; one service wake-up instead of two | Startup/shutdown check; free-host wake-up screen remains possible |
| 3 | Header | Compact product bar and one page heading | Desktop/mobile screenshots |
| 4 | Navigation | Discover, Analyze & investigate, Operate groups | Seven-page navigation |
| 5 | Menu descriptions | Separate category and description with explicit spacing | Sidebar screenshots |
| 6 | Hierarchy | Short page introductions and progressively disclosed details | Overview/model/status screenshots |
| 7 | Typography | Larger metadata, labels and readable heading sizes | Responsive screenshots |
| 8 | Contrast | Brighter placeholders, helpers and metadata | Source colour checks and visual review |
| 9 | Cards | Consistent radius, spacing and responsive KPI grids | Desktop/390/768 px screenshots |
| 10 | Recruiter path | Overview links to data and claim demo | Real public workflow |
| 11 | Executive KPIs | Four primary metrics, further metrics disclosed | Frozen-metric reconciliation |
| 12 | Prevalence | Exact reference prevalence, 409/14,176 | Reproducible evidence builder |
| 13 | Technical context | Deployment checks moved to disclosures | Overview/status screenshots |
| 14 | Science navigation | Eight visible workspace choices | All eight workspace render tests |
| 15 | Analytical context | Corpus, cohort, model and active-view summary | Reference/expanded corpus tests |
| 16 | Filters | Clear filters and empty-view recovery | Filter interaction tests |
| 17 | Chart labels | Business labels, wrapped axes and complete tooltips | Graph screenshots and data tables |
| 18 | Timeline | Monthly ticks, explicit periods, readable bars | Timeline screenshots |
| 19 | Interpretation | Observations and limitations alongside graphics | Exploration/quality/pattern/time views |
| 20 | Chart colours | Stable reference/candidate and outcome colour semantics | Capacity/pattern figures |
| 21 | Original figures | Interactive reference plots; unchanged archives disclosed | Original artifacts retained |
| 22 | Tables | Readable column names and consistent numeric formatting | Real reference/candidate tables |
| 23 | Wide tables | Essential operational columns; full detail/export available | Portfolio/worklist checks |
| 24 | Claim intake | Demo-first entry, grouped smart fields, result-first assessment | Claim workflow and intake screenshots |
| 25 | Demo labels | Claim identifier, service and amount | Demo selector |
| 26 | Claim result | Explanation before claim detail; technical checks disclosed | Real 107-feature SHAP validation |
| 27 | Portfolio result | Worklist before secondary distribution plots | Real upload/scoring workflow |
| 28 | Investigation | Worklist and human review before contract diagnostics | Actual queue/decision workflow |
| 29 | Save/resume | Controls next to progress instead of the page footer | Download/restore round-trip |
| 30 | Cross-page handoff | Native page URLs, reading-position reset, reused portfolio; backend revalidates selection | 500-claim to 15-case test; viewport assertions |
| 31 | Model insights | Lazy Performance, Explainability, Errors & limits, Model contract tabs | Four-tab browser checks |
| 32 | System status | Readiness first; local files distinguished from remote health | Status and diagnostic disclosures |
| 33 | Empty states | Visible demo source and direct launch actions | Fresh claim/portfolio/queue screens |
| 34 | Accessibility | One H1 per page, semantic section headings, labelled controls and focus styling | Heading assertions and browser navigation |
| 35 | Responsive layout | Compact header, adaptive KPI grids, stacked forms and accessible tab scrolling | All pages and science views at 390 and 768 px |

## Limits

- A free Render instance can sleep. The platform wake-up screen cannot be removed by application CSS.
- Interface review is not a WCAG certification or a usability study with independent participants.
- Evidence concerns public synthetic claims. Uploaded operational data are session-local and do not enter shared research corpora.
- User accounts and role management are deliberately outside this public recruiter demonstration.
