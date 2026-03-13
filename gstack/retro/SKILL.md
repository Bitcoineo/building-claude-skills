---
name: retro
version: 2.0.0
description: >-
  Weekly engineering retrospective. Analyzes commit history, work patterns,
  and code quality metrics with persistent history and trend tracking.
  Team-aware: breaks down per-person contributions with praise and growth
  areas. Use when user asks to "run a retro", "team retrospective",
  "how did we do this week", "engineering retro", or "weekly review".
  Do NOT use for individual performance review, code review, or plan review.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# /retro — Weekly Engineering Retrospective

Generates a comprehensive engineering retrospective analyzing commit history, work patterns, and code quality metrics. Team-aware: identifies the user running the command, then analyzes every contributor with per-person praise and growth opportunities. Designed for a senior IC/CTO-level builder using Claude Code as a force multiplier.

## User-invocable
When the user types `/retro`, run this skill.

## Arguments
- `/retro` — default: last 7 days
- `/retro 24h` — last 24 hours
- `/retro 14d` — last 14 days
- `/retro 30d` — last 30 days
- `/retro compare` — compare current window vs prior same-length window
- `/retro compare 14d` — compare with explicit window

## Instructions

Parse the argument to determine the time window. Default to 7 days if no argument given. Use `--since="N days ago"`, `--since="N hours ago"`, or `--since="N weeks ago"` (for `w` units) for git log queries. All times should be reported in **Pacific time** (use `TZ=America/Los_Angeles` when converting timestamps).

**Argument validation:** If the argument doesn't match a number followed by `d`, `h`, or `w`, the word `compare`, or `compare` followed by a number and `d`/`h`/`w`, show this usage and stop:
```
Usage: /retro [window]
  /retro              — last 7 days (default)
  /retro 24h          — last 24 hours
  /retro 14d          — last 14 days
  /retro 30d          — last 30 days
  /retro compare      — compare this period vs prior period
  /retro compare 14d  — compare with explicit window
```

### Step 1: Gather Raw Data

First, fetch origin and identify the current user:
```bash
git fetch origin main --quiet
git config user.name
git config user.email
```

The name returned by `git config user.name` is **"you"** — the person reading this retro. All other authors are teammates. Use this to orient the narrative: "your" commits vs teammate contributions.

Run ALL of these git commands in parallel (they are independent):

```bash
# 1. All commits with timestamps, subject, hash, author, files changed, insertions, deletions
git log origin/main --since="<window>" --format="%H|%aN|%ae|%ai|%s" --shortstat

# 2. Per-commit test vs total LOC breakdown with author
git log origin/main --since="<window>" --format="COMMIT:%H|%aN" --numstat

# 3. Commit timestamps for session detection and hourly distribution (with author)
TZ=America/Los_Angeles git log origin/main --since="<window>" --format="%at|%aN|%ai|%s" | sort -n

# 4. Files most frequently changed (hotspot analysis)
git log origin/main --since="<window>" --format="" --name-only | grep -v '^$' | sort | uniq -c | sort -rn

# 5. PR numbers from commit messages
git log origin/main --since="<window>" --format="%s" | grep -oE '#[0-9]+' | sed 's/^#//' | sort -n | uniq | sed 's/^/#/'

# 6. Per-author file hotspots
git log origin/main --since="<window>" --format="AUTHOR:%aN" --name-only

# 7. Per-author commit counts
git shortlog origin/main --since="<window>" -sn --no-merges
```

### Step 2: Compute Metrics

Calculate and present these metrics in a summary table:

| Metric | Value |
|--------|-------|
| Commits to main | N |
| Contributors | N |
| PRs merged | N |
| Total insertions | N |
| Total deletions | N |
| Net LOC added | N |
| Test LOC (insertions) | N |
| Test LOC ratio | N% |
| Version range | vX.Y.Z.W → vX.Y.Z.W |
| Active days | N |
| Detected sessions | N |
| Avg LOC/session-hour | N |

Then show a **per-author leaderboard** immediately below:

```
Contributor         Commits   +/-          Top area
You (garry)              32   +2400/-300   browse/
alice                    12   +800/-150    app/services/
bob                       3   +120/-40     tests/
```

Sort by commits descending. The current user always appears first, labeled "You (name)".

### Step 3: Commit Time Distribution

Show hourly histogram in Pacific time using bar chart. Identify and call out peak hours, dead zones, whether pattern is bimodal or continuous, and late-night coding clusters (after 10pm).

### Step 4: Work Session Detection

For session detection thresholds, focus score calculation, and other metric formulas, consult `references/metrics-formulas.md`.

Detect sessions and for each report: start/end time (Pacific), number of commits, and duration. Classify sessions as Deep, Medium, or Micro per the thresholds in the reference. Calculate total active coding time, average session length, and LOC per hour of active time.

### Step 5: Commit Type Breakdown

Categorize by conventional commit prefix (feat/fix/refactor/test/chore/docs). Show as percentage bar. Flag if fix ratio exceeds 50% — this signals a "ship fast, fix fast" pattern that may indicate review gaps.

### Step 6: Hotspot Analysis

Show top 10 most-changed files. Flag files changed 5+ times (churn hotspots), test vs production files in the list, and VERSION/CHANGELOG frequency.

### Step 7: PR Size Distribution

From commit diffs, estimate PR sizes and bucket them as Small (<100 LOC), Medium (100-500), Large (500-1500), XL (1500+ — flag with file counts).

### Step 8: Focus Score + Ship of the Week

**Focus score:** See `references/metrics-formulas.md` for the calculation. Report as: "Focus score: 62% (app/services/)".

**Ship of the week:** Auto-identify the single highest-LOC PR in the window. Highlight it with PR number/title, LOC changed, and why it matters.

### Step 9: Team Member Analysis

For each contributor (including the current user), compute:
1. **Commits and LOC** — total commits, insertions, deletions, net LOC
2. **Areas of focus** — top 3 directories/files touched
3. **Commit type mix** — personal feat/fix/refactor/test breakdown
4. **Session patterns** — peak hours, session count
5. **Test discipline** — personal test LOC ratio
6. **Biggest ship** — highest-impact commit or PR in the window

**For the current user ("You"):** Deepest treatment. Include session analysis, time patterns, focus score. Frame in first person.

**For each teammate:** 2-3 sentences on what they worked on, then:
- **Praise** (1-2 specific things): Anchor in actual commits. Not "great work" — say exactly what was good.
- **Opportunity for growth** (1 specific thing): Frame as leveling-up, not criticism. Anchor in data.

**Solo repo:** Skip team breakdown — the retro is personal.

**Co-Authored-By:** Parse `Co-Authored-By:` trailers. Credit co-authors alongside the primary author. Note AI co-authors (e.g., `noreply@anthropic.com`) but do not include them as team members — track "AI-assisted commits" as a separate metric.

### Step 10: Week-over-Week Trends (if window >= 14d)

If 14+ days, split into weekly buckets and show trends for commits (total and per-author), LOC, test ratio, fix ratio, and session count.

### Step 11: Streak Tracking

See `references/metrics-formulas.md` for streak tracking methodology and commands.

Count backward from today. Display both team and personal shipping streaks.

### Step 12: Load History & Compare

Before saving the new snapshot, check for prior retro history:

```bash
ls -t .context/retros/*.json 2>/dev/null
```

**If prior retros exist:** Load the most recent one using the Read tool. Calculate deltas for key metrics and include a **Trends vs Last Retro** section:
```
                    Last        Now         Delta
Test ratio:         22%    →    41%         +19pp
Sessions:           10     →    14          +4
LOC/hour:           200    →    350         +75%
Fix ratio:          54%    →    30%         -24pp (improving)
Commits:            32     →    47          +47%
Deep sessions:      3      →    5           +2
```

**If no prior retros exist:** Skip comparison and note: "First retro recorded — run again next week to see trends."

### Step 13: Save Retro History

Save the JSON snapshot using the schema defined in `references/json-schema.md`.

### Step 14: Write the Narrative

Structure the output as:

---

**Tweetable summary** (first line):
```
Week of Mar 1: 47 commits (3 contributors), 3.2k LOC, 38% tests, 12 PRs, peak: 10pm | Streak: 47d
```

## Engineering Retro: [date range]

### Summary Table
(from Step 2)

### Trends vs Last Retro
(from Step 12 — skip if first retro)

### Time & Session Patterns
(from Steps 3-4)

Narrative interpreting team-wide patterns:
- Most productive hours and what drives them
- Whether sessions are getting longer or shorter over time
- Estimated hours per day of active coding (team aggregate)
- Notable patterns: do team members code at the same time or in shifts?

### Shipping Velocity
(from Steps 5-7)

Narrative covering:
- Commit type mix and what it reveals
- PR size discipline
- Fix-chain detection (sequences of fix commits on the same subsystem)
- Version bump discipline

### Code Quality Signals
- Test LOC ratio trend
- Hotspot analysis (are the same files churning?)
- Any XL PRs that should have been split

### Focus & Highlights
(from Step 8)
- Focus score with interpretation
- Ship of the week callout

### Your Week (personal deep-dive)
(from Step 9, for the current user only)

This is the section the user cares most about. Include their personal commit count, LOC, test ratio, session patterns, peak hours, focus areas, biggest ship, **what you did well** (2-3 specific things), and **where to level up** (1-2 actionable suggestions).

### Team Breakdown
(from Step 9, for each teammate — skip if solo repo)

For each teammate (sorted by commits descending):

#### [Name]
- **What they shipped**: 2-3 sentences on contributions, focus areas, commit patterns
- **Praise**: 1-2 specific things anchored in actual commits. Be genuine — what would you actually say in a 1:1?
- **Opportunity for growth**: 1 specific, constructive suggestion. Frame as investment, not criticism.

**AI collaboration note:** If many commits have AI co-author trailers, note the AI-assisted commit percentage as a team metric. Frame neutrally.

### Top 3 Team Wins
The 3 highest-impact things shipped. For each: what it was, who shipped it, why it matters.

### 3 Things to Improve
Specific, actionable, anchored in actual commits. Mix personal and team-level. Phrase as "to get even better, the team could..."

### 3 Habits for Next Week
Small, practical, realistic. Each takes <5 minutes to adopt. At least one team-oriented.

### Week-over-Week Trends
(if applicable, from Step 10)

---

## Compare Mode

When the user runs `/retro compare` (or `/retro compare 14d`):

1. Compute metrics for the current window (default 7d) using `--since="7 days ago"`
2. Compute metrics for the prior same-length window using both `--since` and `--until` to avoid overlap (e.g., `--since="14 days ago" --until="7 days ago"` for a 7d window)
3. Show a side-by-side comparison table with deltas and arrows
4. Write a brief narrative highlighting the biggest improvements and regressions
5. Save only the current-window snapshot (same as a normal retro run)

## Tone

- Encouraging but candid, no coddling
- Specific and concrete — always anchor in actual commits/code
- Skip generic praise ("great job!") — say exactly what was good and why
- Frame improvements as leveling up, not criticism
- Praise should feel like something you'd actually say in a 1:1 — specific, earned, genuine
- Growth suggestions should feel like investment advice — "this is worth your time because..."
- Never compare teammates against each other negatively
- Keep total output around 3000-4500 words
- Use markdown tables and code blocks for data, prose for narrative
- Output directly to the conversation — do NOT write to filesystem (except the `.context/retros/` JSON snapshot)

## Important Rules

- ALL narrative output goes directly to the user in the conversation. The ONLY file written is the `.context/retros/` JSON snapshot.
- Use `origin/main` for all git queries (not local main which may be stale)
- Convert all timestamps to Pacific time for display (use `TZ=America/Los_Angeles`)
- If the window has zero commits, say so and suggest a different window
- Round LOC/hour to nearest 50 (see `references/metrics-formulas.md`)
- Treat merge commits as PR boundaries
- Do not read CLAUDE.md or other docs — this skill is self-contained
- On first run (no prior retros), skip comparison sections gracefully
