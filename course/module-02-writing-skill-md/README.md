# Module 2: Writing the SKILL.md

**Time estimate:** 30-45 minutes
**Prerequisites:** Completed Module 1 (technical spec and directory plan)
**Outcome:** A first-draft SKILL.md for your git-changelog skill, ready for manual testing in Module 4

---

## Learning Objectives

By the end of this module, you will be able to:

- Write valid YAML frontmatter with a trigger-rich description
- Structure the instruction body with steps, examples, and troubleshooting
- Apply writing best practices: imperative form, specific actions, explain "why"
- Self-audit your SKILL.md against a quality checklist

---

## Theory

### 1. The Description Field

The `description` field in your frontmatter is the single most important line you will write. It determines whether Claude loads your skill at all. When a user types a prompt, Claude scans the `description` of every available skill to decide which ones to activate. A vague description means your skill never fires. An overly broad one means it fires when it shouldn't.

**Structure every description as:** [What it does] + [When to use it] + [Key capabilities]

**Good descriptions:**

```
Generate formatted changelogs and release notes from git history. Use when
user asks to "generate a changelog", "what changed since [version/date]",
"summarize recent commits", or "prepare release notes". Supports conventional
commits, custom date ranges, and multiple output formats.
```

Why this works:
- **What it does** is concrete: "Generate formatted changelogs and release notes from git history"
- **When to use it** includes actual user phrases: "generate a changelog", "what changed since..."
- **Key capabilities** are specific: conventional commits, date ranges, output formats

**Bad descriptions:**

```
Helps with git stuff.
```

Why this fails:
- No trigger phrases -- Claude cannot match user intent to this skill
- "Helps with" is vague -- every skill "helps with" something
- No mention of changelogs, release notes, or any concrete output

```
A comprehensive tool for analyzing repository history using advanced commit
parsing algorithms and multi-format templating engines.
```

Why this fails:
- Written for engineers, not for matching user prompts
- No trigger phrases a user would actually say
- "Comprehensive" and "advanced" are filler words

**The litmus test:** Read the description, then ask yourself: "If a user said 'generate a changelog for the last sprint,' would Claude match this description?" If the answer is uncertain, rewrite it.

---

### 2. YAML Frontmatter Deep Dive

The frontmatter is a YAML block delimited by `---` at the top of your SKILL.md. Here is every field, in order of importance.

#### Required Fields

**`name`** (string)
- Use kebab-case: `git-changelog`, not `gitChangelog` or `Git Changelog`
- Match the folder name exactly. If the folder is `git-changelog/`, the name is `git-changelog`
- Keep it short and descriptive (2-4 words)

**`description`** (string)
- Maximum 1024 characters
- Include what the skill does AND when to use it
- Include specific user phrases that should trigger the skill
- Mention relevant file types if the skill works with specific formats (e.g., "Parses .csv and .tsv files")
- No XML angle brackets (`<` or `>`) -- the parser will reject them

#### Optional Fields

**`license`** (string)
- Standard SPDX identifiers: `MIT`, `Apache-2.0`, `BSD-3-Clause`
- Omit if you don't plan to distribute the skill

**`compatibility`** (string, 1-500 characters)
- Describe environment requirements: "Requires git 2.20+ and Python 3.8+"
- Include OS constraints if relevant: "macOS and Linux only"
- Mention required CLI tools: "Requires the gh CLI for GitHub API access"

**`metadata`** (object)
- Arbitrary key-value pairs for your own use
- Common keys: `author`, `version`, `mcp-server`
- Example:
  ```yaml
  metadata:
    author: your-name
    version: 0.1.0
  ```

#### Security Constraints

Two hard rules for all frontmatter:

1. **No XML angle brackets** in any field value. The `<` and `>` characters will cause the parser to reject your skill entirely. Use parentheses or quotes instead.
2. **No "claude" or "anthropic" in the name field.** These are reserved. `claude-helper` will be rejected; `commit-helper` will not.

#### Complete Frontmatter Example

```yaml
---
name: git-changelog
description: >-
  Generate formatted changelogs and release notes from git history.
  Use when user asks to "generate a changelog", "what changed since
  [version/date]", "summarize recent commits", "prepare release notes",
  or "draft release notes for [version]". Supports conventional commits,
  custom date ranges, and multiple output formats.
license: MIT
compatibility: Requires git 2.20+ installed and accessible on PATH
metadata:
  author: your-name
  version: 0.1.0
---
```

Note the `>-` YAML scalar -- it folds the description into a single line and strips the trailing newline. This is the cleanest way to write long descriptions.

---

### 3. Writing the Main Instructions

The body of your SKILL.md (everything below the frontmatter) is the instruction set Claude follows when executing the skill. Think of it as a runbook: specific enough that someone unfamiliar with the task could follow it step by step.

#### Recommended Structure

```
# Purpose
(2-3 sentences: what this skill produces and why it's useful)

# Steps
(Numbered workflow -- the main execution path)

# Output Format
(Template or example of the expected output)

# Examples
(2-3 Input/Output pairs showing the skill in action)

# Troubleshooting
(Common failure modes with causes and solutions)
```

#### Be Specific and Actionable

Every instruction should tell Claude exactly what to do. Compare:

| Vague | Specific |
|---|---|
| Validate the data | Run `git log --oneline -1` to confirm the repository has commits |
| Process the commits | Parse each commit using `git log --format="%H %s" v1.0..HEAD` |
| Format the output | Group commits under headings: Features, Bug Fixes, Other Changes |

If you find yourself writing "handle appropriately" or "process as needed," stop and spell out what "appropriately" means.

#### Include Error Handling

Do not hope for the happy path. Specify what to do when things go wrong:

```markdown
## Troubleshooting

### No tags found in repository
**Cause:** The repository has no version tags, so tag-based ranges fail.
**Solution:** Fall back to date-based ranges. Ask the user for a start date,
or default to the last 30 days: `git log --after="30 days ago"`.

### Shallow clone detected
**Cause:** `git rev-parse --is-shallow-repository` returns true.
**Solution:** Warn the user that the log may be incomplete. Suggest running
`git fetch --unshallow` if a full history is needed.
```

Notice the pattern: name the error, explain the cause, give a concrete solution. Claude follows this structure reliably.

#### Reference Bundled Resources

When your skill includes helper scripts or reference files, point to them explicitly:

```markdown
Parse commits using the helper script at `scripts/parse_commits.py`.
For conventional commit type definitions, consult `references/conventional-commits.md`.
Use the template at `assets/changelog-template.md` for the final output.
```

Always use relative paths from the skill root. Claude resolves these against the skill directory.

#### Progressive Disclosure

The SKILL.md should stay focused on the primary workflow. Move supplementary detail into reference files:

| Keep in SKILL.md | Move to references/ |
|---|---|
| The 5-step workflow | Full conventional commit spec |
| Output format template | Extended formatting options |
| 2-3 usage examples | Edge case catalog |
| Common troubleshooting | API documentation |

A SKILL.md that tries to cover everything becomes a wall of text that dilutes the core instructions. When in doubt, link out.

---

### 4. Writing Style

How you write matters as much as what you write. Claude is sensitive to tone and structure -- the right style produces more consistent execution.

#### Use Imperative Form

Write commands, not suggestions.

| Do this | Not this |
|---|---|
| Run `git log --oneline` | You should run `git log --oneline` |
| Parse the commit messages | You will need to parse the commit messages |
| Present the changelog to the user | The changelog should be presented to the user |

The imperative form is shorter, clearer, and maps directly to actions.

#### Explain WHY, Not Just WHAT

Instructions without rationale produce brittle execution. When Claude understands the purpose, it can adapt to edge cases.

```markdown
# Good
Use `--format="%aI"` for dates because it outputs strict ISO 8601 format,
which sorts correctly across time zones.

# Less good
Use `--format="%aI"` for dates.
```

The first version gives Claude the context to make a reasonable decision if it encounters a date-related edge case. The second just says "do this" with no basis for judgment.

#### Prefer Explanations Over Rigid Rules

Rigid rules (MUST, NEVER, ALWAYS) have their place, but overusing them creates a brittle, adversarial tone. Compare:

```markdown
# Rigid
NEVER include merge commits in the changelog. ALWAYS filter them out.

# Explanatory
Filter out merge commits because they duplicate information already captured
in the feature commits. If the repository uses a merge-only workflow (no
squash merges), include merge commits but strip the "Merge branch..." prefix.
```

The explanatory version handles more cases and gives Claude room to adapt. Reserve MUST/NEVER for genuine safety constraints (e.g., "Do not expose API keys in the output").

#### Formatting for Scannability

- Use **bullet points** for unordered lists of options or considerations
- Use **numbered lists** for sequential steps that must happen in order
- Use **headings** to create scannable sections -- Claude navigates by heading
- Use **code blocks** for any command, path, or output template
- Keep paragraphs short (3-5 sentences maximum)

#### Size Constraints

- Keep the body under **500 lines** and **5000 words**
- If you are approaching the limit, move content to `references/`
- A skill that is too long wastes tokens and dilutes the important instructions

---

## Exercises

### Exercise 2.1: Write the Frontmatter

Write the complete YAML frontmatter for your git-changelog skill.

**Requirements:**
- Include `name` and `description` (required)
- Add at least one optional field
- Ensure the description includes trigger phrases a user would actually say

**Checklist -- test your frontmatter against these:**
- [ ] `name` is kebab-case and matches your folder name
- [ ] `description` says what the skill does
- [ ] `description` says when to use it (with example phrases)
- [ ] `description` is under 1024 characters
- [ ] No XML angle brackets (`<` or `>`) anywhere in the frontmatter
- [ ] No "claude" or "anthropic" in the name

If any item fails, revise before moving on.

**Reference solution:** See `solutions/git-changelog/SKILL.md` for one valid approach.

---

### Exercise 2.2: Write the Body

Write the full SKILL.md body (everything below the frontmatter) for your git-changelog skill.

**Requirements:**
1. **Purpose section** -- 2-3 sentences explaining what the skill produces and who benefits
2. **Steps section** -- Numbered instructions for the main workflow (determining range, parsing commits, categorizing, formatting, presenting output)
3. **Output format** -- A markdown template showing the structure of a generated changelog
4. **Examples section** -- At least 2 Input/Output pairs:
   - "Generate a changelog since v1.0"
   - "What changed this week?"
5. **Troubleshooting section** -- At least 3 common failure modes with cause and solution

**Tips:**
- Write the steps first, then the examples. The examples should demonstrate the steps in action.
- For the output format, sketch the actual markdown a user would see -- headings, bullet points, commit references.
- Troubleshooting entries should cover the failures you would actually encounter: missing tags, shallow clones, empty ranges.

**Reference solution:** See `solutions/git-changelog/SKILL.md`

---

### Exercise 2.3: Style Audit

Review the SKILL.md you wrote in Exercise 2.2 against these criteria. Fix any issues you find.

**Checklist:**

1. **Second-person language sweep**
   - Search for "you", "your", "you'll", "you should"
   - Rewrite every instance in imperative form
   - Example: "You should run git log" becomes "Run git log"

2. **Rigid rule audit**
   - Search for MUST, NEVER, ALWAYS, DO NOT
   - For each one, ask: "Can this be an explanation instead?"
   - Keep rigid rules only for genuine safety constraints
   - Rewrite the rest as explanations with rationale

3. **Size check**
   - Count the lines in your body (below the frontmatter closing `---`)
   - Target: under 500 lines
   - If over, identify content that belongs in `references/` and move it

4. **Resource reference check**
   - Find every mention of a file path (scripts/, references/, assets/)
   - Confirm each referenced file is in your directory plan from Module 1
   - If you reference something that doesn't exist yet, add it to your plan

5. **Specificity check**
   - Search for vague phrases: "as needed", "appropriately", "handle", "process"
   - Replace each with a concrete action or decision tree

Record what you changed and why. This self-editing habit is as important as the initial writing.

---

## Key Takeaways

1. **The description is your skill's elevator pitch.** If it doesn't include trigger phrases, the skill never fires. Structure it as: what it does + when to use it + key capabilities.

2. **Frontmatter has hard constraints.** No angle brackets, no reserved words in the name, description under 1024 characters. Validate before you move on.

3. **Instructions are runbooks, not documentation.** Every step should tell Claude exactly what command to run, what output to expect, and what to do if something goes wrong.

4. **Progressive disclosure keeps skills focused.** The SKILL.md handles the primary workflow. Reference files handle the long tail of details, edge cases, and specifications.

5. **Style affects execution quality.** Imperative form, concrete actions, and explanations (not just rules) produce more reliable and adaptable behavior from Claude.

---

**Next module:** [Module 3 -- Building Supporting Resources](../module-03-supporting-resources/) -- write the scripts, references, and asset templates your SKILL.md references.
