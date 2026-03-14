# Building Claude Code Skills — Research & Course

A hands-on research project that produced a **10-module course**, a **production skill** (`skill-building-guide`), and a growing library of **audited custom skills**. Validated by auditing and optimizing a real 9-skill suite (gstack) and rebuilding third-party skills to production quality.

## Repository Structure

```
skillsResearch/
├── course/                  # 10-module skill-building course
├── skill-building-guide/    # Production skill: the methodology as a skill
├── gstack/                  # Garry Tan's 10-skill dev workflow suite
├── custom-skills/           # Audited & rebuilt third-party skills
└── git-changelog/           # Example skill built through the course
```

## The Course (`course/`)

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

Each module has a `README.md` with theory, exercises, and expected outcomes. Modules 2-3 include worked solutions. Supporting files: `COURSE-OUTLINE.md`, `course-log.md` (bugs, root causes, lessons, milestones), `reference/` (cheatsheets), `student-workspace/`.

## The Skill-Building Guide (`skill-building-guide/`)

A production Claude Code skill that guides users through building skills — the course methodology distilled into a skill that teaches itself.

```
skill-building-guide/
  SKILL.md                        # 7-step workflow (plan → write → test → optimize)
  scripts/audit_skill.py          # Validates structure, frontmatter, file references (17 checks)
  references/common-pitfalls.md   # 16 pitfalls with symptoms, root causes, fixes
  references/patterns.md          # 5 canonical patterns with decision tree
```

## The Gstack Suite (`gstack/`)

Garry Tan's development workflow suite, audited and improved using the skill-building-guide methodology.

```
gstack/
  gstack-meta/            # Workflow orchestrator (routes to correct skill)
  architect/              # Tech spec & ADRs (bridges plan → implementation)
  plan-ceo-review/        # CEO/founder-mode plan review (3 modes)
  plan-eng-review/        # Eng manager-mode plan review
  review/                 # Pre-landing PR review
  ship/                   # Automated release workflow
  qa/                     # Systematic QA testing
  browse/                 # Headless browser automation
  setup-browser-cookies/  # Cookie import for authenticated testing
  retro/                  # Weekly engineering retrospective
```

**Full development cycle:** `/plan-ceo-review` → `/plan-eng-review` → `/architect` → implement → `/review` → `/ship` → `/qa` → `/retro`

**Audit results:** All 10 skills pass validation (0 WARN, 0 FAIL). Suite-aware eval: 96.1% accuracy on 127 queries, zero misrouting between confusable pairs.

## Custom Skills (`custom-skills/`)

Third-party skills audited against skill-building-guide methodology and rebuilt to production quality.

| Skill | What it does | Origin |
|-------|-------------|--------|
| `seo-optimize` | SEO-optimize a single article with competitor research and HTML report | Rebuilt from a 3,270-line monolithic skill split into two |
| `seo-audit` | Full website SEO audit (up to 15 pages) with scoring and HTML report | Same split — site-wide audit half |
| `scroll-stop-builder` | Build scroll-driven animation websites from video or pre-extracted frames | Rebuilt from B+ to S-tier with dual input, STOP gates, design tokens |

All 3 skills pass audit 15/15 (0 WARN, 0 FAIL).

## Key Findings

The research produced 13 lessons, documented in `course/course-log.md`. The three most significant:

1. **Suite-aware eval beats per-skill eval** (LESSON-011). For N skills sharing a domain, a unified query pool with cross-skill near-miss negatives catches misrouting that per-skill evals miss.

2. **Irreducible ambiguity sets the accuracy floor** (LESSON-012). Once descriptions follow [WHAT + WHEN + WHEN NOT] with cross-referencing negatives, remaining errors are ultra-vague queries. Broadening descriptions to capture them causes more harm than good.

3. **Casual trigger phrases matter** (LESSON-013). Developers say "look over my changes" not "pre-landing review." At least one informal phrasing per skill prevents casual language from falling through.

## How to Use

**Learn skill-building:** Start at `course/module-00-orientation/README.md` and work through sequentially. Budget 30-45 minutes per module.

**Build a skill now:** Copy `skill-building-guide/` to `~/.claude/skills/` and ask Claude to "help me build a skill."

**Use the gstack suite:** Copy skill folders from `gstack/` to `~/.claude/skills/`. Use `/gstack-meta` to route to the right workflow skill.

**Use custom skills:** Copy individual skill folders from `custom-skills/` to `~/.claude/skills/`.
