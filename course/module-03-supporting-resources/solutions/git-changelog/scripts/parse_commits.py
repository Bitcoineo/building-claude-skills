#!/usr/bin/env python3
"""Parse git commits into structured JSON for changelog generation.

Usage:
    python3 parse_commits.py [git-range]
    python3 parse_commits.py v1.0..HEAD
    python3 parse_commits.py HEAD~10..HEAD
    python3 parse_commits.py                  # defaults to latest tag..HEAD

Output:
    JSON array of commit objects to stdout. Each object contains:
        hash        - Full commit hash
        short_hash  - Abbreviated commit hash
        type        - Conventional commit type (feat, fix, docs, etc.) or "other"
        scope       - Conventional commit scope or null
        subject     - Commit subject with type/scope prefix stripped
        body        - Commit body (multi-line description) or empty string
        date        - ISO 8601 date string
        author      - Author name

Exit codes:
    0 - Success
    1 - Error (not a git repo, invalid range, etc.)

Errors are returned as JSON: {"error": "message", "suggestion": "what to do"}
"""

import json
import re
import subprocess
import sys


# Conventional commit types recognized by the changelog skill.
CONVENTIONAL_TYPES = {
    "feat", "fix", "docs", "style", "refactor",
    "perf", "test", "build", "ci", "chore",
    # Common aliases
    "feature", "bugfix", "tests",
}

# Pattern: type(scope): subject  OR  type: subject  OR  type!: / type!(scope): / type(scope)!:
# The ! can appear before or after the scope per the conventional commits spec
CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)"       # type (e.g., feat, fix)
    r"(?P<breaking1>!)?"          # optional ! before scope
    r"(?:\((?P<scope>[^)]+)\))?"  # optional (scope)
    r"(?P<breaking2>!)?"          # optional ! after scope
    r":\s*"                       # colon + space
    r"(?P<subject>.+)$"           # subject line
)


def run_git(*args):
    """Run a git command and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def error_exit(message, suggestion=""):
    """Print a JSON error to stdout and exit with code 1."""
    output = {"error": message}
    if suggestion:
        output["suggestion"] = suggestion
    print(json.dumps(output, indent=2))
    sys.exit(1)


def is_git_repo():
    """Check if the current directory is inside a git repository."""
    _, _, code = run_git("rev-parse", "--is-inside-work-tree")
    return code == 0


def get_latest_tag():
    """Return the most recent reachable tag, or None if no tags exist."""
    stdout, _, code = run_git("describe", "--tags", "--abbrev=0")
    if code == 0 and stdout:
        return stdout
    return None


def get_default_range():
    """Determine a sensible default commit range.

    Strategy:
        1. If tags exist, use <latest-tag>..HEAD
        2. Otherwise, use the last 20 commits
    """
    tag = get_latest_tag()
    if tag:
        return f"{tag}..HEAD"
    return None  # Signal to use --max-count instead


def parse_conventional_commit(subject):
    """Parse a conventional commit subject line.

    Returns:
        (type, scope, subject, is_breaking) if the subject matches the
        conventional commit format, otherwise ("other", None, subject, False).
    """
    match = CONVENTIONAL_RE.match(subject)
    if not match:
        return "other", None, subject, False

    commit_type = match.group("type").lower()
    scope = match.group("scope")
    clean_subject = match.group("subject")
    is_breaking = match.group("breaking1") == "!" or match.group("breaking2") == "!"

    # Normalize common aliases
    if commit_type == "feature":
        commit_type = "feat"
    elif commit_type == "bugfix":
        commit_type = "fix"
    elif commit_type == "tests":
        commit_type = "test"

    # If the type isn't recognized, classify as "other" but keep the full subject
    if commit_type not in CONVENTIONAL_TYPES:
        return "other", None, subject, False

    return commit_type, scope, clean_subject, is_breaking


def get_commits(git_range):
    """Fetch and parse commits for the given range.

    Args:
        git_range: A git revision range (e.g., "v1.0..HEAD") or None to
                   use the last 20 commits.

    Returns:
        A list of commit dictionaries.
    """
    # Field separator unlikely to appear in commit messages.
    sep = "---FIELD_SEP---"
    record_sep = "---RECORD_SEP---"

    # Format: hash, short_hash, date, author, subject, body
    fmt = f"%H{sep}%h{sep}%aI{sep}%an{sep}%s{sep}%b{record_sep}"

    cmd = [
        "log",
        "--no-merges",
        f"--format={fmt}",
    ]

    if git_range:
        cmd.append(git_range)
    else:
        # No tags -- fall back to last 20 commits
        cmd.append("--max-count=20")

    stdout, stderr, code = run_git(*cmd)

    if code != 0:
        if "unknown revision" in stderr or "bad revision" in stderr:
            error_exit(
                f"Invalid git range: {git_range}",
                "Check that the tag or commit reference exists. "
                "Run 'git tag' to see available tags.",
            )
        error_exit(
            f"git log failed: {stderr}",
            "Ensure you are in a valid git repository with commits.",
        )

    if not stdout:
        return []

    commits = []
    records = stdout.split(record_sep)

    for record in records:
        record = record.strip()
        if not record:
            continue

        fields = record.split(sep)
        if len(fields) < 5:
            continue

        full_hash = fields[0].strip()
        short_hash = fields[1].strip()
        date = fields[2].strip()
        author = fields[3].strip()
        subject = fields[4].strip()
        body = fields[5].strip() if len(fields) > 5 else ""

        commit_type, scope, clean_subject, is_breaking = parse_conventional_commit(subject)

        # Check for BREAKING CHANGE in the body
        if not is_breaking and body:
            if "BREAKING CHANGE:" in body or "BREAKING-CHANGE:" in body:
                is_breaking = True

        commit = {
            "hash": full_hash,
            "short_hash": short_hash,
            "type": commit_type,
            "scope": scope,
            "subject": clean_subject,
            "body": body,
            "date": date,
            "author": author,
            "breaking": is_breaking,
        }
        commits.append(commit)

    return commits


def main():
    # Verify we're in a git repository.
    if not is_git_repo():
        error_exit(
            "Not a git repository",
            "Run this script from within a git repository, "
            "or cd into one first.",
        )

    # Determine the commit range.
    if len(sys.argv) > 1:
        git_range = sys.argv[1]
    else:
        git_range = get_default_range()
        # git_range is None when no tags exist (falls back to --max-count)

    # Fetch and parse commits.
    commits = get_commits(git_range)

    # Output as JSON.
    print(json.dumps(commits, indent=2))


if __name__ == "__main__":
    main()
