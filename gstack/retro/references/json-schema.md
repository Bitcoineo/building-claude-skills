# Retro JSON Snapshot Schema

Save retro snapshots to `.context/retros/<date>-<sequence>.json`.

## File Naming

```bash
mkdir -p .context/retros

# Determine next sequence number for today
today=$(TZ=America/Los_Angeles date +%Y-%m-%d)
existing=$(ls .context/retros/${today}-*.json 2>/dev/null | wc -l | tr -d ' ')
next=$((existing + 1))
# Save as: .context/retros/${today}-${next}.json
```

## Schema

```json
{
  "date": "2026-03-08",
  "window": "7d",
  "metrics": {
    "commits": 47,
    "contributors": 3,
    "prs_merged": 12,
    "insertions": 3200,
    "deletions": 800,
    "net_loc": 2400,
    "test_loc": 1300,
    "test_ratio": 0.41,
    "active_days": 6,
    "sessions": 14,
    "deep_sessions": 5,
    "avg_session_minutes": 42,
    "loc_per_session_hour": 350,
    "feat_pct": 0.40,
    "fix_pct": 0.30,
    "peak_hour": 22,
    "ai_assisted_commits": 32
  },
  "authors": {
    "Garry Tan": {
      "commits": 32,
      "insertions": 2400,
      "deletions": 300,
      "test_ratio": 0.41,
      "top_area": "browse/"
    },
    "Alice": {
      "commits": 12,
      "insertions": 800,
      "deletions": 150,
      "test_ratio": 0.35,
      "top_area": "app/services/"
    }
  },
  "version_range": ["1.16.0.0", "1.16.1.0"],
  "streak_days": 47,
  "tweetable": "Week of Mar 1: 47 commits (3 contributors), 3.2k LOC, 38% tests, 12 PRs, peak: 10pm"
}
```

## Field Descriptions

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date the retro was generated (YYYY-MM-DD, Pacific time) |
| `window` | string | Time window analyzed (e.g., "7d", "24h", "14d", "30d") |
| `metrics` | object | Aggregate metrics for the entire team |
| `authors` | object | Per-author breakdown, keyed by author name |
| `version_range` | array | Two-element array: [earliest version, latest version] in the window |
| `streak_days` | number | Team shipping streak — consecutive days with at least 1 commit |
| `tweetable` | string | One-line summary suitable for sharing |

### metrics fields

| Field | Type | Description |
|-------|------|-------------|
| `commits` | number | Total commits to main in the window |
| `contributors` | number | Distinct commit authors |
| `prs_merged` | number | PRs merged (extracted from commit message #NNN patterns) |
| `insertions` | number | Total lines inserted |
| `deletions` | number | Total lines deleted |
| `net_loc` | number | insertions - deletions |
| `test_loc` | number | Lines inserted in test files (matching test/, spec/, __tests__/) |
| `test_ratio` | number | test_loc / insertions (0.0 to 1.0) |
| `active_days` | number | Distinct days with at least one commit |
| `sessions` | number | Detected work sessions (45-min gap threshold) |
| `deep_sessions` | number | Sessions lasting 50+ minutes |
| `avg_session_minutes` | number | Average session duration in minutes |
| `loc_per_session_hour` | number | Net LOC / active coding hours, rounded to nearest 50 |
| `feat_pct` | number | Fraction of commits with feat: prefix (0.0 to 1.0) |
| `fix_pct` | number | Fraction of commits with fix: prefix (0.0 to 1.0) |
| `peak_hour` | number | Hour of day (0-23, Pacific) with most commits |
| `ai_assisted_commits` | number | Commits with Co-Authored-By AI trailers |

### authors fields (per author)

| Field | Type | Description |
|-------|------|-------------|
| `commits` | number | Commit count for this author |
| `insertions` | number | Lines inserted by this author |
| `deletions` | number | Lines deleted by this author |
| `test_ratio` | number | This author's test LOC ratio |
| `top_area` | string | Top-level directory this author changed most |
