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
