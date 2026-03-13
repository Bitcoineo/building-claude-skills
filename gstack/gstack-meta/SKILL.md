---
name: gstack-meta
description: >-
  Orchestrate the gstack skill suite for end-to-end software development
  workflows. Routes to the correct gstack skill based on user intent: plan
  review (CEO or eng), architecture specification, code review, shipping, QA
  testing, browser automation, cookie setup, and retrospectives. Use when user
  asks "which gstack skill should I use", "help me with gstack", "what's the
  right workflow", or needs guidance choosing between similar gstack skills.
  Do NOT use for executing individual skills directly — route to the specific
  skill instead.
allowed-tools:
  - Read
  - Glob
  - Grep
  - AskUserQuestion
---

# Gstack Workflow Orchestrator

Guide the user through the gstack skill suite — 9 specialized skills that turn Claude Code into a team of engineering specialists. This meta-skill helps users choose the right skill, chain skills into workflows, and avoid common misrouting.

## The Gstack Suite

| Skill | Role | When to use |
|-------|------|-------------|
| /plan-ceo-review | CEO/founder brain | Challenge the plan itself — is this the right thing to build? |
| /plan-eng-review | Eng manager brain | Lock in the execution plan — architecture, tests, edge cases |
| /architect | Solutions architect brain | Lock in HOW to build it — ADRs, schemas, contracts, build sequence |
| /review | Staff engineer brain | Pre-landing structural review of code diff |
| /ship | Release engineer brain | Automated merge → test → version → changelog → PR |
| /qa | QA lead brain | Systematic web app testing with health scores |
| /browse | QA engineer brain | Headless browser for individual page interactions |
| /setup-browser-cookies | Session manager brain | Import real browser cookies for authenticated testing |
| /retro | Engineering manager brain | Weekly retrospective with team analysis and trends |

## Routing Logic

When the user's intent is ambiguous, determine the correct skill by asking:

1. **Is this about a PLAN or about CODE?**
   - Plan → Step 2
   - Code → Step 3
   - Testing → Step 4
   - Reflection → /retro

2. **What level of plan review or design?**
   - Challenge the vision, find the 10-star product → /plan-ceo-review
   - Lock in the execution plan (architecture, tests, edge cases) → /plan-eng-review
   - Lock in implementation decisions (schemas, contracts, build sequence) → /architect
   - If unsure: "Do you want to challenge WHAT to build, nail down the PLAN, or lock in HOW to implement it?"

3. **What stage is the code at?**
   - Written but not reviewed → /review
   - Reviewed and ready to ship → /ship
   - If user says "review and ship" → /ship (it includes review in Step 3.5)

4. **What kind of testing?**
   - Full QA session with report → /qa
   - Check one specific page or element → /browse
   - Need to log in first → /setup-browser-cookies, then /qa or /browse

For the complete routing decision tree and disambiguation rules, consult `references/skill-routing.md`.

## Standard Workflows

### Full Development Cycle

```
PLAN → ARCHITECT → IMPLEMENT → REVIEW → SHIP → QA → RETRO
```

1. Start with /plan-ceo-review for new features (challenges the plan)
2. Follow with /plan-eng-review (locks in execution plan)
3. Run /architect to lock in implementation decisions (schemas, contracts, build sequence)
4. Implement the code (following the architect specification)
5. Run /review for pre-landing structural review
6. Run /ship to merge, test, version, and create PR
7. Run /qa to verify the deployed feature works correctly
8. Run /retro at the end of the week to analyze the team's output

### Quick Ship (Small Changes)

```
REVIEW → SHIP
```

1. Run /review to catch structural issues
2. Run /ship to automate the rest

### QA Session

```
COOKIES → QA → BROWSE (for specific issues)
```

1. Run /setup-browser-cookies if the app requires authentication
2. Run /qa for systematic testing (full, quick, or regression mode)
3. Use /browse directly to investigate specific issues found by QA

## Common Mistakes

| Mistake | Why it happens | Correct approach |
|---------|---------------|------------------|
| Using /review for plan review | "Review" is ambiguous | /review is for CODE diffs only. Use /plan-eng-review or /plan-ceo-review for plans |
| Skipping /review before /ship | "Ship includes review" | True, but running /review separately gives you time to fix issues before the automated pipeline |
| Using /browse instead of /qa | "I just want to test" | /qa produces a structured report. /browse is for ad-hoc page interactions |
| Running /retro with no commits | Window has no activity | Suggest a different time window: "/retro 14d" or "/retro 30d" |
| Using /plan-ceo-review for a bug fix | Over-scoping | Bug fixes need /plan-eng-review (HOLD SCOPE) not CEO-level questioning |
| Skipping /architect for large features | "I know how to build it" | Features touching 5+ files benefit from locked decisions. Unresolved decisions become bugs mid-implementation |
| Using /architect for small changes | Over-process | Bug fixes and small features go straight from /plan-eng-review to implementation |

## Improvement Patterns

During the audit and improvement of the gstack suite, 8 recurring patterns were identified that apply to any Claude Code skill. For the full analysis, consult `references/improvement-patterns.md`.

Key takeaways:
- Every skill needs negative triggers to prevent misrouting between similar skills
- Descriptions must include quoted trigger phrases users actually say
- Reference tables and templates belong in `references/`, not the body
- Framework-specific skills should declare their dependencies
- Any skill that ships code needs rollback guidance

## Troubleshooting

**"The wrong skill activated"**
Check the routing table above. If skills are misrouting, the user may need to be more specific in their request. Key disambiguation phrases:
- "Review my plan" → plan-ceo-review or plan-eng-review
- "Architect this" or "write a tech spec" → architect
- "Review this PR" or "review this code" → review
- "Ship it" → ship
- "Test this site" → qa
- "Click this button" → browse

**"I don't know which review to use"**
Ask: "Are you reviewing a plan (what to build) or code (what was built)?"
- Plan → /plan-ceo-review (vision) or /plan-eng-review (execution)
- Architecture → /architect (implementation decisions)
- Code → /review

**"The skill references tools I don't have"**
Some skills are designed for specific stacks:
- /ship expects `bin/test-lane` (Rails) and `npm run test` (Node.js)
- /setup-browser-cookies requires macOS (Keychain for cookie decryption)
- /browse requires the gstack browse binary (built on first use)

# Bundled Resources

- `references/skill-routing.md` — Complete routing decision tree, phrase-to-skill mapping, and disambiguation rules
- `references/improvement-patterns.md` — 8 patterns discovered during the gstack audit with root cause analysis and prevention rules
