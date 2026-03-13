# Module 5: Systematic Testing with Evals

**Time estimate:** 45-60 minutes
**Prerequisites:** Completed Module 4 (a manually tested git-changelog skill with at least one iteration of improvements)
**Outcome:** An evals.json file with 5 test cases, benchmark results comparing your skill against baseline, and a written analysis of assertion quality

---

## Learning Objectives

By the end of this module, you will be able to:

- Write evals.json test cases with objectively verifiable expectations
- Run with-skill and baseline comparisons using the skill-creator eval pipeline
- Interpret grading.json output and identify pass/fail evidence
- Analyze benchmark.json to quantify skill improvement over baseline
- Identify and fix non-discriminating, always-failing, and flaky assertions

---

## Theory

### 1. Why Systematic Evals Matter

Manual testing (Module 4) catches obvious problems but has fundamental limitations:

- **It doesn't scale.** Running 10 prompts by hand, reviewing transcripts, and recording results takes an hour. Running them again after every change takes another hour.
- **It's not repeatable.** Different testers notice different things. You might catch a skipped script today and miss it tomorrow because you're focused on formatting.
- **It doesn't produce evidence.** "I tested it and it seemed fine" is not a convincing argument for a skill's quality. Stakeholders -- including future-you -- want numbers.

Systematic evaluation solves all three. You write test cases once, run them automatically, and get quantitative results you can compare across versions. Specifically, evals let you:

1. **Catch regressions.** You changed the description to fix undertriggering -- did that break the output format? Run the eval suite and find out in minutes, not hours.
2. **Compare skill vs. baseline.** The whole point of a skill is to make Claude better at a task. Evals prove this by running the same prompts with and without the skill, then grading both.
3. **Produce quantitative evidence.** "The skill passes 14/15 assertions and uses 48% fewer tokens than baseline" is a statement you can stand behind.

Think of it this way: Module 4 was exploratory testing -- you were discovering problems. Module 5 is regression testing -- you're building infrastructure to detect problems automatically.

---

### 2. The Eval JSON Format

Test cases live in `evals.json`, a JSON array where each element defines one test scenario. Here is the structure:

```json
[
  {
    "id": "unique-test-id",
    "prompt": "The user prompt to test",
    "expected_output": "Description of what good output looks like",
    "files": ["optional/files/to/include.txt"],
    "expectations": [
      "Assertion 1: The output includes a version header",
      "Assertion 2: Commits are categorized by type"
    ]
  }
]
```

Each field serves a specific purpose:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `id` | string | Yes | Unique identifier for the test case. Use kebab-case: `changelog-since-tag`, `release-notes-v2` |
| `prompt` | string | Yes | The exact user prompt that will be sent to Claude. This is what the user would type. |
| `expected_output` | string | Yes | A qualitative description of what good output looks like. The grader uses this as context, not as a literal match. |
| `files` | string[] | No | Paths to files that should be included as context. Useful for testing with specific repository states. |
| `expectations` | string[] | Yes | List of objectively verifiable assertions. Each one is independently graded as pass or fail. |

The `id` field matters more than you might think. It appears in grading results, benchmark summaries, and the eval viewer. A good id tells you what the test covers at a glance. Compare:

- Bad: `test-1`, `test-2`, `test-3`
- Good: `changelog-since-tag`, `date-range-two-weeks`, `release-notes-breaking-changes`

---

### 3. Writing Good Expectations

Expectations are the core of the eval system. Each expectation is a statement that a grader agent evaluates against Claude's actual output. The grader decides: did the output satisfy this assertion? Yes or no?

This means your expectations must be **objectively verifiable** -- a grader agent reading only the output must be able to determine pass or fail without ambiguity.

**The discrimination test:** A good expectation passes when the skill works correctly and fails when it doesn't. If an expectation always passes regardless of skill quality, it's not testing anything. If it always fails regardless of what you do, the instruction is impossible or the expectation is wrong.

**Good expectations:**

```json
[
  "The output contains a version header in the format '## [vX.Y.Z] - YYYY-MM-DD'",
  "Commits are grouped under category headings (Features, Bug Fixes, etc.)",
  "Each commit entry includes its short hash (7 characters)",
  "Breaking changes, if present, appear before all other sections",
  "The output does not include merge commits"
]
```

Why these work: each one describes a specific, observable property of the output. The grader can scan the output and determine yes or no.

**Bad expectations:**

```json
[
  "The output looks good",
  "The changelog is well-formatted",
  "Output is valid markdown",
  "The skill performed correctly",
  "The result is useful"
]
```

Why these fail:

- "Looks good" and "well-formatted" are subjective -- different graders would disagree.
- "Valid markdown" almost always passes because nearly any text is technically valid markdown. It doesn't discriminate.
- "Performed correctly" is circular -- it restates the question instead of answering it.
- "Useful" is a judgment call, not a verifiable property.

**The middle ground to avoid:**

```json
[
  "The output is a changelog"
]
```

This is technically verifiable, but it's so broad that it passes even when the skill produces a low-quality changelog with missing sections, wrong format, and no commit hashes. Make expectations specific enough to catch the failure modes you care about.

---

### 4. The Eval Loop

The skill-creator runs evals through a structured 5-step process. Understanding this process helps you write better test cases and interpret results correctly.

**Step 1: Spawn with-skill and baseline runs in parallel.**

For each test case, the eval runner launches two separate Claude sessions: one with your skill installed and one without. Both receive the identical prompt. Running them in parallel saves time -- you don't wait for one to finish before starting the other.

**Step 2: Draft assertions while runs are in progress.**

While both runs are executing, the system prepares the grading criteria from your expectations. This is why expectations need to be self-contained -- the grader works from the expectation text alone, not from any external context.

**Step 3: Capture timing data from run notifications.**

When each run completes, the system records: total tokens consumed, wall-clock duration, and number of tool calls. This data feeds into the performance comparison.

**Step 4: Grade and aggregate results.**

A grader agent evaluates each expectation against each run's output. For every expectation, the grader produces a verdict (pass/fail) and evidence (a brief explanation of why). Results are written to `grading.json`.

**Step 5: Launch eval viewer for human review.**

The eval viewer presents results in a format designed for quick review: which assertions passed, which failed, and what the evidence was. This is where you decide whether to adjust your skill or your test cases.

```
    ┌──────────────────────────────────┐
    │  For each test case in evals.json │
    └──────────┬───────────────────────┘
               │
    ┌──────────▼───────────────────────┐
    │  Spawn two parallel runs:         │
    │  • WITH skill installed           │
    │  • WITHOUT skill (baseline)       │
    └──────────┬───────────────────────┘
               │
    ┌──────────▼───────────────────────┐
    │  Grade each run against           │
    │  expectations from evals.json     │
    └──────────┬───────────────────────┘
               │
    ┌──────────▼───────────────────────┐
    │  Aggregate into benchmark.json    │
    │  Compare: skill vs. baseline      │
    └──────────┬───────────────────────┘
               │
    ┌──────────▼───────────────────────┐
    │  Human reviews results            │
    │  Adjusts skill or test cases      │
    └──────────────────────────────────┘
```

---

### 5. Grading Format

The grading output (`grading.json`) records the result of every expectation against every run. Here is the structure:

```json
{
  "test_id": "changelog-since-tag",
  "run_type": "with-skill",
  "expectations": [
    {
      "text": "The output contains a version header in the format '## [vX.Y.Z] - YYYY-MM-DD'",
      "passed": true,
      "evidence": "The output begins with '## [v2.1.0] - 2026-03-12', which matches the expected format."
    },
    {
      "text": "Commits are grouped under category headings (Features, Bug Fixes, etc.)",
      "passed": true,
      "evidence": "The output contains '### Features' with 3 commits and '### Bug Fixes' with 2 commits listed underneath."
    },
    {
      "text": "Each commit entry includes its short hash (7 characters)",
      "passed": false,
      "evidence": "Commit entries use full 40-character hashes instead of 7-character short hashes. Example: 'a1b2c3d4e5f6...' instead of 'a1b2c3d'."
    }
  ],
  "summary": "2/3 expectations passed. The skill correctly formats the version header and groups commits by type, but uses full hashes instead of short hashes.",
  "timing": {
    "tokens_used": 5800,
    "duration_seconds": 12.4
  }
}
```

Key fields to pay attention to:

- **`evidence`** is the most important field. It tells you *why* the grader decided pass or fail. When an expectation fails, the evidence tells you whether the problem is in the skill (it genuinely did the wrong thing) or in the expectation (the expectation was unreasonable or ambiguous).
- **`timing`** lets you compare efficiency. If the with-skill run uses fewer tokens and finishes faster, the skill is providing value beyond just quality.
- **`summary`** gives a quick overview, but always drill into individual expectations when diagnosing issues.

---

### 6. Benchmark Format

While grading.json covers individual runs, `benchmark.json` aggregates results across multiple test cases to produce an overall performance comparison.

```json
{
  "skill_name": "git-changelog",
  "eval_date": "2026-03-12",
  "test_cases": 5,
  "run_summary": {
    "with_skill": {
      "total_expectations": 15,
      "passed": 13,
      "failed": 2,
      "pass_rate": 0.867,
      "mean_tokens": 5200,
      "mean_duration_seconds": 11.3
    },
    "baseline": {
      "total_expectations": 15,
      "passed": 7,
      "failed": 8,
      "pass_rate": 0.467,
      "mean_tokens": 10400,
      "mean_duration_seconds": 24.7
    },
    "delta": {
      "pass_rate_improvement": 0.400,
      "token_reduction": 0.50,
      "duration_reduction": 0.54
    }
  },
  "per_test": [
    {
      "id": "changelog-since-tag",
      "with_skill_passed": 3,
      "baseline_passed": 1,
      "with_skill_tokens": 4800,
      "baseline_tokens": 11200
    }
  ]
}
```

The `delta` section is the punchline. It answers the question: **how much better is the skill than no skill at all?**

- **`pass_rate_improvement`**: The skill passes 40 percentage points more assertions than baseline. This measures quality.
- **`token_reduction`**: The skill uses 50% fewer tokens. This measures efficiency.
- **`duration_reduction`**: The skill finishes 54% faster. This measures speed.

---

### 7. Performance Comparison: What Good Looks Like

The official guide provides concrete numbers for what skill-driven improvement looks like:

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 15 | 2 clarifying questions |
| Failed API calls | 3 | 0 |
| Tokens consumed | 12,000 | 6,000 |

This is the kind of improvement to aim for. Your skill should not just produce slightly better output -- it should fundamentally change the interaction pattern. Fewer messages means the user gets their result faster. Zero failed API calls means the skill's instructions prevent dead ends. Half the tokens means the conversation stays within budget on complex repositories.

When your benchmark shows marginal improvement (e.g., 5% better pass rate, same token usage), the skill isn't pulling its weight. Go back to the SKILL.md and ask: what knowledge does this skill provide that Claude doesn't already have?

---

## Exercises

### Exercise 5.1: Write evals.json

**Goal:** Create a complete evals.json file with 5 test cases for the git-changelog skill.

Write the following file at `student-workspace/git-changelog/evals.json`:

```json
[
  {
    "id": "changelog-since-tag",
    "prompt": "Generate a changelog since the last tag",
    "expected_output": "A formatted changelog covering all commits from the most recent git tag to HEAD, organized by commit type with a version header.",
    "expectations": [
      "The output includes a version header with a version number and date",
      "Commits are grouped under category headings such as Features, Bug Fixes, or similar type-based sections",
      "Individual commit entries include their short commit hash (7-8 characters)"
    ]
  },
  {
    "id": "date-range-two-weeks",
    "prompt": "What changed in the last 2 weeks?",
    "expected_output": "A summary of commits from the past two weeks, with dates visible and only recent commits included.",
    "expectations": [
      "The output uses a date-based range (last 2 weeks) rather than a tag-based range",
      "Dates are visible in the output, either per-commit or in a header",
      "The output does not include commits older than 2 weeks from today"
    ]
  },
  {
    "id": "release-notes-v2",
    "prompt": "Prepare release notes for v2.0",
    "expected_output": "Formal release notes suitable for a v2.0 release, with breaking changes called out and contributors acknowledged.",
    "expectations": [
      "The output uses a release notes format with 'v2.0' referenced in the header or title",
      "A Breaking Changes section is present (even if empty or noted as 'none')",
      "A contributor or author list is included at the end of the output"
    ]
  },
  {
    "id": "commit-range-explicit",
    "prompt": "Summarize commits between abc123 and def456",
    "expected_output": "A changelog or summary covering exactly the commits in the specified range abc123..def456.",
    "expectations": [
      "The output uses the exact commit range abc123..def456 (or equivalent git range syntax) rather than a tag or date range",
      "All commits within the specified range are included in the output",
      "The output does not include commits outside the specified range"
    ]
  },
  {
    "id": "changelog-no-version",
    "prompt": "Generate a changelog for this project",
    "expected_output": "A changelog that automatically determines the appropriate range, falling back gracefully if no tags exist in the repository.",
    "expectations": [
      "The output determines the latest tag automatically or falls back to a reasonable default if no tags exist",
      "The skill does not ask the user to specify a version or range — it resolves the ambiguity itself",
      "The output includes a version header or section title even when no explicit version was requested"
    ]
  }
]
```

**What to check before moving on:**

1. Every `id` is unique and descriptive
2. Every `prompt` is a realistic user request (drawn from the trigger tests in Module 4)
3. Every `expected_output` describes the qualitative goal, not a literal string match
4. Every expectation is objectively verifiable -- a grader agent can evaluate it by reading only the output
5. Expectations discriminate: they should pass with a good skill and fail with no skill

**Self-review questions for each expectation:**

- Can a grader determine pass/fail by reading the output alone? If the grader needs to inspect tool calls, the expectation is testing process, not output.
- Would this expectation pass even with a bad changelog? If yes, it's not discriminating enough.
- Would this expectation fail even with a good changelog? If yes, it's too strict or testing the wrong thing.

---

### Exercise 5.2: Run the Evals

**Goal:** Execute the eval pipeline, running both with-skill and baseline comparisons, and capture the results.

**Step 1: Verify prerequisites.**

Before running evals, confirm your setup:

```bash
# Confirm the skill is installed
ls ~/.claude/skills/git-changelog/SKILL.md

# Confirm evals.json exists
ls student-workspace/git-changelog/evals.json

# Confirm you're in a git repository with commit history
git log --oneline -5
```

**Step 2: Run the eval suite.**

Use the skill-creator to execute evals. The skill-creator handles the full pipeline: spawning parallel runs, grading, and aggregation.

```
Run the evals defined in student-workspace/git-changelog/evals.json against the git-changelog skill
```

The skill-creator will:

1. Read your evals.json
2. For each test case, spawn a with-skill run and a baseline run in parallel
3. Wait for all runs to complete (you'll see timing notifications)
4. Grade each run's output against your expectations
5. Aggregate results into benchmark.json

**Step 3: Understand the timing data.**

While runs execute, note the timing notifications. You'll see something like:

```
[with-skill run "changelog-since-tag"] completed in 11.2s, 4800 tokens
[baseline run "changelog-since-tag"] completed in 23.8s, 10200 tokens
```

Record these in a table:

| Test ID | With-Skill Time | With-Skill Tokens | Baseline Time | Baseline Tokens |
|---------|-----------------|-------------------|---------------|-----------------|
| changelog-since-tag | | | | |
| date-range-two-weeks | | | | |
| release-notes-v2 | | | | |
| commit-range-explicit | | | | |
| changelog-no-version | | | | |
| **Mean** | | | | |

**Step 4: Review the grader output.**

Open the grading results. For each test case, review:

- Which expectations passed and which failed
- The evidence field for every failed expectation -- is the failure a skill problem or an expectation problem?
- Whether the with-skill run outperformed baseline on the same expectations

If a with-skill expectation failed but the baseline also failed, the expectation might be testing something Claude can't do regardless of skill. If the with-skill run failed but baseline passed, the skill is actively making things worse on that dimension -- a critical finding.

---

### Exercise 5.3: Analyze Results

**Goal:** Interpret benchmark.json, classify assertion quality, and write an analysis summary.

**Step 1: Review benchmark.json.**

Open your benchmark.json (generated by the eval pipeline) and record the top-line numbers:

```
Skill pass rate:     __/__ expectations (__%)
Baseline pass rate:  __/__ expectations (__%)
Pass rate delta:     +__%
Token reduction:     __%
Duration reduction:  __%
```

**Step 2: Classify each assertion.**

Go through every expectation across all 5 test cases and classify it into one of four categories:

| Category | Definition | Action |
|----------|-----------|--------|
| **Discriminating** | Passes with skill, fails without | Keep -- this is a good assertion |
| **Always passes** | Passes both with and without skill | Tighten -- it's not testing anything the skill uniquely provides |
| **Always fails** | Fails both with and without skill | Fix -- either the skill instruction or the expectation is wrong |
| **Flaky** | Inconsistent results across runs | Investigate -- why does it sometimes pass? |

Use this tracking table:

```
## Assertion Classification

### Test: changelog-since-tag
| # | Expectation | With Skill | Baseline | Category |
|---|-------------|------------|----------|----------|
| 1 | Version header with version and date | | | |
| 2 | Grouped under category headings | | | |
| 3 | Short commit hash per entry | | | |

### Test: date-range-two-weeks
| # | Expectation | With Skill | Baseline | Category |
|---|-------------|------------|----------|----------|
| 1 | Uses date-based range | | | |
| 2 | Dates visible in output | | | |
| 3 | No commits older than 2 weeks | | | |

### Test: release-notes-v2
| # | Expectation | With Skill | Baseline | Category |
|---|-------------|------------|----------|----------|
| 1 | Release notes format with v2.0 | | | |
| 2 | Breaking Changes section present | | | |
| 3 | Contributor list included | | | |

### Test: commit-range-explicit
| # | Expectation | With Skill | Baseline | Category |
|---|-------------|------------|----------|----------|
| 1 | Uses exact commit range | | | |
| 2 | All commits in range included | | | |
| 3 | No commits outside range | | | |

### Test: changelog-no-version
| # | Expectation | With Skill | Baseline | Category |
|---|-------------|------------|----------|----------|
| 1 | Determines latest tag or falls back | | | |
| 2 | Does not ask user to specify | | | |
| 3 | Includes version header | | | |

## Summary Counts
| Category | Count |
|----------|-------|
| Discriminating | /15 |
| Always passes | /15 |
| Always fails | /15 |
| Flaky | /15 |
```

**Step 3: Diagnose problem assertions.**

For each assertion that isn't discriminating, write a diagnosis:

**Always-passes assertions** are not pulling their weight. Ask: what about this assertion is too easy? Usually the fix is to make the expectation more specific. For example, "the output contains commit information" always passes because even baseline Claude mentions commits. Tighten it to: "each commit entry includes its short hash, author, and conventional commit type."

**Always-fails assertions** have two possible causes:

1. **The skill doesn't teach this.** Your SKILL.md never instructs Claude to include a contributor list, so the "contributor list included" assertion fails on both runs. Fix: add the instruction to SKILL.md.
2. **The expectation is unreasonable.** "The output includes exactly 47 commits" will fail unless the test repository has exactly 47 commits in range. Fix: rewrite the expectation to be verifiable without knowing the exact repository state.

**Flaky assertions** are the trickiest. An assertion that passes 60% of the time usually means:

- The skill instructions are ambiguous (Claude sometimes follows them, sometimes interprets them differently)
- The expectation is borderline (reasonable people would disagree on pass/fail)
- The output varies based on the repository state at test time

For flaky assertions, review the evidence field from multiple runs. Look for patterns in when it passes vs. when it fails.

**Step 4: Write an analysis summary.**

Write a 1-page analysis (in your course log or a separate file) that covers:

1. **Top-line results:** Skill pass rate vs. baseline pass rate, token reduction, time savings
2. **Strongest improvements:** Which test cases showed the biggest skill advantage? Why?
3. **Weakest areas:** Which test cases showed the smallest improvement or regressions? What does the skill need to do better?
4. **Assertion quality:** How many of your 15 assertions are truly discriminating? What changes would improve the non-discriminating ones?
5. **Next steps:** Based on this analysis, what is the single most impactful change to make to the skill?

**Example analysis excerpt:**

> The git-changelog skill achieves an 87% pass rate (13/15 assertions) compared to baseline's 47% (7/15). Token usage is 50% lower with the skill (mean 5,200 vs. 10,400 tokens). The strongest improvement is on structured output: baseline never includes category headings or short hashes, while the skill does consistently.
>
> Two assertions always pass (both runs): "dates visible in output" and "uses exact commit range." These need tightening -- they test behaviors Claude does by default. Two assertions always fail (both runs): "contributor list included" and "breaking changes section present." The SKILL.md doesn't explicitly instruct these, so I need to add those instructions before rerunning.
>
> One assertion is flaky: "does not ask user to specify version." This passes 3 of 5 runs with the skill. The SKILL.md says "resolve ambiguity" but doesn't say "do not ask the user." Tightening the instruction should fix the flakiness.

---

## Key Takeaways

1. **Evals are the infrastructure that makes iteration scalable.** Manual testing discovers problems; evals detect regressions. Once you have evals.json, every change to the skill can be validated in minutes instead of hours.

2. **Good expectations are objectively verifiable and discriminating.** If a grader agent can't determine pass/fail by reading the output alone, the expectation is too vague. If the expectation passes without the skill, it's not testing anything the skill provides.

3. **The baseline comparison is the core value proposition.** A skill's worth is measured by the delta between with-skill and baseline performance. If the delta is small, the skill isn't teaching Claude anything it doesn't already know.

4. **Always-passes and always-fails assertions are diagnostic signals.** Always-passes means your expectation is too easy -- tighten it. Always-fails means either the skill is missing an instruction or the expectation is unreasonable. Both require action.

5. **Benchmark numbers tell a story.** Pass rate measures quality. Token reduction measures efficiency. Duration reduction measures speed. A good skill improves all three, but quality (pass rate delta) is the most important.

6. **Evals test the output, not the process.** If you want to verify that Claude uses `parse_commits.py`, you need transcript review (Module 4). Evals verify the end result, which is the right abstraction for automated testing -- you care *that* the changelog is correct, not *how* Claude produced it.

---

**Next module:** [Module 6 -- Description Optimization](../module-06-description-optimization/) -- use programmatic optimization to improve trigger accuracy with train/test splits and automated evaluation loops.
