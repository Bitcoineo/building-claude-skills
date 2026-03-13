# Changelog Output Formats

Use this reference when formatting changelog output. The default format is **Keep a Changelog**. Switch to an alternative only when the user explicitly requests it.

---

## Format 1: Keep a Changelog (Default)

Based on [keepachangelog.com](https://keepachangelog.com). Best for release notes and public-facing changelogs.

```markdown
# Changelog

## [v2.1.0] - 2024-03-15

### Breaking Changes
- **auth:** Removed legacy session token storage in favor of JWT-based authentication (a1b2c3d)

### Features
- **api:** Added batch endpoint for bulk user operations (d4e5f6a)
- **dashboard:** Added real-time notification panel with WebSocket support (b7c8d9e)

### Bug Fixes
- **auth:** Fixed race condition in token refresh that caused intermittent 401 errors (f0a1b2c)
- Fixed crash when uploading files larger than 100MB (c3d4e5f)

### Performance
- **database:** Optimized user search query, reducing p95 latency from 800ms to 120ms (a6b7c8d)

### Documentation
- Updated API reference with new batch endpoint examples (d9e0f1a)
```

**Rules for this format:**
- Version header uses brackets: `[v2.1.0]`
- Date in ISO 8601: `YYYY-MM-DD`
- Categories appear in order: Breaking Changes, Features, Bug Fixes, Performance, Documentation, Other Changes
- Omit empty categories entirely
- Bold scope prefix when available: `**scope:**`
- Short hash in parentheses at end of each entry
- Past tense for descriptions

---

## Format 2: Simple List

Flat bullet list with no categories. Best for quick summaries, Slack updates, or when the commit history is small.

```markdown
# Changes since v2.0.0

- Added batch endpoint for bulk user operations (d4e5f6a)
- Added real-time notification panel (b7c8d9e)
- Fixed race condition in token refresh (f0a1b2c)
- Fixed crash on large file uploads (c3d4e5f)
- Optimized user search query (a6b7c8d)
- Removed legacy session token storage (a1b2c3d) **BREAKING**
```

**Rules for this format:**
- Single flat list, sorted by date (newest first)
- Append `**BREAKING**` tag to breaking changes
- No category headings
- Keep each entry to one line

---

## Format 3: Grouped by Scope

Organized by component/module instead of change type. Best for monorepos or when the audience cares about which part of the system changed.

```markdown
# Changelog - v2.1.0

## auth
- **BREAKING:** Removed legacy session token storage (a1b2c3d)
- Fixed race condition in token refresh (f0a1b2c)

## api
- Added batch endpoint for bulk user operations (d4e5f6a)

## dashboard
- Added real-time notification panel (b7c8d9e)

## database
- Optimized user search query (a6b7c8d)

## Uncategorized
- Fixed crash on large file uploads (c3d4e5f)
- Updated API reference docs (d9e0f1a)
```

**Rules for this format:**
- Group by scope extracted from conventional commits or inferred from file paths
- Within each scope, sort: breaking changes first, then features, then fixes
- Commits without a clear scope go in "Uncategorized"
- Use `**BREAKING:**` prefix for breaking changes

---

## Format 4: Verbose

Full detail including author, date, and commit body. Best for internal engineering reviews or audit trails.

```markdown
# Detailed Changelog: v2.0.0 → v2.1.0

---

### feat(api): Added batch endpoint for bulk user operations
- **Commit:** d4e5f6a
- **Author:** Jane Smith
- **Date:** 2024-03-14

Implements POST /api/v2/users/batch for creating, updating, and deleting
users in a single request. Supports up to 1000 operations per call with
transactional rollback on failure.

---

### fix(auth): Fixed race condition in token refresh
- **Commit:** f0a1b2c
- **Author:** John Doe
- **Date:** 2024-03-12

The refresh token endpoint could return a new access token while the old
one was still being validated by a concurrent request, causing the
concurrent request to fail with 401.

---
```

**Rules for this format:**
- Full heading per commit using the original subject
- Metadata block with commit hash, author, and date
- Include the full commit body below the metadata
- Horizontal rules between entries
- Sort by date, newest first
