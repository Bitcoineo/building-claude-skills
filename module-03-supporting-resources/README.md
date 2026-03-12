# Module 3: Building Supporting Resources

**Time estimate:** 30-45 minutes
**Prerequisites:** Completed Module 2 (a working SKILL.md for git-changelog)
**Outcome:** A complete skill folder with scripts/, references/, and assets/ that your SKILL.md references

---

## Learning Objectives

By the end of this module, you will be able to:

- Know when to bundle scripts vs. inline instructions
- Write helper scripts that are token-efficient and deterministic
- Create reference files for progressive disclosure
- Add asset templates used in output generation

---

## Theory

### 1. When to Bundle a Script

Not every task needs a script. Many skills work perfectly well with inline instructions in SKILL.md. But some tasks are better handled by executable code. Use a script when any of these conditions are true:

**The same code is rewritten repeatedly.** If Claude generates the same parsing logic or shell pipeline every time the skill runs, extract it into a script. Writing `scripts/parse_commits.py` once means Claude never has to regenerate that logic -- it just calls the script.

**Deterministic reliability is needed.** Language instructions like "categorize commits by their prefix" leave room for interpretation. Code doesn't. A Python script that parses conventional commit messages will produce identical output for identical input every time. Claude interpreting a paragraph of parsing rules might miscategorize an edge case one time in ten.

**The task is computationally intensive.** Parsing 500 commits, filtering by regex, sorting by date, grouping by category -- this is work better done by a script in milliseconds than by Claude token-by-token. Scripts run outside the context window, which means they don't consume tokens during execution.

**Key benefits of scripts:**

- **Token-efficient.** Scripts execute without being loaded into context. Claude reads the output, not the source code.
- **Deterministic.** Code runs the same way every time. Language instructions can drift.
- **Reusable.** A well-written script works across different skill invocations without modification.
- **Testable.** You can unit test a Python script. You can't unit test a paragraph of instructions.

**When NOT to use a script:**

- The task is simple enough that a single shell command handles it (e.g., `git tag --sort=-v:refname | head -1`)
- The logic changes frequently and you want Claude to adapt on the fly
- The script would require dependencies not present on the target machine

**Example:** Consider validation checks. You could write in SKILL.md: "Verify the repository has at least one commit by running `git rev-parse HEAD`." That works for a single check. But if you need to verify: the directory is a git repo, it's not a shallow clone, it has at least one tag, and the range is valid -- that's four checks. A script runs all four and returns a structured result. Instructions would mean four separate tool calls and four paragraphs of "if this fails, do that."

---

### 2. Script Best Practices

Scripts bundled with skills should be reliable, self-documenting, and easy for Claude to call.

**Make scripts executable with proper shebangs.**

```python
#!/usr/bin/env python3
```

```bash
#!/usr/bin/env bash
```

The shebang tells the OS which interpreter to use. `env` finds the interpreter on the PATH, which is more portable than hardcoding `/usr/bin/python3`.

**Document usage at the top of each script.**

```python
#!/usr/bin/env python3
"""Parse git commits into structured JSON.

Usage:
    python3 parse_commits.py [git-range]
    python3 parse_commits.py v1.0..HEAD
    python3 parse_commits.py              # defaults to latest tag..HEAD

Output:
    JSON array of commit objects to stdout.
"""
```

This documentation serves two audiences: Claude (which may read the file to understand how to call it) and human developers maintaining the skill.

**Accept parameters for flexibility.**

Don't hardcode paths, ranges, or formats. Accept them as command-line arguments with sensible defaults:

```python
git_range = sys.argv[1] if len(sys.argv) > 1 else get_default_range()
```

This makes the script reusable across different invocations without modification.

**Return structured output (JSON when possible).**

Claude processes structured data far more reliably than free-form text. Instead of printing human-readable summaries, output JSON:

```python
# Good: structured output Claude can process
print(json.dumps(commits, indent=2))

# Less good: free-form text Claude has to parse
for commit in commits:
    print(f"{commit['hash']} - {commit['subject']}")
```

JSON output lets Claude extract exactly the fields it needs for formatting, filtering, or further processing.

**Handle errors gracefully with clear error messages.**

Scripts should never crash silently or dump stack traces. Return error information in a structure Claude can interpret:

```python
if not is_git_repo():
    print(json.dumps({"error": "Not a git repository", "suggestion": "Run from a directory containing a .git folder"}))
    sys.exit(1)
```

The error message tells Claude what went wrong and what to do about it. Claude can then relay this to the user in natural language.

---

### 3. Reference Files

Reference files live in `references/` and contain detailed documentation that the SKILL.md body links to but doesn't include inline. They are the third level of progressive disclosure: loaded only when Claude needs them.

**Why move content to references/:**

- **Keeps SKILL.md focused.** The body should stay under 500 lines. If your conventional commit specification alone is 200 lines, that's 40% of your budget spent on reference material that's only relevant during the categorization step.
- **Claude loads references only when needed.** If the user asks for a simple date-based changelog, Claude may never need the full conventional commit spec. Progressive disclosure means it only reads `references/conventional-commits.md` when it encounters commits that need categorization.
- **Allows variant-based organization.** A cloud deployment skill might have `references/aws.md`, `references/gcp.md`, and `references/azure.md`. Claude reads only the file that matches the user's environment, saving tokens and reducing noise.

**Formatting guidelines:**

- For files over 300 lines, include a table of contents at the top so Claude can navigate by heading
- Use consistent heading structure (H2 for major sections, H3 for subsections)
- Include examples for every concept -- Claude applies rules more reliably when it has seen examples

**Linking from SKILL.md:**

Always reference files explicitly so Claude knows where to look:

```markdown
For conventional commit type definitions, consult `references/conventional-commits.md`.
```

Don't say "see the references folder" -- be specific about which file and what it contains. Claude treats these as navigation instructions: the clearer the pointer, the faster it finds the right information.

---

### 4. Assets

Assets live in `assets/` and contain templates, fonts, icons, or other files used during output generation. The critical distinction between assets and references:

- **References** are loaded into context for Claude to read and learn from
- **Assets** are used during output creation -- Claude applies them as templates or copies their structure

A changelog template in `assets/changelog-template.md` defines the exact markdown structure every changelog should follow. Claude reads the template, then generates content that conforms to it. This produces more consistent output than describing the format in prose.

Other examples of assets:
- An HTML email template the skill fills in with generated content
- A JSON schema that defines the expected output structure
- A header/footer file prepended/appended to generated documents

Assets are never loaded for their informational content. They exist to standardize output.

---

### 5. Progressive Disclosure in Practice

Here is the complete decision framework for where to put each piece of content in your skill:

| Level | Location | What goes here | When it's loaded | Token budget |
|-------|----------|---------------|-----------------|-------------|
| **Level 1** | Frontmatter | Skill name + description | Always (in available_skills list) | ~100 words |
| **Level 2** | SKILL.md body | Core workflow, key instructions, examples, troubleshooting | When skill activates | <500 lines |
| **Level 3** | references/ | Detailed docs, variant guides, API patterns, edge case catalogs | When Claude navigates to them | No hard limit |
| **Never loaded** | scripts/ | Executable code (run, not read) | Executed, not loaded into context | N/A |
| **Never loaded** | assets/ | Output templates, static files | Applied during generation | N/A |

The "never loaded" row is worth emphasizing. Scripts and assets are *used* but not *read into context*. Claude runs a script and reads its output. Claude applies a template's structure. But the source code of `parse_commits.py` and the raw template file don't consume context window tokens during normal execution.

This means you can write a 200-line Python script without worrying about context budget. The only thing that enters the context is the script's output (the JSON array of parsed commits).

**A practical test for placement decisions:**

1. Does Claude need this to decide whether to activate? Put it in the frontmatter description.
2. Does Claude need this on every invocation? Put it in the SKILL.md body.
3. Does Claude need this only sometimes? Put it in references/.
4. Should Claude run this, not read it? Make it a script.
5. Should Claude use this as a structural template? Make it an asset.

---

## Exercises

### Exercise 3.1: Write a Helper Script

Write `scripts/parse_commits.py` for the git-changelog skill. This script replaces the commit parsing logic that would otherwise need to be described in prose and regenerated by Claude on every invocation.

**Requirements:**

1. Accept a git range as a command-line argument (e.g., `v1.0..HEAD`)
2. Default to `<latest-tag>..HEAD` if no argument is given, or the last 20 commits if no tags exist
3. Run `git log --no-merges --format=...` to extract commit data
4. Parse each commit's subject line for conventional commit format: `type(scope): description`
5. Categorize commits into types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, other
6. Output a JSON array to stdout with objects containing: hash, short_hash, type, scope, subject, body, date, author
7. Handle errors gracefully:
   - Not a git repository: print JSON error and exit 1
   - Invalid range: print JSON error and exit 1
   - No commits found: print empty JSON array

**Testing your script:**

```bash
# Navigate to any git repository
cd /path/to/a/git/repo

# Run with default range
python3 /path/to/parse_commits.py

# Run with specific range
python3 /path/to/parse_commits.py HEAD~5..HEAD

# Check the output is valid JSON
python3 /path/to/parse_commits.py | python3 -m json.tool
```

Verify that:
- The output is valid JSON
- Each commit has all required fields
- Conventional commit prefixes are correctly parsed (a commit message "feat(auth): add SSO" should produce type="feat", scope="auth", subject="add SSO")
- Non-conventional commits get type="other" and scope=null

**Reference solution:** See `solutions/git-changelog/scripts/parse_commits.py`

---

### Exercise 3.2: Write a Reference File

Write `references/conventional-commits.md` for the git-changelog skill. This file is loaded by Claude when it needs to understand how to categorize commits.

**Requirements:**

1. Explain what conventional commits are (1-2 paragraphs)
2. Document the full type list with descriptions:
   - feat, fix, docs, style, refactor, perf, test, build, ci, chore
3. Explain breaking change notation:
   - The `BREAKING CHANGE:` footer
   - The `!` after the type (e.g., `feat!: remove legacy API`)
4. Document scope conventions (when to use scopes, common scope patterns)
5. Provide examples of well-formed and poorly-formed commit messages
6. Explain how git-changelog uses this information (mapping types to changelog headings)

**Guidelines:**

- Keep it under 300 lines (if over, add a table of contents)
- Use tables for the type list -- Claude processes tabular data efficiently
- Include at least 3 examples of good commits and 3 examples of bad commits
- Write for Claude as the primary reader, not a human developer

**Reference solution:** See `solutions/git-changelog/references/conventional-commits.md`

---

### Exercise 3.3: Create an Asset Template

Write `assets/changelog-template.md` -- the template that defines the exact structure of every generated changelog.

**Requirements:**

1. Version header with date placeholder
2. Sections for each commit type (Breaking Changes, Features, Bug Fixes, Documentation, Refactoring, Performance, Tests, Maintenance)
3. Individual commit entry format with scope, description, and hash link
4. Breaking changes section positioned first (they require user action)
5. Contributors section at the bottom
6. Instructions (as markdown comments) for how to use the template

**Guidelines:**

- Use placeholders that Claude can recognize and fill in (e.g., `{{version}}`, `{{date}}`)
- Include markdown comments (`<!-- -->`) with instructions for optional sections
- Omit sections that have zero entries (note this as a comment in the template)

**Reference solution:** See `solutions/git-changelog/assets/changelog-template.md`

---

### Exercise 3.4: Validate the Full Structure

Now that you have all the supporting files, verify the complete skill folder is correct.

**Step 1: Run quick_validate.py**

```bash
python3 ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py student-workspace/git-changelog/
```

You should see `Skill is valid!`

**Step 2: Verify all referenced files exist**

Open your SKILL.md and find every file path reference. For each one, confirm the file exists:

```bash
# These should all exist:
ls student-workspace/git-changelog/scripts/parse_commits.py
ls student-workspace/git-changelog/references/conventional-commits.md
ls student-workspace/git-changelog/assets/changelog-template.md
```

If SKILL.md references a file that doesn't exist, either create the file or update the reference.

**Step 3: Check directory structure**

```bash
find student-workspace/git-changelog/ -type f | sort
```

Expected output:
```
student-workspace/git-changelog/SKILL.md
student-workspace/git-changelog/assets/changelog-template.md
student-workspace/git-changelog/references/conventional-commits.md
student-workspace/git-changelog/scripts/parse_commits.py
```

No extra files, no missing files. Every file in the directory should be referenced from SKILL.md, and every reference in SKILL.md should point to an existing file.

**Step 4: Test the script**

```bash
cd /any/git/repo
python3 /path/to/student-workspace/git-changelog/scripts/parse_commits.py | python3 -m json.tool
```

Confirm the output is valid JSON with the expected structure.

---

## Key Takeaways

1. **Scripts replace repetitive, error-prone generation.** If Claude would write the same parsing logic every time, extract it into a script. The script runs deterministically; Claude just consumes the output.

2. **Scripts are token-free at runtime.** They execute outside the context window. A 200-line Python script costs zero context tokens -- only its output enters the conversation. This makes scripts the most token-efficient way to handle complex data processing.

3. **Reference files are progressive disclosure level 3.** They keep the SKILL.md body focused on the primary workflow while making detailed documentation available on demand. Link to them explicitly: "consult `references/conventional-commits.md` for type definitions."

4. **Assets standardize output, not knowledge.** Unlike references (which Claude reads to learn), assets are templates Claude applies during generation. A changelog template produces more consistent output than describing the format in prose.

5. **The placement test:** Always in context? Frontmatter. Every invocation? SKILL.md body. Sometimes? References. Run, don't read? Scripts. Structural template? Assets.

---

**Next module:** [Module 4 -- Manual Testing](../module-04-manual-testing/) -- test your skill against real prompts and iterate on the results.
