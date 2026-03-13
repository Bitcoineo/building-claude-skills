# Course Build Log

This document captures every bug, root cause analysis, lesson learned, and design decision made while building the "Building Claude Code Skills" course. This is the raw material that will be fed into `skill-creator` to produce the capstone meta-skill.

---

## Bug Log

*Every bug gets full first-principles root cause analysis. No patching and moving on.*

### BUG-001: Conventional commit regex fails on `type!(scope):` format
**Module:** Module 3 — Supporting Resources (parse_commits.py)
**Symptom:** Commit `feat!(auth): redesign token validation` parsed as type "other" with the full prefix in the subject field, instead of type "feat" with scope "auth".
**Root Cause (First Principles):** The regex `^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]*)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$` places the `!` capture group AFTER the scope group. But the Conventional Commits spec allows `!` BEFORE the scope (e.g., `feat!(scope):`) as well as after it (e.g., `feat(scope)!:`). The regex only handled the latter position. When `!` appeared before `(`, the regex couldn't match `!(auth)` as a scope group because `!` broke the expected `(` start.
**Fix:** Split the breaking change capture into two groups — `(?P<breaking1>!)?` before the scope and `(?P<breaking2>!)?` after it. The parse logic ORs both groups: `breaking_mark = (match.group("breaking1") is not None or match.group("breaking2") is not None)`. This handles all valid positions per the spec.
**Prevention:** When implementing spec parsers, always test with ALL valid syntax variants from the spec, not just the most common one. Create test fixtures covering edge cases before writing the regex.
**Category:** execution

### BUG-002: Version bump justification shows negative "other" count
**Module:** Module 3 — Supporting Resources (parse_commits.py)
**Symptom:** Justification string showed "1 breaking, 1 feature, 1 fix, -1 other" for 2 commits.
**Root Cause (First Principles):** The `suggest_version_bump()` function counted breaking commits separately from type counts, but a breaking commit is ALSO counted by type (e.g., a `feat!` commit counts as both "breaking" and "feat"). The formula `other_count = total - breaking_count - feat_count - fix_count` double-subtracted the breaking feat commit, yielding a negative number. This is a set-membership error: the "breaking" set and the "feat" set are not disjoint, but the formula assumed they were.
**Fix:** Changed `feat_count` and `fix_count` to exclude breaking commits: `feat_count = sum(1 for c in parsed if c["type"] == "feat" and not c["breaking"])`. This makes the sets disjoint, so the subtraction works correctly.
**Prevention:** When counting items that belong to multiple categories, always make the categories mutually exclusive before subtracting. Or use a single-pass classification where each item is assigned to exactly one bucket.
**Category:** execution

### BUG-003: quick_validate.py fails with ModuleNotFoundError for yaml
**Module:** Module 4 — Manual Testing (validation step)
**Symptom:** `python3 quick_validate.py` fails with `ModuleNotFoundError: No module named 'yaml'`
**Root Cause (First Principles):** The quick_validate.py script from skill-creator imports `yaml` (PyYAML), which is not in the Python standard library. It's a third-party package that needs to be installed via `pip install pyyaml`. The script doesn't document this dependency, and it's not bundled with the skill-creator.
**Fix:** Install PyYAML: `pip install pyyaml`. Document this prerequisite in Module 0 (environment setup).
**Prevention:** When referencing external scripts in course materials, always verify their dependencies are documented and available in the student's environment. Run every script from a clean environment before including it.
**Category:** validation

### BUG-004: extract-commits.sh crashes with "unbound variable" on empty array
**Module:** Module 3 — Supporting Resources (extract-commits.sh)
**Symptom:** Running the script without `--path` fails with: `line 108: PATH_ARGS[@]: unbound variable`
**Root Cause (First Principles):** The script uses `set -euo pipefail` — the `u` (nounset) flag treats any reference to an unset variable as an error. `PATH_ARGS` is initialized as an empty array `PATH_ARGS=()`, which is technically "set," but in Bash versions before 4.4, `"${array[@]}"` on an empty array is treated as an unbound reference. The expansion `"${PATH_ARGS[@]}"` produces zero words when the array is empty, and under `set -u` this triggers the unbound variable error. This is a well-known Bash gotcha: empty arrays and `nounset` don't mix portably.
**Fix:** Conditionally include the array in the git log command only when it has elements: `if [[ ${#PATH_ARGS[@]} -gt 0 ]]; then ... else ... fi`. The length check `${#array[@]}` is safe under `nounset` because it queries the array's attribute, not its expansion.
**Prevention:** When using `set -u` in bash scripts, never expand potentially-empty arrays directly. Either guard with a length check, use `"${array[@]+"${array[@]}"}"` (the `+` expansion is nounset-safe), or avoid `set -u` entirely in favor of explicit checks. Test all scripts with zero optional arguments.
**Category:** execution

### BUG-005: Single quotes inside single-quoted awk program crash the shell
**Module:** Module 3 — Supporting Resources (extract-commits.sh)
**Symptom:** Running the script fails with: `syntax error near unexpected token '('`. Error points to a comment line inside the awk program.
**Root Cause (First Principles):** The awk program is wrapped in single quotes (`awk '...'`). Inside the program, a comment contained single quotes: `# Extract just the type word (letters before any '(' or '!' or ':')`. In bash, there is no way to escape a single quote inside a single-quoted string — the first `'` before `(` terminates the quoted string. Bash then sees the unquoted `(` as a subshell operator, causing the syntax error. This is a fundamental property of bash quoting: single-quoted strings have NO escape sequences, not even `\'`. The initial diagnosis pointed at awk regex portability (`match()` third argument), but that was a downstream symptom — the script never reached awk execution because bash failed to parse the command first.
**Fix:** Removed all single quotes from comments inside the awk program. Also removed the gawk-specific `match()` third argument and replaced `\(` with `[(]` for regex literal parentheses (belt and suspenders for awk portability).
**Prevention:** Never put single quotes inside a single-quoted bash string. For awk programs that need `'`, either: (1) use `'\''` to break out and re-enter quoting, (2) pass the program via `-f script.awk`, or (3) avoid quotes in comments entirely. Lint: search for `'` inside `awk '...'` blocks before committing.
**Category:** execution

### BUG-006: Breaking change regex `/!:/` matches anywhere in subject
**Module:** Module 3 — Supporting Resources (extract-commits.sh)
**Symptom:** A commit like `chore: update config!: force` would be falsely flagged as a breaking change.
**Root Cause (First Principles):** The regex `subject ~ /!:/` tests whether `!:` appears anywhere in the subject string. The conventional commits spec requires `!` to appear in the type prefix position — immediately before `:` and after the type (or scope). The regex had no anchor to the prefix position, so any `!:` substring anywhere in the message would trigger a false positive.
**Fix:** Changed to `subject ~ /^[a-z]+([(][^)]*[)])?[!]:/` which anchors to the start of the string and requires the `!` to appear in the conventional commit prefix position (after type or scope, before `:`). Also used `[!]` and `[(]`/`[)]` character classes instead of bare `!` and `\(`/`\)` for awk portability.
**Prevention:** When detecting patterns in structured formats, always anchor regexes to the expected position in the structure. Test with at least one false-positive-producing input, not just true positives.
**Category:** execution

### BUG-007: Unresolved `<skill-path>` placeholder in SKILL.md
**Module:** Module 2 — Writing SKILL.md
**Symptom:** SKILL.md instructs Claude to run `bash <skill-path>/scripts/extract-commits.sh` but Claude has no `<skill-path>` variable to resolve.
**Root Cause (First Principles):** When a skill loads, Claude sees the SKILL.md content injected into its context. It knows the skill's directory from the Skill tool invocation. But `<skill-path>` is an invented placeholder that doesn't map to any Claude Code mechanism. The skill-building guide's own convention references scripts by relative path (e.g., "Run `scripts/audit_skill.py`") and lets Claude resolve the location from context. The placeholder introduced an abstraction that doesn't exist.
**Fix:** Replaced with a natural language instruction: "Run the bundled `scripts/extract-commits.sh` script (located in this skill's directory)." Claude resolves the path from the skill load context.
**Prevention:** Don't invent variable syntax in SKILL.md instructions. Use natural language to describe file locations relative to the skill directory. Claude will resolve paths from context.
**Category:** execution

### BUG-013: review skill description missing natural "look over" trigger phrase
**Module:** Gstack eval — Description testing (Step 7)
**Symptom:** Query "look over what I've done so far" (expected: review) routed to "none". The review description's trigger phrases ("review this PR", "check my code before merging", "pre-landing review", "code review") all use formal review vocabulary. Natural, casual phrasing like "look over my work" had no matching trigger.
**Root Cause (First Principles):** Trigger phrases were written from the skill author's perspective (formal task names) rather than the user's perspective (how developers actually talk). Developers say "look over my changes" more often than "pre-landing review." The skill-building guide says to use trigger phrases "users actually say" — this skill used terms the skill author would use.
**Fix:** Added "look over my changes" as a trigger phrase in the review description.
**Prevention:** When writing trigger phrases, imagine 5 different developers asking for this skill. Include at least one casual/informal phrasing alongside the formal ones. Test with queries that avoid any jargon or skill-specific vocabulary.
**Category:** undertriggering

---

## Lessons Learned

*Transferable insights discovered during the build process.*

### LESSON-001: Test spec parsers against ALL valid syntax variants
**Context:** BUG-001 — the conventional commit regex only handled `type(scope)!:` but not `type!(scope):`
**Insight:** When implementing a parser for a specification, the spec document is the source of truth for what's valid. Create test cases from the spec's grammar, not from common usage patterns. Edge cases in specs are where bugs hide.
**Evidence:** The regex worked for 90% of conventional commits but silently misclassified the `!` before scope variant, which is explicitly valid per the spec.

### LESSON-002: Mutually exclusive categories before arithmetic
**Context:** BUG-002 — breaking commits double-counted in version bump justification
**Insight:** When categorizing items into buckets for counting/display, ensure categories are mutually exclusive before doing arithmetic across them. If an item belongs to multiple categories, decide which one "wins" and filter the others.
**Evidence:** `total - breaking - feat - fix = -1` because a `feat!` commit was in both "breaking" and "feat" counts.

### LESSON-003a: Empty arrays + `set -u` is a Bash portability trap
**Context:** BUG-004 — extract-commits.sh crashed on `"${PATH_ARGS[@]}"` when PATH_ARGS was empty
**Insight:** `set -u` (nounset) and empty array expansion are incompatible in Bash < 4.4. This is one of the most common Bash scripting footguns. When writing portable shell scripts with strict mode, always guard empty array expansions with length checks or use the `${var+value}` safe-expansion pattern.
**Evidence:** Script passed all tests where `--path` was provided but crashed on the default case (no path), which is the most common invocation.

### LESSON-004a: Never put single quotes inside awk '...' programs
**Context:** BUG-005 — a comment with `'('` inside a single-quoted awk program caused bash to misparse the entire script
**Insight:** Single-quoted strings in bash have zero escape mechanisms. There is no `\'` inside `'...'`. A single quote always terminates the string. This is particularly treacherous in awk programs, where comments and string literals might naturally contain quotes. The symptom (awk syntax error) misled initial debugging toward awk regex portability, when the real issue was one layer up in bash quoting. Always debug from the outermost layer inward.
**Evidence:** Removing the quotes from the comment line fixed the "awk regex portability issue" that was actually never reached.

### LESSON-004b: Anchor regexes to structural positions, not just content
**Context:** BUG-006 — `/!:/` matched breaking change indicators anywhere in commit subjects
**Insight:** When a pattern has structural meaning (like the `!` in conventional commits appearing only in the prefix), the regex must encode that structural position. An unanchored regex tests content but not structure, leading to false positives on valid content that happens to contain the same characters in a different position.
**Evidence:** `chore: update config!: force` matched as breaking because `!:` appeared mid-subject, not in the prefix position.

### LESSON-004c: Don't invent placeholder syntax in skill instructions
**Context:** BUG-007 — `<skill-path>` placeholder in SKILL.md had no resolution mechanism
**Insight:** Claude doesn't have template variables. SKILL.md content is injected as-is into context. Use natural language to describe file locations relative to the skill directory. Claude resolves paths from the skill load event context. Inventing `<placeholder>` syntax creates an instruction Claude can't follow.
**Evidence:** The skill-building guide's own convention uses relative path names in natural language and works correctly.

### LESSON-011: Suite-aware eval is more efficient than per-skill eval
**Context:** Gstack eval — instead of 9 independent 20-query eval sets (180 queries), created one 127-query pool where each query has an expected routing target
**Insight:** For a skill suite, "should-NOT-trigger" queries for skill A are "should-trigger" queries for skill B. A unified eval pool naturally tests both directions with fewer total queries. The near-miss negatives (3 per skill) are the highest-signal queries — they directly test the boundaries between confusable skills. Creating them forces you to articulate exactly how adjacent skills differ.
**Evidence:** 27 near-miss queries (designed for maximum confusion) all routed correctly. These 27 queries provided more routing confidence than the 90 easy/medium should-trigger queries.

### LESSON-012: Ultra-vague queries set the accuracy floor, not skill overlap
**Context:** Gstack eval — 4 of 5 mismatches were queries too vague for any skill to safely capture ("does this look right to you?", "how should I approach this?")
**Insight:** Once descriptions follow the [WHAT + WHEN + WHEN NOT] structure with cross-referencing negative triggers, the confusable-pair problem is solved. The remaining accuracy gap comes from queries that lack ANY domain vocabulary — they can't be routed without conversation context. Trying to capture them with broader trigger phrases introduces far more false positives than it fixes.
**Evidence:** All 6 confusable pairs showed zero confusion. The only errors were generic queries with no skill-specific vocabulary at all.

### LESSON-013: Trigger phrases should include casual developer language, not just formal task names
**Context:** BUG-013 — review skill missed "look over my changes" because all trigger phrases used formal vocabulary
**Insight:** Developers don't say "pre-landing review" in casual conversation. They say "look over my changes" or "check what I've done." Trigger phrases should be sourced from how users actually talk, not from how skill authors categorize tasks. Include at least one informal/casual trigger phrase per skill.
**Evidence:** Adding "look over my changes" was the only description change needed across all 9 skills — and it addressed the only systematic routing gap (casual language falling through to "none").

### LESSON-003: Verify external tool dependencies before referencing them
**Context:** BUG-003 — quick_validate.py requires PyYAML but it's not installed
**Insight:** Course materials must be self-contained in their dependency documentation. Every external script referenced should have its prerequisites listed in the exercise where it's first used.
**Evidence:** Students hitting `ModuleNotFoundError` on their first validation attempt would be a terrible first experience.

---

## Design Decisions

*Key choices made during course construction and why.*

### LESSON-006: Skills need a CLAUDE.md to be discoverable in local projects
**Context:** Module 0 — setting up the student workspace
**Insight:** A SKILL.md file on its own isn't enough. In Claude Code, you need a CLAUDE.md in the project directory that references the skill for it to be loaded. Without it, Claude won't discover or trigger the skill.
**Evidence:** Had to create a CLAUDE.md in `student-workspace/hello-world/` to make the SKILL.md callable.

### LESSON-004: Skills about skills are recursive — and that's powerful
**Context:** Module 9 capstone — feeding documentation into a meta-skill
**Insight:** The process of building a skill teaches you exactly what a skill-building skill needs to contain. The bugs you hit ARE the pitfalls section. The lessons you learn ARE the best practices. Documentation isn't overhead — it's the domain knowledge.
**Evidence:** The meta-skill's `references/common-pitfalls.md` was almost entirely sourced from bugs encountered during the course build.

### LESSON-005: Validation scripts beat language instructions for correctness
**Context:** Building audit_skill.py vs writing "make sure your frontmatter is valid" in SKILL.md
**Insight:** A 383-line Python script catches 17 specific issues deterministically. No amount of natural language instruction can match this reliability. When correctness matters, bundle a script.
**Evidence:** The audit script caught every issue the Anthropic guide lists as a "common mistake" — including things like missing --- delimiters that a human reviewer might miss.

---

## Milestones

*What was built, how, and the state at each checkpoint.*

### MILESTONE-001: git-changelog skill — initial build complete (2026-03-13)
**What was built:**
Complete `git-changelog` skill with 4 files across 3 directories:
- `SKILL.md` (113 lines) — 5-step workflow: range resolution → extraction → categorization → formatting → edge cases. Includes troubleshooting section and resource index.
- `scripts/extract-commits.sh` — Bash script that extracts commits as JSON using ASCII record/unit separators to avoid delimiter collisions. Parses conventional commit format (type, scope, breaking change) via awk. Accepts `--from`, `--to`, `--since`, `--until`, `--path`, `--include-merges`.
- `references/changelog-formats.md` — 4 output format examples (Keep a Changelog, Simple List, Grouped by Scope, Verbose) with complete samples and formatting rules.
- `references/conventional-commits.md` — Type-to-category mapping table, breaking change detection rules (4 valid patterns), and keyword inference table for non-conventional repos.

**Key decisions:**
- Scripts over language instructions for commit parsing — deterministic JSON output matters more than flexibility
- References over assets — format examples serve as both documentation and templates; separate asset files would be redundant
- Keyword inference table in SKILL.md body (not just references) — needed every invocation since many repos don't use conventional commits
- ASCII separators (0x1e, 0x1f) instead of pipes/commas in git log format — avoids collisions with commit message content

**Validation:**
- Audit script: 17/17 PASS (structure, frontmatter, file references, triggers, negatives)
- Trigger test: 20/20 (10/10 should-trigger, 10/10 correct rejections)
- Script tested: handles invalid refs (exit 2), empty results (`[]`), missing optional args (BUG-004 fixed)
- Frontmatter verified against all 7 rules: kebab-case, folder match, 396/1024 chars, no XML, WHAT+WHEN covered, correct filename

**Bug encountered:** BUG-004 (empty array + `set -u`). See Bug Log.

### MILESTONE-002: git-changelog skill — review and hardening (2026-03-13)
**What happened:**
Code review of the skill found 3 additional bugs in the extract script, all related to portability and quoting:

- **BUG-005 (critical):** Single quotes in an awk comment (`'(' or '!'`) broke bash's parsing of the entire awk program. Bash saw the `'` as ending the single-quoted string and tried to interpret `(` as a subshell. The error message ("awk syntax error") misled initial debugging toward awk regex issues — the real failure was one layer up in shell quoting. This is the most insidious class of bug: the symptom points to the wrong layer.
- **BUG-006 (moderate):** Breaking change regex `/!:/` had no positional anchor — it matched `!:` anywhere in the subject, not just in the conventional commit prefix. Fixed with `^[a-z]+([(][^)]*[)])?[!]:` to anchor to the prefix position.
- **BUG-007 (moderate):** `<skill-path>` placeholder in SKILL.md is not a real Claude Code mechanism. Replaced with natural language description referencing the script by relative path.

**Additional hardening:**
- Replaced `\(` with `[(]` in awk regexes for POSIX awk compatibility (belt and suspenders)
- Removed gawk-only `match()` third argument

**Validation (post-fix):**
- Script tested against real git repo with conventional commits: correctly extracts type, scope for all prefix formats
- Breaking change detection: `feat(api)!: ...` correctly returns `is_breaking: true`
- Non-conventional commits: correctly fall through to `type: "other"`
- Frontmatter: still passes all 7 rules (no changes to frontmatter)

**Key insight:** The initial "awk portability" diagnosis was wrong. The debugging process went: awk third arg → awk regex `\(` → awk `?` quantifier → shell history expansion → **actual root cause: single quotes in comment**. First-principles debugging (testing each layer independently) was essential to not chasing the wrong fix.

---

## Design Decisions

*Key choices made during course construction and why.*

## DECISION-001: git-changelog as the example skill
**Context:** Needed a single skill for students to build progressively across all 10 modules
**Choice:** `git-changelog` — generates formatted changelogs from git history
**Why:** Progressive complexity (SKILL.md → scripts → refs → assets), clear success criteria (verifiable markdown output), rich trigger surface (many natural prompts + near-misses), works in any git repo, exercises multiple patterns
**Alternatives considered:** API doc generator (too MCP-dependent), code reviewer (too complex for early modules), commit message writer (too simple to exercise all features)

---

## Gstack Audit (2026-03-13)

*Audited, improved, and meta-skilled Garry Tan's gstack suite (8 skills) using the skill-building-guide methodology.*

### BUG-008: All 8 gstack skills missing negative triggers
**Module:** Gstack audit — Description improvement
**Symptom:** audit_skill.py returned WARN for "negative triggers" on all 8 skills. Any adjacent query could misfire — "review my plan" could activate the code review skill instead of the plan review skill.
**Root Cause (First Principles):** The gstack skills are a tightly-coupled suite where multiple skills handle variations of "review" (plan-ceo-review, plan-eng-review, review). Without negative triggers, Claude has no disambiguation signal. The description told Claude WHAT the skill does but not WHAT IT DOESN'T DO, leaving boundary detection to inference.
**Fix:** Added explicit "Do NOT use for [adjacent task] (use /correct-skill)" to every description, cross-referencing the correct skill by name.
**Prevention:** Any skill suite with overlapping domains MUST include cross-referencing negative triggers in every skill. Audit rule: if two skills share a keyword in their descriptions, both need negative triggers naming the other.
**Category:** overtriggering

### BUG-009: 5 of 8 skills missing trigger phrases in descriptions
**Module:** Gstack audit — Description improvement
**Symptom:** audit_skill.py returned WARN for "trigger phrases" on plan-ceo-review, plan-eng-review, review, ship, and setup-browser-cookies. These skills had descriptions explaining what they do but not when users would invoke them.
**Root Cause (First Principles):** The descriptions were written as feature summaries, not activation signals. Claude sees only name + description when deciding whether to activate a skill. Without trigger phrases ("review my plan", "ship it"), the description provides no pattern for Claude to match against user utterances.
**Fix:** Added 4-5 quoted trigger phrases to each description following the [WHAT] + [WHEN] + [WHEN NOT] structure from the skill-building guide.
**Prevention:** Every skill description must follow the structure template: [WHAT it does] + [WHEN: "trigger phrase 1", "trigger phrase 2"] + [WHEN NOT: negative triggers]. Use the audit_skill.py heuristic check as a gate.
**Category:** undertriggering

### BUG-010: plan-ceo-review body at 484 lines (near 500-line limit)
**Module:** Gstack audit — Progressive disclosure
**Symptom:** Body was 484 of 500 lines. Adding any content (troubleshooting, compatibility) would exceed the limit. The skill packed detailed reference tables, ASCII templates, and comparison matrices into the body even though they're only consulted during specific review sections.
**Root Cause (First Principles):** The progressive disclosure test ("Is this needed every invocation?") was not applied. Section 2's error/rescue table templates, Section 4's edge case tables, the completion summary template, and the mode comparison matrix are reference material — consulted during specific sections but not needed to understand the overall workflow.
**Fix:** Extracted 4 reference files (error-rescue-tables.md, edge-case-tables.md, completion-summary.md, mode-comparison.md). Body reduced from 484 to 283 lines. Added `Consult references/...` directives in the body.
**Prevention:** Apply the progressive disclosure test to every block of content: "Is this a table or template that's consulted during a specific step?" If yes, it belongs in references/. Target <300 lines for bodies with 10+ workflow steps.
**Category:** execution (context dilution)

### BUG-011: retro body at 429 lines with inline JSON schema
**Module:** Gstack audit — Progressive disclosure
**Symptom:** Body was 429 lines, with ~30 lines consumed by a JSON schema example and ~40 lines by metric formulas. These are reference material consulted during specific steps.
**Root Cause:** Same as BUG-010. The 45-minute session gap threshold, focus score formula, and JSON snapshot schema are constants/references, not workflow instructions.
**Fix:** Extracted 2 reference files (metrics-formulas.md, json-schema.md). Added explanation for the 45-minute gap threshold. Body reduced from 429 to 307 lines.
**Prevention:** JSON schemas and mathematical formulas are always reference material. Extract on sight.
**Category:** execution (context dilution)

### BUG-012: plan-ceo-review uses second-person voice instead of imperative
**Module:** Gstack audit — Style improvement
**Symptom:** Instructions like "You are not here to rubber-stamp this plan" read as motivational writing rather than executable instructions. The skill-building guide specifies imperative form ("Run `git log`" not "You should run `git log`").
**Root Cause:** The skill was written as a persona description ("You are a rigorous reviewer") rather than a runbook ("Review with maximum rigor"). Claude responds more reliably to imperative instructions than to persona descriptions.
**Fix:** Converted key instructions to imperative form: "Do not rubber-stamp. Make it extraordinary." Kept persona-style language only where it sets genuine cognitive mode (SCOPE EXPANSION vs HOLD SCOPE).
**Prevention:** Write SKILL.md body as a runbook for Claude, not a character description for Claude to inhabit. Persona framing goes in the description; the body uses imperative form.
**Category:** execution

### LESSON-008: Skill suites need cross-referencing negative triggers
**Context:** BUG-008 — all 8 gstack skills lacked negative triggers despite having overlapping domains
**Insight:** When building a suite of related skills, negative triggers are MORE important than trigger phrases. A single isolated skill might never misfire, but a suite with "review" in 3 different skill descriptions will constantly misroute without explicit boundaries. Each skill must name the adjacent skills users might confuse it with.
**Evidence:** The gstack routing confusion matrix: "review my plan" could match plan-ceo-review, plan-eng-review, OR review without negative triggers.

### LESSON-009: Progressive disclosure threshold is ~300 lines for complex workflows
**Context:** BUG-010, BUG-011 — plan-ceo-review at 484 lines, retro at 429 lines
**Insight:** Skills with 10+ workflow steps should target ~250-300 lines in the body, not the 500-line maximum. The 500-line limit is a hard ceiling, not a target. At 400+ lines, instruction-following degrades and there's no room for future improvements. Tables, templates, and formulas are almost always extractable.
**Evidence:** plan-ceo-review reduced from 484 to 283 lines with zero workflow loss — all 10 review sections preserved, only reference tables moved to references/.

### LESSON-010: Description structure [WHAT + WHEN + WHEN NOT] is non-negotiable
**Context:** BUG-009 — 5 of 8 skills missing trigger phrases
**Insight:** The skill-building guide's description template ([WHAT] + [WHEN: triggers] + [WHEN NOT: negatives]) isn't a suggestion — it's a structural requirement. Every field serves a distinct routing function: WHAT helps Claude understand the skill, WHEN provides activation patterns, WHEN NOT prevents misfire. Omitting any field degrades routing quality.
**Evidence:** After adding triggers and negatives to all 8 skills, audit_skill.py returned 0 warnings across the entire suite.

### MILESTONE-003: Gstack audit — 8 skills improved + 1 meta-skill created (2026-03-13)
**What was built:**
- Audited and improved all 8 gstack skills (plan-ceo-review, plan-eng-review, review, ship, qa, browse, setup-browser-cookies, retro)
- Created gstack-meta skill for workflow orchestration and skill routing
- Created 8 new reference files across 3 skills
- Enhanced review/checklist.md with concrete suppression examples
- Created audit-report.md with before/after comparison

**Validation:**
- All 9 skills: 0 WARN, 0 FAIL (134 total PASS)
- plan-ceo-review: 18P (including 4 file reference checks)
- retro: 16P (including 2 file reference checks)
- gstack-meta: 16P (including 2 file reference checks)
- All other skills: 14P each

**Key decisions:**
- Progressive disclosure for plan-ceo-review (484→283 lines) and retro (429→307 lines) — extracted tables/templates/schemas to references/
- Cross-referencing negative triggers between all related skills (review/plan-eng-review/plan-ceo-review all reference each other)
- gstack-meta skill routes by user intent, not skill name — uses decision tree and disambiguation rules
- Added compatibility fields to setup-browser-cookies (macOS) and noted framework dependencies in ship (Rails/Node.js) and plan-ceo-review (Rails)

**Bugs encountered:** BUG-008 through BUG-012 (see Bug Log above)

### MILESTONE-004: Gstack eval — suite-aware description testing (2026-03-13)
**What was done:**
Steps 6-7 of the skill-building-guide methodology: tested all 9 gstack skill descriptions against 127 realistic user queries to verify routing accuracy.

**Eval design:**
- Suite-aware eval: one unified query pool where every query has an expected routing target (or "none")
- Per skill: 10 should-trigger queries (3 easy / 4 medium / 3 hard) + 3 near-miss negatives targeting the most confusable adjacent skill
- 10 "none" queries for general coding tasks
- 60/40 train/test split (77 train / 50 test)
- 6 confusable pairs stress-tested: CEO↔eng, eng↔review, review↔ship, qa↔browse, browse↔cookies, retro↔CEO

**Results:**
- Train: 76/77 = 98.7%
- Test: 46/50 = 92.0%
- Total: 122/127 = 96.1%
- Train-test delta: 6.7pp (PASS, under 15% overfit threshold)
- Confusable pair confusion: 0/0/0/0/0/0 (all six pairs: zero misrouting)
- Description changes: 1 (added "look over my changes" to review triggers)
- All 9 skills still pass audit (0 WARN, 0 FAIL)

**5 mismatches (all irreducible or debatable):**
- 3x ultra-vague queries ("how should I approach this?", "does this look right to you?", "look over what I've done so far") → fell to "none" instead of activating a specific skill
- 1x vague workflow query ("what's the best way to handle this before merging?") → fell to "none" instead of gstack-meta
- 1x dual-intent query ("run a full QA pass... use those cookies") → routed to setup-browser-cookies instead of qa (both routings lead to correct behavior)

**Key insight:** The accuracy floor is set by ultra-vague queries, not by skill overlap. The [WHAT + WHEN + WHEN NOT] description structure from the skill-building guide produces descriptions that discriminate perfectly between confusable skills on the first pass.

**Bugs encountered:** BUG-013 (see Bug Log above)
**New lessons:** LESSON-011, LESSON-012, LESSON-013 (see Lessons section)

### MILESTONE-005: Eval lessons fed back into skill-building guide (2026-03-13)
**What was done:**
Integrated LESSON-011, LESSON-012, and LESSON-013 from the gstack eval back into the skill-building guide and Module 6 so future skill builders benefit from suite-level optimization insights.

**Files modified (4):**
- `skill-building-guide/SKILL.md` — Added "Suite Variant: Multi-Skill Optimization" subsection to Step 7 with 5 key differences from single-skill optimization
- `module-06-description-optimization/README.md` — Added Theory Section 7 (Suite-Aware Optimization, ~50 lines), "Recognizing Irreducible Ambiguity" subsection in Section 4, strengthened trigger phrase tip in Section 6 with casual-language guidance, added Key Takeaways #7 and #8
- `skill-building-guide/references/common-pitfalls.md` — Added pitfall #16 (formal-only trigger phrases) with symptom, root cause, fix, prevention, and BUG-013 evidence; updated quick reference table
- `course-log.md` — This milestone entry

**Evidence cited:**
- 96.1% accuracy on 127 queries (gstack eval)
- Zero confusable-pair confusion across 6 pairs
- BUG-013: "look over my changes" as the only needed description change
- 127 queries vs. 180 with standard per-skill approach

**Verification:**
- All existing content preserved (additions only, no deletions)
- Module 6 section numbering consistent (new Section 7 follows Section 6)
- Quick reference table updated with pitfall #16
- Gstack eval data cited with specific numbers throughout
