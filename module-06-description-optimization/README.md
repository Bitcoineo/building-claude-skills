# Module 6: Description Optimization

**Time estimate:** 60-90 minutes
**Prerequisites:** Completed Modules 4 and 5 (a tested skill with manual testing results and familiarity with evals)
**Outcome:** An optimized description field for your git-changelog skill, validated against a 20-query eval set with a train/test split

---

## Learning Objectives

By the end of this module, you will be able to:

- Explain how Claude decides whether to load a skill (the description-matching process)
- Write trigger eval queries that distinguish genuine skill use cases from near-miss negatives
- Apply a train/test split to avoid overfitting the description to a narrow set of test cases
- Run the iterative optimization loop: evaluate, propose, re-evaluate, keep-or-revert
- Interpret optimization results and know when to stop iterating

---

## Theory

### 1. How Claude Decides to Load Skills

When a user message arrives, Claude does not see the full contents of every installed skill. It sees a list of available skills, each represented by just two fields: **name** and **description**. Claude reads this list, compares it against the user's message, and decides which skills (if any) to "consult" -- that is, to load the full SKILL.md for execution.

This means the description is the gatekeeper. If the description does not match the user's intent, the skill never loads. The most carefully crafted SKILL.md in the world is invisible if the description fails to trigger.

Think of it as a two-stage funnel:

```
User message
     │
     ▼
┌─────────────────────────────┐
│  Stage 1: Description scan  │  Claude reads name + description
│  Decision: load or skip?    │  for every enabled skill
└──────────┬──────────────────┘
           │ (only if loaded)
           ▼
┌─────────────────────────────┐
│  Stage 2: Execution         │  Claude reads the full SKILL.md
│  Follow the instructions    │  and executes the workflow
└─────────────────────────────┘
```

If Stage 1 fails, Stage 2 never happens. This is why the description is the most important part of the frontmatter -- and why it deserves its own optimization process.

---

### 2. Undertriggering vs. Overtriggering

Every description sits on a spectrum between too narrow and too broad. The goal is to find the sweet spot.

#### Undertriggering

The skill does not load when it should.

**Common causes:**
- The description uses only one phrase for the skill's purpose ("generate changelogs") and misses synonyms ("release notes", "what changed", "summarize commits")
- The description is technically accurate but uses jargon users don't say ("commit history aggregation" instead of "what changed since v1.0")
- The description omits contextual triggers like date ranges, version numbers, or sprint boundaries

**The cost:** Users have to manually invoke the skill or don't know it exists. The skill delivers value only when explicitly requested, which defeats the purpose of having a smart trigger.

#### Overtriggering

The skill loads for unrelated queries.

**Common causes:**
- The description is too broad: "helps with git operations" matches rebasing, cherry-picking, blame -- everything git-related
- The description includes generic terms without scoping them: "summarize" without specifying "summarize commits"
- No negative triggers to exclude adjacent use cases

**The cost:** Users see the skill activate on unrelated prompts. This erodes trust and may cause them to disable the skill entirely.

#### The Sweet Spot

The ideal description triggers on **all relevant queries** and **none of the irrelevant ones**. In practice, you optimize for this by:

1. Adding trigger phrases drawn from real user prompts (reduces undertriggering)
2. Scoping those phrases to the specific domain (reduces overtriggering)
3. Adding negative triggers for adjacent use cases (further reduces overtriggering)

**Negative triggers** are explicit exclusions in the description. From the official guide: you can write things like "Do NOT use for simple data exploration (use data-viz skill instead)." This gives Claude a clear boundary.

Example for git-changelog:

```
Do NOT use this skill for viewing raw git log output, writing commit
messages, or general git workflow questions.
```

This single line eliminates a whole class of overtrigger candidates.

---

### 3. The Train/Test Split

When you optimize a description, there is a real risk of **overfitting** -- tuning the description to match a specific set of test queries so precisely that it fails on queries you did not test.

The solution is the same one used in machine learning: split your evaluation queries into a **train set** (used during optimization) and a **test set** (held out for validation).

#### The Process

1. Write 20+ eval queries: 10 that should trigger the skill, 10 that should not
2. Split them 60/40: 12 for training, 8 for testing
3. Optimize the description using only the train set
4. After optimization, validate on the test set
5. Compare train performance vs. test performance

#### Interpreting Results

| Train Accuracy | Test Accuracy | Diagnosis |
|---|---|---|
| High | High | Good generalization. Ship it. |
| High | Low | Overfitting. The description is tuned to specific phrases rather than capturing intent. Broaden the language. |
| Low | Low | Underfitting. The description is too vague or missing key concepts. Add more trigger phrases and scope clarifiers. |
| Low | High | Unlikely but possible with small sets. Probably noise. Get more eval queries. |

If the test accuracy is more than 15-20% worse than train accuracy, you have overfit. Go back and make the description more general -- replace specific phrases with broader intent patterns.

---

### 4. The Optimization Loop

Description optimization follows an iterative loop. Each iteration proposes a change, evaluates it, and keeps or reverts it.

```
┌──────────────────────┐
│  Step 1: Evaluate     │  Score current description against train set
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  Step 2: Propose      │  Use Claude (extended thinking) to draft
│                       │  an improved description
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  Step 3: Re-evaluate  │  Score the proposed description
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  Step 4: Decide       │  If better, keep. If worse, revert.
└──────────┬───────────┘
           │
           └──────► Repeat (max 5 iterations)
```

**Step 1: Evaluate.** Run each train query against the current description. For each query, record whether Claude would trigger the skill (match) or not (no match). Calculate the percentage of correct decisions.

**Step 2: Propose.** Feed the current description, the train queries, and the error cases to Claude with extended thinking. Ask it to propose an improved description that fixes the errors without introducing new ones. The prompt should include both the failing queries and the currently passing ones -- you want Claude to see what it needs to preserve.

**Step 3: Re-evaluate.** Score the proposed description on the same train set. Count the correct decisions.

**Step 4: Decide.** If the proposed description scores higher than the current one, keep it. If it scores the same or worse, revert to the previous version. Ties go to the shorter description (fewer tokens, less ambiguity).

**Step 5: Repeat.** Run up to 5 iterations. In practice, most gains happen in the first 2-3 iterations. After 5, you hit diminishing returns -- the remaining errors are usually edge cases that require trade-offs between triggering and not triggering on borderline queries.

The skill-creator tool automates this loop with `scripts/run_loop.py`. But understanding the manual process is important because you need to interpret the results and sometimes override the automation.

---

### 5. Writing Quality Eval Queries

The quality of your optimization depends entirely on the quality of your eval queries. Bad queries produce misleading results and waste iterations.

#### Guidelines for Should-Trigger Queries

- **Realistic:** Write prompts that actual users would type. Not "Please activate the changelog generation facility" but "what changed since last release?"
- **Varied:** Include different phrasings of the same intent. If all 10 queries say "generate a changelog," the optimization will overfit to that exact phrase.
- **Specific:** Include domain terms, version numbers, date ranges, file types. "Generate a changelog from v2.0 to v2.1" is better than "make a changelog."
- **Different specificity levels:** Include both precise ("changelog for commits between abc123 and def456") and vague ("what's new in this project?") queries.

#### Guidelines for Should-NOT-Trigger Queries

This is where most people make mistakes. The negative set is as important as the positive set.

- **Near-miss negatives are essential.** These are queries that seem related but should not trigger the skill. They test whether the description is precise enough to discriminate.
  - Good negative: "Show me the git log for the last week" (git-related, time-scoped, but asking for raw log, not a formatted changelog)
  - Good negative: "Help me write a commit message for this change" (git-related, involves commit text, but a completely different task)
  - Good negative: "Set up conventional commits in this repo" (uses the same terminology but is a configuration task, not a generation task)

- **Avoid trivially different negatives.** If your negative queries are all obviously unrelated, they don't test anything useful.
  - Bad negative: "What's the weather today?" (no one would confuse this with a changelog request)
  - Bad negative: "Write me a poem" (too obviously different -- not discriminating)

- **Include adjacent tool requests.** If users might confuse your skill with another tool, include those requests as negatives.
  - "Create a README for this project" (document generation, but not a changelog)
  - "Summarize this file" (summarization, but of a file, not of commits)

#### The Quality Test

For each eval query, ask yourself: "Would a reasonable description get this wrong?" If the answer is "no, obviously not," the query is too easy and doesn't help optimization. The best queries are the ones that sit right on the decision boundary.

---

### 6. Description Optimization Tips

These practical tips come from the official guide and from common optimization patterns.

**Include specific trigger phrases users would actually say.** Don't guess -- look at how people phrase requests in chat. "What changed since the last release" is a real trigger phrase. "Aggregate commit metadata" is not.

**Mention file types if relevant.** If your skill works with specific formats, say so: "Outputs markdown changelogs" or "Parses conventional commit messages." This helps Claude match queries that mention those formats.

**Add negative triggers to reduce overtriggering.** Explicitly state what the skill is NOT for:

```
Do NOT use this skill for viewing raw git log output, writing commit
messages, configuring git hooks, or general git workflow questions.
```

**Clarify scope with domain specifics.** Instead of "helps with payment processing," write "PayFlow payment processing for e-commerce transactions, not general financial analysis or accounting queries." The more specific the scope, the fewer false matches.

**Keep the description under 1024 characters.** This is a hard limit in the parser. But even without the limit, shorter descriptions tend to perform better -- less text means less room for ambiguous matching. Aim for 400-700 characters as a sweet spot.

**Structure as: [What it does] + [When to use it] + [When NOT to use it].**

```yaml
description: >-
  Generate formatted changelogs and release notes from git commit history.
  Use when the user asks to "generate a changelog", "what changed since
  [version]", "summarize recent commits", "prepare release notes", or
  "list changes between [two points]". Supports conventional commits,
  custom date/tag ranges, and markdown output. Do NOT use for raw git
  log viewing, writing commit messages, or git workflow configuration.
```

---

## Exercises

### Exercise 6.1: Create the Trigger Eval Set

**Goal:** Build a 20-query eval set for git-changelog with a train/test split.

**Step 1: Write 10 should-trigger queries.**

These queries should all be cases where the git-changelog skill SHOULD activate. Vary the phrasing, specificity, and context.

Here is a complete set to use as your starting point. You can modify these or write your own, but make sure they follow the quality guidelines from Theory section 5.

```
SHOULD-TRIGGER QUERIES:

ST-01: "Generate a changelog for this project"
ST-02: "What changed between v1.2 and v1.3?"
ST-03: "Summarize the commits from the last two weeks"
ST-04: "Draft release notes for version 3.0"
ST-05: "Can you create a changelog from the last 50 commits?"
ST-06: "I need to see what's new since the last release"
ST-07: "Write up the changes between these two tags"
ST-08: "Prepare a summary of recent changes for the team"
ST-09: "What went into this sprint? Give me a changelog"
ST-10: "List all the changes since last Monday in changelog format"
```

**Step 2: Write 10 should-NOT-trigger queries.**

These must be **near-miss negatives** -- queries that are related to git, commits, or documentation, but should NOT trigger the changelog skill.

```
SHOULD-NOT-TRIGGER QUERIES:

SN-01: "Show me the git log for the last week"
SN-02: "Help me write a good commit message for this change"
SN-03: "Set up conventional commits for this project"
SN-04: "What's the best git branching strategy?"
SN-05: "Create a README for this project"
SN-06: "Revert the last three commits"
SN-07: "Show me who wrote this line of code"
SN-08: "Squash my last 5 commits into one"
SN-09: "Summarize what this Python file does"
SN-10: "Help me resolve this merge conflict"
```

Notice the quality of the negatives:
- SN-01 is a near-miss: it asks about recent git history but wants raw log, not a formatted changelog
- SN-02 involves commit text but is a writing task, not a summarization task
- SN-03 uses the exact same terminology ("conventional commits") but is a setup task
- SN-05 is document generation but not changelog generation
- SN-09 is a summarization task but of a file, not of commits

**Step 3: Apply the 60/40 train/test split.**

Assign 12 queries to the train set and 8 to the test set. Distribute evenly: 6 should-trigger and 6 should-not-trigger in each set (approximately).

```
TRAIN SET (12 queries — used during optimization):

  Should-trigger:
    ST-01: "Generate a changelog for this project"
    ST-02: "What changed between v1.2 and v1.3?"
    ST-04: "Draft release notes for version 3.0"
    ST-06: "I need to see what's new since the last release"
    ST-08: "Prepare a summary of recent changes for the team"
    ST-09: "What went into this sprint? Give me a changelog"

  Should-NOT-trigger:
    SN-01: "Show me the git log for the last week"
    SN-02: "Help me write a good commit message for this change"
    SN-03: "Set up conventional commits for this project"
    SN-05: "Create a README for this project"
    SN-06: "Revert the last three commits"
    SN-09: "Summarize what this Python file does"

TEST SET (8 queries — held out for validation):

  Should-trigger:
    ST-03: "Summarize the commits from the last two weeks"
    ST-05: "Can you create a changelog from the last 50 commits?"
    ST-07: "Write up the changes between these two tags"
    ST-10: "List all the changes since last Monday in changelog format"

  Should-NOT-trigger:
    SN-04: "What's the best git branching strategy?"
    SN-07: "Show me who wrote this line of code"
    SN-08: "Squash my last 5 commits into one"
    SN-10: "Help me resolve this merge conflict"
```

**Step 4: Save the eval set.**

Create a file at `student-workspace/eval-queries.md` with the full eval set, train/test split labels, and expected outcomes. You will use this in Exercises 6.2 and 6.3.

---

### Exercise 6.2: Run the Optimization Loop

**Goal:** Iterate on your description using the train set, then validate on the test set.

**Option A: Using `scripts/run_loop.py` (automated)**

If the skill-creator tool is available, run the automated loop:

```bash
python scripts/run_loop.py \
  --skill-path student-workspace/git-changelog/SKILL.md \
  --eval-set student-workspace/eval-queries.md \
  --max-iterations 5 \
  --split train
```

The script will:
1. Parse the current description from your SKILL.md
2. Score it against the train set queries
3. Propose an improved description using Claude with extended thinking
4. Score the proposed description
5. Keep the better version and iterate

After it finishes, review the output:
- **Per-iteration scores:** Did accuracy improve each round?
- **Description diffs:** What changed between iterations? Look for added trigger phrases, added negatives, tightened scope.
- **Plateau detection:** At which iteration did improvements stop? This tells you the description has converged.

**Option B: Manual optimization loop**

If running the script is not possible, perform the loop manually. This is more instructive anyway.

**Iteration 1:**

1. Take your current description from SKILL.md.
2. For each train query, ask yourself: "Given this description, would Claude load this skill?" Record yes/no for each.
3. Calculate accuracy: (correct decisions) / (total train queries) * 100.
4. Identify the errors. For each wrong answer, note whether it was an undertrigger or overtrigger and what words in the description (or missing from it) caused the error.
5. Rewrite the description to fix the errors. Be careful not to break what already works.
6. Re-score the new description on the train set.
7. If the new score is higher, keep the new description. If equal or lower, revert.

Record your work:

```
## Optimization Log

### Iteration 1
- Starting description: [paste]
- Starting accuracy (train): __/12 = __%
- Errors identified:
  - [query]: expected [trigger/no-trigger], got [opposite]. Cause: [analysis]
  - [query]: expected [trigger/no-trigger], got [opposite]. Cause: [analysis]
- Proposed description: [paste]
- New accuracy (train): __/12 = __%
- Decision: [KEEP / REVERT]

### Iteration 2
...
```

**Repeat for up to 5 iterations**, or until you hit 100% on the train set, or until two consecutive iterations produce no improvement.

**Validation step (after all iterations):**

Take your final optimized description and score it against the **test set** -- the 8 queries you held out.

```
## Validation Results

- Final description: [paste]
- Train accuracy: __/12 = __%
- Test accuracy: __/8 = __%
- Delta: __% (test minus train)

If delta < -15%: likely overfit. Consider broadening the description.
If delta >= -15%: good generalization. Proceed to Exercise 6.3.
```

---

### Exercise 6.3: Apply and Verify

**Goal:** Deploy the optimized description and confirm it works in practice.

**Step 1: Update your SKILL.md.**

Replace the old description in your SKILL.md frontmatter with the optimized version from Exercise 6.2.

Before:
```yaml
description: >-
  [your original description]
```

After:
```yaml
description: >-
  [your optimized description]
```

**Step 2: Run a manual spot-check.**

Open a Claude Code session with the skill installed. Run these 5 prompts -- a mix of should-trigger and should-not-trigger that were NOT in your eval set:

```
1. "Can you put together release notes for what we shipped this month?"
2. "Show me the diff between main and this branch"
3. "What features were added since the v2.0 tag?"
4. "Help me set up git hooks for this project"
5. "Create a summary of all commits by author"
```

Record the results:

| # | Prompt | Expected | Actual | Correct? |
|---|--------|----------|--------|----------|
| 1 | Release notes for this month | TRIGGER | | |
| 2 | Show me the diff | NO TRIGGER | | |
| 3 | Features since v2.0 tag | TRIGGER | | |
| 4 | Set up git hooks | NO TRIGGER | | |
| 5 | Summary of commits by author | TRIGGER | | |

These are fresh queries the optimization never saw. If the description handles them correctly, you have good evidence of generalization.

**Step 3: Compare old vs. new description.**

Document the delta between your original description (from Module 2) and your optimized description:

```
## Description Comparison

### Original (Module 2):
[paste]

### Optimized (Module 6):
[paste]

### What changed:
- Added trigger phrases: [list]
- Added negative triggers: [list]
- Removed or tightened: [list]
- Character count: [before] → [after]

### Why it changed:
[2-3 sentences explaining the key improvements and what drove them]
```

**Step 4: Update your course log.**

Add an entry to `course-log.md` documenting the optimization process, your train/test results, and the final description. Include any surprises -- queries that were harder to get right than expected, trade-offs you had to make between triggering and not triggering on borderline cases.

---

## Key Takeaways

1. **The description is the gatekeeper.** Claude decides whether to load a skill based solely on the name and description. If the description does not match the user's intent, the skill is invisible -- no matter how good the instructions are. Treat description writing as a first-class optimization problem, not an afterthought.

2. **Near-miss negatives are the real test.** Any description can avoid triggering on "what's the weather?" The hard part is not triggering on "show me the git log" while still triggering on "summarize recent commits." Your eval set is only as good as its hardest negatives.

3. **Train/test splits prevent overfitting.** Optimizing a description against 20 queries and then "validating" on those same 20 queries tells you nothing. Hold out 40% of your queries. If test accuracy is much worse than train accuracy, the description is memorizing phrases rather than capturing intent.

4. **Negative triggers are underused and powerful.** A single line -- "Do NOT use for raw git log viewing or commit message writing" -- can eliminate an entire class of overtrigger errors. Most skill authors forget to include them.

5. **Stop after 5 iterations.** The optimization loop has diminishing returns. Most gains happen in iterations 1-3. After 5 iterations, remaining errors are usually genuine edge cases where reasonable people would disagree on whether the skill should trigger. Accept the trade-off and ship.

6. **The eval set is a reusable asset.** The 20 queries you wrote in Exercise 6.1 are not throwaway test cases. They are the regression suite for your description. Every time you update the description in the future, re-run the eval set to check for regressions.

---

**Next module:** [Module 7 -- Advanced Patterns](../module-07-advanced-patterns/) -- apply skill design patterns for multi-step workflows, MCP server integration, and cross-skill coordination.
