# Scoring Rubric & Severity Guide

## Scoring Categories

Calculate scores for each category on a 0-100 scale.

### Technical SEO Score (weight: 25%)

| Check | Points |
|-------|--------|
| HTTPS | 10 |
| Viewport meta on all pages | 10 |
| robots.txt valid | 10 |
| sitemap.xml valid | 10 |
| Schema markup coverage (proportional to % of pages) | 15 |
| Security headers (2 pts each: HSTS, CSP, X-Content-Type, X-Frame, Referrer-Policy) | 10 |
| Image optimization (modern formats, lazy loading) | 10 |
| Canonical tags present | 10 |
| Compression enabled (gzip/brotli) | 5 |
| Preload/preconnect hints | 5 |
| No blocked resources in robots.txt | 5 |

### Content Score (weight: 25%)

| Check | Points |
|-------|--------|
| Average word count above 300 | 20 |
| No thin content pages (<150 words) | 15 |
| All pages have unique titles | 15 |
| All pages have meta descriptions | 15 |
| All pages have H1 tags | 10 |
| Proper heading hierarchy on all pages | 10 |
| All images have alt text | 10 |
| No duplicate content detected | 5 |

### Architecture Score (weight: 20%)

| Check | Points |
|-------|--------|
| Consistent URL structure | 20 |
| Reasonable click depth (max 3 from homepage) | 20 |
| No orphan pages | 20 |
| No dead-end pages | 15 |
| Logical directory structure | 15 |
| Breadcrumb markup present | 10 |

### Cross-Page Score (weight: 15%)

| Check | Points |
|-------|--------|
| No duplicate titles | 20 |
| No duplicate meta descriptions | 20 |
| No keyword cannibalization | 25 |
| Good internal link distribution | 20 |
| Content theme coverage | 15 |

### Social & Schema Score (weight: 15%)

| Check | Points |
|-------|--------|
| OG tags on all pages | 30 |
| Twitter cards on all pages | 20 |
| Schema markup on all pages | 30 |
| Consistent branding in OG tags | 10 |
| Favicon present | 10 |

### Overall Score

Weighted average of all category scores.

| Score | Grade |
|-------|-------|
| 90-100 | A+ (Excellent) |
| 80-89 | A (Great) |
| 70-79 | B (Good, needs work) |
| 60-69 | C (Fair, significant issues) |
| 50-59 | D (Poor) |
| <50 | F (Critical issues) |

---

## Severity Classification Guide

### Critical
Issues that severely harm SEO or prevent indexing:
- No HTTPS
- robots.txt blocking important pages
- No title tags on key pages
- noindex on pages that should be indexed
- Broken canonical tags pointing to wrong URLs

### High
Issues with significant ranking impact:
- Missing meta descriptions on multiple pages
- Duplicate title tags across pages
- Keyword cannibalization between key pages
- No structured data at all
- No sitemap.xml
- Orphan pages (important pages with zero internal links)
- Thin content on primary pages (<150 words)

### Medium
Issues that noticeably affect SEO:
- Missing OG tags on some pages
- Inconsistent heading hierarchy
- Images without alt text
- No lazy loading on images
- Missing security headers (HSTS, CSP)
- Weak internal linking

### Low
Minor improvements and best practices:
- Missing Twitter Card tags
- No preload/preconnect hints
- Server version exposed in headers
- Minor heading hierarchy issues
- Missing hreflang (if not targeting international)
