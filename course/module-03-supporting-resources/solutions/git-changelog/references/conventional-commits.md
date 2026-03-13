# Conventional Commits Reference

## What Are Conventional Commits?

Conventional Commits is a specification for writing standardized commit messages. Every commit message follows a structured format that makes it possible to automatically parse commit history, generate changelogs, and determine semantic version bumps.

The format adds a machine-readable prefix to each commit message, turning free-form text into structured data. This is what allows the git-changelog skill to automatically categorize commits into sections like "Features," "Bug Fixes," and "Breaking Changes" without requiring manual classification.

## The Format

```
type(scope): description

[optional body]

[optional footer(s)]
```

- **type** -- Required. Describes the kind of change (see full list below).
- **scope** -- Optional. A noun describing the section of the codebase affected, enclosed in parentheses.
- **description** -- Required. A short summary of the change in imperative mood.
- **body** -- Optional. A longer explanation of what and why (not how).
- **footer** -- Optional. Metadata like `BREAKING CHANGE:`, `Reviewed-by:`, or issue references.

## Commit Types

| Type | Description | Changelog Heading | Example |
|------|-------------|-------------------|---------|
| `feat` | A new feature for the user | **New Features** | `feat(auth): add SSO login support` |
| `fix` | A bug fix for the user | **Bug Fixes** | `fix(api): correct pagination offset` |
| `docs` | Documentation changes only | **Documentation** | `docs: update API rate limit guide` |
| `style` | Formatting, whitespace, semicolons -- no logic change | **Styles** | `style: apply consistent quote style` |
| `refactor` | Code restructuring without behavior change | **Refactoring** | `refactor(db): extract query builder` |
| `perf` | Performance improvement | **Performance** | `perf: cache user lookup results` |
| `test` | Adding or updating tests | **Tests** | `test(auth): add SSO integration tests` |
| `build` | Build system or dependency changes | **Maintenance** | `build: upgrade webpack to v5` |
| `ci` | CI/CD configuration changes | **Maintenance** | `ci: add Node 20 to test matrix` |
| `chore` | Routine tasks, maintenance | **Maintenance** | `chore: clean up unused imports` |

**Notes:**
- `build`, `ci`, and `chore` all map to the **Maintenance** heading in the changelog. They are distinct types for commit-level precision but share a section because end users rarely need to distinguish between them.
- `style` changes are typically omitted from user-facing changelogs but included in full developer changelogs.

## Breaking Changes

A breaking change is any modification that requires users to update their code, configuration, or workflow. Breaking changes must be called out prominently because they require action from anyone consuming the project.

### Notation

There are two ways to indicate a breaking change:

**Method 1: The `!` suffix**

Add `!` immediately after the type (and scope, if present):

```
feat!: remove support for Node 14
feat(api)!: change response format to JSON:API
```

**Method 2: The `BREAKING CHANGE` footer**

Add a `BREAKING CHANGE:` footer to the commit body:

```
refactor(auth): switch from session cookies to JWT tokens

Migrate the authentication system from server-side sessions to
stateless JWT tokens for better horizontal scaling.

BREAKING CHANGE: The /api/auth/session endpoint has been removed.
Clients must send a Bearer token in the Authorization header instead
of relying on session cookies. See migration guide at docs/jwt-migration.md.
```

**Both methods can be used together** for maximum visibility. The git-changelog skill checks for both: the `!` in the subject line and `BREAKING CHANGE:` in the body. If either is present, the commit appears in the **Breaking Changes** section of the changelog.

Breaking changes always appear first in the generated changelog, regardless of their type. A `fix!:` is still a fix, but it gets listed under Breaking Changes because the breaking nature takes priority over the fix category.

## Scope Conventions

Scopes identify which part of the codebase is affected. They are optional but recommended for projects with multiple distinct areas.

### Common Patterns

**By module or package:**
```
feat(auth): add two-factor authentication
fix(billing): correct tax calculation for EU
docs(sdk): add Python quickstart guide
```

**By layer:**
```
feat(api): add bulk delete endpoint
fix(db): resolve connection pool exhaustion
refactor(ui): extract shared form components
```

**By domain:**
```
feat(payments): support Apple Pay
fix(notifications): deduplicate email sends
perf(search): add index for full-text queries
```

### Scope Guidelines

- Keep scopes short: one or two words, lowercase, no spaces
- Use consistent scopes across the project -- `auth` always means `auth`, not sometimes `authentication`
- If a change affects multiple scopes, use the most significant one or omit the scope entirely
- Don't invent a new scope for every commit. A project should have 5-15 recognized scopes

## Examples

### Well-Formed Commits

```
feat(dashboard): add real-time metrics widget

Add a WebSocket-powered widget that displays request latency,
error rate, and throughput in real time. Updates every 5 seconds.

Closes #234
```
Why this is good: clear type, scoped to a module, descriptive subject, body explains the what and why, references an issue.

```
fix: prevent crash when config file is missing

The app crashed with an unhandled FileNotFoundError on first run
because no default config was created. Now generates a default
config.yaml if none exists.
```
Why this is good: clear type, no scope needed (it's a general fix), subject describes the fix, body explains the root cause and solution.

```
feat(api)!: require authentication for all endpoints

BREAKING CHANGE: All API endpoints now require a valid Bearer token.
Previously, /api/health and /api/version were public. Clients must
update their requests to include the Authorization header.
```
Why this is good: uses both `!` and `BREAKING CHANGE:` footer, clearly explains what changes for consumers.

### Poorly-Formed Commits

```
updated stuff
```
Problems: no type, no description of what changed, no context whatsoever. The changelog skill would classify this as "other" and include it under Other Changes with the unhelpful subject "updated stuff."

```
feat: things
```
Problems: technically valid conventional commit format, but the subject is meaningless. "things" tells neither the changelog reader nor the developer what actually changed.

```
BUGFIX - fixed the login page issue when users click the button too fast
```
Problems: wrong format ("BUGFIX -" instead of "fix:"), overly verbose subject. Should be: `fix(auth): debounce login button to prevent duplicate submissions`

```
feat(authentication-service-module): implemented
```
Problems: scope is too long (should be `auth`), subject is too terse ("implemented" what?), past tense instead of imperative mood.

## How git-changelog Uses This Information

The git-changelog skill uses conventional commit parsing in two places:

1. **Automatic categorization.** The `scripts/parse_commits.py` script parses each commit's subject line against the conventional commit format. It extracts the type, scope, and description, then assigns each commit to a changelog section based on the type-to-heading mapping in the table above.

2. **Breaking change detection.** The script checks both the `!` suffix in the subject and the `BREAKING CHANGE:` footer in the body. Any commit flagged as breaking is promoted to the Breaking Changes section at the top of the changelog, regardless of its type.

3. **Fallback handling.** When a commit doesn't follow conventional format, the script classifies it as type "other" with a null scope. The changelog skill groups these under "Other Changes." If the majority of commits are "other," the skill suggests the team adopt conventional commits and falls back to keyword-based heuristics (e.g., "add" = feature, "fix" = bug fix).
