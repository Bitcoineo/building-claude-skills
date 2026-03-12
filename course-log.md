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

### LESSON-003: Verify external tool dependencies before referencing them
**Context:** BUG-003 — quick_validate.py requires PyYAML but it's not installed
**Insight:** Course materials must be self-contained in their dependency documentation. Every external script referenced should have its prerequisites listed in the exercise where it's first used.
**Evidence:** Students hitting `ModuleNotFoundError` on their first validation attempt would be a terrible first experience.

---

## Design Decisions

*Key choices made during course construction and why.*

### LESSON-004: Skills about skills are recursive — and that's powerful
**Context:** Module 9 capstone — feeding documentation into a meta-skill
**Insight:** The process of building a skill teaches you exactly what a skill-building skill needs to contain. The bugs you hit ARE the pitfalls section. The lessons you learn ARE the best practices. Documentation isn't overhead — it's the domain knowledge.
**Evidence:** The meta-skill's `references/common-pitfalls.md` was almost entirely sourced from bugs encountered during the course build.

### LESSON-005: Validation scripts beat language instructions for correctness
**Context:** Building audit_skill.py vs writing "make sure your frontmatter is valid" in SKILL.md
**Insight:** A 383-line Python script catches 17 specific issues deterministically. No amount of natural language instruction can match this reliability. When correctness matters, bundle a script.
**Evidence:** The audit script caught every issue the Anthropic guide lists as a "common mistake" — including things like missing --- delimiters that a human reviewer might miss.

---

## Design Decisions

*Key choices made during course construction and why.*

## DECISION-001: git-changelog as the example skill
**Context:** Needed a single skill for students to build progressively across all 10 modules
**Choice:** `git-changelog` — generates formatted changelogs from git history
**Why:** Progressive complexity (SKILL.md → scripts → refs → assets), clear success criteria (verifiable markdown output), rich trigger surface (many natural prompts + near-misses), works in any git repo, exercises multiple patterns
**Alternatives considered:** API doc generator (too MCP-dependent), code reviewer (too complex for early modules), commit message writer (too simple to exercise all features)
