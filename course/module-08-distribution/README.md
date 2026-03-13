# Module 8: Packaging, Distribution, and Positioning

**Time estimate:** 60-90 minutes
**Prerequisites:** Completed Modules 1-7 (a fully built, tested, and optimized git-changelog skill)
**Outcome:** A packaged .skill file, a distribution-ready GitHub README, and three audience-targeted positioning statements for your skill

---

## Learning Objectives

By the end of this module, you will be able to:

- Run through a pre-packaging validation checklist to catch errors before distribution
- Package a skill into the .skill file format using the packaging script
- Choose the right distribution channel for a given use case (Claude.ai, Claude Code, API, organization-level)
- Write a GitHub-ready README that is distinct from the SKILL.md (human audience vs. Claude audience)
- Position a skill for different audiences by focusing on outcomes rather than implementation details

---

## Theory

### 1. Distribution Channels

A finished skill can reach users through several channels. Each channel has different trade-offs in terms of reach, update friction, and target audience.

#### Claude.ai Upload

The simplest channel for end users. The workflow:

1. Download your skill folder
2. Zip it into a `.zip` file
3. Navigate to Settings > Capabilities > Skills in Claude.ai
4. Upload the ZIP

This channel is best for **manual testing, personal use, and sharing with individual users** who interact with Claude through the web interface. Updates require the user to re-upload, so it is not ideal for skills that change frequently.

#### Claude Code Directory

For developers using Claude Code, skills can be installed by placing the skill folder directly in the filesystem:

```
~/.claude/skills/your-skill-name/
  SKILL.md
  supporting-files/
```

Claude Code scans this directory and makes installed skills available in every session. This channel is best for **developers who want skills available in their local environment** without going through a web UI.

#### Organization-Level Deployment

Shipped in December 2025, this channel allows workspace administrators to deploy skills across an entire organization:

- **Automatic updates:** When the admin updates the skill, all users get the new version immediately
- **Centralized management:** Admins control which skills are available, no per-user installation required
- **Audit trail:** Visibility into which skills are deployed and who is using them

This channel is best for **teams and companies** that want consistent skill behavior across all members without relying on individuals to install and update skills manually.

#### API

The most powerful channel for programmatic use. Skills can be managed through dedicated endpoints:

- **`/v1/skills` endpoint:** Create, update, list, and delete skills programmatically
- **`container.skills` parameter:** Pass skills directly in the Messages API request body
- **Agent SDK integration:** Skills work natively with Anthropic's Agent SDK

Use the API channel when:

- Your application needs to load skills dynamically based on context
- You are running automated pipelines that invoke Claude with specific skills
- You need production-scale skill management with version control
- You want to A/B test different skill versions programmatically

#### GitHub Hosting

For open-source skills, a public GitHub repository serves as both a distribution channel and a discovery mechanism. A well-structured repo includes:

- Clear README with installation instructions
- Example usage with screenshots or sample output
- The skill folder ready to download and install
- A LICENSE file

GitHub hosting is best for **community distribution** -- making your skill discoverable and easy to adopt.

---

### 2. When to Use Which Channel

| Scenario | Recommended Channel |
|----------|-------------------|
| Personal use or trying a friend's skill | Claude.ai upload |
| Developer integrating into their workflow | Claude Code directory |
| Team-wide deployment with managed updates | Organization-level |
| Building an app that uses skills | API |
| Automated CI/CD pipelines | API |
| Production at scale | API |
| Open-source community sharing | GitHub + any of the above |

The channels are not mutually exclusive. A skill can be published on GitHub (for discovery and contribution), deployed organization-wide (for the team), and also available via API (for the product's backend). The skill files are the same -- only the delivery mechanism changes.

---

### 3. The .skill File Format

A `.skill` file is a ZIP archive with a specific internal structure. The packaging script (`scripts/package_skill.py` in the skill-creator tool) handles the details, but understanding the format helps with debugging and manual packaging.

**What gets included:**

- `SKILL.md` -- the main skill file with frontmatter and instructions
- Supporting resources -- scripts, templates, schemas, examples referenced in SKILL.md
- `metadata.json` (if present) -- version, author, compatibility information

**What gets excluded:**

- `evals/` -- test cases and results are development artifacts, not runtime requirements
- `.git/` -- version control history is not needed in the package
- `__pycache__/` -- Python bytecode caches
- `*.pyc` -- compiled Python files
- Any files matching common development-only patterns

The exclusion list matters because skill packages should be as small as possible. A user uploading a skill to Claude.ai does not need your eval history or git objects. The packaging script handles these exclusions automatically.

---

### 4. Validation Before Packaging

The official guide provides a two-phase checklist: pre-upload and post-upload. Skipping validation is how broken skills get distributed.

#### Pre-Upload Checklist

Run through every item before creating the package:

| Check | What to verify |
|-------|---------------|
| Trigger testing (obvious) | Skill loads on direct, unambiguous requests |
| Trigger testing (paraphrased) | Skill loads on varied phrasings of the same intent |
| Negative trigger testing | Skill does NOT load on unrelated or adjacent queries |
| Functional tests pass | The skill produces correct output for its core use cases |
| Tool integration works | All referenced scripts, templates, and MCP tools function correctly |
| File naming | SKILL.md is named exactly `SKILL.md` (case-sensitive) |
| Frontmatter valid | YAML frontmatter parses without errors, all required fields present |
| Referenced files exist | Every file mentioned in the instructions is included in the package |
| Compressed as .zip | The package is a valid ZIP archive |

If you have been following this course, most of these checks are already covered by your evals (Module 5) and trigger eval set (Module 6). The pre-packaging checklist is a final confirmation, not a substitute for earlier testing.

#### Post-Upload Checklist

After deploying the skill, validate in the real environment:

| Check | What to verify |
|-------|---------------|
| Real conversation test | Skill works in an actual Claude conversation, not just evals |
| Under-triggering check | Skill activates on queries that real users would ask |
| Over-triggering check | Skill does NOT activate on queries outside its scope |
| User feedback collection | Ask early users whether the skill helped or got in the way |
| Description iteration | Update the description based on real-world triggering patterns |
| Version update | Increment the version in metadata after changes |

Post-upload validation catches problems that evals miss -- differences between your test environment and the real one, edge cases in user phrasing, and interaction effects with other installed skills.

---

### 5. Writing a Distribution README

A distribution README is fundamentally different from SKILL.md. They serve different audiences and purposes:

| | SKILL.md | Distribution README |
|---|---------|-------------------|
| **Audience** | Claude (the AI) | Human visitors (GitHub, docs) |
| **Purpose** | Instruct Claude how to execute the skill | Explain what the skill does and how to install it |
| **Tone** | Imperative, precise, procedural | Conversational, persuasive, user-friendly |
| **Content** | Step-by-step workflows, tool references, output formats | Features, installation, examples, limitations |

A common mistake is writing SKILL.md and treating it as the README, or vice versa. They are complementary documents for completely different readers.

#### Structure of a Good Distribution README

1. **One-sentence description** -- What does the skill do, in a single line? This appears in search results and social previews.

2. **Features list** -- Bullet points of specific capabilities. Not "generates changelogs" (too vague) but "categorizes commits by type using conventional commit parsing" (specific and concrete).

3. **Installation instructions** -- Step-by-step for each supported channel. Include the exact commands and paths. Users should not have to guess.

4. **Usage examples** -- Show real prompts and the output they produce. Include sample output, ideally with screenshots. Users decide whether to install based on what the output looks like, not what the instructions say.

5. **Requirements and limitations** -- What does the skill need to work? (Git repository, specific commit format, MCP server, etc.) What does it NOT do? Setting expectations prevents frustration.

6. **Contributing guide** -- If open source: how to run tests, how to submit changes, coding standards.

7. **License** -- Required for any public distribution.

---

### 6. Positioning Your Skill

Positioning is the art of explaining why someone should care about your skill. The official guide is explicit about this: **focus on outcomes, not features.**

#### The Outcomes Principle

Most skill authors describe their skill in terms of what it is:

> "A folder containing YAML frontmatter and Markdown instructions for generating changelogs from git history."

This is technically accurate and completely unpersuasive. Nobody wants a folder of YAML. They want the result.

The outcomes-first version:

> "Set up complete project changelogs in seconds instead of 30 minutes of manual commit archaeology."

Same skill. Completely different emotional response. The second version answers the question every user asks: "Why should I install this?"

#### Positioning for Different Audiences

The same skill needs different positioning depending on who is reading:

**Technical audience (developers):** Lead with specifics. Mention the technology, the integration points, and the time savings. Developers trust concrete claims backed by metrics.

**Non-technical audience (project managers):** Lead with the problem it solves. Avoid jargon. Focus on team visibility and reduced manual work. PMs care about process improvement, not git internals.

**MCP-integrated version:** Highlight the combination. A skill plus an MCP server is more powerful than either alone. Show how the skill leverages real-time data from the MCP connection to produce results that neither could achieve independently.

#### Before/After Comparisons

The most effective positioning technique is showing the contrast between life without the skill and life with it:

**Before (no skill):**
- Open terminal, run git log
- Manually scan through 200 commits
- Copy-paste relevant ones into a document
- Format by hand, categorize, add headers
- 30 minutes of tedious work per release

**After (with skill):**
- Type "generate release notes for v2.0"
- Get a formatted, categorized changelog in 10 seconds
- Review, adjust, ship

This before/after pattern works for any audience because it makes the value proposition visceral rather than abstract.

---

### 7. Skills as an Open Standard

Skills are published as an open standard, in the same spirit as MCP (Model Context Protocol). This has practical implications:

- **Portability:** A well-built skill is not locked to one platform. The same SKILL.md can be used in Claude.ai, Claude Code, and via the API.
- **Interoperability:** Skills can reference MCP servers, and MCP servers can be used by skills. The two standards complement each other.
- **Compatibility field:** Use the `compatibility` field in your skill's metadata to note environment-specific requirements. If a skill requires Claude Code (because it uses filesystem tools), say so. If it works everywhere, say that too.

Building skills against the open standard rather than a specific client means your skill remains useful as new clients and platforms emerge.

---

## Exercises

### Exercise 8.1: Pre-Package Validation

**Goal:** Run through the complete pre-packaging checklist for your git-changelog skill.

**Step 1: File structure check.**

Verify that your skill directory contains all required files and no extraneous artifacts:

```bash
# List the contents of your skill directory
ls -la student-workspace/git-changelog/

# Verify SKILL.md exists and is named correctly (case-sensitive)
ls student-workspace/git-changelog/SKILL.md

# Check that all files referenced in SKILL.md actually exist
# Open SKILL.md and search for any file references
```

**Step 2: Frontmatter validation.**

Open your SKILL.md and verify the YAML frontmatter:

```yaml
# Check for:
# - name field is present and matches the directory name
# - description field is present and under 1024 characters
# - version field is present and follows semver
# - All YAML syntax is valid (no tabs, proper indentation, correct quoting)
```

If you have `quick_validate.py` available from the skill-creator tool, run it:

```bash
python scripts/quick_validate.py student-workspace/git-changelog/
```

**Step 3: Cross-reference with test results.**

Pull up your results from previous modules:

- Module 4 (manual testing): Were all issues resolved?
- Module 5 (evals): What was the final pass rate? Any always-failing assertions that point to missing functionality?
- Module 6 (description optimization): Is the optimized description deployed in SKILL.md?

**Step 4: Record the validation.**

Create a validation checklist in your course log:

```
## Pre-Package Validation — git-changelog

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | SKILL.md exists and named correctly | | |
| 2 | Frontmatter parses without errors | | |
| 3 | Description under 1024 characters | | |
| 4 | All referenced files present | | |
| 5 | Trigger tests pass (obvious) | | |
| 6 | Trigger tests pass (paraphrased) | | |
| 7 | No overtriggering on unrelated queries | | |
| 8 | Functional eval pass rate > 80% | | |
| 9 | Tool integrations verified | | |
| 10 | Optimized description deployed | | |

Overall: READY / NOT READY
```

Do not move to Exercise 8.2 until every check passes or has a documented exception.

---

### Exercise 8.2: Package the Skill

**Goal:** Create a distributable .skill file and verify its contents.

**Step 1: Run the packaging script.**

If the skill-creator tool is available:

```bash
python scripts/package_skill.py \
  --skill-path student-workspace/git-changelog/ \
  --output student-workspace/git-changelog.skill
```

If the packaging script is not available, create the package manually:

```bash
cd student-workspace/git-changelog/

# Create a ZIP, excluding development artifacts
zip -r ../git-changelog.skill . \
  -x "evals/*" \
  -x ".git/*" \
  -x "__pycache__/*" \
  -x "*.pyc" \
  -x ".DS_Store"
```

**Step 2: Inspect the package contents.**

Verify the ZIP contains exactly what it should -- no more, no less:

```bash
# List the contents of the .skill file
unzip -l student-workspace/git-changelog.skill
```

Check for:
- `SKILL.md` is present at the root of the archive
- All supporting files referenced in SKILL.md are included
- No eval files, git objects, or cache files leaked in
- The total file size is reasonable (a skill package should typically be under 100KB unless it includes large templates)

**Step 3: Record the results.**

```
## Package Results

- File: git-changelog.skill
- Size: __ KB
- File count: __ files
- Contents:
  - [list each file in the package]
- Excluded correctly:
  - [ ] No evals/ directory
  - [ ] No .git/ directory
  - [ ] No __pycache__/
  - [ ] No .pyc files
```

**Step 4: Test the package.**

To verify the package works end-to-end, extract it to a temporary location and install from there:

```bash
# Extract to a temp directory
mkdir /tmp/skill-test
unzip student-workspace/git-changelog.skill -d /tmp/skill-test/git-changelog/

# Install from the extracted package
cp -r /tmp/skill-test/git-changelog/ ~/.claude/skills/git-changelog-test/

# Verify the skill loads in a new Claude Code session
# (test with a simple trigger query)
```

Clean up the test installation afterward to avoid conflicts with your development copy.

---

### Exercise 8.3: Write a Distribution README

**Goal:** Write a GitHub-ready README for git-changelog that is distinct from SKILL.md and targeted at human readers.

Write the following file at `student-workspace/git-changelog/README.md`:

Your README should include these sections, in this order:

**1. Title and one-sentence description.**

The first line should be an H1 with the skill name. The second line should be a single sentence explaining what the skill does in terms of the outcome it provides.

**2. Features list.**

3-5 bullet points listing specific capabilities. Each bullet should describe a concrete feature, not a vague category. Example:

```markdown
- Categorizes commits by type (features, fixes, breaking changes) using conventional commit parsing
- Supports tag-based, date-based, and commit-hash ranges
- Generates markdown output ready for GitHub releases
```

**3. Installation instructions.**

Provide step-by-step instructions for both Claude.ai and Claude Code:

```markdown
### Claude.ai
1. Download this repository as a ZIP
2. Go to Settings > Capabilities > Skills
3. Upload the ZIP file

### Claude Code
1. Clone this repository
2. Copy the skill folder to your skills directory:
   ```bash
   cp -r git-changelog/ ~/.claude/skills/git-changelog/
   ```
```

**4. Usage examples.**

Show 2-3 real prompts and describe the output they produce. If possible, include sample output showing the format:

```markdown
### Example: Generate release notes

**Prompt:** "Prepare release notes for v2.0"

**Output:**
## [v2.0.0] - 2026-03-12

### Breaking Changes
- Removed deprecated `--legacy` flag (a1b2c3d)

### Features
- Added support for date-range filtering (d4e5f6a)
- New markdown template option (b7c8d9e)

### Bug Fixes
- Fixed duplicate commit entries when using merge commits (f0a1b2c)
```

**5. Requirements and limitations.**

Be honest about what the skill needs and what it cannot do:

```markdown
## Requirements
- A git repository with commit history
- Works best with conventional commit messages

## Limitations
- Does not support monorepo per-package changelogs
- Requires at least one commit in the repository
```

**6. License.**

Include a license declaration appropriate for the project.

**Self-review before moving on:**

- Is every section written for a human reader, not for Claude?
- Could someone install and use the skill using only this README?
- Are the usage examples realistic and the sample output accurate?
- Are limitations stated clearly so users know what to expect?

---

### Exercise 8.4: Positioning Exercise

**Goal:** Write three versions of a one-paragraph pitch for git-changelog, each targeted at a different audience.

**Version 1: Technical audience (developers)**

Write a paragraph that would appear in a developer-focused blog post or Hacker News comment. Emphasize:

- Specific technical capabilities (conventional commit parsing, tag ranges, markdown output)
- Time savings with concrete numbers
- Integration with existing developer workflows
- How it compares to doing the task manually

**Version 2: Non-technical audience (project managers)**

Write a paragraph for a team wiki or internal announcement. Emphasize:

- The problem it solves in business terms (release communication, stakeholder updates)
- Reduced manual effort without mentioning git internals
- Team visibility into what shipped
- No technical setup required by the PM

**Version 3: MCP-integrated version (combined with GitHub MCP)**

Write a paragraph for an audience that understands both skills and MCP servers. Emphasize:

- How the skill leverages the GitHub MCP server for real-time repository data
- The combined capability: the MCP server provides the data, the skill provides the structure and formatting
- What becomes possible with the combination that neither could do alone
- The open-standard portability of both components

**Format your output as:**

```
## Positioning Statements

### For Developers
[paragraph]

### For Project Managers
[paragraph]

### For MCP-Integrated Use
[paragraph]
```

**Self-review for each version:**

- Does it lead with an outcome, not a feature?
- Would the target audience understand every word?
- Does it answer "why should I care?" in the first sentence?
- Is the value proposition specific enough to be credible? (Not "saves time" but "saves 30 minutes per release")

---

## Key Takeaways

1. **Validate before you package.** The pre-packaging checklist is not bureaucracy -- it is the last line of defense against shipping a broken skill. Every item on the checklist exists because someone shipped a skill that failed on that exact point. Run the checklist every time, even when you are confident.

2. **Choose the distribution channel based on the audience.** Claude.ai upload for individuals experimenting. Claude Code directory for developers integrating into their workflow. Organization-level for teams that need managed deployment. API for applications and pipelines. Match the channel to how the skill will actually be used.

3. **The README is for humans; SKILL.md is for Claude.** These are two different documents for two different readers. The README sells the skill and explains installation. The SKILL.md instructs Claude how to execute the workflow. Writing one well does not excuse skipping the other.

4. **Position on outcomes, not implementation.** Nobody installs a skill because it has "YAML frontmatter and Markdown instructions." They install it because it "generates release notes in 10 seconds instead of 30 minutes." Lead with the result the user gets, not the mechanism that produces it.

5. **Before/after is the most persuasive format.** Show the painful manual process. Then show the skill-powered version. The contrast makes the value proposition self-evident. This works for developers, project managers, and executives alike.

6. **Skills are an open standard.** Like MCP, skills are designed to be portable across platforms and clients. Build against the standard, not against a specific client. Use the compatibility field to document environment-specific requirements so users know what to expect before installing.

---

**Previous module:** [Module 7 -- Advanced Patterns](../module-07-advanced-patterns/)
