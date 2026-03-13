# Gstack Skill Routing Guide

When the user's request could match multiple gstack skills, use this routing table to select the correct one.

## Decision Tree

```
User request
├── About a PLAN (design, architecture, strategy)?
│   ├── Wants CEO/founder-level critique, 10x thinking, scope decisions?
│   │   └── /plan-ceo-review
│   ├── Wants engineering rigor: architecture, tests, performance, edge cases?
│   │   └── /plan-eng-review
│   └── Wants locked implementation decisions: schemas, contracts, build sequence?
│       └── /architect
│
├── About CODE already written (diff, PR, branch)?
│   ├── Wants structural review before merging?
│   │   └── /review
│   └── Wants to merge, test, version, and create PR?
│       └── /ship
│
├── About TESTING a live web application?
│   ├── Wants systematic QA with health score and report?
│   │   └── /qa
│   ├── Needs to interact with a specific page or element?
│   │   └── /browse
│   └── Needs to log in / import browser sessions?
│       └── /setup-browser-cookies
│
└── About REFLECTION on past work?
    └── /retro
```

## Routing by User Phrase

| User says... | Route to | NOT this |
|---|---|---|
| "review my plan" | /plan-ceo-review | /review |
| "review this PR" | /review | /plan-eng-review |
| "check this architecture" | /plan-ceo-review or /plan-eng-review | /review |
| "architect this" / "tech spec" | /architect | /plan-eng-review |
| "design the implementation" / "how should we build this" | /architect | /plan-eng-review |
| "lock in the architecture" | /architect | /plan-ceo-review |
| "ship it" / "deploy" | /ship | /review |
| "test this site" / "QA" | /qa | /browse |
| "click this button" / "check this element" | /browse | /qa |
| "import cookies" / "log in for testing" | /setup-browser-cookies | /browse |
| "how did we do this week" / "retro" | /retro | /plan-ceo-review |
| "is this plan good enough" | /plan-ceo-review | /plan-eng-review |
| "make this plan bulletproof" | /plan-eng-review | /plan-ceo-review |

## Common Workflows

### Full Ship Cycle
1. `/plan-ceo-review` — Validate the plan is worth building
2. `/plan-eng-review` — Lock in the execution plan
3. `/architect` — Lock in implementation decisions (schemas, contracts, build sequence)
4. (implement the plan)
5. `/review` — Pre-landing structural review
6. `/ship` — Merge, test, version, push, PR

### QA Testing Cycle
1. `/setup-browser-cookies` — Import authenticated sessions
2. `/qa` — Run systematic QA
3. `/browse` — Investigate specific issues found by QA

### Weekly Rhythm
1. `/retro` — Review the week's work
2. Use retro insights to inform next week's planning
3. `/plan-ceo-review` or `/plan-eng-review` for new initiatives

## Disambiguation Rules

- **Plan vs Code**: If the user has uncommitted code changes and says "review", they likely mean `/review` (code). If they're discussing a design doc or plan file, they mean `/plan-eng-review` or `/plan-ceo-review`.
- **CEO vs Eng review**: CEO review challenges WHAT to build. Eng review challenges HOW to build it. If the user seems satisfied with scope but worried about implementation, use eng review.
- **QA vs Browse**: QA is a complete testing workflow with reports. Browse is a tool for individual page interactions. If the user wants a report, use QA. If they want to check one specific thing, use browse.
- **Ship vs Review**: Ship includes a review step (Step 3.5). If the user says "review and ship", just use `/ship` — it handles both.
- **Eng review vs Architect**: Eng review ASKS questions about the plan and identifies issues. Architect LOCKS IN the answers as a formal specification with ADRs, schemas, and contracts. If the user has a reviewed plan with open decisions, use `/architect`. If the plan itself has not been reviewed, use `/plan-eng-review` first.
