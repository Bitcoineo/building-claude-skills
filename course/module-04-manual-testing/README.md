# Module 4: Manual Testing

**Time estimate:** 45-60 minutes
**Prerequisites:** Completed Modules 2 and 3 (a working SKILL.md with supporting scripts, references, and assets)
**Outcome:** A tested git-changelog skill with at least one iteration of improvements, documented in a structured testing log

---

## Learning Objectives

By the end of this module, you will be able to:

- Distinguish the three types of skill problems: undertriggering, overtriggering, and execution issues
- Run systematic trigger tests using should-fire and should-not-fire prompts
- Evaluate execution quality by reading transcripts, not just outputs
- Perform one full iteration cycle: test, identify, fix, retest
- Use the debugging question technique to see what Claude "sees"

---

## Theory

### 1. Three Types of Skill Problems

Every skill bug falls into one of three categories. Knowing which category you're dealing with determines where to look and what to fix.

#### Undertriggering

The skill doesn't load when it should.

**Signals you have this problem:**
- You have to manually tell Claude to use the skill
- Users ask "how do I get it to generate a changelog?" even though the skill is installed
- The skill works great when it fires, but it rarely fires

**Root cause:** The `description` field doesn't contain the phrases users actually say. Claude scans the description to decide whether to load the skill. If the user says "what changed since the last release?" but your description only mentions "generate changelog," Claude may not make the connection.

**Fixes:**
- Add more trigger phrases to the description, drawn from real user prompts
- Include synonyms and variations: "changelog," "release notes," "what changed," "summarize commits"
- Add contextual triggers: "since [version]," "between [dates]," "this sprint"
- Test with the exact prompts that failed, not paraphrases of them

#### Overtriggering

The skill loads for unrelated queries.

**Signals you have this problem:**
- Users see the skill activate on prompts that have nothing to do with changelogs
- Claude starts generating a changelog when the user asked for something else entirely
- Users disable the skill because it keeps interfering

**Root cause:** The description is too broad. If your description says "helps with git operations," Claude will load it for rebasing, cherry-picking, blame -- anything git-related.

**Fixes:**
- Add negative triggers to the description: "Do NOT use this skill for writing commit messages, viewing raw git log output, or configuring git workflows"
- Be more specific about the output: "generates formatted changelogs" instead of "helps with git"
- Narrow the scope: mention the specific artifacts the skill produces (changelogs, release notes, commit summaries)

#### Execution Issues

The skill loads correctly but doesn't follow its own instructions.

**Signals you have this problem:**
- The output is missing sections (no "Breaking Changes" heading, no commit hashes)
- Claude skips steps in the workflow (doesn't run `parse_commits.py`, doesn't categorize)
- The output format doesn't match your template
- Claude invents its own approach instead of following the steps

**Common causes and fixes:**

| Cause | Symptom | Fix |
|---|---|---|
| Instructions too verbose | Claude skips or summarizes steps | Bullet points, numbered lists, move details to references |
| Critical instructions buried | Important steps ignored, minor ones followed | Put critical instructions at the top, use `## Important` headings |
| Ambiguous language | Inconsistent behavior across runs | Replace "handle appropriately" with explicit checklists |
| No validation steps | Claude skips quality checks | Add verification gates: "Before proceeding, confirm that..." |
| Model "laziness" | Claude takes shortcuts on long workflows | Add quality encouragement: "Take care to include every commit" |

The key insight: undertriggering and overtriggering are description problems. Execution issues are body problems. This tells you exactly which part of your SKILL.md to edit.

---

### 2. The Testing Loop

Manual testing follows a tight cycle. Do not try to fix everything at once -- fix the single most impactful issue, verify the fix, then move to the next one.

```
    ┌─────────────┐
    │  Test        │  Run prompts that should and shouldn't trigger
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  Identify   │  Document each problem with its category
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  Fix        │  Change SKILL.md, scripts, or references
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  Retest     │  Run the SAME prompts again
    └──────┬──────┘
           │
           └──────► Did the fix work? If yes, next issue. If no, revise.
```

**Step 1: Test triggering.** Run prompts that should activate the skill and prompts that should not. Record whether each one triggered correctly.

**Step 2: Test execution.** For every prompt that triggered correctly, review the output. Did Claude follow the workflow? Did it use the bundled scripts? Did the output match the template?

**Step 3: Identify issues.** For every failure, classify it: undertrigger, overtrigger, or execution. Write it down with specifics.

**Step 4: Fix the most impactful issue first.** If the skill doesn't trigger on half your test prompts, fix the description before worrying about output formatting. Priority order is almost always: undertrigger > overtrigger > execution.

**Step 5: Retest.** Run the same prompts that originally failed. Confirm the fix works. Check that the fix didn't introduce new failures (e.g., broadening the description to fix undertriggering might cause overtriggering).

---

### 3. Reading Transcripts, Not Just Outputs

This is the skill that separates effective testers from everyone else.

When you test a skill, it's tempting to look only at the final output. "Does the changelog look right? Yes? Ship it." But the output can look correct while the execution was wrong. Consider these scenarios:

- Claude produced a correct changelog but **never ran `parse_commits.py`** -- it parsed commits manually, which means the script is dead weight and will confuse future debugging.
- Claude used the right template but **skipped the categorization step** -- it happened to work because all commits were features, but it will fail on a mixed history.
- Claude generated release notes but **didn't consult `conventional-commits.md`** -- it relied on its training data instead, which may use outdated or incorrect type definitions.

**How to read transcripts in Claude Code:**

After Claude finishes responding, review the full conversation. Look for:

1. **Tool calls:** Did Claude run the commands your SKILL.md specifies? In what order?
2. **File reads:** Did Claude read the reference files you told it to consult?
3. **Decision points:** When the skill says "if X, do Y," did Claude actually check X?
4. **Skipped steps:** Count the steps in your workflow and count the steps Claude actually performed. Any gap is a bug.

This is tedious. Do it anyway. Transcript review reveals execution issues that output review misses entirely.

---

### 4. The Debugging Question

The official guide offers a simple but powerful debugging technique: ask Claude directly what it thinks about your skill.

**The prompt:**

> When would you use the git-changelog skill?

**What happens:** Claude reads the skill's description (and body, if loaded) and tells you when it would activate the skill. This is like asking a colleague "hey, when do you think this tool is useful?" -- the answer reveals misunderstandings.

**What to look for:**

- **Missing use cases:** If Claude doesn't mention "summarize recent commits," your description may not include that trigger.
- **Over-broad scope:** If Claude says "I'd use it whenever someone asks about git," your description is too vague.
- **Misunderstood purpose:** If Claude says "I'd use it to help write commit messages," your description is actively misleading.

**How to act on it:**

Compare Claude's answer to your use cases from Module 1. Every use case Claude misses is a trigger phrase gap. Every extra use case Claude invents is an overtrigger risk. Update the description to close the gaps.

---

### 5. Common Execution Fixes

These patterns come up repeatedly when debugging execution issues. Bookmark them.

#### Problem: Instructions too verbose

The SKILL.md is a wall of text. Claude summarizes or skips sections.

**Fix:** Convert prose to bullet points and numbered lists. Move background explanations to `references/`. Keep the body under 500 lines -- if you're over, you're almost certainly including detail that belongs elsewhere.

#### Problem: Critical instructions buried

Step 4 of a 7-step workflow contains a critical validation, but Claude skips it because it's buried in the middle.

**Fix:** Pull critical instructions to the top. Use a dedicated section:

```markdown
## Important

Before generating any output:
- Verify the repository has commits in the specified range
- Confirm the output format with the user if ambiguous
- Run parse_commits.py rather than parsing commits manually
```

#### Problem: Ambiguous language

The SKILL.md says "categorize commits appropriately." Claude does something different every time.

**Fix:** Replace ambiguous language with explicit checklists:

```markdown
Categorize each commit into exactly one of these groups:
1. **Features** — commits starting with `feat:` or `feature:`
2. **Bug Fixes** — commits starting with `fix:` or `bugfix:`
3. **Breaking Changes** — commits containing `BREAKING CHANGE` in the body or footer
4. **Other** — everything else
```

#### Problem: Scripts not being used

The SKILL.md mentions `scripts/parse_commits.py` but Claude parses commits manually.

**Fix:** Make the instruction unambiguous and explain why:

```markdown
Run `scripts/parse_commits.py` to parse commit data. Do not parse commits
manually — the script handles edge cases (multi-line bodies, special
characters, co-authored commits) that manual parsing misses.
```

For truly critical validations where language instructions aren't enough, bundle the validation into a script. A script that exits non-zero on failure is harder to skip than a sentence that says "make sure to check."

---

## Exercises

### Exercise 4.1: Trigger Testing

**Goal:** Systematically test whether your skill activates on the right prompts and stays silent on the wrong ones.

**Step 1: Install the skill locally.**

Copy your git-changelog skill to the user skills directory:

```bash
cp -r student-workspace/git-changelog ~/.claude/skills/git-changelog
```

**Step 2: Run the should-trigger prompts.**

Open a Claude Code session in a git repository with some commit history. Run each of these prompts one at a time. After each prompt, record whether the git-changelog skill activated.

```
Generate a changelog for this project
```

```
What changed since v1.0?
```

```
Summarize the commits from the last two weeks
```

```
Draft release notes for version 2.0
```

```
Can you create a changelog between these two commits?
```

**Step 3: Run the should-NOT-trigger prompts.**

In the same session (or a fresh one), run each of these. The skill should NOT activate.

```
Show me the git log
```

```
Help me write a good commit message
```

```
Set up conventional commits for this project
```

```
What's the best git branching strategy?
```

```
Create a README for this project
```

**Step 4: Record your results.**

Use this testing log format for every prompt:

```
## Trigger Test Log

### Test T-01
- Prompt: "Generate a changelog for this project"
- Expected: TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes: [any observations]

### Test T-02
- Prompt: "What changed since v1.0?"
- Expected: TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-03
- Prompt: "Summarize the commits from the last two weeks"
- Expected: TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-04
- Prompt: "Draft release notes for version 2.0"
- Expected: TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-05
- Prompt: "Can you create a changelog between these two commits?"
- Expected: TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-06
- Prompt: "Show me the git log"
- Expected: NO TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-07
- Prompt: "Help me write a good commit message"
- Expected: NO TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-08
- Prompt: "Set up conventional commits for this project"
- Expected: NO TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-09
- Prompt: "What's the best git branching strategy?"
- Expected: NO TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:

### Test T-10
- Prompt: "Create a README for this project"
- Expected: NO TRIGGER
- Actual: [TRIGGERED | DID NOT TRIGGER]
- Notes:
```

**Step 5: Analyze the results.**

Count your results:

| Category | Count |
|---|---|
| Correct triggers (should fire, did fire) | /5 |
| Correct non-triggers (should not fire, did not fire) | /5 |
| Undertriggers (should fire, did not fire) | /5 |
| Overtriggers (should not fire, did fire) | /5 |

If you have any undertriggers or overtriggers, note the specific prompts -- you'll fix these in Exercise 4.3.

---

### Exercise 4.2: Execution Testing

**Goal:** For each prompt that correctly triggered the skill, evaluate whether Claude followed the instructions properly.

**Step 1: Review each triggered test.**

Go back to each test from Exercise 4.1 where the skill correctly triggered. For each one, answer these five questions:

```
## Execution Test Log

### Test E-01 (from T-01: "Generate a changelog for this project")

1. Did Claude follow the workflow steps in order?
   [ ] Yes  [ ] No — skipped steps: ___

2. Did Claude use scripts/parse_commits.py?
   [ ] Yes  [ ] No — parsed commits manually

3. Did Claude reference conventional-commits.md?
   [ ] Yes  [ ] No — used its own categorization

4. Did Claude use the changelog template from assets/?
   [ ] Yes  [ ] No — used its own format

5. Output quality (1-5):
   [ ] 1 — Unusable
   [ ] 2 — Major issues (missing sections, wrong format)
   [ ] 3 — Acceptable (right structure, some gaps)
   [ ] 4 — Good (complete, well-formatted, minor nits)
   [ ] 5 — Excellent (matches or exceeds template quality)

Specific issues noted:
-
-
```

**Step 2: Read the transcript.**

This is the critical step most people skip. For at least two of your triggered tests, go back through the full transcript and check:

- **Tool call sequence:** List every tool call Claude made, in order. Compare this to the step sequence in your SKILL.md. Note any missing steps, reordered steps, or extra steps.
- **File reads:** Did Claude read the files your SKILL.md told it to? (references/conventional-commits.md, assets/changelog-template.md, etc.)
- **Decision points:** If your workflow has conditionals ("if no tags exist, fall back to date range"), did Claude actually evaluate the condition?

Record your transcript review findings in the execution test log.

**Step 3: Summarize patterns.**

After reviewing all execution tests, look for patterns:

- Is the same step consistently skipped?
- Is Claude consistently ignoring a specific resource file?
- Is the output quality consistent or does it vary by prompt type?

Write a 2-3 sentence summary of execution quality. Example: "Claude follows the main workflow but skips the parse_commits.py script in 3 of 4 tests, parsing commits manually instead. Output quality averages 3.5/5 — correct structure but missing the Breaking Changes section when relevant."

---

### Exercise 4.3: First Iteration

**Goal:** Fix the single most impactful issue from your testing and verify the fix.

**Step 1: Identify the most impactful issue.**

Rank the issues you found by impact:

1. **Undertriggering** on common prompts — highest impact, because the skill is invisible
2. **Overtriggering** on unrelated prompts — high impact, because it erodes trust
3. **Skipped workflow steps** — medium-high, because it undermines consistency
4. **Ignored resource files** — medium, because it reduces output quality
5. **Minor output formatting** — lower, but still worth tracking

Pick the single most impactful issue.

**Step 2: Document the bug.**

Use the bug log template from `course-log.md`:

```
## BUG-001: [Title]
**Module:** 4
**Symptom:** [What went wrong — be specific]
**Root Cause (First Principles):** [WHY did this happen? Trace it to a specific
line or section in SKILL.md, a missing trigger phrase, a vague instruction, etc.]
**Fix:** [What you will change — specific file, specific section, specific edit]
**Prevention:** [How to avoid this class of bug in future skills]
**Category:** undertrigger | overtrigger | execution
```

**Step 3: Apply the fix.**

Edit your SKILL.md (or scripts, references, or description) to address the root cause. Make one targeted change -- resist the urge to rewrite everything.

**Step 4: Retest.**

Run the same prompts that originally exposed the issue. Record the before/after:

```
## Iteration 1: Before/After

**Issue:** [one-line summary]
**Fix applied:** [what you changed]

| Prompt | Before | After |
|--------|--------|-------|
| [prompt 1] | [old result] | [new result] |
| [prompt 2] | [old result] | [new result] |

**Fix successful?** [ ] Yes  [ ] No — still failing because: ___
**Regression check:** Did the fix break anything that was working before?
[ ] No regressions  [ ] Regression found: ___
```

**Step 5: Update your course log.**

Add the bug entry to `course-log.md`. This is not busywork -- the course log is the raw material for Module 9's capstone project.

---

### Exercise 4.4: The Debugging Question

**Goal:** See what Claude "sees" when it looks at your skill, and use that to improve the description.

**Step 1: Ask the question.**

In a Claude Code session with your skill installed, type:

```
When would you use the git-changelog skill?
```

**Step 2: Analyze Claude's answer.**

Compare Claude's response to your three use cases from Module 1:

| Use Case | In Claude's Answer? | Notes |
|---|---|---|
| Generate a changelog for a release | [ ] Yes  [ ] No | |
| Summarize recent work | [ ] Yes  [ ] No | |
| Prepare release notes | [ ] Yes  [ ] No | |

Also check for false positives -- use cases Claude mentions that you did NOT intend:

```
Extra use cases Claude mentioned:
-
-
```

**Step 3: Update the description if needed.**

For every use case Claude missed, add a trigger phrase to the description. For every false positive, add a negative trigger or tighten the language.

Before:
```yaml
description: >-
  [your current description]
```

After:
```yaml
description: >-
  [your updated description]
```

**Step 4: Re-ask the question.**

After updating the description, ask the same question again:

```
When would you use the git-changelog skill?
```

Does Claude's answer now match your intended use cases? If not, iterate.

---

## Sample Testing Log

Here is a complete testing log template you can copy into your working notes. Having a consistent format makes it easier to spot patterns across tests and across iterations.

```markdown
# git-changelog Skill — Manual Testing Log

## Test Date: [YYYY-MM-DD]
## Skill Version: [e.g., "initial draft" or "post-iteration-1"]

---

## Trigger Tests

| ID | Prompt | Expected | Actual | Match? |
|----|--------|----------|--------|--------|
| T-01 | Generate a changelog for this project | TRIGGER | | |
| T-02 | What changed since v1.0? | TRIGGER | | |
| T-03 | Summarize the commits from the last two weeks | TRIGGER | | |
| T-04 | Draft release notes for version 2.0 | TRIGGER | | |
| T-05 | Can you create a changelog between these two commits? | TRIGGER | | |
| T-06 | Show me the git log | NO TRIGGER | | |
| T-07 | Help me write a good commit message | NO TRIGGER | | |
| T-08 | Set up conventional commits for this project | NO TRIGGER | | |
| T-09 | What's the best git branching strategy? | NO TRIGGER | | |
| T-10 | Create a README for this project | NO TRIGGER | | |

**Summary:** _/5 correct triggers, _/5 correct non-triggers

---

## Execution Tests

| ID | Prompt | Workflow Followed? | Script Used? | Refs Consulted? | Template Used? | Quality (1-5) |
|----|--------|--------------------|--------------|-----------------|----------------|---------------|
| E-01 | [from T-01] | | | | | |
| E-02 | [from T-02] | | | | | |
| E-03 | [from T-03] | | | | | |
| E-04 | [from T-04] | | | | | |
| E-05 | [from T-05] | | | | | |

**Execution summary:** [2-3 sentences on patterns observed]

---

## Debugging Question

**Prompt:** "When would you use the git-changelog skill?"

**Claude's answer:** [paste or summarize]

**Use case coverage:**
- Generate changelog: [ ] covered [ ] missing
- Summarize recent work: [ ] covered [ ] missing
- Prepare release notes: [ ] covered [ ] missing
- False positives mentioned: [list any]

---

## Issues Found

| ID | Category | Description | Impact | Fixed? |
|----|----------|-------------|--------|--------|
| I-01 | [under/over/exec] | | [high/med/low] | |
| I-02 | | | | |
| I-03 | | | | |

---

## Iteration 1

**Most impactful issue:** I-__
**Root cause:** [one sentence]
**Fix applied:** [what changed, in which file]
**Retest result:** [pass/fail]
**Regressions:** [none / describe]
```

---

## Key Takeaways

1. **Every skill bug is one of three types.** Undertriggering, overtriggering, and execution issues each have distinct symptoms, root causes, and fixes. Classify before you debug -- it tells you whether to edit the description or the body.

2. **Fix the most impactful issue first.** A skill that doesn't trigger is worse than a skill with imperfect output. Priority order: undertriggering > overtriggering > execution issues.

3. **Read transcripts, not just outputs.** The output can look correct while the execution was wrong. Transcript review reveals skipped steps, ignored scripts, and unchecked conditions that will fail on harder inputs.

4. **The debugging question reveals mismatches.** Asking Claude "when would you use this skill?" surfaces gaps between your intent and Claude's understanding. It's the fastest way to diagnose description problems.

5. **One fix, one retest.** Resist the urge to fix everything at once. Change one thing, test it, confirm it works, check for regressions. This is slower per iteration but faster to convergence because you know exactly what each fix did.

6. **Document everything.** The bug log entries you write now are the raw material for Module 9's capstone. They're also how you build intuition for skill debugging across future projects.

---

**Next module:** [Module 5 — Systematic Testing with Evals](../module-05-systematic-evals/) — move from manual testing to automated evaluation with evals.json, baseline comparisons, and benchmark analysis.
