# Module 7: Advanced Patterns

**Time estimate:** 60-90 minutes
**Prerequisites:** Completed Modules 1-6 (a fully tested and optimized git-changelog skill with evals and an optimized description)
**Outcome:** A pattern analysis of your git-changelog skill, identification of enhancement opportunities, and one implemented pattern enhancement validated by your eval suite

---

## Learning Objectives

By the end of this module, you will be able to:

- Identify the 5 canonical skill patterns from Anthropic's guide and explain when each applies
- Classify which patterns a given skill currently uses
- Evaluate the tradeoff between complexity added and value gained when layering patterns
- Implement a pattern enhancement and validate it with evals
- Use a decision tree to select appropriate patterns for new skills

---

## Theory

Anthropic's skill design guide identifies 5 canonical patterns that cover the vast majority of real-world skill architectures. Most production skills combine two or three of these patterns. Understanding them gives you a vocabulary for designing skills and a checklist for spotting enhancement opportunities.

The patterns are not mutually exclusive. A well-designed skill often uses Sequential Workflow Orchestration as its backbone and layers on one or two other patterns where they add value. The key is knowing when a pattern earns its complexity.

---

### Pattern 1: Sequential Workflow Orchestration

**Use when:** A task requires multiple steps in a specific order, where each step depends on the output of the previous one.

**Example from the guide:** Onboard New Customer

```
Create Account → Setup Payment → Create Subscription → Send Welcome Email
```

Each step depends on the previous step's output: you can't set up payment without an account ID, you can't create a subscription without a payment method, and you can't send a welcome email without a subscription confirmation.

**Key techniques:**

- **Explicit step ordering.** Number the steps. Don't leave the execution order to Claude's judgment -- specify it. "Step 1: Determine the commit range. Step 2: Extract commits. Step 3: Categorize by type."
- **Dependencies between steps.** State what each step needs from the previous one. "Step 2 uses the commit range from Step 1 to run `git log`."
- **Validation at each stage.** Before proceeding to the next step, verify the current step's output. "Before categorizing, confirm at least one commit was found. If zero commits, stop and report an empty range."
- **Rollback instructions for failures.** Tell Claude what to do when a step fails. "If `git log` returns an error, check whether the range references exist. If not, fall back to the last 20 commits."

**How this applies to git-changelog:**

Your git-changelog skill IS this pattern. The 5-step workflow you built in Module 2 is a sequential orchestration:

```
Step 1: Determine range    (parse user intent → resolve to git refs)
         │
Step 2: Extract commits    (run git log with the resolved range)
         │
Step 3: Categorize          (parse conventional commit types)
         │
Step 4: Format output       (assemble into markdown sections)
         │
Step 5: Present              (return the formatted changelog)
```

If your SKILL.md already has this structure with clear step numbering, dependency declarations, and validation checks, Pattern 1 is covered. If it doesn't, that's a sign your workflow instructions need tightening.

---

### Pattern 2: Multi-MCP Coordination

**Use when:** A workflow spans multiple services, each accessed through a different MCP server, and the output of one service feeds into the next.

**Example from the guide:** Design-to-Development Handoff

```
Figma MCP         →  Drive MCP       →  Linear MCP        →  Slack MCP
(export assets)      (upload specs)      (create tickets)      (notify team)
```

The Figma export produces design assets. Those assets are uploaded to Drive, producing URLs. The URLs are attached to Linear tickets. The ticket IDs are sent to Slack as a notification.

**Key techniques:**

- **Clear phase separation.** Each MCP interaction is its own phase with defined inputs and outputs. Don't interleave calls to different MCPs in the same step.
- **Data passing between MCPs.** Explicitly state what data flows between phases. "The Figma export produces asset URLs. Pass these URLs to the Drive upload step."
- **Validation before moving to next phase.** After each MCP call, verify the result before proceeding. "Confirm the Drive upload returned a file ID before creating the Linear ticket."
- **Centralized error handling.** When one MCP fails, the skill should handle it gracefully rather than crashing the entire workflow. "If Slack is unavailable, still complete the Linear ticket and log a warning."

**How this applies to git-changelog:**

The basic git-changelog skill uses only local git commands -- no MCP coordination needed. But Multi-MCP Coordination becomes relevant when you want to extend the skill beyond local output:

```
git-changelog skill (generate changelog)
         │
         ├──→ Slack MCP (post changelog to #releases channel)
         ├──→ GitHub MCP (create a GitHub Release with the changelog body)
         └──→ Linear MCP (update the sprint summary with a changelog link)
```

Each extension adds a phase after the core changelog generation. The key decision is whether the added integration justifies the complexity and the additional failure modes.

---

### Pattern 3: Iterative Refinement

**Use when:** Output quality improves with iteration -- an initial draft is good but can be made better through self-review and correction.

**Example from the guide:** Report Generation

```
Initial Draft → Quality Check → Refinement Loop → Finalization
```

The first draft captures the structure and content. A quality check identifies gaps -- missing data, unclear phrasing, inconsistent formatting. The refinement loop addresses each gap. Finalization applies a final consistency pass.

**Key techniques:**

- **Explicit quality criteria.** Define what "good enough" means before iterating. Don't say "improve the output" -- say "verify all commits in the range appear in the output, each commit is categorized, and no category is empty."
- **Iterative improvement.** Each iteration targets specific deficiencies identified in the quality check. Don't re-do the entire output -- fix what's wrong.
- **Validation scripts.** When possible, use programmatic checks rather than LLM judgment. "Count the commits in `git log` output and count the commits in the changelog. If the numbers don't match, identify which commits are missing."
- **Know when to stop iterating.** Set a maximum iteration count (2-3 is typical) and a "good enough" threshold. Infinite refinement wastes tokens without improving quality.

**How this applies to git-changelog:**

The current git-changelog skill generates output in a single pass. Adding iterative refinement means the skill checks its own work:

```
Step 1-4: Generate draft changelog (existing workflow)
         │
Step 5:   Quality check
         ├── Are all commits from the range present in the output?
         ├── Is every commit assigned to exactly one category?
         ├── Are there any duplicate entries?
         └── Does the formatting match the template?
         │
Step 6:   If any check fails, fix the specific issue
         │
Step 7:   Re-validate (max 2 iterations)
         │
Step 8:   Finalize and present
```

The tradeoff is clear: iterative refinement catches errors that a single pass misses, but it costs additional tokens and time. For a 50-commit changelog, the single-pass version might miss 2-3 commits. The iterative version catches them at the cost of roughly 30-50% more tokens.

---

### Pattern 4: Context-Aware Tool Selection

**Use when:** The same goal can be achieved through different tools or approaches, and the right choice depends on the context of the request.

**Example from the guide:** Smart File Storage

```
Check file type and size
         │
         ├── Image > 10MB    → Cloud storage
         ├── Document < 1MB  → Notion page
         ├── Code file       → GitHub repository
         └── Default          → Local storage
```

The skill examines the input context (file type, size, purpose) and routes to the appropriate tool. The user doesn't need to know which storage backend is used -- the skill makes the decision.

**Key techniques:**

- **Clear decision criteria.** Spell out the rules for choosing between tools. Don't rely on Claude's judgment for routing decisions -- make them explicit. "If the user is writing to a file, use Markdown. If the user is piping to another command, use plain text. If the user asks for programmatic output, use JSON."
- **Fallback options.** Always have a default path. "If the output context cannot be determined, default to Markdown."
- **Transparency about choices.** Tell the user which path was taken and why. "Generating JSON output because you mentioned 'API' in your request."

**How this applies to git-changelog:**

The current skill always outputs Markdown. Context-aware selection would let the skill adapt its output format:

```
Analyze user request
         │
         ├── "...for the README"         → Markdown with headers
         ├── "...for the API response"   → JSON with structured fields
         ├── "...in the terminal"        → Plain text, no markup
         ├── "...for the release page"   → GitHub-flavored Markdown
         └── Default                      → Markdown
```

The decision criteria should be based on explicit signals in the user's request, not guesses. If the user says "generate a changelog," default to Markdown. If they say "I need this as JSON for our build script," switch to JSON.

---

### Pattern 5: Domain-Specific Intelligence

**Use when:** The skill's value comes not just from orchestrating tools, but from embedding specialized knowledge that Claude doesn't have by default.

**Example from the guide:** Financial Compliance

```
Receive transaction
         │
         ├── Compliance check (amount thresholds, regulatory flags, counterparty screening)
         │        │
         │        ├── Pass → Process transaction
         │        └── Fail → Flag for review, generate audit trail
         │
         └── Document everything regardless of outcome
```

The skill's value isn't in calling APIs -- it's in knowing the compliance rules. Which thresholds trigger review? Which counterparties are flagged? What documentation is required? This domain knowledge is the skill's core contribution.

**Key techniques:**

- **Domain expertise embedded in logic.** The skill's instructions encode specialized knowledge that Claude would otherwise lack or get wrong. "A commit message starting with `feat!:` or containing `BREAKING CHANGE:` in the footer indicates a breaking change."
- **Compliance before action.** Domain rules are checked before producing output, not after. "Before categorizing a commit, verify it follows the conventional commit format. If it doesn't, classify it as 'Other' rather than guessing."
- **Comprehensive documentation.** The skill produces output that meets domain standards without the user needing to specify them. "Always include the full conventional commit type (feat, fix, chore, etc.) rather than abbreviations."
- **Clear governance.** When domain rules conflict, the skill has a defined resolution order. "If a commit message contains both `feat` and `fix`, categorize based on the prefix type, not the body content."

**How this applies to git-changelog:**

Domain-specific intelligence is arguably what makes the git-changelog skill valuable in the first place. Without the skill, Claude might produce a changelog but wouldn't know:

- **Conventional commit parsing rules.** The exact syntax for `feat:`, `fix:`, `chore:`, `feat!:`, `BREAKING CHANGE` footers. Claude has general knowledge of conventional commits, but the skill encodes the precise parsing rules your project follows.
- **Breaking change treatment.** Breaking changes need special visual treatment (separate section, warning markers) and have semantic versioning implications. The skill knows to surface them prominently.
- **Semver implications.** If all commits since the last release are `fix:`, suggest a patch bump. If any are `feat:`, suggest minor. If any are breaking, suggest major. This is domain logic that the skill provides -- Claude wouldn't apply it consistently without explicit instructions.
- **Project-specific conventions.** Your team might use `perf:` for performance improvements or `dx:` for developer experience changes. The skill can encode these custom types and their categorization rules.

The deeper the domain knowledge embedded in the skill, the larger the gap between with-skill and baseline performance.

---

## Exercises

### Exercise 7.1: Pattern Classification

**Goal:** Analyze your git-changelog skill through the lens of the 5 canonical patterns. Identify what it already uses, what could enhance it, and the tradeoffs involved.

**Step 1: Classify the current skill.**

Open your SKILL.md from `student-workspace/git-changelog/SKILL.md` and map each section to a pattern:

```
## Pattern Classification: git-changelog

### Currently Used Patterns

Pattern 1 (Sequential Workflow Orchestration): [YES/NO]
  Evidence: [cite specific sections of your SKILL.md that demonstrate this pattern]
  Completeness: [does your workflow have explicit ordering, dependencies, validation,
                  and rollback? or is it missing some of these?]

Pattern 5 (Domain-Specific Intelligence): [YES/NO]
  Evidence: [cite where your skill encodes domain knowledge -- conventional commit
             parsing, categorization rules, formatting standards]
  Completeness: [how deep is the domain knowledge? surface-level or comprehensive?]
```

Your skill should use Pattern 1 (sequential workflow) as its backbone and Pattern 5 (domain intelligence) for its commit parsing and categorization logic. If it doesn't clearly use both, note what's missing.

**Step 2: Evaluate candidate enhancements.**

For each of the remaining patterns, assess whether it would add value to git-changelog:

```
### Candidate Enhancement Patterns

Pattern 2 (Multi-MCP Coordination): [CANDIDATE / NOT APPLICABLE]
  What it would add: [describe the enhancement]
  Complexity cost: [what new failure modes, dependencies, or configuration
                     does this introduce?]
  Value gained: [what does the user get that they don't have now?]
  Verdict: [WORTH IT / NOT WORTH IT / MAYBE LATER]

Pattern 3 (Iterative Refinement): [CANDIDATE / NOT APPLICABLE]
  What it would add: [describe the enhancement]
  Complexity cost: [additional tokens, time, potential for infinite loops]
  Value gained: [what errors does this catch that single-pass misses?]
  Verdict: [WORTH IT / NOT WORTH IT / MAYBE LATER]

Pattern 4 (Context-Aware Tool Selection): [CANDIDATE / NOT APPLICABLE]
  What it would add: [describe the enhancement]
  Complexity cost: [format detection logic, multiple output templates]
  Value gained: [does the user actually need multiple formats?]
  Verdict: [WORTH IT / NOT WORTH IT / MAYBE LATER]
```

**Step 3: Rank the candidates.**

Order the candidate patterns by value-to-complexity ratio. The best enhancement is the one that adds the most user value with the least additional complexity.

```
### Pattern Enhancement Ranking

1. [Pattern _]: [one sentence justification]
2. [Pattern _]: [one sentence justification]
3. [Pattern _]: [one sentence justification]
```

Save your analysis to `student-workspace/pattern-analysis.md`.

---

### Exercise 7.2: Pattern Enhancement

**Goal:** Choose one additional pattern to implement in your git-changelog skill. Integrate it, then re-run your evals to measure the impact.

Choose **one** of the following options. Each corresponds to a different pattern.

---

#### Option A: Iterative Refinement (Pattern 3)

**What you're adding:** A self-verification step where the skill checks that all commits in the range appear in the output, and fixes any gaps.

**Step 1: Add a verification step to your SKILL.md.**

After the formatting step in your workflow, add a verification phase:

```markdown
## Step 5: Verify Completeness

After generating the changelog draft:

1. Count the number of commits returned by `git log` in Step 2.
2. Count the number of commit entries in the formatted output from Step 4.
3. If the counts do not match:
   - Identify which commits are missing by comparing hashes.
   - Add the missing commits to the appropriate category.
   - If a missing commit cannot be categorized, place it under "Other Changes."
4. If the counts match, proceed to Step 6.

Maximum verification iterations: 2. If counts still do not match after
2 attempts, present the output with a note: "Warning: [N] commits could
not be included. Run `git log [range]` for the complete list."
```

**Step 2: Add a new eval to test verification.**

Add this test case to your `evals.json`:

```json
{
  "id": "verification-completeness",
  "prompt": "Generate a complete changelog since the last tag. Make sure every commit is included.",
  "expected_output": "A changelog that accounts for every commit in the range, with a completeness verification.",
  "expectations": [
    "The number of commits listed in the changelog matches the total number of commits in the git range",
    "No commits from the range are missing from the output",
    "If any commits could not be categorized, they appear under an 'Other Changes' or similar catch-all section"
  ]
}
```

**Step 3: Run evals and compare.**

Run your full eval suite (original 5 test cases + the new verification test). Compare results:

```
## Enhancement Results: Iterative Refinement

### Before Enhancement
- Pass rate: __/15 assertions (__%)
- Mean tokens: ___
- Mean duration: ___s

### After Enhancement
- Pass rate: __/18 assertions (__%)  [15 original + 3 new]
- Mean tokens: ___
- Mean duration: ___s

### Analysis
- Did existing test cases regress? [YES/NO — list any regressions]
- Did the new verification assertions pass? [YES/NO — explain failures]
- Token cost increase: __% [is the verification step worth the extra tokens?]
- Quality improvement: [describe any cases where verification caught a real error]
```

---

#### Option B: Context-Aware Tool Selection (Pattern 4)

**What you're adding:** Output format detection -- the skill chooses Markdown, JSON, or plain text based on the user's request context.

**Step 1: Add format detection logic to your SKILL.md.**

Before the formatting step in your workflow, add a format selection phase:

```markdown
## Step 4: Determine Output Format

Analyze the user's request to determine the appropriate output format:

- **Markdown** (default): Use when the user asks for a "changelog," "release notes,"
  or any request intended for human reading. Use when writing to a file.
- **JSON**: Use when the user mentions "API," "programmatic," "parse," "JSON,"
  or any indication the output will be consumed by code.
- **Plain text**: Use when the user mentions "terminal," "console," "print,"
  or asks for a simple/minimal format.

If the format cannot be determined from the request, default to Markdown.

State the chosen format before producing output: "Generating [format] output
because [reason]."

### Markdown format
- Use `##` headers for version, `###` for categories
- Use `-` bullet points for commit entries
- Include commit hashes as inline code: `abc1234`

### JSON format
- Top-level object with `version`, `date`, `categories` fields
- Each category contains an array of commit objects
- Each commit object has `hash`, `type`, `scope`, `description`, `breaking` fields

### Plain text format
- No markup characters
- Use ALL CAPS for section headers
- Use simple indentation (2 spaces) for commit entries
- Separate sections with blank lines
```

**Step 2: Add new evals to test format detection.**

Add these test cases to your `evals.json`:

```json
{
  "id": "format-json",
  "prompt": "Generate a changelog since the last tag as JSON for our build script",
  "expected_output": "A changelog in valid JSON format with structured fields for version, categories, and commits.",
  "expectations": [
    "The output is valid JSON (parseable, with curly braces and proper syntax)",
    "The JSON contains a top-level version or release field",
    "Individual commits are represented as objects with at least a hash and description field"
  ]
},
{
  "id": "format-plain-text",
  "prompt": "Print a quick summary of recent changes for the terminal",
  "expected_output": "A plain text changelog with no markdown formatting, suitable for terminal display.",
  "expectations": [
    "The output does not contain markdown syntax (no #, **, or ` characters used for formatting)",
    "Section headers are distinguishable from content (e.g., ALL CAPS or underlined)",
    "The output is readable in a monospace terminal without rendering"
  ]
}
```

**Step 3: Run evals and compare.**

Run your full eval suite (original 5 test cases + the 2 new format tests). Compare results:

```
## Enhancement Results: Context-Aware Tool Selection

### Before Enhancement
- Pass rate: __/15 assertions (__%)
- Mean tokens: ___

### After Enhancement
- Pass rate: __/21 assertions (__%)  [15 original + 6 new]
- Mean tokens: ___

### Analysis
- Did existing test cases regress? [YES/NO — list any regressions]
- Did the format detection assertions pass? [YES/NO — explain failures]
- Did the skill correctly identify format from context? [describe accuracy]
- Is the format detection adding value or over-engineering? [honest assessment]
```

---

#### Option C: Domain-Specific Intelligence (Pattern 5)

**What you're adding:** Semantic versioning analysis -- the skill analyzes commit types to suggest the appropriate version bump.

**Step 1: Add semver analysis to your SKILL.md.**

After the categorization step in your workflow, add a version analysis phase:

```markdown
## Step 4: Analyze Semantic Versioning Impact

After categorizing commits, determine the appropriate version bump:

1. **Major bump** (X.0.0): Suggested if ANY commit contains a breaking change.
   Breaking changes are indicated by:
   - A `!` after the type/scope: `feat!:` or `feat(auth)!:`
   - A `BREAKING CHANGE:` footer in the commit body
   - A `BREAKING-CHANGE:` footer (hyphenated variant)

2. **Minor bump** (x.Y.0): Suggested if no breaking changes exist AND at least
   one commit has type `feat`.

3. **Patch bump** (x.y.Z): Suggested if all commits are `fix`, `chore`, `docs`,
   `style`, `refactor`, `perf`, `test`, `build`, or `ci` — with no `feat` or
   breaking changes.

Present the version suggestion in the changelog header:

```
## [v1.2.3] - 2026-03-12 (suggested: patch bump)
```

Include a brief justification: "Patch bump suggested: 8 fixes, 2 chores,
0 features, 0 breaking changes."

If the previous version cannot be determined from git tags, omit the specific
version number but still state the bump type: "Suggested bump type: minor
(3 features detected)."
```

**Step 2: Add new evals to test semver analysis.**

Add these test cases to your `evals.json`:

```json
{
  "id": "semver-patch",
  "prompt": "Generate a changelog since the last tag and tell me what version bump is needed",
  "expected_output": "A changelog with a semver bump suggestion based on the types of commits in the range.",
  "expectations": [
    "The output includes a version bump recommendation (major, minor, or patch)",
    "The recommendation is justified by citing the count of commit types (e.g., '3 fixes, 0 features')",
    "The bump recommendation follows semver rules: breaking changes trigger major, features trigger minor, fixes trigger patch"
  ]
},
{
  "id": "semver-breaking",
  "prompt": "We have some breaking changes in the last few commits. Generate a changelog and version recommendation.",
  "expected_output": "A changelog that identifies breaking changes and recommends a major version bump.",
  "expectations": [
    "Breaking changes are identified and listed in a dedicated section",
    "The version bump recommendation is 'major' if any breaking changes are present",
    "The breaking change section appears prominently, before other categories or clearly marked with a warning"
  ]
}
```

**Step 3: Run evals and compare.**

Run your full eval suite (original 5 test cases + the 2 new semver tests). Compare results:

```
## Enhancement Results: Domain-Specific Intelligence

### Before Enhancement
- Pass rate: __/15 assertions (__%)
- Mean tokens: ___

### After Enhancement
- Pass rate: __/21 assertions (__%)  [15 original + 6 new]
- Mean tokens: ___

### Analysis
- Did existing test cases regress? [YES/NO — list any regressions]
- Did the semver assertions pass? [YES/NO — explain failures]
- Does the version recommendation match what a human would suggest? [accuracy check]
- Is the domain knowledge deep enough to be useful? [honest assessment]
```

---

## Key Takeaways

1. **Most skills start as Pattern 1.** Sequential Workflow Orchestration is the backbone of nearly every skill. If your skill doesn't have a clear step-by-step workflow, fix that before layering on other patterns. The numbered steps, dependency declarations, and validation checks from Pattern 1 are what make a skill reliable.

2. **Pattern 5 is what makes a skill worth building.** Domain-Specific Intelligence is the pattern that separates a useful skill from a glorified prompt. If your skill doesn't encode knowledge that Claude lacks by default -- parsing rules, categorization logic, domain conventions -- then the skill isn't pulling its weight. The eval delta between with-skill and baseline performance is almost entirely driven by Pattern 5.

3. **Multi-MCP Coordination (Pattern 2) has the highest complexity cost.** Every MCP you add is a new failure mode, a new dependency, and a new configuration requirement. Add MCP integrations only when the user's workflow genuinely spans multiple services and manual handoff between them is a real pain point. Don't integrate Slack just because you can.

4. **Iterative Refinement (Pattern 3) trades tokens for accuracy.** Self-verification catches errors that single-pass generation misses, but it costs 30-50% more tokens. Use it when accuracy is more important than speed -- changelogs going into release notes are worth verifying; quick "what changed today?" summaries are not.

5. **Context-Aware Tool Selection (Pattern 4) prevents over-engineering.** Before adding multiple output formats, ask: does the user actually need JSON output? If 95% of usage is Markdown changelogs, building a JSON formatter is wasted effort. Add format detection only when real usage data shows demand for multiple formats.

6. **Layer patterns deliberately, not exhaustively.** A skill that uses all 5 patterns is not better than one that uses 2 patterns well. Each pattern adds complexity, code to maintain, and failure modes to handle. The right number of patterns is the minimum needed to serve the user's actual workflow.

### Pattern Selection Decision Tree

Use this tree when designing a new skill or evaluating whether to add a pattern to an existing one:

```
Start: What does the skill need to do?
  │
  ├── Does it involve multiple steps in order?
  │     └── YES → Pattern 1: Sequential Workflow Orchestration
  │               (almost always yes — this is your foundation)
  │
  ├── Does it require specialized knowledge beyond tool access?
  │     └── YES → Pattern 5: Domain-Specific Intelligence
  │               (embed the rules, don't rely on Claude's general knowledge)
  │
  ├── Does it span multiple external services/MCPs?
  │     └── YES → Is manual handoff between them a real pain point?
  │               ├── YES → Pattern 2: Multi-MCP Coordination
  │               └── NO  → Skip it. Manual handoff is fine for rare cases.
  │
  ├── Does output quality improve with self-review?
  │     └── YES → Is accuracy critical for this use case?
  │               ├── YES → Pattern 3: Iterative Refinement
  │               └── NO  → Skip it. Single-pass is good enough.
  │
  └── Does the same goal have multiple valid approaches?
        └── YES → Do users actually request different approaches?
                  ├── YES → Pattern 4: Context-Aware Tool Selection
                  └── NO  → Pick the best default and ship it.
```

The tree encodes a bias toward simplicity: at every decision point, the "NO" branch skips the pattern. Only add a pattern when you have a clear, affirmative reason to do so.

---

**Previous module:** [Module 6 -- Description Optimization](../module-06-description-optimization/) -- optimize trigger accuracy with train/test splits and automated evaluation loops.
