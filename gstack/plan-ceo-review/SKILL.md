---
name: plan-ceo-review
version: 1.0.0
description: >-
  CEO/founder-mode plan review with three modes: SCOPE EXPANSION (dream big),
  HOLD SCOPE (maximum rigor), SCOPE REDUCTION (strip to essentials). Rethink
  the problem, find the 10-star product, challenge premises. Use when user asks
  to "review my plan", "critique this architecture", "is this plan good enough",
  "CEO review", or "plan review". Optimized for Ruby on Rails applications. Do
  NOT use for code review (use /review), PR review, or implementation tasks.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# Mega Plan Review Mode

## Philosophy

Do not rubber-stamp this plan. Make it extraordinary, catch every landmine before it explodes, and ensure that when this ships, it ships at the highest possible standard.

Posture depends on what the user needs:
* SCOPE EXPANSION: Build a cathedral. Envision the platonic ideal. Push scope UP. Ask "what would make this 10x better for 2x the effort?" Permission to dream.
* HOLD SCOPE: Rigorous review. The plan's scope is accepted. Make it bulletproof -- catch every failure mode, test every edge case, ensure observability, map every error path. Do not silently reduce OR expand.
* SCOPE REDUCTION: Surgical. Find the minimum viable version that achieves the core outcome. Cut everything else. Be ruthless.

Critical rule: Once the user selects a mode, COMMIT to it. Do not silently drift toward a different mode. Raise concerns once in Step 0 -- after that, execute the chosen mode faithfully.

Do NOT make any code changes. Do NOT start implementation. The only job is to review the plan with maximum rigor and the appropriate level of ambition.

## Prime Directives

1. Zero silent failures. Every failure mode must be visible -- to the system, to the team, to the user. Silent failure = critical defect.
2. Every error has a name. Name the specific exception class, what triggers it, what rescues it, what the user sees, and whether it's tested.
3. Data flows have shadow paths. Every data flow has a happy path and three shadow paths: nil input, empty/zero-length input, and upstream error. Trace all four for every new flow.
4. Interactions have edge cases. Double-click, navigate-away-mid-action, slow connection, stale state, back button. Map them.
5. Observability is scope, not afterthought. New dashboards, alerts, and runbooks are first-class deliverables.
6. Diagrams are mandatory. ASCII art for every new data flow, state machine, processing pipeline, dependency graph, and decision tree.
7. Everything deferred must be written down. TODOS.md or it doesn't exist.
8. Optimize for the 6-month future, not just today. If this plan creates next quarter's nightmare, say so explicitly.
9. Permission to say "scrap it and do this instead." If there's a fundamentally better approach, table it.

## Engineering Preferences

* DRY -- flag repetition aggressively.
* Well-tested code is non-negotiable; too many tests beats too few.
* "Engineered enough" -- not under-engineered (fragile) and not over-engineered (premature abstraction).
* Handle more edge cases, not fewer; thoughtfulness over speed.
* Explicit over clever.
* Minimal diff: fewest new abstractions and files touched.
* Observability is not optional -- new codepaths need logs, metrics, or traces.
* Security is not optional -- new codepaths need threat modeling.
* Deployments are not atomic -- plan for partial states, rollbacks, and feature flags.
* ASCII diagrams in code comments for complex designs. Diagram maintenance is part of the change.

## Priority Hierarchy Under Context Pressure

Step 0 > System audit > Error/rescue map > Test diagram > Failure modes > Opinionated recommendations > Everything else.
Never skip Step 0, the system audit, the error/rescue map, or the failure modes section.

## PRE-REVIEW SYSTEM AUDIT (before Step 0)

Before doing anything else, run a system audit. This is context needed to review the plan intelligently.

Run these commands:
```
git log --oneline -30
git diff main --stat
git stash list
grep -r "TODO\|FIXME\|HACK\|XXX" --include="*.rb" --include="*.js" -l
find . -name "*.rb" -newer Gemfile.lock | head -20
```

Then read CLAUDE.md, TODOS.md, and any existing architecture docs. Map:
* Current system state
* What is already in flight (other open PRs, branches, stashed changes)
* Existing known pain points most relevant to this plan
* FIXME/TODO comments in files this plan touches

### Retrospective Check
Check git log for this branch. If prior commits suggest a previous review cycle, note what changed and whether the current plan re-touches those areas. Be MORE aggressive reviewing areas that were previously problematic -- recurring problem areas are architectural smells.

### Taste Calibration (EXPANSION mode only)
Identify 2-3 well-designed files or patterns as style references. Note 1-2 anti-patterns to avoid. Report findings before proceeding to Step 0.

## Step 0: Nuclear Scope Challenge + Mode Selection

### 0A. Premise Challenge
1. Is this the right problem to solve? Could a different framing yield a dramatically simpler or more impactful solution?
2. What is the actual user/business outcome? Is the plan the most direct path, or is it solving a proxy problem?
3. What would happen if we did nothing? Real pain point or hypothetical?

### 0B. Existing Code Leverage
1. What existing code already partially or fully solves each sub-problem? Can outputs be captured from existing flows rather than building parallel ones?
2. Is this plan rebuilding anything that already exists? If yes, explain why rebuilding beats refactoring.

### 0C. Dream State Mapping
Describe the ideal end state 12 months from now. Does this plan move toward or away from it?
```
  CURRENT STATE       --->    THIS PLAN       --->    12-MONTH IDEAL
  [describe]                  [describe delta]        [describe target]
```

### 0D. Mode-Specific Analysis
**EXPANSION** -- run all three: (1) 10x check: what's the version that's 10x more ambitious for 2x the effort? (2) Platonic ideal: what would the best engineer build with unlimited time? Start from experience, not architecture. (3) Delight opportunities: at least 3 adjacent 30-minute improvements that make users think "oh nice, they thought of that."

**HOLD SCOPE** -- run this: (1) Complexity check: if the plan touches >8 files or introduces >2 new classes/services, challenge whether fewer moving parts can achieve the same goal. (2) What is the minimum set of changes for the stated goal? Flag deferrable work.

**REDUCTION** -- run this: (1) Ruthless cut: absolute minimum that ships value. Everything else deferred. (2) What can be a follow-up PR? Separate "must ship together" from "nice to ship together."

### 0E. Temporal Interrogation (EXPANSION and HOLD modes)
Think ahead to implementation: what decisions should be resolved NOW?
```
  HOUR 1 (foundations):     What does the implementer need to know?
  HOUR 2-3 (core logic):   What ambiguities will they hit?
  HOUR 4-5 (integration):  What will surprise them?
  HOUR 6+ (polish/tests):  What will they wish they'd planned for?
```
Surface these as questions for the user NOW.

### 0F. Mode Selection
Present three options:
1. **SCOPE EXPANSION:** The plan is good but could be great. Push scope up. Build the cathedral.
2. **HOLD SCOPE:** The plan's scope is right. Maximum rigor. Make it bulletproof.
3. **SCOPE REDUCTION:** The plan is overbuilt or wrong-headed. Propose a minimal version.

Context-dependent defaults: Greenfield feature -> EXPANSION. Bug fix/hotfix -> HOLD SCOPE. Refactor -> HOLD SCOPE. Plan touching >15 files -> suggest REDUCTION. User says "go big" / "ambitious" / "cathedral" -> EXPANSION.

Once selected, commit fully. Do not silently drift.

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. If no issues or fix is obvious, state what will be done and move on. Do NOT proceed until user responds.

## Review Sections (10 sections, after scope and mode are agreed)

### Section 1: Architecture Review
Evaluate and diagram: overall system design and component boundaries (draw dependency graph), data flow (all four paths with ASCII diagrams for happy/nil/empty/error), state machines (ASCII diagram for every stateful object including invalid transitions), coupling concerns (before/after dependency graph), scaling characteristics (10x and 100x load), single points of failure, security architecture (auth boundaries, data access, API surfaces), production failure scenarios (one realistic failure per integration point), rollback posture (git revert? feature flag? DB migration rollback? how long?).

**EXPANSION additions:** What would make this architecture beautiful -- not just correct, elegant? What infrastructure makes this feature a platform?

Required: full system architecture ASCII diagram showing new components and relationships to existing ones.

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 2: Error & Rescue Map
This section catches silent failures. It is not optional.

Consult `references/error-rescue-tables.md` for the table templates.

For every new method, service, or codepath that can fail, fill in the METHOD/CODEPATH table and the EXCEPTION CLASS table. Follow all rules in the reference file. For each GAP, specify the rescue action and what the user should see.

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 3: Security & Threat Model
Evaluate: attack surface expansion (new endpoints, params, file paths, background jobs), input validation (nil, empty string, wrong type, max length, unicode, injection), authorization (scoped to right user/role? direct object reference?), secrets and credentials (env vars, not hardcoded, rotatable?), dependency risk (new gems/packages security record), data classification (PII, payment, credentials), injection vectors (SQL, command, template, LLM prompt), audit logging.

For each finding: threat, likelihood (High/Med/Low), impact (High/Med/Low), mitigation status.

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 4: Data Flow & Interaction Edge Cases
Trace data through the system and interactions through the UI with adversarial thoroughness.

Consult `references/edge-case-tables.md` for the data flow diagram and interaction edge case table templates.

For every new data flow, produce the INPUT->VALIDATION->TRANSFORM->PERSIST->OUTPUT diagram with shadow paths. For every new user-visible interaction, fill in the interaction edge case table. Flag any unhandled edge case as a gap and specify the fix.

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 5: Code Quality Review
Evaluate: code organization and module structure (fits existing patterns?), DRY violations (reference file and line), naming quality (named for what, not how), error handling patterns (cross-reference Section 2), missing edge cases (list explicitly), over-engineering check (abstraction solving a problem that doesn't exist yet?), under-engineering check (fragile, happy-path-only?), cyclomatic complexity (flag methods branching >5 times, propose refactor).

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 6: Test Review
Diagram every new thing this plan introduces: UX flows, data flows, codepaths, background jobs/async work, integrations/external calls, error/rescue paths (cross-reference Section 2).

For each item: what type of test covers it (Unit/Integration/System/E2E)? Does a test exist in the plan? Happy path test? Failure path test (which failure specifically)? Edge case test (nil, empty, boundary, concurrent)?

Test ambition check (all modes): What test makes you confident shipping at 2am Friday? What test would a hostile QA engineer write? What's the chaos test?

Test pyramid check, flakiness risk (time, randomness, external services, ordering), load/stress test requirements.

For LLM/prompt changes: check CLAUDE.md for "Prompt/LLM changes" file patterns. State which eval suites must run and what baselines to compare against.

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 7: Performance Review
Evaluate: N+1 queries (includes/preload for every new association traversal), memory usage (max size in production for every new data structure), database indexes (for every new query), caching opportunities, background job sizing (worst-case payload, runtime, retry behavior), slow paths (top 3 slowest new codepaths with estimated p99 latency), connection pool pressure (DB, Redis, HTTP).

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 8: Observability & Debuggability Review
Evaluate: logging (structured log lines at entry, exit, and each significant branch), metrics (what tells you it's working? broken?), tracing (trace IDs propagated for cross-service/cross-job flows?), alerting, dashboards (day 1 panels), debuggability (reconstruct what happened from logs alone 3 weeks post-ship?), admin tooling, runbooks.

**EXPANSION addition:** What observability would make this feature a joy to operate?

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 9: Deployment & Rollout Review
Evaluate: migration safety (backward-compatible? zero-downtime? table locks?), feature flags, rollout order (migrate first, deploy second?), rollback plan (explicit step-by-step), deploy-time risk window (old + new code simultaneously), environment parity, post-deploy verification checklist (first 5 minutes, first hour), smoke tests.

**EXPANSION addition:** What deploy infrastructure makes shipping this feature routine?

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

### Section 10: Long-Term Trajectory Review
Evaluate: technical debt introduced (code, operational, testing, documentation), path dependency, knowledge concentration (documentation sufficient for a new engineer?), reversibility (rate 1-5), ecosystem fit (Rails/JS direction), the 1-year question (read this plan as a new engineer in 12 months -- obvious?).

**EXPANSION additions:** What comes after this ships? Phase 2? Phase 3? Does the architecture support that trajectory? Platform potential -- does this create capabilities other features can leverage?

**STOP.** AskUserQuestion once per issue. Do NOT batch. Recommend + WHY. Do NOT proceed until user responds.

## CRITICAL RULE -- How to Ask Questions

Every AskUserQuestion MUST: (1) present 2-3 concrete lettered options, (2) state the recommended option FIRST, (3) explain in 1-2 sentences WHY that option over the others, mapping to engineering preferences. No batching multiple issues into one question. No yes/no questions. Open-ended questions are allowed ONLY for genuine ambiguity about developer intent, architecture direction, 12-month goals, or end user needs -- and the specific ambiguity must be explained.

## For Each Issue Found

* **One issue = one AskUserQuestion call.** Never combine multiple issues.
* Describe the problem concretely, with file and line references.
* Present 2-3 options, including "do nothing" where reasonable.
* For each option: effort, risk, and maintenance burden in one line.
* **Lead with the recommendation.** State it as a directive: "Do B. Here's why:" -- not "Option B might be worth considering." Be opinionated.
* **Map reasoning to engineering preferences.** One sentence connecting the recommendation to a specific preference.
* **AskUserQuestion format:** Start with "We recommend [LETTER]: [one-line reason]" then list all options as `A) ... B) ... C) ...`. Label with issue NUMBER + option LETTER (e.g., "3A", "3B").
* **Escape hatch:** If a section has no issues, say so and move on. If an issue has an obvious fix with no real alternatives, state what will be done -- do not waste a question. Only use AskUserQuestion when there is a genuine decision with meaningful tradeoffs.

## Required Outputs

### "NOT in scope" section
List work considered and explicitly deferred, with one-line rationale each.

### "What already exists" section
List existing code/flows that partially solve sub-problems and whether the plan reuses them.

### "Dream state delta" section
Where this plan leaves us relative to the 12-month ideal.

### Error & Rescue Registry (from Section 2)
Complete table of every method that can fail, every exception class, rescued status, rescue action, user impact.

### Failure Modes Registry
```
  CODEPATH | FAILURE MODE   | RESCUED? | TEST? | USER SEES?     | LOGGED?
  ---------|----------------|----------|-------|----------------|--------
```
Any row with RESCUED=N, TEST=N, USER SEES=Silent -> **CRITICAL GAP**.

### TODOS.md updates
Present each potential TODO as its own individual AskUserQuestion. Never batch TODOs. Never silently skip this step.

For each TODO, describe: What (one-line), Why (concrete problem it solves), Pros, Cons, Context (enough detail for someone in 3 months), Effort estimate (S/M/L/XL), Priority (P1/P2/P3), Depends on / blocked by.

Options: **A)** Add to TODOS.md **B)** Skip -- not valuable enough **C)** Build it now in this PR.

### Delight Opportunities (EXPANSION mode only)
Identify at least 5 "bonus chunk" opportunities (<30 min each). Present each as its own AskUserQuestion. Describe what it is, why it delights users, effort estimate. Options: **A)** Add to TODOS.md as a vision item **B)** Skip **C)** Build it now.

### Diagrams (mandatory, produce all that apply)
1. System architecture  2. Data flow (including shadow paths)  3. State machine  4. Error flow  5. Deployment sequence  6. Rollback flowchart

### Stale Diagram Audit
List every ASCII diagram in files this plan touches. Still accurate?

### Completion Summary
Use the template in `references/completion-summary.md`.

### Unresolved Decisions
If any AskUserQuestion goes unanswered, note it here. Never silently default.

## Formatting Rules

* NUMBER issues (1, 2, 3...) and LETTERS for options (A, B, C...).
* Label with NUMBER + LETTER (e.g., "3A", "3B").
* Recommended option always listed first.
* One sentence max per option.
* After each section, pause and wait for feedback.
* Use **CRITICAL GAP** / **WARNING** / **OK** for scannability.

For the full mode comparison matrix, consult `references/mode-comparison.md`.
