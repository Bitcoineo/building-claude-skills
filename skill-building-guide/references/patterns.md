# Canonical Skill Patterns

Five patterns cover the vast majority of real-world skill architectures. Most production skills combine 2-3 patterns. Understanding them gives you a vocabulary for designing skills and a checklist for spotting enhancement opportunities.

---

## Table of Contents

- [Pattern Selection Decision Tree](#pattern-selection-decision-tree)
- [Pattern 1: Sequential Workflow Orchestration](#pattern-1-sequential-workflow-orchestration)
- [Pattern 2: Multi-MCP Coordination](#pattern-2-multi-mcp-coordination)
- [Pattern 3: Iterative Refinement](#pattern-3-iterative-refinement)
- [Pattern 4: Context-Aware Tool Selection](#pattern-4-context-aware-tool-selection)
- [Pattern 5: Domain-Specific Intelligence](#pattern-5-domain-specific-intelligence)
- [Worked Example: git-changelog](#worked-example-git-changelog)

---

## Pattern Selection Decision Tree

Use this tree when designing a new skill or evaluating whether to add a pattern to an existing one. The tree encodes a bias toward simplicity: at every decision point, the "NO" branch skips the pattern.

```
Start: What does the skill need to do?
  |
  +-- Does it involve multiple steps in order?
  |     YES -> Pattern 1: Sequential Workflow Orchestration
  |             (almost always yes -- this is your foundation)
  |
  +-- Does it require specialized knowledge beyond tool access?
  |     YES -> Pattern 5: Domain-Specific Intelligence
  |             (embed the rules, don't rely on Claude's general knowledge)
  |
  +-- Does it span multiple external services/MCPs?
  |     YES -> Is manual handoff between them a real pain point?
  |             YES -> Pattern 2: Multi-MCP Coordination
  |             NO  -> Skip it. Manual handoff is fine for rare cases.
  |
  +-- Does output quality improve with self-review?
  |     YES -> Is accuracy critical for this use case?
  |             YES -> Pattern 3: Iterative Refinement
  |             NO  -> Skip it. Single-pass is good enough.
  |
  +-- Does the same goal have multiple valid approaches?
        YES -> Do users actually request different approaches?
                YES -> Pattern 4: Context-Aware Tool Selection
                NO  -> Pick the best default and ship it.
```

**Key principle:** A skill that uses all 5 patterns is not better than one that uses 2 patterns well. Each pattern adds complexity, code to maintain, and failure modes to handle. The right number is the minimum needed to serve the user's actual workflow.

---

## Pattern 1: Sequential Workflow Orchestration

### When to Use

A task requires multiple steps in a specific order, where each step depends on the output of the previous one. This is the most common pattern -- almost every skill uses it as its backbone.

### Structure Template

```markdown
# Steps

## 1. [First step name]
[What to do]
[What this step produces -- used by Step 2]
[Validation: confirm X before proceeding]

## 2. [Second step name]
[What to do with output from Step 1]
[What this step produces]
[Validation gate]

## 3. [Third step name]
...

## N. [Final step]
[Present results to user]
[Offer next actions]
```

### Key Techniques

- **Explicit step ordering.** Number the steps. Don't leave execution order to Claude's judgment.
- **Dependency declarations.** State what each step needs from the previous one. "Step 2 uses the commit range resolved in Step 1."
- **Validation gates.** Before proceeding to the next step, verify the current step's output. "Before categorizing, confirm at least one commit was found."
- **Rollback instructions.** Tell Claude what to do when a step fails. "If `git log` returns an error, check whether the range references exist. If not, fall back to the last 20 commits."
- **Single responsibility per step.** Each step does one thing. If a step description needs "AND" in the middle, split it.

### Common Mistakes

- Leaving step order implicit ("do these things" without numbering)
- Missing validation gates between steps -- errors cascade silently
- Steps that are too granular (10+ steps for a simple workflow) or too coarse (2 steps covering 6 distinct operations)
- No error handling -- the skill assumes the happy path

---

## Pattern 2: Multi-MCP Coordination

### When to Use

A workflow spans multiple services, each accessed through a different MCP server, and the output of one service feeds into the next. Only add this pattern when manual handoff between services is a genuine pain point.

### Structure Template

```markdown
# Steps

## Phase 1: [Service A operation]
Use [MCP-A] to [action].
Expected output: [what data this produces]
Validation: [confirm the operation succeeded]

## Phase 2: [Service B operation]
Pass [data from Phase 1] to [MCP-B].
Use [MCP-B] to [action].
Expected output: [what this produces]
Validation: [confirm success]

## Phase 3: [Service C operation]
...

# Error Handling
If [MCP-A] fails: [graceful degradation]
If [MCP-B] fails: [complete what's possible, log warning]
```

### Key Techniques

- **Clear phase separation.** Each MCP interaction is its own phase with defined inputs and outputs. Don't interleave calls to different MCPs in the same step.
- **Data passing between phases.** Explicitly state what flows between MCPs. "The Figma export produces asset URLs. Pass these URLs to the Drive upload step."
- **Validation before next phase.** After each MCP call, verify the result. "Confirm the Drive upload returned a file ID before creating the Linear ticket."
- **Centralized error handling.** When one MCP fails, handle it gracefully. "If Slack is unavailable, still complete the Linear ticket and log a warning."
- **Declare MCP dependencies in frontmatter.** Use the `compatibility` or `metadata` field to list required MCP servers.

### Common Mistakes

- Adding MCP coordination "because you can" -- every MCP adds a failure mode and a configuration requirement
- Interleaving calls to different MCPs in the same step (makes error handling ambiguous)
- No fallback when an MCP is unavailable
- Assuming MCP server configuration (API keys, permissions) is already set up

---

## Pattern 3: Iterative Refinement

### When to Use

Output quality improves with self-review. An initial draft is good, but checking it against criteria and fixing gaps makes it significantly better. Use when accuracy is more important than speed.

### Structure Template

```markdown
# Steps

## 1-N. [Core workflow -- generate initial output]

## N+1. Quality Check
After generating the draft:
1. [Check criterion 1 -- e.g., count items match expected count]
2. [Check criterion 2 -- e.g., all required sections present]
3. [Check criterion 3 -- e.g., no duplicate entries]

If all checks pass, proceed to final step.

## N+2. Fix Identified Issues
For each failed check:
- [Criterion 1 failure]: [specific fix action]
- [Criterion 2 failure]: [specific fix action]

## N+3. Re-validate
Run the quality check again.
Maximum iterations: 2.
If checks still fail after 2 attempts, present output with a warning
noting the remaining issues.

## N+4. Present Final Output
```

### Key Techniques

- **Explicit quality criteria.** Define "good enough" before iterating. "Verify all commits in the range appear in the output" not "improve the output."
- **Programmatic checks over LLM judgment.** When possible, use scripts or counts rather than asking Claude to judge quality. "Count commits in `git log` and count entries in the changelog."
- **Targeted iteration.** Each iteration fixes specific issues identified in the check. Don't regenerate the entire output.
- **Bounded iteration.** Set a maximum (2-3 is typical). Infinite refinement wastes tokens.
- **Transparent degradation.** If iteration cannot fix all issues, say so. "Warning: 3 commits could not be categorized."

### Common Mistakes

- No maximum iteration count (potential infinite loop)
- Vague quality criteria ("make it better" -- Claude doesn't know what to fix)
- Regenerating everything instead of patching specific gaps
- Adding iteration to tasks where single-pass is good enough (over-engineering)

### Cost/Benefit

Iterative refinement costs 30-50% more tokens than single-pass. Use it for high-stakes output (release notes, compliance docs) where errors have consequences. Skip it for quick summaries or exploratory queries.

---

## Pattern 4: Context-Aware Tool Selection

### When to Use

The same goal can be achieved through different tools or approaches, and the right choice depends on the context of the request. Only add this when users actually request different approaches.

### Structure Template

```markdown
# Steps

## 1. Analyze Request Context
Examine the user's request to determine the appropriate [tool/format/approach]:

- **Option A** ([specific signals]): Use when the user mentions [keywords].
  [Why this is the right choice for this context]
- **Option B** ([specific signals]): Use when the user mentions [keywords].
  [Why this is the right choice]
- **Default**: [fallback option when context is ambiguous]

State the chosen option before proceeding:
"Using [Option X] because [reason]."

## 2-N. [Execute using the selected approach]
### If Option A
[specific steps]

### If Option B
[specific steps]
```

### Key Techniques

- **Explicit decision criteria.** Spell out the rules for routing. Don't rely on Claude's intuition -- make the decision tree visible.
- **Signal-based routing.** Map specific words or patterns in the user's request to options. "If the user mentions 'API', 'programmatic', or 'JSON', use JSON format."
- **Always have a default.** Ambiguous requests should produce reasonable output, not an error.
- **Transparency.** Tell the user which path was taken and why. "Generating JSON output because you mentioned 'API.'"

### Common Mistakes

- Adding options nobody uses (over-engineering)
- Relying on Claude's judgment instead of explicit decision rules
- No default path -- skill fails on ambiguous input
- Decision criteria that overlap (multiple options match the same signals)

---

## Pattern 5: Domain-Specific Intelligence

### When to Use

The skill's value comes from embedding specialized knowledge that Claude doesn't have by default -- or has unreliably. This is what makes a skill worth building instead of just writing a prompt.

### Structure Template

```markdown
# [Domain] Rules

## Classification Rules
[Explicit rules for categorizing inputs]
| Input Pattern | Category | Action |
|...            |...       |...     |

## Precedence Rules
When inputs match multiple categories:
1. [Highest priority rule]
2. [Next priority]
3. [Default]

## Domain Vocabulary
| Term | Definition | Skill Behavior |
|...   |...         |...             |

## Validation Rules
Before producing output, verify:
- [Domain constraint 1]
- [Domain constraint 2]
```

### Key Techniques

- **Embed rules in instructions, not in hope.** If the skill depends on knowing that `feat!:` means a breaking change, encode that rule explicitly. Don't assume Claude's training data covers it correctly.
- **Tables for classification.** Claude processes tabular data reliably. Use tables for type mappings, priority rules, and vocabulary definitions.
- **Precedence ordering.** When rules conflict, define which wins. "Breaking changes take precedence over type-based categorization."
- **Domain vocabulary.** Define terms Claude might misinterpret. "In this context, 'scope' means the code module affected, not the project scope."
- **Progressive depth.** Core rules in the body, extended rules and edge cases in references/.

### Common Mistakes

- Assuming Claude knows domain rules from training (it might, inconsistently)
- No precedence ordering when rules conflict
- Domain knowledge buried in prose instead of structured in tables
- Not measuring the delta: if the skill's output is the same as baseline Claude, the domain knowledge isn't deep enough

---

## Worked Example: git-changelog

The git-changelog skill demonstrates how patterns layer in a real skill. Here is the pattern analysis.

### Patterns Used

**Pattern 1: Sequential Workflow Orchestration (backbone)**

The skill defines a 7-step sequential workflow:

```
Step 1: Determine commit range (parse user intent -> resolve git refs)
Step 2: Extract commits (run git log with resolved range)
Step 3: Categorize commits (parse conventional commit types)
Step 4: Determine output format (context-aware selection)
Step 5: Generate formatted output (apply template)
Step 6: Verify completeness (iterative check)
Step 7: Present for review (offer next actions)
```

Each step has explicit dependencies, validation gates, and error handling. This is the foundation everything else builds on.

**Pattern 5: Domain-Specific Intelligence (core value)**

The skill encodes knowledge Claude has unreliably:
- Conventional commit parsing rules (including the `!` position variants)
- Type-to-category mappings with aliases (`feature` -> `feat`, `bugfix` -> `fix`)
- Semantic versioning bump logic (breaking -> major, feat -> minor, everything else -> patch)
- Breaking change detection from both `!` markers and `BREAKING CHANGE:` footers
- Category precedence (breaking > type-based categorization)

This domain knowledge is what creates the measurable delta between with-skill and baseline performance. Without it, Claude produces changelogs that miss edge cases and apply semver rules inconsistently.

**Pattern 3: Iterative Refinement (quality assurance)**

Step 6 adds self-verification:
1. Count commits in git log output
2. Count entries in generated changelog
3. If mismatch: identify missing commits, add to appropriate category
4. Maximum 2 iterations
5. If still mismatched: present with warning

This catches the 2-5% of commits that single-pass generation misses, at a cost of ~30% more tokens. Worth it for release notes; skip for quick summaries.

**Pattern 4: Context-Aware Tool Selection (output adaptation)**

Step 4 routes to different output formats based on context signals:
- "changelog" or "release notes" -> Markdown (default)
- "API" or "programmatic" or "JSON" -> JSON
- "terminal" or "print" or "simple" -> Plain text

The skill states the chosen format and why: "Generating plain text output because you asked for terminal display."

### Pattern NOT Used

**Pattern 2: Multi-MCP Coordination** -- The skill operates entirely on local git history. No external services are needed. MCP coordination could be added (post to Slack, create GitHub Release), but the complexity cost does not justify the value for the core use case.

### Pattern Layering Decisions

The git-changelog skill demonstrates deliberate pattern selection:

| Pattern | Included? | Justification |
|---------|-----------|---------------|
| 1. Sequential Workflow | Yes | Foundation -- the task is inherently multi-step |
| 2. Multi-MCP Coordination | No | Core workflow is local. MCP extensions would be separate skills. |
| 3. Iterative Refinement | Yes | Release notes demand completeness. 2-5% miss rate on single-pass is unacceptable for published changelogs. |
| 4. Context-Aware Selection | Yes | Users genuinely need Markdown, JSON, and plain text formats. Real usage confirmed all three. |
| 5. Domain Intelligence | Yes | Conventional commit parsing, semver rules, and breaking change detection are the skill's core value. |

**Key lesson:** Pattern 2 was explicitly rejected despite being technically feasible. Each pattern must earn its complexity. The question is not "can we add this?" but "does the user actually need this, and is the value worth the added failure modes?"

### Bug Patterns Encountered

During development, the git-changelog skill exposed these pattern-specific bugs:

1. **Pattern 5 bug (BUG-001):** The conventional commit regex handled `type(scope)!:` but not `type!(scope):`. Both positions are valid per the spec. The root cause: the regex was developed from common examples, not from the specification grammar.

2. **Pattern 5 bug (BUG-002):** Version bump justification showed negative "other" count. A `feat!` commit was counted in both "breaking" and "feat" categories, making the subtraction formula produce `-1`. Fix: make categories mutually exclusive before arithmetic.

3. **Pattern 1 bug (BUG-003):** A validation script referenced in the workflow required PyYAML, which isn't in the Python standard library and wasn't documented as a dependency. Fix: document dependencies or use only stdlib.

All three bugs share a common thread: they were exposed by edge cases that mainstream testing missed. The prevention pattern is the same across all three: test against the full spec, not just common usage.
