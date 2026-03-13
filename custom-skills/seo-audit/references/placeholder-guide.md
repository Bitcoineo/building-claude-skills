# Placeholder Reference — SEO Audit Report

When generating the report from `assets/seo-report.html`, replace these placeholders with actual data.

## Placeholder Table

| Placeholder | Description |
|---|---|
| `{{SITE_DOMAIN}}` | Root domain being audited (e.g., "example.com") |
| `{{PAGE_COUNT}}` | Number of pages audited |
| `{{REPORT_DATE}}` | Current date in "March 6, 2026" format |
| `{{OVERALL_SCORE}}` | Computed overall score 0-100 |
| `{{SCORE_DASHOFFSET}}` | SVG ring offset: `502 - (502 * score / 100)` rounded to integer |
| `{{GRADE}}` | Letter grade (A+, A, B, C, D, F) |
| `{{SCORE_HEADLINE}}` | One-line assessment summary |
| `{{SCORE_SUMMARY}}` | 2-3 sentence explanation |
| `{{TECH_SCORE}}`, `{{CONTENT_SCORE}}`, `{{ARCH_SCORE}}`, `{{CROSS_SCORE}}`, `{{SOCIAL_SCORE}}` | Category scores 0-100 |
| `{{*_SCORE_COLOR}}` | CSS color: `var(--green)` for 80+, `var(--yellow)` for 60-79, `var(--orange)` for 40-59, `var(--red)` for <40 |
| `{{CRITICAL_COUNT}}`, `{{HIGH_COUNT}}`, `{{WARNINGS_COUNT}}` | Issue counts by severity |
| `{{AVG_WORD_COUNT}}` | Average word count across pages |
| `{{SCHEMA_COVERAGE}}` | Percentage of pages with schema markup |
| `{{SITEWIDE_ISSUE_COUNT}}` | Total site-wide issues |
| `{{KEY_FINDINGS_PARAGRAPH}}` | 3-5 sentence summary |
| `{{TOP_3_PRIORITIES}}` | HTML for 3 action-item divs |
| `{{PAGE_TABLE_ROWS}}` | HTML table rows for page summary |
| `{{PAGE_DETAIL_COLLAPSIBLES}}` | HTML for per-page collapsible sections |
| `{{DUPLICATE_CONTENT_FINDINGS}}` | HTML finding items for duplicate content |
| `{{CONSISTENCY_FINDINGS}}` | HTML finding items for consistency issues |
| `{{ROBOTS_SITEMAP_FINDINGS}}` | HTML finding items for robots/sitemap |
| `{{SECURITY_HEADERS_FINDINGS}}` | HTML finding items for security headers |
| `{{TECHNICAL_CHECKLIST}}` | HTML checklist items |
| `{{SCHEMA_STRATEGY}}` | HTML table or findings for schema |
| `{{PERFORMANCE_FINDINGS}}` | HTML findings for performance |
| `{{THIN_PAGES}}`, `{{STRONG_PAGES}}`, `{{TOTAL_WORDS}}`, `{{MISSING_META}}` | Content health stats |
| `{{KEYWORD_MAP_ROWS}}` | HTML table rows for keyword map |
| `{{CONTENT_CLUSTERS}}` | HTML cluster cards |
| `{{CONTENT_GAPS}}` | HTML for content gap recommendations |
| `{{TOTAL_INTERNAL_LINKS}}`, `{{ORPHAN_PAGES}}`, `{{DEAD_END_PAGES}}`, `{{AVG_LINKS_PER_PAGE}}` | Linking stats |
| `{{LINK_EQUITY_ROWS}}` | HTML table rows for link equity |
| `{{ORPHAN_PAGES_DETAIL}}` | HTML for orphan page details |
| `{{SUGGESTED_LINKS}}` | HTML for suggested internal links |
| `{{QUICK_WINS}}`, `{{HIGH_IMPACT_ACTIONS}}`, `{{STRATEGIC_ACTIONS}}` | HTML action-item divs |
| `{{FULL_CHECKLIST}}` | HTML checklist items |

## HTML Snippet Patterns

### Finding Item

```html
<div class="finding">
  <div class="finding-status [pass|warning|fail]"></div>
  <div class="finding-content">
    <h4>[Concise title]</h4>
    <p>[Description of what was found and why it matters]</p>
    <div class="finding-rec">[Specific, actionable recommendation]</div>
  </div>
  <span class="badge badge-[critical|high|medium|low]">[Level]</span>
</div>
```

### Action Item

```html
<div class="action-item">
  <div class="action-number">[N]</div>
  <div class="action-content">
    <div class="action-title">[Action title]</div>
    <div class="action-desc">[What to do and how]</div>
    <div class="action-impact">Expected impact: [description]</div>
  </div>
  <span class="badge badge-[critical|high|medium|low]">[Level]</span>
</div>
```

### Collapsible Page Detail

```html
<div class="collapsible">
  <div class="collapsible-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="collapsible-title">
      <span class="page-url">[/page-url]</span>
      <span class="badge badge-[worst_severity]">[N] issues</span>
    </span>
    <span class="collapse-icon">&#9660;</span>
  </div>
  <div class="collapsible-body">
    <div class="collapsible-body-inner">
      [Finding items for this page]
    </div>
  </div>
</div>
```
