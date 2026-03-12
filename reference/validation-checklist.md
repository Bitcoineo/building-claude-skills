# Skill Validation Checklist

Pre-flight checklist for packaging and uploading a Claude Code custom skill.

---

## Before You Start

- [ ] **Use cases identified** -- You can name 3+ specific user requests this skill should handle. Vague scope leads to poor trigger matching.
- [ ] **Tools planned** -- You know which tools (Bash, Read, Edit, WebFetch, MCP, etc.) the skill needs. Unplanned tool use causes permission errors or over-broad access.
- [ ] **Reviewed the skill-authoring guide** -- Re-read the latest docs so you don't build against outdated conventions.

---

## During Development

### Structure

- [ ] **Folder uses kebab-case name** -- The folder name must match the `name` field exactly. Mismatches cause silent upload failures.
- [ ] **SKILL.md exists at the folder root** -- Not README.md, not skill.md. The file must be named `SKILL.md` or it will be ignored.
- [ ] **No extra top-level files that shouldn't ship** -- Stray files increase zip size and may confuse the runtime.

### Frontmatter

- [ ] **Opens and closes with `---`** -- Missing delimiters mean the entire frontmatter is treated as plain text instructions.
- [ ] **`name` is kebab-case, no spaces/capitals/underscores** -- Invalid names are silently rejected on upload.
- [ ] **`name` does not contain "claude" or "anthropic"** -- Reserved terms; the upload will fail.
- [ ] **`description` is under 1024 characters** -- Anything longer is truncated, potentially losing your trigger phrases.
- [ ] **`description` contains no XML angle brackets (`<` `>`)** -- They break frontmatter parsing and can cause injection issues.
- [ ] **`description` includes natural trigger phrases** -- This is what the router matches against. No trigger phrases means the skill never fires.
- [ ] **Quotes are properly closed** -- An unclosed quote swallows the rest of the frontmatter. Use block scalars (`>-`) for safety.

### Instructions (Body of SKILL.md)

- [ ] **Instructions are clear and self-contained** -- The LLM has no memory of your intent. Everything it needs must be in the file.
- [ ] **Error handling is specified** -- Tell the skill what to do when a command fails, a file is missing, or input is ambiguous. Unhandled errors produce confusing output.
- [ ] **Examples of expected input/output are included** -- Concrete examples reduce hallucinated behavior and anchor the skill's format.
- [ ] **References to external files use correct paths** -- Relative paths inside the skill package work; absolute paths to your machine do not.

---

## Before Upload

### Trigger Testing

- [ ] **Exact trigger phrases activate the skill** -- Test with the phrases listed in your description. If these don't work, nothing will.
- [ ] **Paraphrased requests also activate the skill** -- Real users won't use your exact wording. Test with 3+ rephrasings.
- [ ] **Unrelated requests do NOT activate the skill** -- False positives erode user trust. Test with adjacent-but-wrong prompts.

### Functional Testing

- [ ] **Core functionality produces correct output** -- Run the skill end-to-end on a real project. Verify the output, not just the absence of errors.
- [ ] **Tool integrations work** -- If the skill calls Bash, Read, Edit, or MCP tools, confirm each tool call succeeds with realistic inputs.
- [ ] **Edge cases are handled gracefully** -- Empty repos, missing dependencies, unsupported languages. The skill should fail informatively, not silently.

### Packaging

- [ ] **Compressed as a .zip file** -- The upload endpoint expects a zip archive of the skill folder. Tar, gzip, and bare folders are rejected.
- [ ] **Zip contains the folder at the root** -- The zip should contain `my-skill/SKILL.md`, not just `SKILL.md` at the top level.

---

## After Upload

- [ ] **Test in a real conversation** -- Synthetic tests miss integration issues. Open Claude Code, type a natural request, and confirm the skill activates and runs.
- [ ] **Monitor triggering accuracy** -- Use the skill for a few days. Note false positives (fires when it shouldn't) and false negatives (doesn't fire when it should).
- [ ] **Collect user feedback** -- If others use your skill, ask what confused them or what broke. First-party testing has blind spots.
- [ ] **Iterate on the description** -- Adjust trigger phrases based on real usage patterns. The description is the single biggest lever for activation quality.
- [ ] **Update the version in metadata** -- Bump the version on every publish so you can track which version users are running.
