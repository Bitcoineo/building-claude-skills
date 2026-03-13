# Metrics Formulas Reference

## Session Detection Logic

**Gap threshold: 45 minutes** between consecutive commits.

**Why 45 minutes?** This threshold is derived from the standard Pomodoro technique (25 min work + 5 min break) with a generous buffer for context-switching, building, and testing. It's also a well-established threshold in engineering productivity research — gaps shorter than 45 minutes almost always represent the same work session, while longer gaps indicate a real break or task switch.

**How it works:** Sort all commits by timestamp. Walk the sorted list; any gap of 45+ minutes between consecutive commits starts a new session. A session's duration is the time from its first commit to its last commit.

### Session Classification

| Category | Duration | Description |
|----------|----------|-------------|
| **Deep session** | 50+ minutes | Sustained focused work — multiple commits, real progress |
| **Medium session** | 20-50 minutes | Meaningful but shorter — a PR's worth of work |
| **Micro session** | <20 minutes | Single-commit fire-and-forget — hotfix, typo, config change |

### Session Metrics

- **Total active coding time** = sum of all session durations
- **Average session length** = total active coding time / number of sessions
- **LOC per session-hour** = net LOC changed / (total active coding time in hours), rounded to nearest 50

## Focus Score Calculation

**Focus score** = percentage of commits touching the single most-changed top-level directory.

1. For each commit, identify which top-level directories were modified (e.g., `app/services/`, `browse/`, `tests/`)
2. Count how many commits touched each top-level directory
3. The directory with the highest count is the "focus area"
4. Focus score = (commits touching focus area / total commits) * 100

**Interpretation:**
- Higher score = deeper focused work on a single area
- Lower score = scattered context-switching across the codebase
- Report as: `"Focus score: 62% (app/services/)"`

## LOC/Hour Rounding

Always round LOC/hour to the **nearest 50**. This avoids false precision — the underlying data (commit timestamps) is too coarse for exact rates.

Examples: 347 → 350, 124 → 100, 275 → 300, 225 → 250

## Streak Tracking

Count consecutive days with at least 1 commit to `origin/main`, counting backward from today.

- **Team streak**: Uses all commits regardless of author
- **Personal streak**: Uses only commits matching the current user's `git config user.name`

Both queries use Pacific time (`TZ=America/Los_Angeles`) for date boundaries.

```bash
# Team streak: all unique commit dates (Pacific time) — no hard cutoff
TZ=America/Los_Angeles git log origin/main --format="%ad" --date=format:"%Y-%m-%d" | sort -u

# Personal streak: only the current user's commits
TZ=America/Los_Angeles git log origin/main --author="<user_name>" --format="%ad" --date=format:"%Y-%m-%d" | sort -u
```

Count backward from today's date — how many consecutive days have at least one commit? The query has no `--since` cutoff so streaks of any length are reported accurately.

Display format:
```
Team shipping streak: 47 consecutive days
Your shipping streak: 32 consecutive days
```

## Test LOC Ratio

**Test LOC ratio** = test file insertions / total insertions

Test files are identified by path matching: `test/`, `spec/`, or `__tests__/`.

Use the `--numstat` output to separate test files from production files per commit.

## Health Score Signals

These are not combined into a single number — they are reported individually:

| Signal | Healthy | Warning |
|--------|---------|---------|
| Test ratio | >30% | <15% |
| Fix ratio | <40% | >50% (ship fast, fix fast pattern — may indicate review gaps) |
| PR sizes | Mostly small/medium | Multiple XL (1500+ LOC) |
| File churn | Distributed | Same files changed 5+ times |
| Session depth | Mostly deep/medium | Mostly micro sessions |

## PR Size Buckets

| Size | LOC changed | Notes |
|------|-------------|-------|
| Small | <100 | Ideal for review |
| Medium | 100-500 | Acceptable |
| Large | 500-1500 | Worth flagging |
| XL | 1500+ | Flag with file counts — should have been split |
