# Changelog

<!--
  Changelog Template for git-changelog skill

  Usage: Claude reads this template and generates a changelog that follows
  this exact structure. Placeholders ({{...}}) are replaced with actual values.

  Rules:
  - Omit any section that has zero entries
  - Breaking Changes always appears first (when present)
  - Within each section, list commits in reverse chronological order
  - Include the short hash after each entry for traceability
  - If a commit has a scope, prefix the entry with the scope in bold
-->

## [{{version}}] - {{date}}

<!-- If no version tag is available, use a descriptive header instead:
     ## Changes ({{start_date}} to {{end_date}})
     ## Changes since {{base_ref}}
-->

### Breaking Changes

<!-- List any commit with a ! suffix or BREAKING CHANGE footer. These require
     action from users and must appear first regardless of commit type. -->

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### New Features

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### Bug Fixes

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### Documentation

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### Refactoring

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### Performance

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### Tests

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### Maintenance

<!-- Includes build, ci, and chore commit types -->

- **{{scope}}:** {{description}} ({{short_hash}})
- {{description}} ({{short_hash}})

### Other Changes

<!-- Commits that don't follow conventional commit format -->

- {{description}} ({{short_hash}})

---

### Contributors

<!-- Deduplicated list of commit authors, sorted alphabetically -->

- {{author_name}}

<!--
  Section ordering reference:
  1. Breaking Changes  (highest priority -- requires user action)
  2. New Features      (most interesting to end users)
  3. Bug Fixes         (second most interesting)
  4. Documentation     (helpful but lower impact)
  5. Refactoring       (internal changes)
  6. Performance       (internal improvements)
  7. Tests             (internal quality)
  8. Maintenance       (routine upkeep)
  9. Other Changes     (uncategorized)
  10. Contributors     (always last)
-->
