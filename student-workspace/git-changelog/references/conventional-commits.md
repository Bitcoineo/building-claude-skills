# Conventional Commits Quick Reference

Reference for parsing and categorizing commits that follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Format

```
<type>(<scope>)!: <description>

[optional body]

[optional footer(s)]
```

- **type** -- Required. Lowercase. Determines the changelog category.
- **scope** -- Optional. In parentheses. Identifies the component/module affected.
- **!** -- Optional. Before the colon. Indicates a breaking change.
- **description** -- Required. Imperative mood, lowercase start, no period.

## Type Mapping

| Type | Changelog Category | Description |
|------|-------------------|-------------|
| `feat` | Features | A new feature visible to users |
| `fix` | Bug Fixes | A bug fix visible to users |
| `perf` | Performance | A performance improvement |
| `docs` | Documentation | Documentation-only changes |
| `refactor` | Other Changes | Code change that neither fixes a bug nor adds a feature |
| `test` | Other Changes | Adding or correcting tests |
| `chore` | Other Changes | Maintenance tasks (deps, config, build) |
| `style` | Other Changes | Formatting, whitespace, semicolons (not CSS) |
| `ci` | Other Changes | CI/CD configuration changes |
| `build` | Other Changes | Build system or external dependency changes |
| `revert` | Other Changes | Reverts a previous commit |

## Breaking Changes

A commit is a breaking change if ANY of these are true:

1. The type has a `!` suffix before the colon: `feat!: remove endpoint`
2. The type+scope has a `!` suffix: `feat(api)!: rename User to Account`
3. The footer contains `BREAKING CHANGE: <description>` (note: no hyphen)
4. The footer contains `BREAKING-CHANGE: <description>` (hyphenated variant, also valid)

Breaking changes should ALWAYS appear in a dedicated "Breaking Changes" section at the top of the changelog, regardless of their type prefix.

## Scope Conventions

Common scope patterns seen in practice:

- **Module/package name:** `feat(auth):`, `fix(api):`
- **File or component:** `docs(README):`, `style(header):`
- **Broad area:** `chore(deps):`, `ci(github-actions):`
- **No scope:** `fix: handle null pointer` -- place in category without bold scope prefix

## Keyword Inference for Non-Conventional Commits

When commits don't follow conventional format, use these keyword patterns to infer the category:

| Category | Keywords in Subject |
|----------|-------------------|
| Features | add, implement, introduce, support, create, enable, allow |
| Bug Fixes | fix, resolve, patch, correct, handle, repair, address |
| Performance | optimize, speed, cache, reduce, improve performance, faster |
| Documentation | document, readme, jsdoc, comment, update docs, api reference |
| Breaking | remove, drop, rename, delete, deprecate (+ API/endpoint/interface context) |
| Revert | revert, undo, rollback |

**Important:** Keyword inference is a heuristic. When ambiguous, default to "Other Changes" rather than guessing wrong.
