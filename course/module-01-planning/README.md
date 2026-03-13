# Module 1: Planning and Designing Your Skill

**Time estimate:** 30-45 minutes

**Learning objectives:**
- Identify concrete use cases before writing any code
- Classify skills into the three categories (Document & Asset Creation, Workflow Automation, MCP Enhancement)
- Define quantitative and qualitative success criteria
- Write a technical spec with directory plan and frontmatter draft

**Prerequisites:** Module 0 completed. You understand the anatomy of a skill folder (SKILL.md + optional subdirectories) and progressive disclosure (frontmatter, body, linked files).

---

## Theory

### 1. Start with Use Cases

The single biggest mistake new skill authors make is jumping straight into writing SKILL.md. Before you write a single line of Markdown, answer this question: **what does the user want to accomplish?**

Good use case definition has three parts:

| Component | Question | Example |
|-----------|----------|---------|
| **Trigger** | What does the user say? | "Generate a changelog for v2.0" |
| **Steps** | What multi-step workflow happens? | Read git log, group by type, format as Markdown |
| **Result** | What artifact is produced? | A formatted changelog ready to paste into RELEASES.md |

For each use case, also ask:

- **What tools are needed?** Does the skill need Bash (to run `git log`), file read/write, or external MCP servers?
- **What domain knowledge should be embedded?** Conventional commit parsing, semantic versioning rules, changelog formatting conventions — this is the expertise the user shouldn't have to provide every time.
- **What multi-step workflows are involved?** A simple lookup ("what's the latest tag?") is not a skill. A workflow ("find the latest tag, gather commits since then, categorize them, format a changelog, write it to a file") is.

Aim for 2-3 concrete use cases. If you can only think of one, the skill may be too narrow. If you have more than five, consider splitting into multiple skills.

#### Running Example: git-changelog

Here are three use cases we'll design the `git-changelog` skill around:

**Use Case 1 — Generate a changelog for a release:**
The user is about to cut a release and needs a formatted summary of everything that changed.
- *Trigger:* "generate changelog", "what changed since v1.2?"
- *Steps:* Identify the comparison range (tag-to-HEAD or tag-to-tag), run `git log`, parse and categorize commits, format as grouped Markdown
- *Result:* A Markdown changelog grouped by category (features, fixes, etc.)

**Use Case 2 — Summarize recent work:**
The user wants a quick summary of recent activity — for standups, status updates, or personal review.
- *Trigger:* "summarize recent commits", "what did we ship this week?"
- *Steps:* Determine the time window, run `git log` with date filters, summarize by author or area, format concisely
- *Result:* A human-readable summary of recent work

**Use Case 3 — Prepare release notes:**
The user needs polished, audience-facing release notes (not just a raw changelog).
- *Trigger:* "prepare release notes", "draft the release notes for v2.0"
- *Steps:* Gather commits, identify highlights and breaking changes, write user-facing descriptions, organize by impact
- *Result:* Release notes suitable for a GitHub Release or announcement

Notice how all three use cases share a core workflow (read git history, categorize, format) but differ in scope, audience, and output style. That's a sign the skill boundary is right.

### 2. Three Skill Categories

Every skill falls into one of three categories. Knowing which category yours belongs to determines what techniques you'll rely on.

#### Category 1: Document & Asset Creation

**Purpose:** Produce consistent, high-quality output — docs, designs, code, templates.

**Key techniques:**
- Embedded style guides ("always use sentence case for headings")
- Template structures the skill fills in every time
- Quality checklists to self-verify before delivering

**External tools required:** None. These skills work purely with Claude's generation capabilities.

**Examples:** API documentation generator, design system component scaffolder, meeting notes formatter.

#### Category 2: Workflow Automation

**Purpose:** Execute multi-step processes with a consistent methodology every time.

**Key techniques:**
- Step-by-step workflows with explicit ordering
- Validation gates between steps ("verify the tag exists before proceeding")
- Templates for intermediate and final output
- Review suggestions ("check that no commits were missed")
- Iterative refinement loops ("if the user asks to regenerate, re-run from step 3")

**External tools required:** Usually Bash for running commands, sometimes file read/write.

**Examples:** Git changelog generator, code review workflow, database migration planner.

#### Category 3: MCP Enhancement

**Purpose:** Provide workflow guidance on top of MCP tool access. The MCP server gives you raw capabilities; the skill tells Claude *how* and *when* to use them.

**Key techniques:**
- Coordinate multiple MCP calls in sequence
- Embed domain expertise ("when creating a GitHub release, always include migration notes for breaking changes")
- Provide context that the MCP tools don't have
- Error handling and fallback strategies

**External tools required:** One or more MCP servers.

**Examples:** GitHub release manager (GitHub MCP), Slack standup poster (Slack MCP), multi-service deployment coordinator.

#### Where does git-changelog fit?

`git-changelog` is primarily a **Category 2 (Workflow Automation)** skill. It runs a multi-step process (identify range, gather commits, categorize, format) and produces a consistent artifact. It uses Bash to run git commands but doesn't need any MCP servers.

It also has elements of Category 1 (the output follows a consistent template). Many real skills blend categories — that's normal. Pick the primary category to guide your design decisions.

### 3. Success Criteria

Define how you'll know the skill is working well. There are two types of criteria.

#### Quantitative Criteria

These are measurable targets:

- **Trigger accuracy:** The skill activates on 90%+ of relevant user prompts (and does *not* activate on unrelated prompts)
- **Execution efficiency:** The skill completes in a reasonable number of tool calls (e.g., under 10 for a simple changelog)
- **Error rate:** 0 failed API/tool calls during normal operation
- **Output completeness:** The generated changelog includes all commits in the specified range

#### Qualitative Criteria

These are judgment calls, assessed through vibes:

- **No redirection needed:** The user doesn't have to say "no, I meant..." or "you forgot to..."
- **Consistent across sessions:** Running the same prompt twice produces structurally identical output (content varies with git history, but format and organization stay the same)
- **Appropriate scope:** The skill doesn't try to do too much (e.g., automatically pushing a release) or too little (e.g., just dumping raw `git log` output)

These are aspirational targets, not pass/fail gates. In Module 5 you'll write formal evals that test some of these. For now, write them down so you have a north star.

### 4. Technical Requirements

Before you start writing your SKILL.md (that's Module 2), you need to know the rules of the format.

#### File Structure

A skill lives in a folder with this layout:

```
skill-name/
  SKILL.md          # Required. The main instruction file.
  scripts/          # Optional. Helper scripts Claude can run.
  references/       # Optional. Reference docs loaded on demand.
  assets/           # Optional. Templates, examples, static files.
```

#### Naming Rules

- Folder name: **kebab-case**. No spaces, no underscores, no capital letters.
  - Good: `git-changelog`, `api-doc-generator`
  - Bad: `gitChangelog`, `Git_Changelog`, `git changelog`
- The main file must be named exactly `SKILL.md` (all caps, case-sensitive).
- Do **not** put a README.md inside the skill folder. `SKILL.md` is the only Markdown file Claude reads.

#### YAML Frontmatter

Every SKILL.md starts with YAML frontmatter between `---` fences. Two fields are required:

```yaml
---
name: git-changelog
description: "Generate formatted changelogs from git history. Use when the user asks to generate a changelog, summarize recent commits, prepare release notes, or review what changed between versions or over a time period."
---
```

**Rules for `name`:**
- Must be kebab-case
- Must match the folder name

**Rules for `description`:**
- Under 1024 characters
- No XML tags
- Must answer two questions: **WHAT** does this skill do, and **WHEN** should it activate?
- Pack in trigger phrases — this is how Claude decides whether to load the skill

The description is the most important line in your entire skill. It's the only thing Claude sees when deciding whether to load your skill from the available list. If your description doesn't match the user's intent, the skill never activates. You'll optimize this heavily in Module 6.

---

## Exercises

### Exercise 1.1: Use Case Brainstorming

**Goal:** Define the full trigger surface for `git-changelog` — both what *should* activate it and what *should not*.

#### Part A: Define 3 Use Cases

For each use case, fill out this template:

```
**Use Case [N]: [Title]**
- Trigger phrases: [3-5 things a user might say]
- Steps: [numbered list of what the skill does]
- Result: [what artifact is produced]
- Tools needed: [Bash, file write, etc.]
```

The three use cases to define:

1. **Generate a changelog for a release** — The user is cutting a release and needs a formatted diff of what changed. Trigger phrases include "generate changelog", "what changed since v1.2?", "changelog for the next release", "list changes since last tag".

2. **Summarize recent work** — The user wants a quick summary for standups or personal review. Trigger phrases include "summarize recent commits", "what did we ship this week?", "show me what changed this sprint", "recap of recent changes".

3. **Prepare release notes** — The user needs polished, external-facing release notes. Trigger phrases include "prepare release notes", "draft the release notes for v2.0", "write up release notes for this version", "create release announcement".

#### Part B: Define Near-Misses (Should NOT Trigger)

Write at least 5 prompts that are *close* to the skill's domain but should **not** activate it. These are critical for avoiding overtriggering.

Examples to get you started:

1. "show me the git log" — This is asking for raw git output, not a formatted changelog.
2. "write a commit message" — This is about *creating* commits, not summarizing existing ones.
3. "set up conventional commits" — This is tooling configuration, not changelog generation.
4. "rebase my branch onto main" — Git operation, not changelog.
5. "who authored this file?" — Git blame, different intent entirely.

Think of at least 2-3 more. The more near-misses you identify now, the better your description will be, and the fewer overtrigger bugs you'll hit in Module 4.

#### Deliverable

A document (or section of notes) listing:
- 3 use cases with full trigger/steps/result definitions
- 10+ total trigger phrases across the use cases
- 5+ near-miss prompts that should NOT trigger the skill

---

### Exercise 1.2: Technical Spec

**Goal:** Write the technical blueprint for `git-changelog` before touching SKILL.md.

#### Part A: YAML Frontmatter Draft

Write the frontmatter block for your skill. Remember:

- `name` must be kebab-case and match the folder name
- `description` must be under 1024 characters, include WHAT + WHEN, and pack in trigger phrases from Exercise 1.1

Here's a starting point to iterate on:

```yaml
---
name: git-changelog
description: "Generate formatted changelogs from git history. Use when the user asks to generate a changelog, summarize recent commits, prepare release notes, or review what changed between versions or over a time period."
---
```

Ask yourself: does this description contain enough trigger phrases? If a user says "what did we ship this week?", would Claude match it to this description? If not, add more context.

#### Part B: Directory Structure Plan

Decide which subdirectories you'll need and why:

```
git-changelog/
  SKILL.md              # Core instructions (always loaded)
  scripts/              # Do you need helper scripts? What would they do?
  references/           # What reference material should be available on demand?
  assets/               # Any templates for the output format?
```

For each subdirectory you include, write one sentence justifying it. For each you omit, explain why it's not needed (yet).

Think about progressive disclosure:
- **Frontmatter** (always visible): name and description — must trigger correctly
- **Body** (loaded when skill activates): step-by-step instructions, formatting rules, examples
- **Linked files** (loaded on demand): detailed reference material, large templates, edge case documentation

What goes where? If instructions are critical to every run, they belong in the body. If they're only relevant sometimes (e.g., handling monorepo changelogs), they belong in a reference file.

#### Part C: Success Criteria

Write specific success criteria for `git-changelog`:

**Quantitative (write 3):**
1. Example: "Triggers on 9 out of 10 changelog-related prompts from the test set"
2. Example: "Completes a basic changelog in under 8 tool calls"
3. (Write your own)

**Qualitative (write 2):**
1. Example: "User never needs to say 'you forgot the breaking changes section'"
2. (Write your own)

#### Deliverable

A technical spec document containing your frontmatter draft, directory plan with justifications, and 5 success criteria.

---

### Exercise 1.3: Spec Validation

**Goal:** Stress-test your spec against real prompts before you start building.

#### The Walkthrough

Take every prompt from Exercise 1.1 — both the trigger phrases and the near-misses — and run this mental test:

> Given my `description` field, would Claude select this skill from a list of available skills?

For each prompt, mark it:
- **HIT** — Claude would (correctly) load the skill
- **MISS** — Claude would (incorrectly) skip the skill
- **FALSE POSITIVE** — Claude would (incorrectly) load the skill

Go through your full list:

| Prompt | Expected | Predicted | Match? |
|--------|----------|-----------|--------|
| "generate changelog" | HIT | ? | |
| "what changed since v1.2?" | HIT | ? | |
| "summarize recent commits" | HIT | ? | |
| "what did we ship this week?" | HIT | ? | |
| "prepare release notes for v2.0" | HIT | ? | |
| "show me the git log" | NO HIT | ? | |
| "write a commit message" | NO HIT | ? | |
| "set up conventional commits" | NO HIT | ? | |
| "rebase my branch onto main" | NO HIT | ? | |
| "who authored this file?" | NO HIT | ? | |
| *(add your additional prompts)* | | | |

#### Frontmatter Rule Check

Verify your frontmatter against every rule:

- [ ] `name` is kebab-case
- [ ] `name` matches the folder name
- [ ] `description` is under 1024 characters
- [ ] `description` contains no XML tags
- [ ] `description` explains WHAT the skill does
- [ ] `description` explains WHEN to use it
- [ ] File is named exactly `SKILL.md`

If any prompt produces a MISS or FALSE POSITIVE, revise your description and re-run the walkthrough. Iterate until you're satisfied.

#### Deliverable

A completed validation table and a final revised version of your frontmatter (if changes were needed).

---

## Key Takeaways

1. **Plan before you build.** The 20 minutes you spend on use cases and success criteria will save you hours of rework. Every skill that undertriggers or overtriggers can be traced back to skipping this step.

2. **Use cases define the skill boundary.** Three well-defined use cases tell you what to include *and* what to leave out. If "write a commit message" isn't in your use cases, don't build support for it.

3. **Near-misses are as important as triggers.** Defining what should NOT activate your skill is how you avoid overtriggering, which is harder to debug than undertriggering.

4. **The description is your most important line.** Claude uses it to decide whether to load your skill. If the description doesn't match, nothing else matters — the body and scripts never get read.

5. **Know your category.** Whether your skill is Document Creation, Workflow Automation, or MCP Enhancement determines which techniques to prioritize. `git-changelog` is a Workflow Automation skill — so in Module 2, we'll focus on step-by-step instructions with validation gates.

6. **Success criteria are your north star.** Without them, you can't evaluate whether the skill is working. Write them now, even if they're rough. You'll formalize them as evals in Module 5.

---

**Next up:** [Module 2 — Writing the SKILL.md](../module-02-writing-skill-md/) where you'll turn this spec into a working skill file.
