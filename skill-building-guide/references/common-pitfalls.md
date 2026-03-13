# Common Skill-Building Pitfalls

Top 16 pitfalls organized by category, synthesized from real bugs encountered during skill development and common issues from the Anthropic skill-authoring guide.

---

## Table of Contents

- [Undertriggering](#undertriggering)
- [Overtriggering](#overtriggering)
- [Execution Issues](#execution-issues)
- [Validation and Parsing](#validation-and-parsing)
- [Packaging and Structure](#packaging-and-structure)

---

## Undertriggering

### 1. Description uses only one phrase for the skill's purpose

**Symptom:** The skill works great when it fires, but it rarely fires. Users have to manually tell Claude to use it.

**Root cause:** The description says "generate changelogs" but the user said "summarize recent commits" or "what changed since v1.0?" -- Claude cannot connect different phrasings to the same intent without explicit help.

**Fix:** Add 4-6 varied trigger phrases that real users would say. Include synonyms, different levels of specificity, and contextual triggers (dates, versions, sprints).

**Prevention:** During planning (Step 1), collect trigger phrases from 2-3 different people describing the task. If everyone uses the same words, cast a wider net -- think about how someone unfamiliar with the tool would ask for it.

### 2. Description uses jargon instead of natural language

**Symptom:** Technical users trigger the skill fine, but non-technical users never do.

**Root cause:** "Aggregate commit metadata into categorized release artifacts" describes the task accurately but nobody says that. Users say "what changed this week?" or "make release notes."

**Fix:** Replace technical terms with the natural language equivalents users actually type. Keep one technical phrase for precision, but lead with plain language.

**Prevention:** Read the description aloud. If it sounds like API documentation, rewrite it.

### 3. Missing contextual triggers

**Symptom:** The skill triggers on general requests ("generate a changelog") but not on specific ones ("what changed since the v2.0 tag?" or "summarize this sprint's work").

**Root cause:** The description mentions the core action but not the context modifiers (date ranges, version tags, sprint boundaries) that distinguish real requests from generic ones.

**Fix:** Add contextual trigger phrases: "since [version]", "between [dates]", "this week/sprint", "since the last release."

**Prevention:** For each use case, write down the 3 most common context modifiers users would include. Add them to the description.

---

## Overtriggering

### 4. Description too broad -- matches adjacent tasks

**Symptom:** The skill fires on prompts that are related to the same domain but require completely different behavior. A changelog skill fires on "help me write a commit message" or "set up git hooks."

**Root cause:** The description says "helps with git" or "works with commit history" which is true but too broad. Claude matches any git-related prompt.

**Fix:** Add explicit negative triggers: "Do NOT use for writing commit messages, viewing raw git log, or configuring git workflows." Scope the description to the specific artifact produced.

**Prevention:** During planning, write 5+ near-miss negative prompts. After writing the description, verify it would NOT match those prompts.

### 5. Generic terms without scoping

**Symptom:** A "summarize" skill fires on "summarize this Python file" when it was designed for "summarize recent commits."

**Root cause:** The description includes "summarize" without qualifying what is being summarized. Claude sees "summarize" in the user prompt, matches it to "summarize" in the description.

**Fix:** Always qualify action verbs with their object: "summarize git commits" not "summarize." "Generate markdown changelogs" not "generate documents."

**Prevention:** Search the description for unqualified verbs (summarize, generate, create, analyze, format). Each one should specify its target domain.

### 6. No negative triggers defined

**Symptom:** The skill overtriggers on predictable near-miss prompts that could have been excluded.

**Root cause:** The description defines when to activate but never defines when NOT to activate. Claude has no explicit boundary to enforce.

**Fix:** Add a "Do NOT use for..." clause listing 2-4 adjacent tasks that share vocabulary with the skill but require different behavior.

**Prevention:** Every description should have three parts: WHAT it does, WHEN to use it, WHEN NOT to use it. If the third part is missing, add it.

---

## Execution Issues

### 7. Critical instructions buried in the body

**Symptom:** Claude follows most of the workflow but consistently skips one important step -- often a validation gate, a specific script to run, or a formatting requirement.

**Root cause:** The critical instruction is in paragraph 4 of step 3 of a 7-step workflow. Claude processes the early and late parts of the body more reliably than the middle.

**Fix:** Pull critical instructions to a dedicated section near the top:

```markdown
## Important

Before generating any output:
- Run parse_commits.py rather than parsing commits manually
- Include the short commit hash in every entry
- Put Breaking Changes before all other sections
```

**Prevention:** After writing the body, identify the 3 instructions that would cause the worst output if skipped. Make sure each one is either in the first 50 lines or has its own heading.

### 8. Instructions too verbose -- Claude summarizes or skips

**Symptom:** Claude takes shortcuts. A 7-step workflow gets compressed to 3 steps. Entire sections are omitted.

**Root cause:** The body is a wall of prose. Claude's attention distributes across the full context, so diluting it with verbose explanations means important instructions get less weight.

**Fix:** Convert prose to bullet points and numbered lists. Move background explanations to `references/`. Keep the body under 500 lines.

**Prevention:** Apply the "would a senior engineer approve this runbook?" test. Runbooks are terse, structured, and scannable. If a section reads like an essay, it belongs in a reference file.

### 9. Ambiguous language produces inconsistent behavior

**Symptom:** The skill works differently every time. Sometimes it categorizes commits, sometimes it does not. Sometimes it includes hashes, sometimes not.

**Root cause:** The instructions say "categorize commits appropriately" or "include relevant details" -- language that leaves room for interpretation.

**Fix:** Replace every ambiguous instruction with an explicit checklist or decision tree. "Categorize each commit into exactly one of: Features (feat:), Bug Fixes (fix:), Other."

**Prevention:** Search the body for words like: appropriately, relevant, suitable, as needed, properly, handle. Each one is a bug waiting to happen. Replace with specifics.

### 10. Scripts referenced but not used by Claude

**Symptom:** `scripts/parse_commits.py` exists and is referenced in SKILL.md, but Claude parses commits manually instead.

**Root cause:** The instruction says "use parse_commits.py to parse commits" but doesn't explain why manual parsing is worse. Claude may decide it can handle the task inline.

**Fix:** Make the instruction unambiguous AND explain the consequence: "Run `scripts/parse_commits.py` to parse commit data. Do not parse commits manually -- the script handles edge cases (multi-line bodies, special characters, co-authored commits) that manual parsing misses."

**Prevention:** For every script reference, include: (1) the exact command to run, (2) why the script is better than ad hoc code, (3) what goes wrong without it.

---

## Validation and Parsing

### 11. Regex parser does not cover all valid syntax variants

**Symptom:** Most inputs parse correctly, but certain valid syntax forms are silently misclassified. A conventional commit regex handles `feat(scope)!:` but not `feat!(scope):`.

**Root cause:** The regex was developed from common examples, not from the specification grammar. Edge cases in the spec were never tested.

**Fix:** Read the specification grammar. Create test cases for every valid production rule, including rarely-used variants. For the conventional commits spec, this means testing: type only, type with scope, type with `!`, type with scope and `!` in both positions, type with body, type with footer, type with both.

**Prevention:** When implementing a spec parser, generate test cases from the spec's grammar before writing the regex. Edge cases in specs are where bugs hide.

### 12. Category counting with overlapping sets

**Symptom:** Derived counts go negative or exceed the total. "1 breaking, 1 feature, 1 fix, -1 other" for 2 commits.

**Root cause:** An item belongs to multiple categories (a `feat!` commit is both "breaking" and "feat"), but the counting formula assumes categories are disjoint: `other = total - breaking - feat - fix`.

**Fix:** Make categories mutually exclusive before arithmetic. Decide which category "wins" and filter the others. For example, count breaking commits separately, then count feat/fix only among non-breaking commits.

**Prevention:** Whenever counting items across categories, ask: "Can an item be in two categories?" If yes, define a precedence order and make each item belong to exactly one bucket.

### 13. External dependency not documented or available

**Symptom:** Script fails with `ModuleNotFoundError` or `command not found` on the user's machine.

**Root cause:** The script imports a third-party package (PyYAML, requests, etc.) that is not in the standard library and not documented as a prerequisite.

**Fix:** Either: (a) remove the external dependency and use standard library equivalents, (b) document the dependency in the `compatibility` frontmatter field, or (c) bundle a requirements.txt and add installation instructions.

**Prevention:** Run every script from a clean environment (new virtualenv, no extras installed) before including it. If it fails, the dependency is undocumented.

---

## Packaging and Structure

### 14. File named README.md instead of SKILL.md

**Symptom:** The skill folder exists with a well-written instruction file, but the skill never loads. Claude says no relevant skills are available.

**Root cause:** The instruction file is named `README.md` (or `skill.md` or `Skill.md`). Claude only reads `SKILL.md` -- exact name, case-sensitive.

**Fix:** Rename the file to `SKILL.md`.

**Prevention:** Always check: `ls -la skill-dir/SKILL.md`. If that command fails, the name is wrong.

### 15. Folder name does not match name field

**Symptom:** The skill uploads but never appears in the available skills list, or appears with unexpected behavior.

**Root cause:** The folder is named `git_changelog/` but the frontmatter says `name: git-changelog`. Or the folder is `GitChangelog/` but the name is `git-changelog`. The system expects an exact match.

**Fix:** Ensure the folder name and the `name` field are identical. Both must be kebab-case.

**Prevention:** After writing the frontmatter, run `audit_skill.py` which explicitly checks this match. Or simply check: does `basename $(pwd)` equal the value of the `name` field?

### 16. Trigger phrases use only formal task names

**Symptom:** Technical users who know the skill's name trigger it fine, but casual or informal requests don't. "Pre-landing review" works, "look over my changes" doesn't.

**Root cause:** All trigger phrases use formal task names ("pre-landing review", "code review", "run QA suite") but developers in a CLI often speak casually: "look over my changes", "check what I did", "try this out in a browser." The description provides no pattern for Claude to match against informal phrasing.

**Fix:** Include at least one casual phrasing per skill that matches how developers actually talk. For each formal trigger, ask: "would I say this in a Slack message to a teammate?" If not, add the version you would.

**Prevention:** When writing trigger phrases, imagine 5 different developers asking for the skill. At least one should be a junior dev who doesn't know the skill's formal name. Include whatever they would say.

**Evidence:** BUG-013 from the gstack eval -- the only systematic routing gap across 9 skills was casual language falling through to "none" because all trigger phrases used formal vocabulary. Adding "look over my changes" to the review skill fixed the gap.

---

## Quick Reference

| # | Pitfall | Category | Severity |
|---|---------|----------|----------|
| 1 | Single trigger phrase | Undertriggering | High |
| 2 | Jargon in description | Undertriggering | Medium |
| 3 | Missing context modifiers | Undertriggering | Medium |
| 4 | Description too broad | Overtriggering | High |
| 5 | Unqualified generic terms | Overtriggering | High |
| 6 | No negative triggers | Overtriggering | Medium |
| 7 | Critical instructions buried | Execution | High |
| 8 | Body too verbose | Execution | Medium |
| 9 | Ambiguous language | Execution | High |
| 10 | Scripts not used | Execution | Medium |
| 11 | Regex misses spec variants | Validation | High |
| 12 | Overlapping category counts | Validation | Medium |
| 13 | Undocumented dependencies | Validation | High |
| 14 | README.md instead of SKILL.md | Packaging | Critical |
| 15 | Folder/name mismatch | Packaging | Critical |
| 16 | Formal-only trigger phrases | Undertriggering | Medium |
