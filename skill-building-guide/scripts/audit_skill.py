#!/usr/bin/env python3
"""Validate a Claude Code skill directory.

Usage:
    python3 audit_skill.py /path/to/skill-directory

Checks:
    - SKILL.md exists (exact name, case-sensitive)
    - YAML frontmatter is valid (--- delimiters, name, description)
    - Name is kebab-case with no spaces or capitals
    - Name does not contain "claude" or "anthropic"
    - Description is under 1024 characters
    - Description contains no angle brackets
    - Description includes trigger phrases (heuristic)
    - Body is under 500 lines
    - All files referenced in body actually exist
    - No README.md inside the skill folder
    - Folder name matches the name field

Output:
    PASS/WARN/FAIL for each check with explanations.
    Exit 0 if all pass, exit 1 if any fail.
"""

import os
import re
import sys


def parse_frontmatter(content):
    """Extract YAML frontmatter from SKILL.md content.

    Returns (frontmatter_dict, body_text, error_message).
    frontmatter_dict is None on parse failure.
    """
    lines = content.split("\n")

    # Find opening ---
    if not lines or lines[0].strip() != "---":
        return None, content, "No opening --- delimiter found"

    # Find closing ---
    closing_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break

    if closing_idx is None:
        return None, content, "No closing --- delimiter found"

    frontmatter_lines = lines[1:closing_idx]
    body_lines = lines[closing_idx + 1:]

    # Parse simple YAML (name and description fields)
    fm = {}
    current_key = None
    current_value_lines = []

    for line in frontmatter_lines:
        # Check for a new key: value pair
        key_match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if key_match and not line.startswith(" ") and not line.startswith("\t"):
            # Save previous key if exists
            if current_key:
                fm[current_key] = "\n".join(current_value_lines).strip()
            current_key = key_match.group(1)
            value = key_match.group(2).strip()
            # Handle >- or | block scalars
            if value in (">-", ">", "|", "|-"):
                current_value_lines = []
            else:
                # Strip surrounding quotes
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                current_value_lines = [value]
        elif current_key:
            # Continuation line for block scalar or multi-line value
            current_value_lines.append(line.strip())

    # Save last key
    if current_key:
        fm[current_key] = " ".join(current_value_lines).strip()

    body_text = "\n".join(body_lines)
    return fm, body_text, None


def find_file_references(body_text):
    """Find file paths referenced in the SKILL.md body.

    Looks for patterns like:
    - `scripts/something.py`
    - `references/something.md`
    - `assets/something.md`
    - scripts/something.py (without backticks)
    """
    refs = set()

    # Match backtick-wrapped paths
    backtick_pattern = r"`((?:scripts|references|assets)/[^`]+)`"
    refs.update(re.findall(backtick_pattern, body_text))

    # Match bare paths after common prepositions
    bare_pattern = r"(?:at|from|in|consult|use|read|run|see)\s+((?:scripts|references|assets)/\S+)"
    for match in re.findall(bare_pattern, body_text, re.IGNORECASE):
        # Strip trailing punctuation
        clean = match.rstrip(".,;:)")
        refs.add(clean)

    return refs


def check_kebab_case(name):
    """Return True if name is valid kebab-case."""
    return bool(re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name))


def run_checks(skill_dir):
    """Run all validation checks on the skill directory.

    Returns a list of (status, check_name, message) tuples.
    Status is one of: PASS, WARN, FAIL.
    """
    results = []
    skill_dir = os.path.abspath(skill_dir)
    folder_name = os.path.basename(skill_dir)

    # Check 1: SKILL.md exists
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md_path):
        results.append(("FAIL", "SKILL.md exists", f"No SKILL.md found at {skill_md_path}"))
        # Check for common mistakes
        for variant in ["skill.md", "Skill.md", "README.md", "readme.md"]:
            if os.path.isfile(os.path.join(skill_dir, variant)):
                results.append(("FAIL", "SKILL.md naming",
                                f"Found {variant} instead of SKILL.md. The file must be named exactly SKILL.md (all caps)."))
        return results  # Can't continue without SKILL.md
    else:
        results.append(("PASS", "SKILL.md exists", "Found SKILL.md at skill root"))

    # Check 2: No README.md inside skill folder
    readme_path = os.path.join(skill_dir, "README.md")
    if os.path.isfile(readme_path):
        results.append(("WARN", "No README.md",
                        "README.md found inside skill folder. Claude ignores README.md -- "
                        "all instructions belong in SKILL.md. Consider removing it or "
                        "moving it outside the skill directory for distribution purposes."))
    else:
        results.append(("PASS", "No README.md", "No README.md found (correct)"))

    # Read SKILL.md
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check 3: Frontmatter parsing
    fm, body_text, fm_error = parse_frontmatter(content)
    if fm_error:
        results.append(("FAIL", "Frontmatter parsing", fm_error))
        return results  # Can't continue without valid frontmatter
    else:
        results.append(("PASS", "Frontmatter parsing", "YAML frontmatter parsed successfully"))

    # Check 4: name field exists
    name = fm.get("name")
    if not name:
        results.append(("FAIL", "name field", "Required field 'name' is missing from frontmatter"))
    else:
        results.append(("PASS", "name field", f"name: {name}"))

    # Check 5: description field exists
    description = fm.get("description")
    if not description:
        results.append(("FAIL", "description field", "Required field 'description' is missing from frontmatter"))
    else:
        results.append(("PASS", "description field", f"description: {description[:80]}..."))

    # Check 6: name is kebab-case
    if name:
        if check_kebab_case(name):
            results.append(("PASS", "name kebab-case", f"'{name}' is valid kebab-case"))
        else:
            results.append(("FAIL", "name kebab-case",
                            f"'{name}' is not valid kebab-case. Use lowercase letters, numbers, "
                            f"and hyphens only. Example: 'my-skill-name'"))

    # Check 7: name does not contain reserved terms
    if name:
        name_lower = name.lower()
        if "claude" in name_lower:
            results.append(("FAIL", "name reserved terms",
                            f"'{name}' contains 'claude', which is a reserved term. "
                            f"Upload will be rejected."))
        elif "anthropic" in name_lower:
            results.append(("FAIL", "name reserved terms",
                            f"'{name}' contains 'anthropic', which is a reserved term. "
                            f"Upload will be rejected."))
        else:
            results.append(("PASS", "name reserved terms", "No reserved terms in name"))

    # Check 8: description length
    if description:
        desc_len = len(description)
        if desc_len > 1024:
            results.append(("FAIL", "description length",
                            f"Description is {desc_len} characters (max 1024). "
                            f"Trim to essentials: what it does, when to use it, key trigger phrases."))
        elif desc_len > 900:
            results.append(("WARN", "description length",
                            f"Description is {desc_len} characters (max 1024). "
                            f"Getting close to the limit. Consider tightening."))
        else:
            results.append(("PASS", "description length", f"Description is {desc_len} characters (max 1024)"))

    # Check 9: no angle brackets in description
    if description:
        if "<" in description or ">" in description:
            results.append(("FAIL", "description angle brackets",
                            "Description contains XML angle brackets (< or >). "
                            "These break the frontmatter parser. Use parentheses or quotes instead."))
        else:
            results.append(("PASS", "description angle brackets", "No angle brackets found"))

    # Check 10: description includes trigger phrases (heuristic)
    if description:
        desc_lower = description.lower()
        has_when = "when" in desc_lower or "use when" in desc_lower
        has_quotes = '"' in description or "'" in description
        has_trigger_words = any(w in desc_lower for w in [
            "use when", "use for", "use this", "trigger",
            "asks to", "asks for", "says", "wants to",
        ])

        if has_when or has_quotes or has_trigger_words:
            results.append(("PASS", "trigger phrases",
                            "Description appears to include trigger context"))
        else:
            results.append(("WARN", "trigger phrases",
                            "Description may be missing trigger phrases. "
                            "Include 'Use when...' or quoted phrases that describe when the skill "
                            "should activate. Without trigger phrases, the skill may never fire."))

    # Check 11: description includes negative triggers (heuristic)
    if description:
        desc_lower = description.lower()
        has_negative = any(phrase in desc_lower for phrase in [
            "do not use", "don't use", "not for", "do not",
            "not use for", "not applicable",
        ])
        if has_negative:
            results.append(("PASS", "negative triggers",
                            "Description includes negative triggers to prevent overtriggering"))
        else:
            results.append(("WARN", "negative triggers",
                            "No negative triggers found in description. Consider adding "
                            "'Do NOT use for [adjacent tasks]' to prevent overtriggering."))

    # Check 12: body line count
    body_lines = [line for line in body_text.split("\n") if line.strip()]
    body_line_count = len(body_text.split("\n"))
    if body_line_count > 500:
        results.append(("FAIL", "body length",
                        f"Body is {body_line_count} lines (max 500). "
                        f"Move detailed content to references/ to stay within budget."))
    elif body_line_count > 400:
        results.append(("WARN", "body length",
                        f"Body is {body_line_count} lines (max 500). "
                        f"Approaching the limit. Consider moving some content to references/."))
    elif body_line_count == 0:
        results.append(("WARN", "body length",
                        "Body is empty. Add instructions for the skill to follow."))
    else:
        results.append(("PASS", "body length", f"Body is {body_line_count} lines (max 500)"))

    # Check 13: folder name matches name field
    if name:
        if folder_name == name:
            results.append(("PASS", "folder name match", f"Folder '{folder_name}' matches name field '{name}'"))
        else:
            results.append(("FAIL", "folder name match",
                            f"Folder name '{folder_name}' does not match name field '{name}'. "
                            f"These must be identical. Rename the folder or update the name field."))

    # Check 14: all referenced files exist
    refs = find_file_references(body_text)
    if refs:
        all_exist = True
        for ref in sorted(refs):
            ref_path = os.path.join(skill_dir, ref)
            if os.path.exists(ref_path):
                results.append(("PASS", f"file ref: {ref}", f"Referenced file exists"))
            else:
                results.append(("FAIL", f"file ref: {ref}",
                                f"Referenced file does not exist at {ref_path}. "
                                f"Create the file or update the reference in SKILL.md."))
                all_exist = False
        if all_exist:
            results.append(("PASS", "all file references", f"All {len(refs)} referenced files exist"))
    else:
        results.append(("PASS", "all file references", "No file references found in body (OK for simple skills)"))

    return results


def print_report(results):
    """Print a formatted validation report."""
    print()
    print("=" * 70)
    print("  SKILL VALIDATION REPORT")
    print("=" * 70)
    print()

    pass_count = 0
    warn_count = 0
    fail_count = 0

    for status, check, message in results:
        if status == "PASS":
            icon = "\033[32mPASS\033[0m"
            pass_count += 1
        elif status == "WARN":
            icon = "\033[33mWARN\033[0m"
            warn_count += 1
        elif status == "FAIL":
            icon = "\033[31mFAIL\033[0m"
            fail_count += 1
        else:
            icon = status

        print(f"  [{icon}] {check}")
        if status != "PASS":
            # Wrap message for readability
            indent = "         "
            words = message.split()
            line = indent
            for word in words:
                if len(line) + len(word) + 1 > 75:
                    print(line)
                    line = indent + word
                else:
                    line = line + " " + word if line.strip() else indent + word
            if line.strip():
                print(line)
        print()

    print("-" * 70)
    print(f"  Results: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")
    print("-" * 70)

    if fail_count > 0:
        print("  Status: FAILED -- fix FAIL items before uploading")
    elif warn_count > 0:
        print("  Status: PASSED with warnings -- consider addressing WARN items")
    else:
        print("  Status: ALL CHECKS PASSED")

    print()
    return fail_count


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} /path/to/skill-directory")
        print()
        print("Validates a Claude Code skill directory structure,")
        print("frontmatter, and file references.")
        sys.exit(2)

    skill_dir = sys.argv[1]

    if not os.path.isdir(skill_dir):
        print(f"Error: '{skill_dir}' is not a directory")
        sys.exit(2)

    results = run_checks(skill_dir)
    fail_count = print_report(results)

    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
