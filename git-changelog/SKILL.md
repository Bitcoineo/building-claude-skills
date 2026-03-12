---
name: git-changelog
description: Generate formatted changelogs and release notes from git history. Use when user asks to "generate a changelog", "what changed since [version/date]", "summarize recent commits", "prepare release notes", or "draft release notes for [version]". Supports conventional commits, custom date ranges, and multiple output formats. Do NOT use for viewing raw git log, writing commit messages, or setting up git conventions.
---

# Purpose

Generate human-readable changelogs and release notes from git commit history. Parse commits, categorize them by type (features, fixes, breaking changes, etc.), and produce formatted output suitable for release notes, team updates, or CHANGELOG.md files. Suggest semantic version bumps based on the types of changes detected.

# Steps

## 1. Determine the commit range

Check for these range specifiers in order of priority:

1. **Tag-based** -- User specifies a version (e.g., "since v1.0"): resolve with `git tag -l "v1.0*" --sort=-v:refname | head -1`, then use `v1.0..HEAD`
2. **Date-based** -- User specifies a time period (e.g., "this week"): use `git log --after="7 days ago"`
3. **Two-tag range** -- User wants a span (e.g., "from v1.0 to v2.0"): use `git log v1.0..v2.0`
4. **Default** -- No range specified: use `$(git describe --tags --abbrev=0)..HEAD`, or last 30 days if no tags exist

Validate the range before proceeding. Run `git rev-parse --verify <ref>` for each ref. If a ref does not exist, report the error and suggest alternatives.

## 2. Extract commits

Run git log with a structured format:

```
git log --no-merges --format="%H|%h|%aI|%an|%s" <range>
```

Fields: full hash, short hash, ISO date, author name, subject line. The `--no-merges` flag excludes merge commits because they duplicate information already in the feature commits.

For automated parsing and categorization, use the helper script at `scripts/parse_commits.py`:

```
python3 scripts/parse_commits.py [range] --format markdown --categorize
```

## 3. Categorize commits

Group each commit by its conventional commit prefix. For the full specification, consult `references/conventional-commits.md`.

| Prefix | Heading | Semver Impact |
|---|---|---|
| `feat:`, `feature:` | New Features | minor |
| `fix:`, `bugfix:` | Bug Fixes | patch |
| `docs:` | Documentation | patch |
| `refactor:` | Refactoring | patch |
| `test:`, `tests:` | Tests | patch |
| `chore:`, `build:`, `ci:` | Maintenance | patch |
| `perf:` | Performance | patch |
| `style:` | Style | patch |
| `!` suffix or `BREAKING CHANGE` footer | Breaking Changes | **major** |
| No matching prefix | Other Changes | patch |

Strip the type prefix and optional scope from each entry. Capitalize the first letter of the remaining text.

## 4. Determine output format and version suggestion

### Format selection

Analyze the user's request to select the appropriate output format:

- **Markdown** (default): Use when the user asks for a "changelog," "release notes," or any request intended for human reading. Use when writing to a file.
- **JSON**: Use when the user mentions "API," "programmatic," "parse," "JSON," or any indication the output will be consumed by code.
- **Plain text**: Use when the user mentions "terminal," "console," "print," or asks for a simple/minimal format.

If the format cannot be determined from the request, default to Markdown. State the chosen format before producing output: "Generating [format] output because [reason]."

### Semantic version suggestion

After categorizing commits, determine the appropriate version bump:

1. **Major** (X.0.0): Any commit contains a breaking change (`feat!:`, `fix(auth)!:`, or `BREAKING CHANGE:` / `BREAKING-CHANGE:` footer).
2. **Minor** (x.Y.0): No breaking changes exist AND at least one commit has type `feat`.
3. **Patch** (x.y.Z): All commits are non-feature, non-breaking types (`fix`, `chore`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `style`).

Resolve the previous version from the latest git tag. If no tags exist, omit the specific version number but still state the bump type.

Include a brief justification: "Patch bump suggested: 8 fixes, 2 chores, 0 features, 0 breaking changes."

## 5. Generate formatted output

Apply the template from `assets/changelog-template.md`.

### Markdown format

```markdown
## [vX.Y.Z] - YYYY-MM-DD (suggested: [bump type] bump)

### Breaking Changes
- Description of change (short-hash)

### New Features
- Description of feature (short-hash)

### Bug Fixes
- Description of fix (short-hash)
```

Omit any heading with zero entries. Keep Breaking Changes first because they require user action. Include the short hash after each entry for traceability.

### JSON format

```json
{
  "version": "X.Y.Z",
  "date": "YYYY-MM-DD",
  "suggested_bump": "minor",
  "categories": {
    "breaking": [{"hash": "abc1234", "description": "..."}],
    "features": [{"hash": "def5678", "description": "..."}]
  }
}
```

### Plain text format

```
VERSION X.Y.Z (YYYY-MM-DD) - Suggested: minor bump

BREAKING CHANGES
  - Description of change (abc1234)

NEW FEATURES
  - Description of feature (def5678)
```

## 6. Verify completeness

After generating the changelog draft:

1. Count the number of commits returned by `git log` in Step 2.
2. Count the number of commit entries in the formatted output from Step 5.
3. If the counts do not match:
   - Identify which commits are missing by comparing hashes.
   - Add the missing commits to the appropriate category.
   - If a missing commit cannot be categorized, place it under "Other Changes."
4. If the counts match, proceed to Step 7.

Maximum verification iterations: 2. If counts still do not match after 2 attempts, present the output with a note: "Warning: [N] commits could not be included. Run `git log [range]` for the complete list."

## 7. Present for review

Display the formatted changelog. Ask whether to:
- Write it to `CHANGELOG.md` in the repository root
- Prepend it to an existing `CHANGELOG.md` (newest release first)
- Copy it for use elsewhere (e.g., a GitHub release)

# Examples

## Example 1: Changelog since a tag

**Input:** "Generate a changelog since v1.2.0"

**Output:**
```markdown
## [v1.3.0] - 2026-03-12 (suggested: minor bump)

Minor bump suggested: 2 features, 2 fixes, 1 chore, 0 breaking changes.

### New Features
- Add dark mode support for dashboard (a1b2c3d)
- Implement CSV export for reports (d4e5f6a)

### Bug Fixes
- Fix timezone offset in scheduled emails (b7c8d9e)
- Resolve memory leak in WebSocket handler (f0a1b2c)

### Maintenance
- Upgrade dependencies to latest patch versions (e6f7a8b)
```

## Example 2: Recent changes with format detection

**Input:** "What changed this week? Just print it in the terminal."

**Output:**
```
Generating plain text output because you asked for terminal display.

CHANGES THIS WEEK (2026-03-05 to 2026-03-12)
Suggested bump type: patch (1 fix, 1 chore, 0 features, 0 breaking changes)

BUG FIXES
  - Fix pagination off-by-one on search results (d4e5f6a)

MAINTENANCE
  - Update CI pipeline to Node 20 (b7c8d9e)
```

## Example 3: Release notes with breaking changes

**Input:** "Prepare release notes for v2.0, everything since v1.5"

**Output:**
```markdown
## [v2.0.0] - 2026-03-12 (suggested: major bump)

Major bump suggested: 1 breaking change, 2 features, 1 fix, 1 perf improvement.

### Breaking Changes
- Remove deprecated /api/v1 endpoints -- migrate to /api/v2 (c3d4e5f)

### New Features
- Add real-time collaboration via WebSocket (a1b2c3d)
- Implement role-based access control (d4e5f6a)

### Bug Fixes
- Fix race condition in concurrent file uploads (f0a1b2c)

### Performance
- Reduce dashboard load time by 40% via query optimization (c8d9e0f)

### Contributors
- Alice Chen (3 commits)
- Bob Martinez (2 commits)
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

## Verification count mismatch after retries
**Cause:** Some commits may have unusual formatting that prevents categorization, or multi-line subjects confuse the parser.
**Solution:** Place uncategorizable commits under "Other Changes" with their full subject line. Present the output with a warning noting the discrepancy.

# Bundled Resources

- `scripts/parse_commits.py` -- Parse and categorize git commits into structured JSON
- `references/conventional-commits.md` -- Full conventional commit specification and type definitions
- `assets/changelog-template.md` -- Markdown template with placeholder syntax for changelog generation
