---
name: scroll-stop-builder
version: 1.0.0
description: >-
  Build a production-quality scroll-driven animation website from a video file
  or pre-extracted frame images. The video/frames play forward and backward as
  the user scrolls, using canvas-based rendering with snap-stop annotation
  cards, animated starscape, count-up specs, glass-morphism design, and full
  mobile responsiveness. Use when user says "scroll-stop build", "scroll
  animation website", "scroll-driven video site", "build a frame sequence
  scroll site", "Apple-style product page", or provides a video or frame zip
  and asks for scroll-controlled playback. Do NOT use for simple CSS scroll
  effects, parallax websites, video autoplay on scroll, general website
  building, or single-page animations without frame extraction.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - WebFetch
  - AskUserQuestion
---

# Scroll-Stop Builder

Take a video file or a set of pre-extracted frame images and build a scroll-driven animation website. The video plays forward and backward as the user scrolls, creating a dramatic Apple-style scroll-stopping effect. Canvas-based rendering with extracted frames gives frame-perfect control that `<video>` with `currentTime` cannot match.

## Step 1: Interview

Gather project details before writing any code. Do not assume brand names, colors, or content.

### 1a. Brand & Design

Use AskUserQuestion. Ask in a natural, conversational way:

1. **Brand name** — "What's the brand or product name for this site?"
2. **Logo** — "Do you have a logo file? (SVG or PNG preferred)"
3. **Accent color** — "What's your primary accent color? (hex code, or describe it and I'll suggest options)"
4. **Background color** — "What background color? (dark backgrounds work best for this effect)"
5. **Overall vibe** — "What feel are you going for? (e.g., premium tech launch, luxury, playful, minimal, bold)"

Processing rules:
- If no logo provided, use brand name text with Space Grotesk font as the logo.
- If accent color is described ("electric blue"), suggest 2-3 hex options and confirm.
- If background not specified, default to `#0a0a0a` (near-black).

### 1b. Content Sourcing

Use AskUserQuestion:

- **Option A: Existing website** — "Is this based on an existing website? Share the URL and I'll pull the real content (product name, features, specs, copy)."
- **Option B: Paste it in** — "You can paste in product descriptions, feature lists, specs, testimonials."
- **Option C: Provide later** — "I'll build the structure first with placeholder sections you can fill in."

If Option A, use WebFetch to retrieve the page and extract relevant copy, product details, feature descriptions, spec numbers, and testimonials.

### 1c. Optional Sections

Use AskUserQuestion:

- **Testimonials** — "Want a testimonials section? If yes, provide them or I'll pull from the website."
- **Confetti** — "Want a confetti burst effect? (e.g., on CTA button click)"
- **Card Scanner** — "Want a 3D particle showcase section? (Three.js-based — good for showing off a card, device, or object)"

Include these sections only if the user explicitly opts in.

Store all answers — reference them in Steps 3-5.

## Step 2: Validate Input & Extract Frames

Determine whether the user provided a video file or pre-extracted frames, then prepare the frame sequence.

### Path A: Video File

1. Verify FFmpeg is installed: `which ffmpeg`. If missing, tell the user to run `brew install ffmpeg`.
2. Verify the video file exists and is readable.
3. Analyze with ffprobe:
   ```bash
   ffprobe -v quiet -print_format json -show_streams -show_format "{VIDEO_PATH}"
   ```
   Extract: duration, fps, resolution, total frame count.
4. Calculate target FPS to produce 60-150 total frames. Formula: `target_fps = desired_frames / duration`. Aim for ~120 frames.
5. Extract frames:
   ```bash
   mkdir -p "{OUTPUT_DIR}/frames"
   ffmpeg -i "{VIDEO_PATH}" -vf "fps={TARGET_FPS},scale=1920:-2" -q:v 2 "{OUTPUT_DIR}/frames/frame_%04d.jpg"
   ```
   Use `-q:v 2` for high-quality JPEG. Always JPEG, not PNG.
6. Count extracted frames. If fewer than 30, the video may be too short — warn the user. If more than 200, subsample (keep every Nth frame) to reach ~120.
7. Verify the first frame (`frame_0001.jpg`) shows a white or near-white background. If not, warn the user: "The first frame should be on a white background for the best hero transition. Re-export the video with a white opening frame, or provide a separate white-background hero image."

### Path B: Frame Zip / Image Directory

1. If a zip file: unzip to `{OUTPUT_DIR}/frames/`.
   ```bash
   mkdir -p "{OUTPUT_DIR}/frames"
   unzip "{ZIP_PATH}" -d "{OUTPUT_DIR}/frames/"
   ```
   If images are nested in a subdirectory, flatten them into `frames/`.
2. Count image files (`.jpg`, `.jpeg`, `.png`, `.webp`). Need at least 60 frames. If fewer, warn the user.
3. Detect the naming pattern. Common patterns: `frame_0001.jpg`, `frame0001.jpg`, `001.jpg`, `IMG_0001.jpg`. Sort files alphabetically/numerically to establish sequence order.
4. Rename to a consistent `frame_NNNN.jpg` pattern if names are non-standard:
   ```bash
   i=1; for f in $(ls -1v {OUTPUT_DIR}/frames/*.{jpg,jpeg,png,webp} 2>/dev/null); do
     mv "$f" "$(printf "{OUTPUT_DIR}/frames/frame_%04d.jpg" $i)"; i=$((i+1));
   done
   ```
5. If frames are PNG or WebP, convert to JPEG for smaller file sizes:
   ```bash
   mogrify -format jpg -quality 90 {OUTPUT_DIR}/frames/*.png
   ```
6. If frame count exceeds 200, subsample to ~120. Keep every Nth frame where N = total / 120, rounded. Renumber sequentially after subsampling.
7. Verify the first frame shows a white or near-white background. Same warning as Path A if not.

**STOP.** Tell the user: "Extracted {N} frames at {W}x{H} resolution. The first frame is [white/not white]. Confirm this looks correct before I build the site."

## Step 3: Design System

Construct the design system from interview answers (Step 1).

**Fonts** (defaults — overridable if user has brand fonts):
- Headings: Space Grotesk
- Body: Archivo
- Monospace: JetBrains Mono

**Colors:**
- Accent: from interview (buttons, glows, progress bars, highlights)
- Background: from interview (body, sections)
- Text: derive from background — dark bg → white primary + `rgba(255,255,255,0.6)` secondary; light bg → dark primary + muted secondary
- Selection: accent background with contrasting text

**Design tokens based on vibe:**

| Vibe | Glass-morphism | Orbs | Grid overlay | Starscape | Glow intensity |
|------|---------------|------|-------------|-----------|----------------|
| Premium tech | Full | 2 large | Subtle | Yes, 180 stars | Medium |
| Luxury | Full | 1 subtle | None | Yes, 100 stars | Soft |
| Minimal | Reduced (lighter borders) | None | None | Optional, 80 stars | Low |
| Playful | Full, brighter borders | 3 colorful | Bold | Yes, 200 stars | High |
| Bold | Full | 2 large | Bold | Yes, 150 stars | High |

**Card style:** Glass-morphism — semi-transparent bg, subtle border, `backdrop-filter: blur(20px)`, `border-radius: 20px`.

**Buttons:** Primary = accent bg + contrasting text + accent glow. Secondary = transparent + white/dark border.

**Scrollbar:** Dark track, gradient thumb using accent color, glow on hover.

**STOP.** Present the design system summary to the user: fonts, colors, vibe-derived settings, sections to include. Wait for confirmation before building.

## Step 4: Build the Website

Create a single self-contained HTML file with all CSS and JS inline. Sections top to bottom:

1. **Starscape** — Fixed background canvas with twinkling animated stars
2. **Loader** — Full-screen overlay with brand logo, progress bar, disappears when frames loaded
3. **Scroll Progress Bar** — Fixed 3px bar at viewport top showing page scroll progress
4. **Navbar** — Brand logo + name, transforms from full-width to centered pill on scroll (glass-morphism)
5. **Hero** — Title, subtitle, CTA buttons, scroll hint, background orbs + grid overlay
6. **Scroll Animation** — Sticky canvas with frame sequence, height controls scroll speed (default 350vh)
7. **Annotation Cards** — Glass-morphism cards that appear at specific scroll progress points with snap-stop freeze (~600ms per card)
8. **Specs** — Stat numbers with count-up animation (easeOutExpo, staggered 200ms, IntersectionObserver trigger)
9. **Features Grid** — Glass-morphism cards in responsive grid (3-col → 1-col on mobile)
10. **CTA** — Call-to-action section with accent orb behind it
11. **Testimonials** — *(only if opted in)* Horizontal drag-to-scroll cards with snap
12. **Card Scanner** — *(only if opted in)* Three.js particle showcase
13. **Footer** — Brand name, links, copyright

For each section, consult `references/sections-guide.md` for the detailed HTML structure, CSS styling, and JavaScript behavior.

### Key Implementation Patterns

**Canvas rendering:** Scale canvas dimensions by `devicePixelRatio` for Retina. Resize handler must redraw current frame.

```javascript
canvas.width = window.innerWidth * window.devicePixelRatio;
canvas.height = window.innerHeight * window.devicePixelRatio;
canvas.style.width = window.innerWidth + 'px';
canvas.style.height = window.innerHeight + 'px';
```

**Cover-fit (desktop) / Zoomed contain-fit (mobile):** On desktop, the frame fills edge-to-edge (cover). On mobile (≤768px), use a 1.2x zoomed contain-fit so the object stays centered and visible.

**Scroll-to-frame mapping:** Map scroll progress through `.scroll-animation` section to a frame index. Use `requestAnimationFrame` — never draw directly in the scroll handler. Only call `drawFrame` when the frame index changes.

**Snap-stop annotation cards:** Cards use `data-show` and `data-hide` attributes (0.0–1.0 progress). When scroll enters a snap zone, freeze the body overflow for ~600ms, then release. Creates a "boom, boom, boom" reveal rhythm.

**Navbar pill transform:** Full-width at top → centered pill (max-width 820px) with glass-morphism on scroll past 80px. Transition: `cubic-bezier(0.16, 1, 0.3, 1)`.

**Count-up animation:** `easeOutExpo` easing, staggered 200ms per stat. Accent-color glow pulse while counting. Triggered by IntersectionObserver at 30% threshold.

**Frame preloading:** Load all frames as `Image` objects. Update loader progress bar as each loads. Only hide loader and enable scrolling after all frames are loaded.

## Step 5: Customize Content

All content comes from the interview (Step 1). Never use placeholder text. If content came from a website URL (Option A), use the actual text from that site. Adapt:

- **Hero:** Title (product/brand headline), subtitle (value proposition), CTA button text
- **Annotation cards:** Number of cards matches the content provided. Each card: number, title, description, optional stat number + label. Distribute `data-show`/`data-hide` ranges evenly across 0.0–1.0 progress.
- **Specs:** 4 stat numbers with labels (pulled from product specs, features, or metrics)
- **Features:** Glass-morphism cards with icon/emoji, title, and description
- **CTA:** Headline, supporting text, button text
- **Testimonials** *(if included)*: Quote, author name, author role/company

If the user chose Option C (provide later), use descriptive section labels like "[Product headline goes here]" — not Lorem Ipsum.

## Step 6: Serve & Verify

Start a local server and open the site:

```bash
cd "{OUTPUT_DIR}" && python3 -m http.server 8080
```

Open `http://localhost:8080` in the browser for the user.

**Verification checklist:**
- [ ] Loader appears, progress bar fills, loader fades out
- [ ] Hero section renders with correct brand name and colors
- [ ] Scroll animation plays forward on scroll down, backward on scroll up
- [ ] Annotation cards appear at correct scroll positions with snap-stop freeze
- [ ] Specs numbers count up when scrolled into view
- [ ] Features grid displays correctly
- [ ] CTA section renders
- [ ] Testimonials scroll horizontally *(if included)*
- [ ] Card Scanner renders *(if included)*
- [ ] Footer displays brand name
- [ ] Mobile: test at 375px width — compact annotation cards, stacked features, 2x2 specs grid

## Mobile Responsiveness

Key adaptations (details in `references/sections-guide.md`):

- **Annotation cards:** Compact single-line — hide description, stat number, stat label. Show only card number + title in a flex row. Position at `bottom: 1.5vh`.
- **Scroll animation height:** 350vh (desktop) → 300vh (tablet ≤1024px) → 250vh (phone ≤768px)
- **Navbar:** Hide links on mobile, show only logo in the pill shape
- **Testimonials:** Touch-scrollable, snap to card edges
- **Features:** Stack to single column
- **Specs:** 2×2 grid

## Important Rules

1. **No placeholder content.** Every piece of text comes from the interview. The entire point of this skill is tailored output, not generic templates.
2. **White first frame is a hard requirement.** The hero-to-scroll-animation transition depends on it. Validate in Step 2 before proceeding.
3. **`requestAnimationFrame` for canvas drawing.** Never draw directly in the scroll handler — it causes jank.
4. **`{ passive: true }` on all scroll listeners.** Enables browser scroll optimizations.
5. **Canvas scaled by `devicePixelRatio`.** Without this, the canvas is blurry on Retina displays.
6. **Preload ALL frames before showing content.** No pop-in during scroll. The loader exists for this reason.
7. **No `scroll-behavior: smooth`.** It interferes with frame-accurate scroll-to-frame mapping.
8. **Vanilla JS only.** No jQuery, no React, no animation libraries. Exception: Three.js for the Card Scanner section if opted in.
9. **JPEG frames, not PNG.** JPEG files are 5-10x smaller. Target <100KB per frame.
10. **Cap frames at ~150 for performance.** If input exceeds 200 frames, subsample. More frames = slower initial load with diminishing visual improvement.

## Troubleshooting

| Problem | Root Cause | Solution | Prevention |
|---------|-----------|----------|------------|
| Frames don't load | Wrong file paths or no local server | Check frame paths, ensure `python3 -m http.server` is running | Always serve via HTTP, never open from `file://` |
| Animation is choppy | Too many frames or PNG format | Reduce frame count, convert to JPEG <100KB each | Target 60-150 JPEG frames from the start |
| Canvas is blurry | Missing `devicePixelRatio` scaling | Apply DPR scaling in the resize handler | Always use the resize handler pattern from `references/sections-guide.md` |
| Scroll feels too fast/slow | `.scroll-animation` height is wrong | Adjust: 200vh = fast, 350vh = default, 500vh = slow, 800vh = cinematic | Test scroll speed early, adjust before polishing |
| Mobile cards overlap content | Full card layout on small screen | Switch to compact single-line card design at ≤768px | Always test at 375px viewport width |
| Snap-stop feels jarring | HOLD_DURATION too long or SNAP_ZONE too small | Reduce HOLD_DURATION to 400ms or widen SNAP_ZONE | Test with both trackpad and mouse wheel |
| Stars too bright or dim | Starscape canvas opacity is wrong | Adjust from default 0.6 up or down | Start at 0.6, tune per background color |
| First frame isn't white | Video/frames don't start on white background | Ask user to re-export video or provide a white-background hero image | Validate first frame in Step 2 before building |
| Zip frames out of order | Non-sequential or inconsistent naming | Sort alphabetically/numerically, rename to `frame_NNNN.jpg` | Normalize naming in Step 2 Path B |
| Too many frames cause slow load | 200+ high-res frames without subsampling | Subsample to ~120 frames, compress to JPEG quality 90 | Cap at 150 frames, compress if any exceed 100KB |

## Bundled Resources

- `references/sections-guide.md` — Detailed HTML/CSS/JS implementation patterns for all 13 website sections: Starscape, Loader, Scroll Progress Bar, Navbar, Hero, Scroll Animation, Annotation Cards, Specs, Features Grid, CTA, Testimonials, Card Scanner, and Footer. Consult the relevant section when building each part of the site in Step 4.
