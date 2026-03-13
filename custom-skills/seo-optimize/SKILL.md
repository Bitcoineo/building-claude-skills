---
name: seo-optimize
version: 1.0.0
description: >-
  SEO-optimize a single article or page for higher Google rankings. Research
  competitors, build a keyword and LSI strategy, rewrite the content, and
  produce an interactive HTML report with revised article, changelog, and
  original for comparison. Use when user asks to "SEO optimize this article",
  "make this rank", "optimize this for Google", "improve this for SEO",
  "rewrite for SEO", or "help this article rank". Do NOT use for site-wide
  SEO audits (use /seo-audit), general writing improvement, copywriting,
  or content calendar planning.
allowed-tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

# SEO Article Optimization

Research what's ranking, understand why, and rewrite the user's article to compete with and surpass the top results. Every change is data-informed by competitor analysis, not guesswork.

The output is a self-contained HTML report with three tabs: Revised Article, Changelog, and Original.

## Step 1: Intake

Use AskUserQuestion to gather essential context before any research. Present all questions in one message.

**Essential (always ask):**

1. **Target keyword** — "What keyword or phrase do you want this article to rank for? If unsure, say 'suggest for me' and I'll infer from the article."
2. **Target audience** — "Who is the reader? (e.g., homeowners in the UK, first-time buyers, developers)"
3. **Constraints** — "Any constraints? Max word count, tone/voice, topics to avoid, mandatory sections or CTAs?"

**Optional (ask only if relevant context is missing):**

- Search intent (informational / transactional / commercial / navigational) — infer from keyword if not provided
- Geographic focus — infer from article content if not provided
- Specific competitor URLs to analyze — find automatically via search if not provided
- LSI/semantic keyword preferences — extract from competitors if not provided

**Processing rules:**
- If user says "suggest for me" for keywords: infer from the article, then confirm with user before proceeding.
- If user provides specific keywords: use those as definitive. Do NOT override with your own inference.
- Store all answers and reference them throughout every step.

## Step 2: Competitor Research

This is the most important step. Research what's ranking before making any changes.

### 2a. Find Top-Ranking Competitors

Use WebSearch for the target keyword. Examine the top 5-10 results.

For each, note: title tag, URL structure, meta description (if visible).

Use WebFetch to retrieve the full HTML of the top 3-5 pages. For each, extract:
- Title tag and H1
- All H2 and H3 headings (reveals subtopics competitors cover)
- Word count (approximate)
- Key topics and sections covered
- Content structure (listicle, how-to, comparison, etc.)

### 2b. Build Keyword & LSI Strategy

From the competitor pages, build a keyword map:

1. **Primary keyword** — From user's Step 1 answer. Confirm/refine based on competitor targeting.
2. **Secondary keywords** — Close variations and long-tail versions from competitor titles/H2s.
3. **LSI keywords** — Semantically related terms appearing in 2+ competitor pages. NOT synonyms — contextually related terms that signal topical depth to Google. This is one of the most powerful ranking signals.

**LSI extraction method:**
- Read competitor content for terms appearing in 2+ results
- Group by category: process terms, cost/pricing, trust/quality, problem, comparison, location
- Use WebSearch for "[keyword] related searches" and "people also ask"
- Target 20-40 LSI terms
- Include any user-provided LSI terms as priority inclusions

4. **Density targets** — Note competitor keyword density (typically 1-2%). LSI terms: 1-3 appearances each, natural placement.

### 2c. Gap Analysis

Compare user's article against competitors:
- **Content gaps** — Subtopics ALL top competitors cover that the article misses (mandatory additions)
- **Structural gaps** — Formats competitors use (tables, FAQ, step-by-step) the article doesn't
- **Depth gaps** — Sections thinner than competitors
- **Keyword gaps** — Missing LSI and secondary keywords
- **Unique angles** — What the article offers that competitors don't (preserve and amplify)

## Step 3: Analyze Current Article

1. **Current SEO strengths** — What's already working. Don't fix what isn't broken.
2. **SEO gaps** — Mapped against the competitor research.
3. **Author's voice and style** — Note the tone to preserve it in the rewrite.

## Step 4: Optimize

Work through the optimization checklist. Every decision informed by competitor research from Step 2. Consult `references/optimization-checklist.md` for the detailed checklist with specific rules per category.

**Categories (highest impact first):**
1. Content quality and search intent match
2. LSI keyword integration (weave naturally, never force)
3. E-E-A-T signals (experience, expertise, authoritativeness, trustworthiness)
4. Title tag / H1 (keyword near start, under 60 chars, compelling)
5. Meta description (150-160 chars, keyword included, CTA)
6. Heading structure (cross-reference competitor H2s)
7. Keyword usage (primary in first 100 words, match competitor density)
8. Internal and external linking opportunities
9. URL slug (short, hyphenated, includes keyword)
10. Readability (short paragraphs, bullet points, clear intro/conclusion)
11. Featured snippet optimization
12. Image/media recommendations with alt text

## Step 5: Produce the HTML Report

Generate a self-contained HTML report using the template at `assets/seo-report.html`. Replace all `{{PLACEHOLDER}}` values with data from the analysis. Do NOT improvise the design — use the template verbatim.

Consult `references/placeholder-guide.md` for the complete placeholder reference and HTML snippet patterns for generating findings and changelog items.

**Three tabs in the report:**
1. **Revised Article** — Fully rewritten, SEO-optimized version the user can publish as-is
2. **Changelog** — Every change grouped by category with impact badges (High/Medium/Low)
3. **Original** — Unmodified article for comparison

Save as `seo-report-{URL_SLUG}.html` next to the user's article. Open in the browser with `open <path>` and tell the user where it's saved.

## Important Rules

- **Preserve the author's voice.** SEO editor, not ghostwriter. Match their tone, vocabulary, and style.
- **Don't over-optimize.** Google penalizes content written for bots. Every keyword insertion must feel natural. If it can't fit naturally, skip it.
- **Substance over tricks.** The most important ranking factor is whether the content genuinely helps the reader.
- **Be honest in the changelog.** If the article was strong in an area, say so. The user wants to understand what changed, not see trivial edits inflated.
- **Never keyword-stuff.** If it sounds unnatural when read aloud, remove it.

## Troubleshooting

1. **WebFetch blocked by competitor site** — Try an alternative competitor from the search results. If 3+ fail, note it and work with what's available. Search result snippets still provide title/description data.
2. **No competitors ranking for the keyword** — The keyword may be too niche or too new. Suggest a broader variation and confirm with the user.
3. **User has no keyword idea** — Read the article, infer the 2-3 most likely keywords, present options with estimated search intent. Let the user choose.
4. **Article is very short (<200 words)** — This is likely a draft. Ask if the user wants a full rewrite expanding to competitive length, or just optimization of what exists.

## Bundled Resources

- `assets/seo-report.html` — HTML template for the interactive 3-tab report (Revised Article, Changelog, Original)
- `references/placeholder-guide.md` — Complete placeholder reference table and HTML snippet patterns
- `references/optimization-checklist.md` — Detailed SEO optimization checklist with rules per category
