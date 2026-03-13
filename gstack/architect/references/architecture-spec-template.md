# Architecture Specification Template

Use this template when compiling the full specification in Step 9. Fill every section. If a section does not apply, state why and move on.

## Format

```markdown
# Architecture Specification: {FEATURE NAME}

| Field | Value |
|-------|-------|
| **Date** | {DATE} |
| **Author** | {USER} + Claude |
| **Status** | Draft / Approved |
| **Eng Review** | {link or "see TODOS.md"} |
| **Scope** | {one-line summary} |

## Architecture Decision Records

### ADR-001: {Decision Title}
- **Status:** Decided
- **Context:** {Why this decision needed making}
- **Decision:** {What was decided}
- **Alternatives considered:** {What was rejected and why}
- **Consequences:** {What follows from this decision}

(Repeat for each ADR)

## Data Model

{ASCII relationship diagram}

### {ModelName}
| Field | Type | Constraints | Index? | Notes |
|-------|------|-------------|--------|-------|

### Migrations (ordered)
1. {migration description}
2. {migration description}

## API / Interface Contracts

### {Endpoint or Method}
- **Signature:** {method signature or HTTP method + path}
- **Auth:** {requirements}
- **Request:** {shape}
- **Response:** {shape}
- **Errors:** {error responses}

## Component Structure

{ASCII file tree with [NEW]/[MOD] tags and responsibilities}

**Total files:** {N} ({new} new, {mod} modified)

## Implementation Sequence

| Step | Files | Build | Test | Depends on |
|------|-------|-------|------|------------|

## Error Handling Patterns

| Codepath | Failure Mode | Exception | Strategy | User Sees | Logged? |
|----------|-------------|-----------|----------|-----------|---------|

## Edge Case Guards

| Location | Guard | Handles |
|----------|-------|---------|

## Observability (if applicable)

### Logging
### Metrics
### Alerts

## NOT in Scope (carried from eng review + any additions)

- {item}: {rationale}

## Unresolved Decisions

None. All decisions locked in ADRs above.
```
