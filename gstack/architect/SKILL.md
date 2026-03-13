---
name: architect
version: 1.0.0
description: >-
  Technical architecture specification. Turns an approved eng plan into locked
  implementation decisions: ADRs, data models, API contracts, component tree,
  build sequence, error patterns, and observability spec. Use when user asks to
  "architect this", "design the implementation", "write a tech spec", "lock in
  the architecture", or "how should we build this". Do NOT use for challenging
  WHAT to build (use /plan-ceo-review), reviewing the execution plan (use
  /plan-eng-review), or reviewing code diffs (use /review).
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
---

# /architect: Technical Architecture Specification

Produce a complete technical architecture specification before any code is written. Every unresolved technical decision must be surfaced, discussed with the user via AskUserQuestion, and locked into an Architecture Decision Record. The output is a document the implementer follows without making further design decisions.

## Prerequisites

Check that the plan has been reviewed before proceeding.

1. Read `TODOS.md` or whatever plan document the user points to.
2. Glob for plan-related files: `**/plan*.md`, `**/architecture*.md`, `**/design*.md`, `**/spec*.md`.
3. Grep for eng review artifacts: "NOT in scope", "What already exists", "Failure modes".
4. If no eng review outputs exist, STOP. Tell the user: "Run /plan-eng-review first. The architect skill needs a locked execution plan as input."

## Step 1: Inventory Unresolved Decisions

Scan the eng review outputs for:
- Questions the eng review raised that the user answered — these become ADR candidates (decisions to lock in).
- Open questions or "Unresolved decisions" sections — these must be resolved NOW.
- TODO items marked for the current feature (scope boundary for this spec).
- Failure modes flagged without specified error handling patterns (error pattern decisions needed).

Produce a numbered list of every decision that needs locking. For each, note whether it was already decided (extract the decision) or still open (needs AskUserQuestion).

**STOP.** AskUserQuestion: "Does this inventory capture all the technical decisions that need locking? A) Yes, proceed with these. B) Add these additional decisions: [list]. C) Some of these are already decided — let me clarify."

## Step 2: Architecture Decision Records

For each unresolved decision from Step 1, use AskUserQuestion individually. One decision per question. For each:
- State the decision in one sentence.
- Present 2-3 concrete options with lettered labels (A, B, C).
- For each option: one sentence on tradeoffs (effort, risk, flexibility).
- Lead with the recommendation: "Recommend B. Here's why:" with reasoning tied to the eng review findings.

After all decisions are resolved, compile into ADR format. Consult `references/adr-template.md` for the structure.

**STOP.** AskUserQuestion: "Review these locked decisions. A) All correct, proceed. B) Revise decision [number]. C) Add a decision I missed."

## Step 3: Data Model / Schema Design

For each new model, table, or data structure in the plan:
1. List fields with types, constraints, defaults, and indexes.
2. Draw relationships as ASCII (one-to-many, many-to-many, polymorphic).
3. Specify migration ordering (which migrations must run first).
4. Note fields needing encryption, normalization, or computed values.
5. For each new index, state the query it supports.

If no data model changes are needed, state "No data model changes required" and skip to Step 4.

**STOP** for each schema decision with alternatives (polymorphic vs STI, JSON column vs normalized table, etc.). Use AskUserQuestion — one decision per question. Present tradeoffs concretely: query performance, migration complexity, future flexibility.

## Step 4: API / Interface Contracts

For each new endpoint, service method, or public interface:
1. Signature: method name, parameters with types, return type.
2. Request/response shapes (if HTTP): example JSON with all fields typed.
3. Error responses: status codes, error body shapes.
4. Auth requirements: who can call this, what scopes/roles.
5. Rate limits or throttling (if applicable).

For internal service boundaries (service objects, concerns): specify the public API only. Private methods are implementation detail.

**STOP** for ambiguous interface decisions (pagination strategy, response envelope format, idempotency approach). Use AskUserQuestion — one per decision.

## Step 5: Component Structure

Produce an ASCII file tree showing every new and modified file with a one-line responsibility description:

```
app/
  models/
    new_model.rb           # [NEW] Model for X, validates Y, belongs_to Z
  services/
    new_service.rb         # [NEW] Orchestrates X workflow
  controllers/
    existing_controller.rb # [MOD] Add #create action for X
test/
  models/
    new_model_test.rb      # [NEW] Unit tests for NewModel
  services/
    new_service_test.rb    # [NEW] Unit + integration tests
```

Tag each file `[NEW]` or `[MOD]`. For `[MOD]` files, state what changes.

Count total files. If more than 12, flag as a complexity warning and AskUserQuestion: "This touches {N} files. A) Proceed as one PR. B) Split at step [N] of the build sequence into multiple PRs."

## Step 6: Implementation Sequence

Order the file tree from Step 5 into a dependency-ordered build sequence. Each step must be independently testable — no broken imports, no references to code that does not exist yet.

Format:
```
Step 1: [file(s)] — build what, test what, depends on what
Step 2: [file(s)] — build what, test what, depends on what
...
```

This sequence maps directly to bisectable commits in `/ship`.

**STOP.** AskUserQuestion: "Does this build order match your mental model? A) Yes, proceed. B) Reorder: [specify]. C) Split into multiple PRs at step [N]."

## Step 7: Error Handling & Edge Case Patterns

Cross-reference the failure modes registry from `/plan-eng-review`. For each failure mode:
1. Specify the exact exception class or error condition.
2. Specify the rescue/catch strategy (retry, degrade, re-raise with context).
3. Specify what the user sees (error message, fallback UI, silent recovery).
4. Specify what gets logged (structured log fields).

For edge cases: specify the exact guard (nil check, type check, boundary check) and where it goes (model validation, controller before_action, service input check).

If the eng review produced an error/rescue table, extend it with implementation-specific details. If not, build one from the patterns in the plan.

## Step 8: Observability Spec (conditional)

Skip if the feature is small (fewer than 3 new files, no new async work, no external integrations). State "Observability: not warranted for this scope" and move to Step 9.

For features that warrant observability:
1. **Logging:** Structured log lines at entry, exit, and each significant branch. Include the fields.
2. **Metrics:** Counters, gauges, or histograms to add. What dashboard panel shows this.
3. **Alerting:** What threshold triggers a page. What runbook to follow.
4. **Tracing:** If cross-service or cross-job, specify trace ID propagation.

## Step 9: Compile Specification

Compile all outputs from Steps 2-8 into a single specification document. Consult `references/architecture-spec-template.md` for the structure.

Present the complete specification to the user. AskUserQuestion: "A) Specification is complete — save to [suggested filename] and begin implementation. B) Revise section [name]. C) The scope has changed — return to Step 1."

## Important Rules

- Read-only. Produce specifications, never code. Do not create files unless the user explicitly approves saving.
- One decision per AskUserQuestion. Never batch. Lead with recommendation. Explain WHY in one sentence.
- Every ADR needs a "Decided" status and a rationale. No "TBD" in the final specification.
- If the eng review is missing or incomplete, STOP and route to `/plan-eng-review`. Do not architect without a locked plan.
- If scope changes during architecture, note the change explicitly and update the NOT-in-scope list.
- The specification must be concrete enough that an implementer can build each step without asking "but how?" If a section reads as hand-wavy, it is not done.
- Do not repeat the eng review's analysis. Reference it. The architect adds implementation decisions ON TOP of the eng review's findings.

## Troubleshooting

1. **"No eng review exists"** — Route to `/plan-eng-review`. The architect skill requires a locked plan as input.
2. **"The plan is too vague to architect"** — Ask the user to describe the specific files and codepaths they expect to change. If they cannot, the plan is not ready.
3. **"Too many decisions to lock"** — Split into phases. Architect Phase 1 (the minimum shippable slice) first.
4. **"User wants to skip to implementation"** — Warn that unresolved decisions become bugs. Offer compressed mode: Steps 1-2 (decisions only) + Step 6 (build sequence). Skip data model, API contracts, and observability.

## Bundled Resources

- `references/architecture-spec-template.md` — Output template for the compiled specification document
- `references/adr-template.md` — Architecture Decision Record format with rules and examples
