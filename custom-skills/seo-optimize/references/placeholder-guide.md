# Placeholder Reference — SEO Article Report

When generating the report from `assets/seo-report.html`, replace these placeholders with actual data from the analysis.

## Placeholder Table

| Placeholder | Description |
|---|---|
| `{{ARTICLE_TITLE}}` | The article's title (used in page header and `<title>` tag) |
| `{{REPORT_DATE}}` | Current date in "March 6, 2026" format |
| `{{OVERALL_SCORE}}` | Computed SEO score 0-100 |
| `{{SCORE_DASHOFFSET}}` | SVG ring offset: `502 - (502 * score / 100)` rounded to integer |
| `{{SCORE_HEADLINE}}` | One-line assessment, e.g., "Good foundation, but missing key topics competitors cover" |
| `{{SCORE_SUMMARY}}` | 2-3 sentence explanation of what's strong and what needs work |
| `{{CONTENT_SCORE}}`, `{{KEYWORDS_SCORE}}`, `{{STRUCTURE_SCORE}}`, `{{TECHNICAL_SCORE}}` | Sub-scores 0-100 |
| `{{*_SCORE_COLOR}}` | CSS color: `var(--green)` for 80+, `var(--yellow)` for 60-79, `var(--orange)` for 40-59, `var(--red)` for <40 |
| `{{COMPETITORS_ANALYZED}}` | Number of competitors researched (e.g., "5") |
| `{{LSI_TOTAL}}` | Total LSI keywords identified |
| `{{CONTENT_GAPS_COUNT}}` | Number of content gaps found |
| `{{TARGET_KEYWORD_DENSITY}}` | Target density from competitors (e.g., "1.4%") |
| `{{TARGET_KEYWORD}}` | The primary target keyword |
| `{{COMPETITOR_CARDS}}` | HTML for all competitor cards (see HTML patterns below) |
| `{{KEYWORD_TABLE_ROWS}}` | HTML table rows for keyword strategy table |
| `{{LSI_CLOUD}}` | HTML for LSI tag cloud with integrated/missing classes |
| `{{CONTENT_GAPS_LIST}}` | HTML `<li>` items for content gaps |
| `{{STRUCTURAL_GAPS_LIST}}` | HTML `<li>` items for structural gaps |
| `{{UNIQUE_ADVANTAGES_LIST}}` | HTML `<li>` items for unique advantages |
| `{{KEYWORD_GAPS_LIST}}` | HTML `<li>` items for keyword gaps |
| `{{TITLE_TAG}}` | Optimized title tag |
| `{{META_DESCRIPTION}}` | Optimized meta description |
| `{{URL_SLUG}}` | Suggested URL slug |
| `{{NEW_KEYWORD_DENSITY}}` | Keyword density in revised article |
| `{{OLD_KEYWORD_DENSITY}}` | Keyword density in original article |
| `{{LSI_INTEGRATED}}` | Count of LSI keywords successfully integrated |
| `{{REVISED_ARTICLE_HTML}}` | Full revised article as HTML (h1, h2, h3, p, ul, ol, etc.) |
| `{{CHANGELOG_COUNT}}` | Total number of changes made |
| `{{CHANGELOG_CATEGORY_COUNT}}` | Number of change categories |
| `{{CHANGELOG_HTML}}` | Full changelog HTML (grouped by category with impact badges) |
| `{{ORIGINAL_ARTICLE_HTML}}` | Original article as HTML, unmodified |
