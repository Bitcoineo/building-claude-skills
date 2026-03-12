---
name: skill-building-guide
description: Guide users through building Claude Code skills from scratch. Use when user asks to "create a skill", "build a skill", "help me make a skill", "write a SKILL.md", "improve my skill", or "troubleshoot my skill". Covers planning, writing SKILL.md, testing, description optimization, and packaging. Do NOT use for building MCP servers, writing plugins, or general coding tasks.
---

# Purpose

Guide the user through building a complete Claude Code custom skill, from initial concept to tested, optimized, distributable package. This skill encodes the full methodology for skill creation -- planning, writing, testing, and optimization -- so the user produces production-quality skills on their first attempt.

# Workflow Overview

Follow these 7 steps in order. Each step has a clear deliverable. Do not skip steps -- earlier steps prevent rework in later ones.

1. **Understand intent** -- What the skill should do and who it serves
2. **Plan structure** -- Directory layout and content placement
3. **Write frontmatter** -- Name, description, and metadata
4. **Write body** -- Instructions, examples, troubleshooting
5. **Add resources** -- Scripts, references, assets
6. **Test** -- Trigger testing, execution testing, iteration
7. **Optimize description** -- Systematic eval-based refinement

# Step 1: Understand Intent

Before writing anything, establish the skill's purpose and boundaries.

Ask the user for:
- **What the skill enables.** A concrete task, not a vague capability. "Generate changelogs from git history" not "help with git."
- **Which category it fits.** One of three:
  - **Document & Asset Creation** -- Produces consistent output (docs, designs, templates). Techniques: embedded style guides, quality checklists, output templates.
  - **Workflow Automation** -- Executes multi-step processes (deploy, review, migrate). Techniques: step ordering, validation gates, rollback instructions.
  - **MCP Enhancement** -- Orchestrates MCP server tools with domain knowledge. Techniques: phase separation, data passing between MCPs, centralized error handling.
- **2-3 concrete use cases.** Each with: trigger phrase, steps, expected result. If only one use case exists, the skill may be too narrow. If more than five, consider splitting.
- **5+ near-miss negatives.** Prompts that sound related but should NOT trigger the skill. These are more valuable than obviously-different negatives for description tuning.

Deliverable: A written spec with use cases, trigger phrases, near-misses, category classification, and success criteria.

# Step 2: Plan Structure

Decide what goes where using progressive disclosure:

| Level | Location | What goes here | When loaded | Budget |
|-------|----------|---------------|-------------|--------|
| 1 | Frontmatter | Name + description | Always (~100 words) | Max 1024 chars for description |
| 2 | SKILL.md body | Core workflow, examples, troubleshooting | When skill activates | Under 500 lines |
| 3 | references/ | Detailed docs, edge cases, specs | On demand | No hard limit |
| N/A | scripts/ | Executable code (run, not read) | Executed at runtime | N/A (zero context cost) |
| N/A | assets/ | Output templates, static files | Applied during generation | N/A |

Placement decision test:
1. Needed to decide whether to activate? -> Frontmatter description
2. Needed every invocation? -> SKILL.md body
3. Needed only sometimes? -> references/
4. Should be run, not read? -> scripts/
5. Structural template for output? -> assets/

Subdirectory decisions:
- **scripts/** -- Include when deterministic reliability matters, when the same logic would be regenerated every invocation, or when the task is computationally intensive. Code is more reliable than language instructions for parsing, validation, and data transformation.
- **references/** -- Include when detailed documentation exceeds what fits in the body, or when variant-specific docs exist (e.g., per-provider guides).
- **assets/** -- Include when output should follow a consistent template structure.

Deliverable: A directory tree with one-sentence justification for each included or omitted subdirectory.

# Step 3: Write Frontmatter

Create the YAML frontmatter block between `---` delimiters.

## Rules

**name field:**
- kebab-case only: `my-skill-name`, never `mySkillName` or `my_skill_name`
- Must match the folder name exactly
- Must NOT contain "claude" or "anthropic" (reserved terms, upload will be rejected)
- Keep it 2-4 words, descriptive

**description field:**
- Structure as: [WHAT it does] + [WHEN to use it with trigger phrases] + [WHEN NOT to use it]
- Maximum 1024 characters (anything longer is truncated, potentially losing trigger phrases)
- No XML angle brackets (`<` or `>`) anywhere -- they break the parser
- Include natural trigger phrases users would actually say, in quotes
- Include negative triggers to prevent overtriggering: "Do NOT use for [adjacent tasks]"
- Mention relevant file types or output formats if applicable

**Optional fields:**
- `license`: SPDX identifier (MIT, Apache-2.0)
- `compatibility`: Environment requirements, 1-500 chars
- `allowed-tools`: Whitelist of permitted tools (space-separated)
- `metadata`: Arbitrary key-value pairs (author, version, category, tags)

## Template

```yaml
---
name: skill-name-here
description: >-
  [What it does]. Use when user asks to "[trigger 1]", "[trigger 2]",
  or "[trigger 3]". Do NOT use for [adjacent task 1] or [adjacent task 2].
---
```

Use `>-` for multi-line descriptions -- it folds to a single line and strips trailing newlines.

Deliverable: Complete YAML frontmatter block validated against all rules.

# Step 4: Write Body

The body is everything below the frontmatter closing `---`. Write it as a runbook -- specific enough that someone unfamiliar with the task could follow it.

## Structure

```
# Purpose
(2-3 sentences: what the skill produces and why)

# Steps
(Numbered workflow with validation gates)

# Examples
(2-3 input/output pairs demonstrating the skill)

# Troubleshooting
(Common failures with cause, solution, and prevention)

# Bundled Resources
(List of scripts, references, assets with one-line descriptions)
```

## Writing Rules

- **Use imperative form.** "Run `git log`" not "You should run `git log`."
- **Explain WHY, not just WHAT.** "Use `--format="%aI"` for dates because it outputs strict ISO 8601, which sorts correctly across time zones" gives Claude context to handle edge cases.
- **Prefer explanations over rigid rules.** Reserve MUST/NEVER for genuine safety constraints. For everything else, explain the reasoning so Claude can adapt to edge cases.
- **Be specific.** Replace "handle appropriately" with explicit decision trees or checklists.
- **Number sequential steps.** Do not leave execution order to Claude's judgment.
- **State dependencies between steps.** "Step 2 uses the commit range from Step 1."
- **Add validation gates.** "Before proceeding to Step 3, confirm at least one result was found."
- **Include error handling.** For each step, specify what to do when it fails.
- **Reference bundled files explicitly.** Name the specific file and what it contains, not just the folder. Good: "For type definitions, consult the conventional-commits reference." Bad: "see the references folder."
- **Keep under 500 lines.** If approaching the limit, move detail to references/.

## Example and Troubleshooting Formats

Examples: show realistic user input and complete expected output. Include at least one simple and one complex case.

Troubleshooting: name the error, explain the cause, give a concrete solution. Claude follows this pattern reliably.

Deliverable: Complete SKILL.md body under 500 lines.

# Step 5: Add Resources

## Scripts

Bundle a script when:
- The same code would be regenerated every invocation
- Deterministic output matters (code > language instructions for parsing/validation)
- The task is computationally intensive

Script requirements:
- Proper shebang (`#!/usr/bin/env python3` or `#!/usr/bin/env bash`)
- Usage documentation at the top
- Accept parameters with sensible defaults
- Return structured output (JSON preferred)
- Handle errors gracefully with JSON error messages and non-zero exit codes
- No undocumented external dependencies

## References

Create when detailed docs exceed body budget, variant-specific content exists, or edge cases would clutter the workflow. Include a table of contents for files over 300 lines. Write for Claude as the primary reader.

## Assets

Create when output should follow a consistent template structure. Assets standardize output format, not knowledge.

All files referenced in SKILL.md must actually exist. Run `scripts/audit_skill.py` to verify.

Deliverable: All supporting files created and referenced correctly from SKILL.md.

# Step 6: Test

Three types of problems to test for:

## Undertriggering (skill does not load when it should)

Symptoms: User has to manually invoke the skill. Works great when it fires, but rarely fires.
Root cause: Description missing trigger phrases users actually say.
Fix: Add more trigger phrases, synonyms, and contextual triggers to the description.

## Overtriggering (skill loads for unrelated queries)

Symptoms: Skill activates on unrelated prompts. Users disable it because it interferes.
Root cause: Description too broad, generic terms without scoping, no negative triggers.
Fix: Add negative triggers, be more specific about outputs, narrow the scope.

## Execution Issues (skill loads but does not follow instructions)

Symptoms: Missing sections, skipped steps, wrong format, Claude invents its own approach.
Root causes and fixes:
- Instructions too verbose -> Convert to bullet points, move details to references
- Critical instructions buried -> Pull to top, use dedicated headings
- Ambiguous language -> Replace with explicit checklists
- Scripts not being used -> Make instruction unambiguous, explain why the script matters

## Testing Process

1. Create 5 should-trigger prompts and 5 should-not-trigger prompts
2. Run each prompt and record: expected outcome, actual outcome, notes
3. For triggered prompts, review execution: Did Claude follow the steps? Use the scripts? Consult references?
4. Classify each issue: undertrigger, overtrigger, or execution
5. Fix the single most impactful issue first (priority: undertrigger > overtrigger > execution)
6. Retest with the same prompts. Check for regressions.
7. Repeat until trigger accuracy is above 80% and execution quality is consistent

Use the debugging question technique: ask Claude "When would you use the [skill-name] skill?" and compare the answer to intended use cases.

Deliverable: Testing log with results, identified issues, and at least one fix-and-retest cycle.

# Step 7: Optimize Description

The description is the gatekeeper. Claude sees only name + description when deciding whether to load a skill.

## Optimization Process

1. Create 20 eval queries: 10 should-trigger, 10 should-NOT-trigger
   - Should-trigger: realistic, varied phrasing, different specificity levels
   - Should-NOT-trigger: near-miss negatives that test discrimination (not trivially different queries)
2. Split 60/40: 12 train, 8 test
3. Score the current description against the train set
4. Propose an improved description targeting the errors
5. Re-score. Keep if better, revert if worse. Ties go to the shorter description.
6. Repeat up to 5 iterations (most gains happen in iterations 1-3)
7. Validate on the held-out test set
8. If test accuracy is 15%+ worse than train: description is overfit, broaden the language

## Quality Guidelines for Eval Queries

Near-miss negatives are more valuable than obviously-different negatives:
- Good negative: "Show me the git log for the last week" (related domain, different intent)
- Bad negative: "What's the weather today?" (trivially different, tests nothing)

Deliverable: Optimized description with train/test accuracy scores.

# Common Pitfalls

For detailed pitfall analysis with symptoms, root causes, and fixes, consult `references/common-pitfalls.md`.

Summary of the most frequent issues:

1. **Regex parsers not tested against all spec variants.** Test with every valid syntax form, not just common usage.
2. **Category counting with non-disjoint sets.** Make categories mutually exclusive before arithmetic.
3. **External dependencies not documented.** Verify all scripts work in a clean environment.
4. **Description too vague.** Leads to undertriggering. Include specific trigger phrases users actually say.
5. **Description too broad.** Leads to overtriggering. Add negative triggers and scope qualifiers.
6. **Critical instructions buried in the body.** Claude may skip them. Put important instructions at the top.
7. **README.md instead of SKILL.md.** The file MUST be named `SKILL.md`. README.md is ignored.
8. **Folder name does not match name field.** Mismatches cause silent upload failures.
9. **Body over 500 lines.** Dilutes critical instructions. Move detail to references/.
10. **Angle brackets in frontmatter.** Breaks the parser entirely.

# Skill Patterns

Five canonical patterns cover most skill architectures. Most production skills combine 2-3 patterns.

1. **Sequential Workflow Orchestration** -- Multi-step processes with dependencies between steps
2. **Multi-MCP Coordination** -- Workflows spanning multiple MCP servers
3. **Iterative Refinement** -- Self-verification and correction loops
4. **Context-Aware Tool Selection** -- Routing to different tools based on context
5. **Domain-Specific Intelligence** -- Embedding specialized knowledge Claude lacks by default

For detailed pattern descriptions, decision tree, and worked examples, consult `references/patterns.md`.

Pattern selection shortcut:
- Almost every skill uses Pattern 1 (Sequential Workflow) as its backbone
- Pattern 5 (Domain Intelligence) is what makes a skill worth building over a raw prompt
- Add other patterns only when you have a clear, affirmative reason

# Output Format

When helping a user build a skill, deliver these artifacts:

1. **Technical spec** -- Use cases, trigger phrases, near-misses, category, success criteria
2. **SKILL.md** -- Complete file with frontmatter and body
3. **Supporting files** -- Any scripts, references, or assets referenced in the body
4. **Testing log** -- Trigger test results and execution quality assessment
5. **Validation report** -- Run `scripts/audit_skill.py` and fix any FAIL items

Present each artifact with a brief explanation of the decisions made and trade-offs considered.

# Bundled Resources

- `scripts/audit_skill.py` -- Validate a skill directory structure, frontmatter, and file references
- `references/common-pitfalls.md` -- Top 15 pitfalls with symptoms, root causes, fixes, and prevention
- `references/patterns.md` -- 5 canonical skill patterns with decision tree and worked example
