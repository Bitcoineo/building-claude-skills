---
name: git-changelog
description: >-
  Generate formatted changelogs from git history. Use when user asks to
  "generate a changelog", "summarize recent commits", "prepare release notes",
  "what changed since last release", "review changes between versions",
  "create release notes for v2.0", or "what did we ship this sprint".
  Do NOT use for writing commit messages, rebasing, resolving merge conflicts,
  or general git workflow questions.
---

# Purpose

Generate well-structured changelogs from git commit history. Produces categorized, human-readable summaries suitable for release notes, team updates, or project documentation.

# Steps

## 1. Determine the commit range

Ask the user or infer from context which commits to include. Common patterns:

- **Between tags:** `v1.0.0..v2.0.0` -- for release notes between versions
- **Since last tag:** `$(git describe --tags --abbrev=0)..HEAD` -- for "what's new since last release"
- **Date range:** `--since="2024-01-01" --until="2024-02-01"` -- for sprint/period summaries
- **Last N commits:** `-n 20` -- for quick recent summaries
- **Between branches:** `main..feature-branch` -- for PR-style summaries

If the user doesn't specify, default to: last tag to HEAD. If no tags exist, use the last 20 commits.

## 2. Extract commits

Run the bundled `scripts/extract-commits.sh` script (located in this skill's directory) to get structured commit data. Pass the range determined in Step 1 via `--from` and `--to` flags.

The script outputs JSON with: hash, author, date, subject, body, type, scope, and breaking change flag.

If the script is unavailable or fails, fall back to:
```bash
git log <range> --format="%H|%an|%aI|%s|%b" --no-merges
```

## 3. Categorize commits

Group commits by type using conventional commit prefixes when present. For commits without prefixes, infer the category from the subject line.

**Categories (in display order):**

| Category | Conventional Prefix | Inferred From |
|----------|-------------------|---------------|
| Breaking Changes | `!` suffix or `BREAKING CHANGE:` in body | "remove", "drop", "rename API" |
| Features | `feat:` | "add", "implement", "introduce", "support" |
| Bug Fixes | `fix:` | "fix", "resolve", "patch", "correct", "handle" |
| Performance | `perf:` | "optimize", "speed", "cache", "reduce memory" |
| Documentation | `docs:` | "document", "readme", "jsdoc", "comment" |
| Other Changes | `refactor:`, `chore:`, `style:`, `test:`, `ci:`, `build:` | Everything else |

**Validation gate:** If zero commits are found in the range, stop and tell the user. Do not generate an empty changelog.

## 4. Format the changelog

For format details and examples, consult `references/changelog-formats.md`.

**Default format: Keep a Changelog**

Use this unless the user requests a different format. Structure:

```markdown
# Changelog

## [version or range] - YYYY-MM-DD

### Breaking Changes
- **scope:** description (hash)

### Features
- **scope:** description (hash)

### Bug Fixes
- description (hash)
```

**Rules:**
- Omit empty categories entirely -- do not show "### Features" with no entries
- Use the scope from conventional commits as a bold prefix when available
- Include the short hash (first 7 chars) as a reference
- Write entries in past tense: "Added support for..." not "Add support for..."
- Each entry is one line. Collapse multi-line commit bodies into a single summary
- Sort entries within categories by scope alphabetically, then by date

**Alternative formats** (when user requests):
- **Simple list** -- flat bullet list, no categories
- **Grouped by scope** -- organized by component/module instead of type
- **Verbose** -- includes author, full date, and commit body

## 5. Handle edge cases

- **Merge commits:** Exclude by default (the script uses `--no-merges`). Include only if the user explicitly asks.
- **Squash merges:** Treat as single commits. Check the body for embedded commit lists.
- **Non-conventional commits:** Infer category from subject keywords (Step 3 table). If ambiguous, place in "Other Changes."
- **Monorepo:** If the user specifies a path, add `-- <path>` to the git log command to scope commits.

# Troubleshooting

**Problem:** Script returns empty results but commits exist.
**Cause:** The commit range is inverted (newer..older) or references don't exist.
**Fix:** Verify both refs exist with `git rev-parse`. Ensure the range is older..newer.

**Problem:** All commits land in "Other Changes."
**Cause:** Repository doesn't use conventional commit format.
**Fix:** Rely on keyword inference from the categorization table. Inform the user that adopting conventional commits would improve changelog accuracy.

**Problem:** Breaking changes are missed.
**Cause:** Breaking changes noted only in commit body, not subject line.
**Fix:** The extract script checks both subject (`!` suffix) and body (`BREAKING CHANGE:` token). If using the fallback git log command, grep the body field explicitly.

# Bundled Resources

- `scripts/extract-commits.sh` -- Extracts structured commit data as JSON. Accepts `--from`, `--to`, `--since`, and `--path` parameters.
- `references/changelog-formats.md` -- Output format examples: Keep a Changelog, simple list, grouped by scope, and verbose formats with complete samples.
- `references/conventional-commits.md` -- Quick reference for conventional commit types, scopes, and breaking change notation.
