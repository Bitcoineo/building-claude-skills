# Conventional Commits Reference

A comprehensive reference for the Conventional Commits specification as used by the git-changelog skill.

## Table of Contents

- [Overview](#overview)
- [Commit Message Format](#commit-message-format)
- [Commit Types](#commit-types)
- [Breaking Changes](#breaking-changes)
- [Scopes](#scopes)
- [Examples](#examples)
  - [Good Commit Messages](#good-commit-messages)
  - [Bad Commit Messages](#bad-commit-messages)
- [Type Aliases](#type-aliases)
- [How git-changelog Uses This Specification](#how-git-changelog-uses-this-specification)
- [Semantic Versioning Mapping](#semantic-versioning-mapping)
- [Multi-line Commits and Footers](#multi-line-commits-and-footers)

---

## Overview

Conventional Commits is a specification for adding human- and machine-readable meaning to commit messages. It provides a lightweight convention on top of commit messages, making it easier to write automated tools that parse commit history.

The specification is defined at <https://www.conventionalcommits.org/en/v1.0.0/>.

The git-changelog skill parses commits following this convention to automatically categorize changes, detect breaking changes, and suggest semantic version bumps.

---

## Commit Message Format

Every conventional commit follows this structure:

```
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

**Required parts:**
- `type` -- A noun describing the category of the change
- `description` -- A short summary of the change in imperative mood

**Optional parts:**
- `scope` -- A noun in parentheses describing the section of the codebase affected
- `!` -- Placed after the type/scope to indicate a breaking change
- `body` -- Free-form text providing additional context (separated from description by a blank line)
- `footer` -- One or more `key: value` pairs (e.g., `BREAKING CHANGE: description`)

---

## Commit Types

The following types are recognized by the git-changelog skill. Types are case-insensitive during parsing but conventionally written in lowercase.

| Type | Description | Changelog Heading | Semver Impact |
|------|-------------|-------------------|---------------|
| `feat` | A new feature visible to the end user | New Features | Minor |
| `fix` | A bug fix visible to the end user | Bug Fixes | Patch |
| `docs` | Changes to documentation only | Documentation | Patch |
| `style` | Code style changes (formatting, semicolons, whitespace) -- no logic change | Style | Patch |
| `refactor` | Code restructuring that neither fixes a bug nor adds a feature | Refactoring | Patch |
| `perf` | A change that improves performance | Performance | Patch |
| `test` | Adding or correcting tests | Tests | Patch |
| `build` | Changes to the build system or external dependencies | Maintenance | Patch |
| `ci` | Changes to CI configuration files and scripts | Maintenance | Patch |
| `chore` | Other changes that do not modify src or test files | Maintenance | Patch |
| `revert` | Reverts a previous commit | Reverts | Patch |

### Type Priority in Changelog Output

When generating a changelog, sections appear in this order:

1. Breaking Changes (always first -- requires user action)
2. New Features
3. Bug Fixes
4. Performance
5. Refactoring
6. Documentation
7. Tests
8. Maintenance (combines `build`, `ci`, `chore`)
9. Style
10. Reverts
11. Other Changes (commits that do not match any type)

---

## Breaking Changes

A breaking change indicates that the public API or behavior has changed in a way that requires consumers to update their code. Breaking changes always trigger a **major** version bump in semver.

### Method 1: Exclamation mark after type/scope

Append `!` immediately before the colon:

```
feat!: remove support for Node 14
feat(api)!: change authentication endpoint response format
fix!: rename exported function from `getData` to `fetchData`
```

### Method 2: Footer notation

Include a `BREAKING CHANGE:` or `BREAKING-CHANGE:` footer in the commit body:

```
feat(auth): switch to OAuth 2.0 token format

The authentication tokens now use JWT format instead of opaque strings.
All clients must update their token validation logic.

BREAKING CHANGE: Authentication tokens are now JWTs. Opaque token
validation will no longer work. Update your middleware to use
jwt.verify() instead of token lookup.
```

### Precedence

Both methods are equivalent. If either is present, the commit is marked as a breaking change. The git-changelog skill detects both forms and places the commit under "Breaking Changes" regardless of its original type.

---

## Scopes

Scopes provide additional context about which part of the codebase a commit affects. They appear in parentheses after the type.

### Common scope conventions

| Scope | Meaning |
|-------|---------|
| `api` | Public API endpoints or interfaces |
| `auth` | Authentication and authorization |
| `core` | Core library or framework code |
| `db` | Database schema, queries, or migrations |
| `ui` | User interface components |
| `config` | Configuration files or settings |
| `deps` | Dependency updates |
| `cli` | Command-line interface |

### Scope rules

- Scopes are **optional** -- a commit without a scope is valid
- Scopes are **freeform** -- any noun is acceptable
- Scopes should be **consistent** within a project (use `auth` everywhere, not `auth` in some commits and `authentication` in others)
- Scopes can be **nested** with slashes: `feat(api/users): add pagination`

The git-changelog skill preserves scopes in the output. When a scope is present, the changelog entry is formatted as:

```
- **api:** Change authentication endpoint response format (abc1234)
```

---

## Examples

### Good Commit Messages

**Simple feature:**
```
feat: add dark mode toggle to settings page
```

**Feature with scope:**
```
feat(dashboard): add CSV export button for analytics data
```

**Bug fix with context:**
```
fix(auth): prevent session expiry during active requests

The session timeout was based on the initial login time rather than
the last activity timestamp. Active users were being logged out
unexpectedly after 30 minutes regardless of activity.
```

**Breaking change with explanation:**
```
feat(api)!: return pagination metadata in response headers

Previously, pagination info was nested in the response body under
a `meta` key. It is now returned via Link and X-Total-Count headers,
matching REST conventions.

BREAKING CHANGE: Pagination metadata moved from response body to
headers. Update your client code to read X-Total-Count and Link
headers instead of response.meta.
```

**Performance improvement:**
```
perf(db): add composite index on (user_id, created_at) for timeline queries
```

**Maintenance commit:**
```
chore(deps): upgrade eslint from 8.x to 9.x
```

### Bad Commit Messages

**Too vague:**
```
fix: fix bug
```
Problem: Does not describe what was fixed. Produces an unhelpful changelog entry.

**Not imperative mood:**
```
feat: added new button
```
Problem: Should be "add new button" (imperative), not "added" (past tense).

**Type missing:**
```
update login page styles
```
Problem: No conventional commit prefix. The git-changelog skill will place this under "Other Changes."

**Scope used as type:**
```
auth: fix token refresh logic
```
Problem: `auth` is not a recognized type. Should be `fix(auth): fix token refresh logic`.

**Overly long subject:**
```
feat: add new user onboarding flow with email verification, profile setup, preference selection, and welcome tutorial that guides users through all major features of the application
```
Problem: Subject lines should be under 72 characters. Move details to the body.

---

## Type Aliases

The git-changelog skill recognizes the following aliases and maps them to canonical types:

| Written As | Parsed As | Rationale |
|------------|-----------|-----------|
| `feature` | `feat` | Common longhand variant |
| `bugfix` | `fix` | Common longhand variant |
| `tests` | `test` | Plural form used by some teams |

All other types must match their canonical form exactly.

---

## How git-changelog Uses This Specification

1. **Parsing:** The skill (and `scripts/parse_commits.py`) apply a regex to each commit subject line:
   ```
   ^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]*)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$
   ```

2. **Alias resolution:** The extracted type is lowercased and checked against the alias table. Unknown types map to "other."

3. **Breaking change detection:** The skill checks for the `!` marker in the subject AND scans the body for `BREAKING CHANGE:` or `BREAKING-CHANGE:` footers.

4. **Categorization:** Each commit is placed into its changelog heading. Breaking commits always go to "Breaking Changes" regardless of their original type.

5. **Formatting:** The type prefix and scope are stripped from the subject. The first letter of the remaining text is capitalized. Scopes are rendered in bold before the description.

6. **Version suggestion:** The skill scans all categorized commits and applies semver rules (see below).

---

## Semantic Versioning Mapping

The git-changelog skill uses commit types to suggest the appropriate version bump following [Semantic Versioning 2.0.0](https://semver.org/):

| Condition | Bump | Example |
|-----------|------|---------|
| Any commit has a breaking change | Major | 1.2.3 -> 2.0.0 |
| Any commit has type `feat` (no breaking changes) | Minor | 1.2.3 -> 1.3.0 |
| All commits are `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` | Patch | 1.2.3 -> 1.2.4 |

Breaking changes take absolute precedence. A single breaking change among 50 fix commits still triggers a major bump.

---

## Multi-line Commits and Footers

### Body

The body is separated from the subject by a blank line. It provides additional context that does not fit in the 72-character subject line.

```
fix(parser): handle escaped quotes in CSV fields

The CSV parser was splitting on all comma characters, including those
inside quoted strings. This caused data corruption when importing files
with text fields containing commas.

The fix adds a state machine to track whether the parser is inside a
quoted string before splitting.
```

### Footers

Footers appear after the body, separated by a blank line. Each footer is a `key: value` or `key #value` pair.

```
fix(auth): rate limit login attempts

Refs: #1234
Reviewed-by: Alice
BREAKING CHANGE: The /login endpoint now returns 429 after 5 failed
attempts within 15 minutes.
```

The git-changelog skill specifically scans for `BREAKING CHANGE:` and `BREAKING-CHANGE:` footers. All other footers are ignored during changelog generation but preserved in the raw commit data.
