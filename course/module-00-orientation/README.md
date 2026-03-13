# Module 0: Orientation and Setup

**Time estimate:** 30-45 minutes
**Goal:** Understand what skills are, how they work, and verify your environment is ready for the rest of the course.

---

## Theory

### What Is a Skill?

A skill is a folder that teaches Claude how to handle a specific task or workflow. At its simplest, it's a `SKILL.md` file with YAML frontmatter and markdown instructions. At its most complex, it includes executable scripts, reference documents, and asset files.

```
my-skill/
├── SKILL.md          # Required. The core instructions.
├── scripts/          # Optional. Executable code for deterministic/repetitive tasks.
├── references/       # Optional. Docs loaded into context as needed.
└── assets/           # Optional. Templates, fonts, icons used in output generation.
```

The `SKILL.md` is the only required file. Everything else is there to support it when the task demands more than markdown instructions alone can provide.

Skills live in `~/.claude/skills/` (user-level) or can be installed from plugins. When Claude encounters a user request, it checks its list of available skills and decides whether any of them are relevant.

### Progressive Disclosure

Skills use a three-level loading system designed to minimize token usage while maintaining deep expertise. This is one of the most important concepts in skill design.

**Level 1: YAML Frontmatter (always loaded)**

The `name` and `description` fields from the frontmatter are always present in Claude's system prompt as part of the `available_skills` list. This is roughly ~100 words. Claude uses this information to decide: "Is this skill relevant to what the user just asked?"

```yaml
---
name: git-changelog
description: Generate formatted changelogs from git history. Use when the user asks for release notes, changelogs, or wants to summarize recent commits.
---
```

This is your skill's elevator pitch. If the description doesn't convince Claude to look further, the rest of the skill never gets loaded.

**Level 2: SKILL.md Body (loaded on demand)**

When Claude decides a skill is relevant, it reads the full SKILL.md body. This contains the actual instructions: steps to follow, output formats, examples, troubleshooting guidance. Keep this under 500 lines. If you're approaching that limit, push detail into Level 3.

**Level 3: Linked Files (navigated as needed)**

Scripts in `scripts/`, docs in `references/`, and templates in `assets/` are only accessed when the SKILL.md body tells Claude to use them. A skill supporting multiple cloud providers might have `references/aws.md`, `references/gcp.md`, and `references/azure.md` -- Claude reads only the one that matches the user's context.

```
cloud-deploy/
├── SKILL.md                  # Workflow + decision logic
└── references/
    ├── aws.md                # Only loaded for AWS tasks
    ├── gcp.md                # Only loaded for GCP tasks
    └── azure.md              # Only loaded for Azure tasks
```

The key insight: every token loaded into context has a cost (latency, attention dilution, money). Progressive disclosure ensures Claude gets just enough information at each stage to do its job well.

### Core Design Principles

Three principles guide good skill design:

**Composability.** Skills work alongside other skills. Don't assume yours is the only one loaded. Don't override global behaviors or conflict with how Claude normally operates. A well-designed skill enhances Claude's capabilities for a specific domain without stepping on anything else.

**Portability.** Skills work across Claude.ai, Claude Code, and the API. Avoid hard-coding assumptions about the environment. If a skill requires specific tools (like filesystem access or a particular MCP server), declare that in the `compatibility` frontmatter field rather than assuming it.

**Progressive disclosure.** (Yes, it's both a mechanism and a principle.) Minimize what's always loaded. Maximize what's available on demand. The best skills are lightweight in Level 1, focused in Level 2, and rich in Level 3.

### Skills + MCP: The Kitchen Analogy

MCP (Model Context Protocol) servers give Claude access to tools and data -- APIs, databases, file systems, external services. Skills give Claude instructions on how to use those tools effectively.

Think of it like a professional kitchen:
- **MCP** provides the kitchen: the stove, the knives, the pantry full of ingredients, the refrigerator with fresh produce.
- **Skills** provide the recipes: step-by-step instructions for turning those raw ingredients and tools into a finished dish.

A chef with a great kitchen but no recipes will improvise (sometimes well, sometimes not). A chef with great recipes but no kitchen can't cook at all. Together, they produce consistent, high-quality results.

In practice, this means a skill might say: "Use the GitHub MCP to fetch open PRs, filter by label, summarize each one, and format the output as a markdown table." The MCP provides the `fetch PRs` tool; the skill provides the workflow that orchestrates it.

### The Skill-Creator Tool

Anthropic ships a built-in skill called `skill-creator` that helps you build other skills. It's available both in Claude.ai and Claude Code. It can:

- Generate a new skill from a description of what you want
- Review an existing skill and suggest improvements
- Run test cases against your skill and collect results
- Benchmark skill performance with variance analysis
- Optimize your skill's description for better triggering accuracy

In Claude Code, you'll find it installed at:
```
~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/
```

This is itself a complex skill with `scripts/`, `references/`, `assets/`, and even `agents/` -- making it a great specimen to study. We'll use it later in the course.

---

## Exercises

### Exercise 0.1: Verify Your Environment

Before building anything, confirm your tools are in place.

**Step 1: Confirm the Claude CLI is installed.**

```bash
claude --version
```

You should see a version number. If you get "command not found," install Claude Code first: https://docs.anthropic.com/en/docs/claude-code

**Step 2: Locate the skill-creator.**

```bash
ls ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/
```

You should see:
```
agents/
assets/
eval-viewer/
LICENSE.txt
references/
scripts/
SKILL.md
```

This is the most complex skill you'll encounter in this course. Note how it uses every optional directory.

**Step 3: Locate the frontend-design skill.**

```bash
ls ~/.claude/skills/frontend-design/
```

You should see a `SKILL.md` file. This is a simpler skill -- just a single file, no scripts or references.

**Step 4: Run quick_validate.py on frontend-design.**

```bash
python3 ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py ~/.claude/skills/frontend-design/
```

You should see: `Skill is valid!`

This script checks that a skill has valid YAML frontmatter with the required `name` and `description` fields, proper kebab-case naming, and no unexpected properties. You'll use it throughout the course to sanity-check your work.

---

### Exercise 0.2: Anatomy Dissection

Now that you know where things live, take them apart.

**Part A: Read the frontend-design skill.**

```bash
cat ~/.claude/skills/frontend-design/SKILL.md
```

As you read, identify:
1. **Frontmatter fields** -- What's in the YAML block between the `---` markers? Which fields are required vs. optional?
2. **Body structure** -- How are the instructions organized? What headings are used?
3. **Writing style** -- Is it formal or conversational? Does it use imperative form ("Do X") or descriptive form ("The skill does X")? Does it explain *why* things matter, not just *what* to do?

**Part B: Read the skill-creator skill.**

```bash
cat ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/SKILL.md
```

This one is much longer. Pay attention to:
1. How it handles multiple workflows (creating, testing, improving, optimizing)
2. How it references external files (`agents/grader.md`, `references/schemas.md`, etc.)
3. How it adapts to different environments (Claude Code vs. Claude.ai vs. Cowork)

**Part C: Compare minimal vs. full-featured.**

Create a mental (or written) comparison:

| Aspect | frontend-design (minimal) | skill-creator (full-featured) |
|--------|--------------------------|-------------------------------|
| Frontmatter fields | name, description, license | name, description |
| Body length | ~40 lines | ~470 lines |
| scripts/ | No | Yes (7+ Python scripts) |
| references/ | No | Yes (schemas, docs) |
| assets/ | No | Yes (HTML templates) |
| agents/ | No | Yes (grader, comparator, analyzer) |
| External file references | None | Many (with guidance on when to read each) |

The takeaway: a skill can be as simple as a single file with a few dozen lines, or as complex as a multi-file system with executable scripts and specialized subagents. Start simple. Add complexity only when the task demands it.

---

### Exercise 0.3: Your First Skill (Hello World)

Time to build something. You'll create the simplest possible skill to see the full lifecycle.

**Step 1: Create the skill folder.**

```bash
mkdir -p student-workspace/hello-world
```

(Run this from the course root: `/Users/alexis/claudeCode/skillsResearch/`)

**Step 2: Write a minimal SKILL.md.**

Create `student-workspace/hello-world/SKILL.md` with this content:

```yaml
---
name: hello-world
description: A practice skill that greets the user. Use this when the user says hello, asks for a greeting, or wants to test if skills are working.
---
```

```markdown
# Hello World Skill

When the user greets you or asks for a greeting, respond with a warm, personalized hello.

## Steps

1. Greet the user by name if they've provided one, otherwise use a friendly generic greeting.
2. Mention that this response is powered by the hello-world skill.
3. Suggest one fun fact about the current day to make the greeting memorable.

## Example

**User:** "Hey there!"
**Response:** "Hello! This greeting is brought to you by the hello-world skill. Here's a fun fact: [interesting fact about today]. What can I help you with?"
```

**Step 3: Validate it.**

```bash
python3 ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py student-workspace/hello-world/
```

You should see `Skill is valid!`

**Step 4: Test it.**

To actually use your skill, you'd install it to `~/.claude/skills/hello-world/` and then start a Claude Code session. When you say "hello," Claude should consult your skill and follow its instructions. For now, just knowing the skill passes validation is enough -- we'll cover testing properly in Module 4.

---

## Key Takeaways

- A skill is just a folder with a `SKILL.md` file. Scripts, references, and assets are optional add-ons for when you need them.
- Progressive disclosure is the core mechanism: frontmatter is always loaded (~100 words), the SKILL.md body loads on demand, and linked files are accessed only as needed. Design with this in mind.
- The `description` field in your frontmatter is the single most important piece of text in your skill. It determines whether Claude ever looks at the rest. Make it count.
- Start minimal. A valid skill needs only `name` and `description` in the frontmatter and a body with instructions. Add complexity when the task requires it, not before.
- Use `quick_validate.py` early and often to catch structural issues before they become debugging sessions.
- The `skill-creator` tool is both a useful utility and an excellent reference implementation. Study it when you want to see advanced patterns in action.
