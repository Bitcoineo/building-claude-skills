#!/usr/bin/env python3
"""Parse git commit history and output structured changelog data.

Reads git log output, parses conventional commit format, categorizes commits
by type, detects breaking changes, and outputs structured JSON or formatted
text suitable for changelog generation.

Usage:
    python3 parse_commits.py [range] [--format markdown|json|text] [--output FILE] [--categorize]

Examples:
    python3 parse_commits.py v1.0.0..HEAD
    python3 parse_commits.py --format json --categorize
    python3 parse_commits.py v1.2.0..v1.3.0 --format markdown --output CHANGELOG.md
"""

import argparse
import json
import re
import subprocess
import sys
from collections import OrderedDict
from datetime import date


# Conventional commit type aliases and their canonical forms
TYPE_ALIASES = {
    "feat": "feat",
    "feature": "feat",
    "fix": "fix",
    "bugfix": "fix",
    "docs": "docs",
    "style": "style",
    "refactor": "refactor",
    "perf": "perf",
    "test": "test",
    "tests": "test",
    "build": "build",
    "ci": "ci",
    "chore": "chore",
    "revert": "revert",
}

# Mapping from canonical type to changelog heading (in display order)
TYPE_HEADINGS = OrderedDict([
    ("breaking", "Breaking Changes"),
    ("feat", "New Features"),
    ("fix", "Bug Fixes"),
    ("perf", "Performance"),
    ("refactor", "Refactoring"),
    ("docs", "Documentation"),
    ("test", "Tests"),
    ("build", "Maintenance"),
    ("ci", "Maintenance"),
    ("chore", "Maintenance"),
    ("style", "Style"),
    ("revert", "Reverts"),
    ("other", "Other Changes"),
])

# Conventional commit pattern: type(scope)!: subject
# The ! can appear either before or after the scope per the spec:
#   feat!: breaking without scope
#   feat!(scope): breaking with scope
#   feat(scope)!: breaking with scope (also valid)
COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-zA-Z]+)"        # type (e.g., feat, fix)
    r"(?P<breaking1>!)?"            # optional ! before scope
    r"(?:\((?P<scope>[^)]*)\))?"    # optional scope in parens
    r"(?P<breaking2>!)?"            # optional ! after scope
    r":\s*"                         # colon and space
    r"(?P<subject>.+)$"             # subject line
)

GIT_LOG_FORMAT = "%H%x1f%h%x1f%aI%x1f%an%x1f%s%x1f%b%x00"


def check_git_repo():
    """Verify the current directory is inside a git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error: Not inside a git repository.", file=sys.stderr)
        sys.exit(1)


def resolve_default_range():
    """Resolve the default commit range (latest tag to HEAD).

    Falls back to the last 50 commits if no tags exist.
    """
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        latest_tag = result.stdout.strip()
        return f"{latest_tag}..HEAD"

    # No tags found -- use last 50 commits
    return "HEAD~50..HEAD"


def validate_range(git_range):
    """Validate that both ends of a git range exist."""
    parts = git_range.split("..")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        result = subprocess.run(
            ["git", "rev-parse", "--verify", part],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Error: Invalid git ref '{part}'.", file=sys.stderr)
            sys.exit(1)


def get_commits(git_range):
    """Run git log and return raw commit data.

    Returns a list of dicts with keys: hash, short_hash, date, author,
    subject, body.
    """
    cmd = [
        "git", "log", "--no-merges",
        f"--format={GIT_LOG_FORMAT}",
        git_range
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running git log: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    raw = result.stdout.strip()
    if not raw:
        print("No commits found in the specified range.", file=sys.stderr)
        sys.exit(0)

    commits = []
    # Split on null byte delimiter (each commit ends with \x00)
    entries = raw.split("\x00")
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        # Split on unit separator (\x1f) -- exactly 6 fields
        parts = entry.split("\x1f", 5)
        if len(parts) < 5:
            continue

        full_hash = parts[0].strip()
        short_hash = parts[1].strip()
        commit_date = parts[2].strip()
        author = parts[3].strip()
        subject = parts[4].strip()
        body = parts[5].strip() if len(parts) > 5 else ""

        commits.append({
            "hash": full_hash,
            "short_hash": short_hash,
            "date": commit_date,
            "author": author,
            "subject": subject,
            "body": body,
        })

    return commits


def parse_commit(commit):
    """Parse a single commit into structured fields.

    Extracts conventional commit type, scope, subject, and breaking change
    indicator. Returns an enriched commit dict.
    """
    subject = commit["subject"]
    body = commit.get("body", "")

    match = COMMIT_PATTERN.match(subject)
    if match:
        raw_type = match.group("type").lower()
        canonical_type = TYPE_ALIASES.get(raw_type, "other")
        scope = match.group("scope") or ""
        breaking_mark = (match.group("breaking1") is not None
                         or match.group("breaking2") is not None)
        parsed_subject = match.group("subject").strip()
        # Capitalize first letter
        if parsed_subject:
            parsed_subject = parsed_subject[0].upper() + parsed_subject[1:]
    else:
        canonical_type = "other"
        scope = ""
        breaking_mark = False
        parsed_subject = subject

    # Detect breaking changes from body footer
    has_breaking_footer = bool(
        re.search(r"^BREAKING[ -]CHANGE:\s*", body, re.MULTILINE)
    )
    is_breaking = breaking_mark or has_breaking_footer

    return {
        "hash": commit["hash"],
        "short_hash": commit["short_hash"],
        "type": canonical_type,
        "scope": scope,
        "subject": parsed_subject,
        "body": body,
        "date": commit["date"],
        "author": commit["author"],
        "breaking": is_breaking,
    }


def categorize_commits(parsed_commits):
    """Group parsed commits by their changelog category.

    Returns an OrderedDict mapping heading names to lists of commits.
    Breaking changes are always first.
    """
    categories = OrderedDict()

    # Initialize categories in display order
    seen_headings = set()
    for commit_type, heading in TYPE_HEADINGS.items():
        if heading not in seen_headings:
            categories[heading] = []
            seen_headings.add(heading)

    for commit in parsed_commits:
        if commit["breaking"]:
            categories["Breaking Changes"].append(commit)
        else:
            heading = TYPE_HEADINGS.get(commit["type"], "Other Changes")
            categories[heading].append(commit)

    # Remove empty categories
    return OrderedDict(
        (k, v) for k, v in categories.items() if v
    )


def suggest_version_bump(parsed_commits, current_version=None):
    """Suggest a semver bump based on commit types.

    Returns a dict with bump type, suggested version, and justification.
    """
    has_breaking = any(c["breaking"] for c in parsed_commits)
    has_feat = any(c["type"] == "feat" and not c["breaking"] for c in parsed_commits)

    type_counts = {}
    for commit in parsed_commits:
        t = commit["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    breaking_count = sum(1 for c in parsed_commits if c["breaking"])

    if has_breaking:
        bump = "major"
    elif has_feat:
        bump = "minor"
    else:
        bump = "patch"

    suggested = None
    if current_version:
        # Parse version string (strip leading 'v' if present)
        ver = current_version.lstrip("v")
        parts = ver.split(".")
        if len(parts) == 3:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            if bump == "major":
                suggested = f"v{major + 1}.0.0"
            elif bump == "minor":
                suggested = f"v{major}.{minor + 1}.0"
            else:
                suggested = f"v{major}.{minor}.{patch + 1}"

    justification_parts = []
    if breaking_count:
        justification_parts.append(f"{breaking_count} breaking")
    # Don't double-count: breaking commits are already counted above
    feat_count = sum(1 for c in parsed_commits if c["type"] == "feat" and not c["breaking"])
    fix_count = sum(1 for c in parsed_commits if c["type"] == "fix" and not c["breaking"])
    if feat_count:
        justification_parts.append(f"{feat_count} feature{'s' if feat_count != 1 else ''}")
    if fix_count:
        justification_parts.append(f"{fix_count} fix{'es' if fix_count != 1 else ''}")
    other_count = len(parsed_commits) - breaking_count - feat_count - fix_count
    if other_count:
        justification_parts.append(f"{other_count} other")

    return {
        "bump": bump,
        "suggested_version": suggested,
        "justification": ", ".join(justification_parts),
    }


def get_latest_tag():
    """Return the latest tag name, or None if no tags exist."""
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def format_markdown(categories, version_info):
    """Format categorized commits as Markdown."""
    lines = []

    version_str = version_info.get("suggested_version") or "vX.Y.Z"
    today = date.today().isoformat()
    bump = version_info["bump"]
    lines.append(f"## [{version_str}] - {today} (suggested: {bump} bump)")
    lines.append("")
    lines.append(f"{bump.capitalize()} bump suggested: {version_info['justification']}.")
    lines.append("")

    for heading, commits in categories.items():
        lines.append(f"### {heading}")
        for commit in commits:
            scope_part = f"**{commit['scope']}:** " if commit["scope"] else ""
            lines.append(f"- {scope_part}{commit['subject']} ({commit['short_hash']})")
        lines.append("")

    # Contributors section
    authors = {}
    for commits in categories.values():
        for commit in commits:
            author = commit["author"]
            authors[author] = authors.get(author, 0) + 1

    if authors:
        lines.append("### Contributors")
        for author, count in sorted(authors.items(), key=lambda x: -x[1]):
            lines.append(f"- {author} ({count} commit{'s' if count != 1 else ''})")
        lines.append("")

    return "\n".join(lines)


def format_json(parsed_commits, categories, version_info):
    """Format commits and categories as JSON."""
    today = date.today().isoformat()

    output = {
        "version": version_info.get("suggested_version", "").lstrip("v") or None,
        "date": today,
        "suggested_bump": version_info["bump"],
        "bump_justification": version_info["justification"],
        "categories": {},
        "commits": [],
    }

    for heading, commits in categories.items():
        output["categories"][heading] = [
            {
                "hash": c["short_hash"],
                "full_hash": c["hash"],
                "type": c["type"],
                "scope": c["scope"] or None,
                "description": c["subject"],
                "author": c["author"],
                "date": c["date"],
                "breaking": c["breaking"],
            }
            for c in commits
        ]

    for commit in parsed_commits:
        output["commits"].append({
            "hash": commit["short_hash"],
            "full_hash": commit["hash"],
            "type": commit["type"],
            "scope": commit["scope"] or None,
            "subject": commit["subject"],
            "body": commit["body"] or None,
            "date": commit["date"],
            "author": commit["author"],
            "breaking": commit["breaking"],
        })

    return json.dumps(output, indent=2)


def format_plain(categories, version_info):
    """Format categorized commits as plain text for terminal display."""
    lines = []

    version_str = version_info.get("suggested_version") or "X.Y.Z"
    version_str = version_str.lstrip("v")
    today = date.today().isoformat()
    bump = version_info["bump"]
    lines.append(f"VERSION {version_str} ({today}) - Suggested: {bump} bump")
    lines.append(f"{bump.capitalize()} bump suggested: {version_info['justification']}.")
    lines.append("")

    for heading, commits in categories.items():
        lines.append(heading.upper())
        for commit in commits:
            scope_part = f"[{commit['scope']}] " if commit["scope"] else ""
            lines.append(f"  - {scope_part}{commit['subject']} ({commit['short_hash']})")
        lines.append("")

    # Contributors
    authors = {}
    for commits in categories.values():
        for commit in commits:
            author = commit["author"]
            authors[author] = authors.get(author, 0) + 1

    if authors:
        lines.append("CONTRIBUTORS")
        for author, count in sorted(authors.items(), key=lambda x: -x[1]):
            lines.append(f"  - {author} ({count} commit{'s' if count != 1 else ''})")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Parse git commits and generate structured changelog data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "range",
        nargs="?",
        default=None,
        help="Git commit range (e.g., v1.0..HEAD). Defaults to latest tag..HEAD.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "text"],
        default="markdown",
        dest="output_format",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write output to file instead of stdout.",
    )
    parser.add_argument(
        "--categorize",
        action="store_true",
        help="Group commits by type in the output.",
    )

    args = parser.parse_args()

    # Validate environment
    check_git_repo()

    # Resolve range
    git_range = args.range or resolve_default_range()
    validate_range(git_range)

    # Extract and parse commits
    raw_commits = get_commits(git_range)
    if not raw_commits:
        print("No commits found in the specified range.", file=sys.stderr)
        sys.exit(0)

    parsed = [parse_commit(c) for c in raw_commits]

    # Version suggestion
    latest_tag = get_latest_tag()
    version_info = suggest_version_bump(parsed, latest_tag)

    # Output
    if args.categorize or args.output_format in ("markdown", "text"):
        categories = categorize_commits(parsed)

        if args.output_format == "markdown":
            output = format_markdown(categories, version_info)
        elif args.output_format == "text":
            output = format_plain(categories, version_info)
        else:
            output = format_json(parsed, categories, version_info)
    else:
        # JSON without categorization: flat commit list
        if args.output_format == "json":
            if args.categorize:
                categories = categorize_commits(parsed)
                output = format_json(parsed, categories, version_info)
            else:
                output = json.dumps(
                    {
                        "suggested_bump": version_info["bump"],
                        "bump_justification": version_info["justification"],
                        "commits": [
                            {
                                "hash": c["short_hash"],
                                "full_hash": c["hash"],
                                "type": c["type"],
                                "scope": c["scope"] or None,
                                "subject": c["subject"],
                                "body": c["body"] or None,
                                "date": c["date"],
                                "author": c["author"],
                                "breaking": c["breaking"],
                            }
                            for c in parsed
                        ],
                    },
                    indent=2,
                )
        else:
            output = format_markdown(categorize_commits(parsed), version_info)

    # Write or print
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
            if not output.endswith("\n"):
                f.write("\n")
        print(f"Changelog written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
