# Building Claude Code Skills — Research & Course

A hands-on research project that produced two things: a **10-module course** teaching how to build Claude Code custom skills, and a **production skill** (`skill-building-guide`) that encodes the full methodology. Both were validated by auditing and optimizing a real 9-skill suite (gstack).

## What's in this repo

### The Course (`module-00` through `module-09`)

10 progressive modules where you build a `git-changelog` skill from scratch:

| Module | Topic | Key Concept |
|--------|-------|-------------|
| 0 | Orientation & Setup | Skill anatomy, progressive disclosure |
| 1 | Planning | Use cases, categories, success criteria |
| 2 | Writing SKILL.md | Frontmatter, trigger phrases, body structure |
| 3 | Supporting Resources | Scripts, references, assets |
| 4 | Manual Testing | Undertriggering, overtriggering, execution issues |
| 5 | Systematic Evals | evals.json, train/test splits, benchmarking |
| 6 | Description Optimization | Iterative optimization loop, suite-aware eval |
| 7 | Advanced Patterns | 5 canonical skill architecture patterns |
| 8 | Distribution | Packaging, distribution channels |
| 9 | Capstone | Meta-skill generation from course corpus |

Each module has a `README.md` with theory, exercises, and expected outcomes. Modules 2-3 include worked solutions in `solutions/`.

### The Skill-Building Guide (`skill-building-guide/`)

A production Claude Code skill that guides users through building skills. This is the capstone output — the course methodology distilled into a skill that teaches itself.

```
skill-building-guide/
  SKILL.md                        # 7-step workflow (plan → write → test → optimize)
  scripts/audit_skill.py          # Validates structure, frontmatter, file references
  references/common-pitfalls.md   # 16 pitfalls with symptoms, root causes, fixes
  references/patterns.md          # 5 canonical patterns with decision tree
```

### The Gstack Suite (`gstack/`)

Garry Tan's 8-skill development workflow suite, audited and improved using the skill-building-guide methodology, plus a meta-orchestrator skill created during the audit.

```
gstack/
  browse/                 # Headless browser automation
  gstack-meta/            # Workflow orchestrator (routes to correct skill)
  plan-ceo-review/        # CEO/founder-mode plan review (3 modes)
  plan-eng-review/        # Eng manager-mode plan review
  qa/                     # Systematic QA testing
  retro/                  # Weekly engineering retrospective
  review/                 # Pre-landing PR review
  setup-browser-cookies/  # Cookie import for authenticated testing
  ship/                   # Automated release workflow
  audit-report.md         # Before/after comparison
  eval-queries.json       # 127-query suite-aware eval set
  eval-report.md          # 96.1% accuracy, zero confusable-pair confusion
```

**Audit results:** All 9 skills pass validation (0 WARN, 0 FAIL). Suite-aware eval: 96.1% accuracy on 127 queries, zero misrouting between confusable pairs.

### Supporting Files

- **`git-changelog/`** — The example skill built progressively through the course
- **`student-workspace/`** — Working directory for course exercises (includes hello-world starter and in-progress git-changelog)
- **`reference/`** — Standalone cheatsheets (frontmatter, validation checklist)
- **`course-log.md`** — Every bug, root cause analysis, lesson, design decision, and milestone
- **`COURSE-OUTLINE.md`** — Module-by-module learning objectives

## Key Findings

The research produced 13 lessons, documented in `course-log.md`. The three most significant:

1. **Suite-aware eval beats per-skill eval** (LESSON-011). For N skills sharing a domain, a unified query pool with cross-skill near-miss negatives is more efficient (127 queries for 9 skills vs. 180 with standard approach) and catches misrouting that per-skill evals miss.

2. **Irreducible ambiguity sets the accuracy floor** (LESSON-012). Once descriptions follow [WHAT + WHEN + WHEN NOT] with cross-referencing negatives, remaining errors are ultra-vague queries with no domain vocabulary. Broadening descriptions to capture them causes more harm than good.

3. **Casual trigger phrases matter** (LESSON-013). Developers say "look over my changes" not "pre-landing review." At least one informal phrasing per skill prevents casual language from falling through to "none."

## Bug Tracker

13 bugs encountered and resolved with first-principles root cause analysis. Highlights:

| Bug | Summary | Category |
|-----|---------|----------|
| BUG-001 | Conventional commit regex missed `type!(scope):` variant | Execution |
| BUG-005 | Single quotes in awk comment broke bash parsing | Execution |
| BUG-008 | All 8 gstack skills missing negative triggers | Overtriggering |
| BUG-013 | Review skill missing casual "look over" trigger | Undertriggering |

Full details with root cause analyses in `course-log.md`.

## How to Use

**To learn skill-building:** Start at `module-00-orientation/README.md` and work through sequentially. Each module builds on the previous one. Budget 30-45 minutes per module.

**To build a skill now:** Copy `skill-building-guide/` to `~/.claude/skills/` and ask Claude to "help me build a skill." The guide handles the rest.

**To use the gstack suite:** Copy the individual skill folders from `gstack/` to `~/.claude/skills/`. Use `/gstack-meta` to route to the right workflow skill.
