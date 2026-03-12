# Building Claude Code Skills: From Zero to Skill Creator

A hands-on course where you build a real Claude Code skill from scratch, learning every concept from Anthropic's official guide along the way.

**What you'll build:** A `git-changelog` skill that generates formatted changelogs from git history — progressively enhanced across 10 modules.

**Prerequisites:** Claude Code CLI installed, basic familiarity with Markdown and YAML, a git repository to test against.

**Time estimate:** 4-6 hours total (30-45 minutes per module).

---

## Module 0: Orientation and Setup
**Learning objectives:**
- Understand what a skill is (SKILL.md + scripts/ + references/ + assets/)
- Understand progressive disclosure (3 levels: frontmatter, body, linked files)
- Verify your environment and locate key tools
- Dissect an existing skill to understand its anatomy

## Module 1: Planning and Designing Your Skill
**Learning objectives:**
- Identify concrete use cases before writing code
- Classify skills into the three categories (Document Creation, Workflow Automation, MCP Enhancement)
- Define quantitative and qualitative success criteria
- Write a technical spec with directory plan and frontmatter draft

## Module 2: Writing the SKILL.md
**Learning objectives:**
- Write valid YAML frontmatter (name, description, optional fields)
- Craft trigger-rich descriptions that activate reliably
- Structure the instruction body (steps, examples, troubleshooting)
- Apply writing best practices (imperative form, specific actions, explain "why")

## Module 3: Building Supporting Resources
**Learning objectives:**
- Know when to bundle scripts vs. inline instructions
- Write helper scripts that are token-efficient and deterministic
- Create reference files for progressive disclosure
- Add asset templates used in output generation

## Module 4: Manual Testing
**Learning objectives:**
- Distinguish undertriggering, overtriggering, and execution issues
- Run systematic trigger tests (should-fire vs. should-not-fire)
- Evaluate execution quality through transcript review
- Perform one iteration cycle: test → identify → fix → retest

## Module 5: Systematic Testing with Evals
**Learning objectives:**
- Write evals.json with test cases and expectations
- Run with-skill and baseline comparisons
- Use the grading and benchmarking pipeline
- Interpret benchmark results and identify discriminating assertions

## Module 6: Description Optimization
**Learning objectives:**
- Understand how Claude decides to load skills (the available_skills list)
- Create train/test splits for trigger evaluation
- Run the programmatic optimization loop
- Apply and verify the optimized description

## Module 7: Advanced Patterns
**Learning objectives:**
- Recognize and apply the 5 canonical skill patterns:
  1. Sequential Workflow Orchestration
  2. Multi-MCP Coordination
  3. Iterative Refinement
  4. Context-Aware Tool Selection
  5. Domain-Specific Intelligence
- Classify your skill's pattern and enhance it

## Module 8: Distribution and Packaging
**Learning objectives:**
- Package a skill as a .skill file (ZIP)
- Write a distribution README (separate from SKILL.md)
- Understand distribution channels (Claude.ai, Claude Code, API, org-level)
- Position your skill effectively (outcomes over features)

## Module 9: Capstone — The Meta-Skill
**Learning objectives:**
- Aggregate all documentation (bugs, lessons, patterns) into a corpus
- Feed the corpus into skill-creator to generate a meta-skill
- Evaluate the meta-skill against baseline
- Package and reflect on the full learning journey
