<!--
  CHANGELOG TEMPLATE
  ==================
  This template is used by the git-changelog skill to generate formatted
  changelogs. Fill in the placeholders (wrapped in {{ }}) with actual data
  from the parsed git history.

  Usage:
  1. Replace all {{ placeholder }} values with real data.
  2. Remove any section (### heading + its entries) that has zero commits.
  3. Keep sections in the order shown below -- Breaking Changes always first.
  4. The Contributors section is optional; include it for release notes,
     omit it for incremental changelogs.
  5. Delete these HTML comments before publishing.

  Placeholder reference:
    {{ version }}           - Semantic version string (e.g., v1.3.0)
    {{ date }}              - Release date in ISO 8601 (e.g., 2026-03-12)
    {{ bump_type }}         - Suggested bump: major, minor, or patch
    {{ bump_justification }}- E.g., "2 features, 3 fixes, 0 breaking changes"
    {{ description }}       - Commit description with prefix stripped
    {{ short_hash }}        - 7-character abbreviated commit hash
    {{ scope }}             - Optional scope in bold (e.g., **api:**), omit if empty
    {{ author }}            - Commit author display name
    {{ commit_count }}      - Number of commits by this author
    {{ total_commits }}     - Total commits in this release
    {{ previous_version }}  - The version this changelog starts from
-->

# Changelog

## [{{ version }}] - {{ date }}

<!-- Summarize the release in one line. Include the bump suggestion. -->
{{ bump_type | capitalize }} bump suggested: {{ bump_justification }}.

<!--
  SECTION ORDER: Do not rearrange. Breaking Changes must appear first
  because they require action from consumers. Remove empty sections entirely.
-->

### Breaking Changes
<!-- Include ALL commits with breaking change indicators (! or BREAKING CHANGE footer) -->
- {{ scope }} {{ description }} ({{ short_hash }})

### New Features
<!-- Type: feat, feature -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Bug Fixes
<!-- Type: fix, bugfix -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Performance
<!-- Type: perf -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Refactoring
<!-- Type: refactor -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Documentation
<!-- Type: docs -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Tests
<!-- Type: test, tests -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Maintenance
<!-- Type: chore, build, ci -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Style
<!-- Type: style -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Reverts
<!-- Type: revert -->
- {{ scope }} {{ description }} ({{ short_hash }})

### Other Changes
<!-- Commits that do not match any conventional commit type -->
- {{ description }} ({{ short_hash }})

<!--
  CONTRIBUTORS SECTION
  Include for release notes. Omit for incremental/weekly changelogs.
  Sort by commit count descending.
-->

### Contributors
- {{ author }} ({{ commit_count }} commits)

---

<!--
  FOOTER
  Link the version tag comparison for easy diffing on GitHub/GitLab.
  Adjust the URL pattern to match your hosting platform.
-->
[{{ version }}]: https://github.com/OWNER/REPO/compare/{{ previous_version }}...{{ version }}

<!--
  MULTIPLE RELEASES
  When prepending to an existing CHANGELOG.md, insert the new release block
  (from ## [version] through the --- separator) directly below the # Changelog
  heading and above the previous release. Keep newest releases at the top.

  Example structure:
    # Changelog
    ## [v1.3.0] - 2026-03-12    <-- newest
    ...
    ## [v1.2.0] - 2026-02-15    <-- previous
    ...
    ## [v1.1.0] - 2026-01-20    <-- older
    ...
-->
