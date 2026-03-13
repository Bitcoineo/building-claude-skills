---
name: seo-audit
version: 1.0.0
description: >-
  Full website SEO audit. Crawls up to 15 pages, analyzes technical SEO,
  content quality, site architecture, cross-page patterns, and internal
  linking. Produces a scored interactive HTML report with findings, action
  plan, and per-page details. Use when user asks to "audit my site", "full
  SEO audit", "website SEO review", "check my site's SEO", "SEO health
  check", or "site audit". Do NOT use for optimizing a single article or
  page (use /seo-optimize), general website design, performance profiling,
  or security audits.
allowed-tools:
  - WebSearch
  - WebFetch
  - Read
  - Glob
  - Write
  - Bash
  - AskUserQuestion
---

# Full Website SEO Audit

Crawl and analyze a website's SEO health across multiple pages. Evaluate technical SEO, content quality, site architecture, cross-page patterns, and internal linking. Produce a scored, interactive HTML report with prioritized findings and an action plan.

## Step 1: Intake

Use AskUserQuestion to gather essential context. Present all questions in one message.

**Essential (always ask):**

1. **Target keywords** — "What are the top 3-5 keywords your site should rank for? If unsure, say 'analyze and suggest' and I'll infer from your content."
2. **Business type & audience** — "Briefly describe your business and target audience."
3. **SEO goals** — "What's your primary goal? (more organic traffic / rank for specific keywords / improve local SEO / fix technical issues / build content strategy / other)"

**Optional (ask only if context is missing):**

- Geographic focus — infer from site content if not provided
- Competitor URLs — find via search if not provided
- LSI/semantic keyword priorities — extract from content and competitors if not provided
- Known issues — helpful but not required to proceed

**Processing rules:**
- If user says "analyze and suggest" for keywords: infer from page content, highlight suggestions in the Content Strategy tab for user review.
- If user provides specific keywords: evaluate every page against those keywords, check cannibalization and coverage.
- If user provides competitor URLs: include in analysis, compare structure and keyword coverage.
- Store all answers and reference throughout every step.

## Step 2: Collect Pages

### Live URL (root domain or homepage)

1. Use WebFetch to retrieve the homepage HTML.
2. Parse all internal links from the HTML — `<a href="...">` tags where the href starts with `/` or the same domain. Exclude static assets, anchors, and query-only variations.
3. Deduplicate links. Remove query parameters and fragments.
4. Select up to 15 pages to audit (always include homepage):
   - Main navigation links (in `<nav>` or `<header>`)
   - Key content pages (blog posts, service pages, about, contact)
   - Pages at different URL depths to assess architecture
5. Use WebFetch to retrieve each page's HTML.
6. Also fetch: `{domain}/robots.txt`, `{domain}/sitemap.xml`, `{domain}/sitemap_index.xml`

### Local directory

1. Use Glob to find all HTML files: `{directory}/**/*.html`
2. Use Read to load each file (up to 15).
3. Treat root `index.html` as homepage.
4. robots.txt and sitemap.xml: check if they exist in the directory.

### Data to Extract Per Page

**Meta:** title tag (content + char count), meta description (content + char count), meta robots, canonical, viewport, lang attribute.

**Headings:** H1 (content + count — should be exactly 1), H2s, H3s, hierarchy validation (no skipped levels).

**Content:** Word count (visible text only — exclude nav, footer, script, style), reading time (200 wpm), paragraph count, image count, image alt text presence.

**Links:** Internal link count and hrefs (for cross-page analysis), external link count, broken-looking links (href="#", javascript:void(0), empty).

**Technical:** Schema/structured data (JSON-LD or microdata), Open Graph tags (title, description, image, url), Twitter Card tags, favicon, external CSS/JS count, modern image formats (WebP/AVIF), lazy loading, preload/preconnect, breadcrumbs, hreflang.

## Step 3: Site-Wide Resource Analysis

### robots.txt
- Exists and valid? User-agents specified? Important paths blocked? Sitemap referenced? Crawl-delay directives?

### sitemap.xml
- Exists and valid XML? URL count? Are audited pages included? Recent lastmod dates? Index sitemap pointing to sub-sitemaps?

### Server Headers (live URLs only)
Examine response headers from WebFetch:
- HTTPS, HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- Cache-Control/Expires headers, Content-Encoding (gzip/brotli), Server header (flag if version exposed)

## Step 4: Per-Page Analysis

Evaluate each page and assign PASS, WARNING, or FAIL per check.

### On-Page SEO

| Check | PASS | WARNING | FAIL |
|-------|------|---------|------|
| Title tag | Present, 30-60 chars, descriptive | Too short/long or generic | Missing |
| Meta description | Present, 120-160 chars | Too short/long | Missing |
| H1 tag | Exactly one, descriptive | Multiple H1s | None |
| Heading hierarchy | Logical (H1>H2>H3) | Minor skips (H2>H4) | No headings or severely broken |
| Content length | 300+ words | 150-299 (thin) | <150 (extremely thin) |
| Image alt text | All images have alt | Some missing | Most/all missing |
| Canonical | Present, correct URL | Points to different URL | Missing |

### Technical SEO

| Check | PASS | FAIL |
|-------|------|------|
| Viewport meta | Present with proper content | Missing |
| Structured data | Valid JSON-LD or microdata | None |
| Open Graph | All 4 core tags present | Missing or incomplete |
| Twitter Card | Tags present and complete | Missing |

## Step 5: Cross-Page Analysis

### Duplicate Content
Compare title tags, meta descriptions, and H1 tags across all pages. Flag exact duplicates.

### Keyword Cannibalization
Infer target keyword per page (from title, H1, first 150 words). Flag pages targeting the same keyword. Recommend which page should be canonical.

### Internal Linking
Build a link matrix: which pages link to which. Calculate:
- Internal links received per page (equity distribution)
- **Orphan pages** — zero internal links from other audited pages
- **Hub pages** — link out to many internal pages
- **Dead ends** — no outgoing internal links
- Suggest specific links to add: "Page A discusses X but doesn't link to Page B which covers X"

### Site Architecture
- URL structure consistency (lowercase, hyphens, no underscores, logical directories)
- Maximum click depth from homepage (target: max 3 clicks)
- Flat vs deep architecture assessment

### Content Theme Clustering
Group pages by topic/theme. Identify pillar page + cluster content opportunities. Note major topic gaps.

### LSI Coverage (Cross-Page)
For each target keyword from Step 1:
1. Identify 15-25 semantically related terms (use same extraction as /seo-optimize Step 2b)
2. Map which LSI terms appear on which pages
3. Flag important missing terms
4. Check for LSI cannibalization (same terms clustered on too few pages)

## Step 6: Scoring

Calculate scores per category (0-100). Consult `references/scoring-rubric.md` for the detailed point breakdowns and severity classification guide.

| Category | Weight |
|----------|--------|
| Technical SEO | 25% |
| Content | 25% |
| Architecture | 20% |
| Cross-Page | 15% |
| Social & Schema | 15% |

**Overall score** = weighted average. Grade: A+ (90-100), A (80-89), B (70-79), C (60-69), D (50-59), F (<50).

## Step 7: Generate the HTML Report

Generate a self-contained HTML report using the template at `assets/seo-report.html`. Replace all `{{PLACEHOLDER}}` values with data from the analysis. Do NOT improvise the design — use the template verbatim.

Consult `references/placeholder-guide.md` for the complete placeholder reference and HTML snippet patterns for findings, action items, and collapsible page details.

**Report tabs:**
1. **Overview** — Overall score, grade, executive summary, top 3 priorities
2. **Page Analysis** — Summary table + per-page collapsible details with PASS/WARNING/FAIL findings
3. **Technical** — Duplicate content, robots/sitemap, security headers, schema, performance
4. **Content Strategy** — Keyword map, content clusters, gaps, LSI coverage
5. **Internal Linking** — Link equity distribution, orphan pages, dead ends, suggested links
6. **Action Plan** — Prioritized quick wins, high-impact actions, strategic actions, full checklist

Save as `seo-audit-{DOMAIN}.html`. Open in the browser with `open <path>` and tell the user where it's saved.

## Important Rules

- **Be specific, not generic.** Every finding must reference actual URLs, content, or text. Never say "some pages have issues" — name the pages and the issues.
- **Prioritize ruthlessly.** Not all issues are equal. Communicate what matters most for ranking impact.
- **Think like a search engine.** Focus on crawlability, content quality, relevance signals, technical health.
- **Think like a site owner.** The report must be understandable by someone who is not an SEO expert. Explain WHY each issue matters.
- **Be honest about limitations.** This audit is HTML analysis only. It cannot measure actual page speed, backlink profile, Core Web Vitals, or real search rankings. Note these in the executive summary.

## Troubleshooting

1. **SPA with mostly empty HTML** — Note prominently. The audit is limited to initial HTML. Recommend SSR or pre-rendering.
2. **Site behind authentication** — Pages returning login redirects: note them, audit only accessible pages.
3. **WebFetch failures** — Report on pages that succeeded. Note which failed and why. If 50%+ fail, recommend the user provide a local directory export.
4. **Very large site (many pages found)** — Cap at 15 pages. Prioritize homepage, top-nav, and a sample at different depths. Note the audit covers a sample, not the full site.
5. **Subdomains** — Only audit the domain the user specified. Note if links to other subdomains are found.
6. **International sites** — Check hreflang consistency across pages if present.

## Bundled Resources

- `assets/seo-report.html` — HTML template for the interactive multi-tab audit report
- `references/placeholder-guide.md` — Complete placeholder reference and HTML snippet patterns
- `references/scoring-rubric.md` — Scoring weights, point breakdowns per category, and severity classification guide
