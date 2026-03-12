---
name: git-changelog
description: >-
  Generate formatted changelogs and release notes from git history.
  Use when user asks to "generate a changelog", "what changed since
  [version/date]", "summarize recent commits", "prepare release notes",
  or "draft release notes for [version]". Supports conventional commits,
  custom date ranges, and multiple output formats.
---

# Purpose

Generate human-readable changelogs and release notes from git commit history. Parse commits, categorize them by type (features, fixes, chores, etc.), and produce formatted markdown suitable for release notes, team updates, or CHANGELOG.md files.

# Steps

## 1. Determine the commit range

Check for these range specifiers in order of priority:

1. **Tag-based** -- User specifies a version (e.g., "since v1.0"): resolve with `git tag -l "v1.0*" --sort=-v:refname | head -1`, then use `v1.0..HEAD`
2. **Date-based** -- User specifies a time period (e.g., "this week"): use `git log --after="7 days ago"`
3. **Two-tag range** -- User wants a span (e.g., "from v1.0 to v2.0"): use `git log v1.0..v2.0`
4. **Default** -- No range specified: use `<latest-tag>..HEAD`, or last 30 days if no tags exist

## 2. Extract commits

Run git log with a structured format:

```
git log --no-merges --format="%H|%h|%aI|%an|%s" <range>
```

Fields: full hash, short hash, ISO date, author name, subject line. The `--no-merges` flag excludes merge commits because they duplicate information already in the feature commits.

## 3. Categorize commits

Group each commit by its subject line prefix. For the full specification, consult `references/conventional-commits.md`.

| Prefix | Heading |
|---|---|
| `feat:`, `feature:` | New Features |
| `fix:`, `bugfix:` | Bug Fixes |
| `docs:` | Documentation |
| `refactor:` | Refactoring |
| `test:`, `tests:` | Tests |
| `chore:`, `build:`, `ci:` | Maintenance |
| `perf:` | Performance |
| `breaking:` or `BREAKING CHANGE` | Breaking Changes |
| No matching prefix | Other Changes |

Strip the type prefix from the entry. Capitalize the first letter of the remaining text.

For automated parsing and categorization, use the helper script at `scripts/parse_commits.py`.

## 4. Generate formatted output

Apply the template from `assets/changelog-template.md`:

```markdown
# Changelog

## [vX.Y.Z] - YYYY-MM-DD

### Breaking Changes
- Description of change (short-hash)

### New Features
- Description of feature (short-hash)

### Bug Fixes
- Description of fix (short-hash)
```

Omit any heading with zero entries. Keep Breaking Changes first because they require user action. Include the short hash after each entry for traceability.

## 5. Present for review

Display the formatted changelog. Ask whether to:
- Write it to `CHANGELOG.md` in the repository root
- Prepend it to an existing `CHANGELOG.md` (newest release first)
- Copy it for use elsewhere (e.g., a GitHub release)

# Examples

## Example 1: Changelog since a tag

**Input:** "Generate a changelog since v1.2.0"

**Output:**
```markdown
# Changelog

## [v1.3.0] - 2024-03-08

### New Features
- Add dark mode support for dashboard (a1b2c3d)
- Implement CSV export for reports (d4e5f6a)

### Bug Fixes
- Fix timezone offset in scheduled emails (b7c8d9e)
- Resolve memory leak in WebSocket handler (f0a1b2c)

### Maintenance
- Upgrade dependencies to latest patch versions (e6f7a8b)
```

## Example 2: Recent changes by date

**Input:** "What changed this week?"

**Output:**
```markdown
# Changes This Week (2024-03-01 to 2024-03-08)

### New Features
- Add bulk delete endpoint for archived items (a1b2c3d)

### Bug Fixes
- Fix pagination off-by-one on search results (d4e5f6a)
- Correct currency formatting for JPY (b7c8d9e)
```

## Example 3: Release notes between versions

**Input:** "Prepare release notes for v2.0, everything since v1.5"

**Output:**
```markdown
# Release Notes

## [v2.0.0] - 2024-03-08

### Breaking Changes
- Remove deprecated /api/v1 endpoints -- migrate to /api/v2 (c3d4e5f)

### New Features
- Add real-time collaboration via WebSocket (a1b2c3d)
- Implement role-based access control (d4e5f6a)

### Bug Fixes
- Fix race condition in concurrent file uploads (f0a1b2c)

### Performance
- Reduce dashboard load time by 40% via query optimization (c8d9e0f)
```

# Troubleshooting

## No tags found
**Cause:** Repository has no version tags; tag-based ranges fail with `fatal: ambiguous argument`.
**Solution:** Fall back to date-based ranges (default: last 30 days). Suggest the user create a tag: `git tag -a v0.1.0 -m "Initial release"`.

## Shallow clone -- incomplete history
**Cause:** `git rev-parse --is-shallow-repository` returns `true`. CI environments often fetch limited history.
**Solution:** Warn the user the changelog may be incomplete. Suggest `git fetch --unshallow`. If not feasible, note the limitation in the output header.

## Empty commit range
**Cause:** The range contains no commits (tag already at HEAD, or date range too narrow).
**Solution:** Report that no commits were found. Suggest widening the range or checking that the tag/date is correct.

## Non-conventional commit messages
**Cause:** Repository does not use conventional commit prefixes; everything lands in "Other Changes."
**Solution:** Fall back to keyword heuristics: "add/implement" = features, "fix/resolve" = bug fixes, "update/upgrade" = maintenance, "remove/delete" = removals. Inform the user and suggest adopting conventional commits per `references/conventional-commits.md`.
