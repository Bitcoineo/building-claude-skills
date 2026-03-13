# Gstack Audit Report: Before vs After

## Validation Results

| Skill | Before (P/W/F) | After (P/W/F) | Changes Made |
|-------|----------------|----------------|--------------|
| plan-ceo-review | 12P 2W 0F | 18P 0W 0F | +triggers, +negatives, progressive disclosure (484→283 lines), 4 reference files, imperative voice |
| plan-eng-review | 12P 2W 0F | 14P 0W 0F | +triggers, +negatives, +troubleshooting section |
| review | 12P 2W 0F | 14P 0W 0F | +triggers, +negatives, checklist examples added |
| ship | 12P 2W 0F | 14P 0W 0F | +triggers, +negatives, +rollback guidance, +compatibility |
| qa | 13P 1W 0F | 14P 0W 0F | +negatives, clarified navigation targets, framework guidance note |
| browse | 13P 1W 0F | 14P 0W 0F | +negatives, +error recovery table |
| setup-browser-cookies | 12P 2W 0F | 14P 0W 0F | +triggers, +negatives, +compatibility field, +session management |
| retro | 11P 3W 0F | 16P 0W 0F | +triggers, +negatives, progressive disclosure (429→307 lines), 2 reference files |
| gstack-meta | N/A (new) | 16P 0W 0F | New meta-skill with routing logic and workflow guidance |

**Total: 9 skills, 134 PASS, 0 WARN, 0 FAIL**

---

## Description Comparison (Before → After)

### plan-ceo-review
**Before:**
```
CEO/founder-mode plan review. Rethink the problem, find the 10-star product,
challenge premises, expand scope when it creates a better product. Three modes:
SCOPE EXPANSION (dream big), HOLD SCOPE (maximum rigor), SCOPE REDUCTION
(strip to essentials).
```
**After:**
```
CEO/founder-mode plan review with three modes: SCOPE EXPANSION (dream big),
HOLD SCOPE (maximum rigor), SCOPE REDUCTION (strip to essentials). Rethink
the problem, find the 10-star product, challenge premises. Use when user asks
to "review my plan", "critique this architecture", "is this plan good enough",
"CEO review", or "plan review". Optimized for Ruby on Rails applications. Do
NOT use for code review (use /review), PR review, or implementation tasks.
```
**Changes:** +5 trigger phrases, +3 negative triggers, +compatibility note

### plan-eng-review
**Before:**
```
Eng manager-mode plan review. Lock in the execution plan — architecture,
data flow, diagrams, edge cases, test coverage, performance. Walks through
issues interactively with opinionated recommendations.
```
**After:**
```
Eng manager-mode plan review. Lock in the execution plan — architecture,
data flow, diagrams, edge cases, test coverage, performance. Use when user
asks to "review my engineering plan", "check this implementation plan",
"eng review", or "technical plan review". Do NOT use for code review or PR
review (use /review instead) or CEO-level plan critique (use /plan-ceo-review).
```
**Changes:** +4 trigger phrases, +2 negative triggers with skill cross-references

### review
**Before:**
```
Pre-landing PR review. Analyzes diff against main for SQL safety, LLM trust
boundary violations, conditional side effects, and other structural issues.
```
**After:**
```
Pre-landing PR review. Analyzes diff against main for SQL safety, LLM trust
boundary violations, conditional side effects, and other structural issues.
Use when user asks to "review this PR", "check my code before merging",
"pre-landing review", or "code review". Do NOT use for plan review (use
/plan-eng-review or /plan-ceo-review) or shipping code (use /ship).
```
**Changes:** +4 trigger phrases, +3 negative triggers with skill cross-references

### ship
**Before:**
```
Ship workflow: merge main, run tests, review diff, bump VERSION, update
CHANGELOG, commit, push, create PR.
```
**After:**
```
Automated ship workflow: merge main, run tests, review diff, bump VERSION,
update CHANGELOG, commit, push, create PR. Use when user says "ship it",
"deploy this", "create a release", "push and PR", or "merge and push".
Designed for Ruby on Rails and Node.js projects. Do NOT use for code review
(use /review) or plan review (use /plan-eng-review).
```
**Changes:** +5 trigger phrases, +2 negative triggers, +compatibility note

### qa
**Before:**
```
Systematically QA test a web application. Use when asked to "qa", "QA",
"test this site", "find bugs", "dogfood", or review quality. Three modes:
full (systematic exploration), quick (30-second smoke test), regression
(compare against baseline). Produces structured report with health score,
screenshots, and repro steps.
```
**After:**
```
Systematically QA test a web application. Use when asked to "qa", "QA",
"test this site", "find bugs", "dogfood", or "review quality". Three modes:
full (systematic exploration), quick (30-second smoke test), regression
(compare against baseline). Produces structured report with health score,
screenshots, and repro steps. Do NOT use for unit testing, code review,
or automated CI testing.
```
**Changes:** +negative triggers (had trigger phrases already)

### browse
**Before:**
```
Fast headless browser for QA testing and site dogfooding. Navigate any URL,
interact with elements, verify page state, diff before/after actions, take
annotated screenshots, check responsive layouts, test forms and uploads,
handle dialogs, and assert element states. ~100ms per command. Use when you
need to test a feature, verify a deployment, dogfood a user flow, or file
a bug with evidence.
```
**After:**
```
Fast headless browser for QA testing and site dogfooding. Navigate any URL,
interact with elements, verify page state, diff before/after actions, take
annotated screenshots, check responsive layouts, test forms and uploads,
handle dialogs, and assert element states. ~100ms per command. Use when you
need to "test a feature", "verify a deployment", "dogfood a user flow", or
"file a bug with evidence". Do NOT use for API testing, unit testing, or
non-browser automation tasks.
```
**Changes:** Quoted trigger phrases, +negative triggers

### setup-browser-cookies
**Before:**
```
Import cookies from your real browser (Comet, Chrome, Arc, Brave, Edge) into
the headless browse session. Opens an interactive picker UI where you select
which cookie domains to import. Use before QA testing authenticated pages.
```
**After:**
```
Import cookies from your real browser (Comet, Chrome, Arc, Brave, Edge) into
the headless browse session. Opens an interactive picker UI where you select
which cookie domains to import. Use when user asks to "import cookies",
"set up browser session", "login to site for testing", or wants to "test
authenticated pages". macOS only — requires macOS Keychain for cookie
decryption. Do NOT use for clearing cookies or managing browser profiles.
```
**Changes:** +4 trigger phrases, +negative triggers, +compatibility note, +compatibility field in frontmatter

### retro
**Before:**
```
Weekly engineering retrospective. Analyzes commit history, work patterns,
and code quality metrics with persistent history and trend tracking.
Team-aware: breaks down per-person contributions with praise and growth areas.
```
**After:**
```
Weekly engineering retrospective. Analyzes commit history, work patterns,
and code quality metrics with persistent history and trend tracking.
Team-aware: breaks down per-person contributions with praise and growth
areas. Use when user asks to "run a retro", "team retrospective",
"how did we do this week", "engineering retro", or "weekly review".
Do NOT use for individual performance review, code review, or plan review.
```
**Changes:** +5 trigger phrases, +3 negative triggers

---

## Body Size Comparison

| Skill | Before (lines) | After (lines) | Delta | Reference files |
|-------|---------------|---------------|-------|-----------------|
| plan-ceo-review | 484 | 283 | -201 | 4 new |
| plan-eng-review | 162 | 170 | +8 | 0 |
| review | 78 | 81 | +3 | 0 |
| ship | 300 | 315 | +15 | 0 |
| qa | 295 | 297 | +2 | 0 (2 existing) |
| browse | 128 | 140 | +12 | 0 |
| setup-browser-cookies | 82 | 93 | +11 | 0 |
| retro | 429 | 307 | -122 | 2 new |
| gstack-meta | N/A | 142 | new | 2 new |

---

## New Files Created

### Reference Files (8 total)
1. `plan-ceo-review/references/error-rescue-tables.md` — Error & rescue map templates
2. `plan-ceo-review/references/edge-case-tables.md` — Data flow & interaction edge case templates
3. `plan-ceo-review/references/mode-comparison.md` — EXPANSION/HOLD/REDUCTION comparison matrix
4. `plan-ceo-review/references/completion-summary.md` — Review completion summary template
5. `retro/references/metrics-formulas.md` — Session detection, focus score, streak tracking formulas
6. `retro/references/json-schema.md` — Retro history JSON snapshot schema
7. `gstack-meta/references/skill-routing.md` — Skill routing decision tree and disambiguation
8. `gstack-meta/references/improvement-patterns.md` — 8 audit patterns with root cause analysis

### Enhanced Existing Files (1)
- `review/checklist.md` — Added concrete examples to each suppression rule

---

## Universal Issues Fixed

1. **Zero negative triggers** → All 9 skills now have negative triggers
2. **Missing trigger phrases** → All 9 skills now have quoted trigger phrases
3. **Body near limit** → plan-ceo-review reduced from 484 to 283 lines; retro from 429 to 307
4. **Second-person voice** → plan-ceo-review converted to imperative form
5. **Missing compatibility** → ship and setup-browser-cookies now declare framework/OS requirements
6. **No rollback guidance** → ship now includes rollback section
7. **No error recovery** → browse now includes error recovery table
8. **Ambiguous instructions** → qa clarified "top 5 navigation targets"
