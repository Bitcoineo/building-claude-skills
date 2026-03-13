# YAML Frontmatter Cheatsheet

Quick reference for SKILL.md frontmatter in Claude Code custom skills.

---

## Required Fields

| Field         | Rules                                                                 |
|---------------|-----------------------------------------------------------------------|
| `name`        | kebab-case only. No spaces, capitals, or underscores. Must match the folder name exactly. |
| `description` | What the skill does + when to invoke it. Max 1024 characters. No XML angle brackets (`<` `>`). Include natural trigger phrases users would actually say. |

## Optional Fields

| Field            | Rules                                                              |
|------------------|--------------------------------------------------------------------|
| `license`        | SPDX identifier. Examples: `MIT`, `Apache-2.0`, `GPL-3.0-only`.   |
| `compatibility`  | Environment requirements. 1--500 characters. Example: `"Requires Node.js 18+ and npm"`. |
| `allowed-tools`  | Whitelist of tools the skill may use. Space-separated. Example: `"Bash(python:*) Bash(npm:*) WebFetch"`. If omitted, all tools are available. |
| `metadata`       | Arbitrary key-value pairs. Common keys below.                      |

### Common Metadata Keys

```yaml
metadata:
  author: your-name
  version: 1.0.0
  category: testing
  tags: ["lint", "python", "ci"]
  mcp-server: server-name
  documentation: https://example.com/docs
  support: https://github.com/you/repo/issues
```

---

## Security Rules

- **No XML angle brackets** (`<` `>`) anywhere in frontmatter values. They will break parsing.
- **No "claude" or "anthropic"** in the `name` field. Reserved terms; upload will be rejected.
- **Frontmatter is injected into the system prompt.** Malicious content in any field could act as a prompt injection. Treat every field as security-sensitive.

---

## Common Mistakes

| Mistake                            | Fix                                                        |
|------------------------------------|------------------------------------------------------------|
| Missing `---` delimiters           | Frontmatter must start and end with exactly `---` on its own line. |
| Unclosed quotes in `description`   | Use block scalars (`>-` or `|`) for multi-line descriptions instead of fighting quote escaping. |
| Spaces or capitals in `name`       | Use `my-skill-name`, never `My Skill Name` or `my_skill`.  |
| `description` over 1024 chars      | Trim to essentials: what it does, when to use it, key trigger phrases. |
| File named `README.md`             | The file **must** be called `SKILL.md`. `README.md` is ignored. |
| Folder name doesn't match `name`   | The folder containing `SKILL.md` must have the same name as the `name` field. |

---

## Minimal Example

```yaml
---
name: run-pytest
description: >-
  Runs pytest on the current project and reports results.
  Use when the user says "run tests", "run pytest", or "check test suite".
---
```

## Full Example

```yaml
---
name: python-lint-fix
description: >-
  Lints Python files with ruff and auto-fixes what it can. Reports remaining
  issues with file paths and line numbers. Use when the user says "lint this",
  "fix lint errors", "run ruff", or "clean up the code style".
license: MIT
compatibility: "Requires Python 3.10+ and ruff installed via pip or pipx"
allowed-tools: "Bash(ruff:*) Bash(python:*) Read Edit"
metadata:
  author: your-name
  version: 2.1.0
  category: code-quality
  tags: ["python", "linting", "ruff"]
  documentation: https://github.com/you/python-lint-fix#readme
  support: https://github.com/you/python-lint-fix/issues
---
```
