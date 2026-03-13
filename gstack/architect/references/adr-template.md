# Architecture Decision Record Template

Use this format for each decision locked in Step 2. Every ADR must have Status = Decided by the time the specification is finalized.

## Format

```markdown
### ADR-{NNN}: {Decision Title}

- **Status:** Decided | Superseded by ADR-{NNN}
- **Date:** {YYYY-MM-DD}
- **Context:** Why this decision is necessary. What forces are at play. What the eng review identified. One paragraph max.
- **Decision:** The chosen approach in one clear sentence.
- **Alternatives considered:**
  - {Alternative A}: {Why rejected — one sentence}
  - {Alternative B}: {Why rejected — one sentence}
- **Consequences:**
  - Positive: {What this enables}
  - Negative: {What this costs or constrains}
  - Neutral: {What changes without clear positive/negative valence}
```

## Rules

- Every ADR must have Status = Decided. No "TBD", "Pending", or "To be discussed."
- If a decision is superseded later, update Status to "Superseded by ADR-{NNN}" — never delete.
- Context must reference the specific eng review finding or user decision that drove it.
- Alternatives must include at least one rejected option. A decision with no alternatives was not a real decision — it was obvious and does not need an ADR.
- Consequences must be honest. If the decision has no downsides, you have not thought hard enough.
