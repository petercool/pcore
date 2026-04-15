# content-types.md — Format Definitions

> Six canonical content formats. Each post maps to one. The format determines structure; the platform determines voice and length.

## 1. Thread / Multi-Part Post

**Platforms:** X (thread), LinkedIn (multi-paragraph post), Newsletter (as structured section)

**When to use:** Step-by-step reasoning, frameworks, listicles with real content, analytical walk-throughs.

**Structure:**
- Hook (first tweet / first paragraph) — per `hooks.md`
- Numbered steps or clearly-delineated points (usually 3–7)
- One counterargument or invalidation condition inline
- Close with a concrete takeaway, a framework summary, or a genuine question

**Length:**
- X: 5–12 tweets, each standalone (no "1/" "2/" counters — each tweet must work alone)
- LinkedIn: 1,300–2,000 chars, ~5–8 short paragraphs

**Pitfalls:**
- Don't pad for thread length. 5 strong tweets > 12 mediocre ones.
- Don't bury the core claim. The hook tweet is also the thesis.
- Don't end with "follow for more" — end with substance.

---

## 2. Carousel / Slide Post

**Platforms:** Instagram, LinkedIn (document post) — STUB for v1 (Instagram not active yet)

**When to use:** Visual guides, process diagrams, comparison matrices, data dashboards.

**Structure:**
- Slide 1: bold hook + visual anchor
- Slides 2–8: one idea per slide, max ~30 words per slide
- Last slide: summary + CTA (one clear next step)

**Design notes:**
- High contrast (dark background + light text, or vice versa)
- Sans-serif (Inter, Source Sans, or similar)
- Minimum font size 18pt for legibility on mobile

**v1 status:** stub format — rarely used until Instagram goes active. LinkedIn document posts work but aren't Peter's primary format.

---

## 3. Short-Form Video

**Platforms:** TikTok, Instagram Reels, YouTube Shorts — STUB for v1 (none active)

**When to use:** Quick framework explanations, reactions to market events, short demos.

**Structure:**
- Hook (2 seconds) — visual + spoken
- Content (30–50 seconds) — the core point, ideally one clear takeaway
- CTA (3–5 seconds) — follow for more / subscribe / visit link

**v1 status:** stub format — add full spec when video platforms go active.

---

## 4. Long-Form Video

**Platforms:** YouTube (primary) — STUB for v1

**When to use:** Deep tutorials, framework walk-throughs, system architecture explanations.

**Structure:**
- Hook (0:00–0:30) — state the problem + promise the outcome
- Context (0:30–2:00) — why this matters, who cares
- Main content (2:00–9:00) — step-by-step walk-through, with visuals
- Recap + CTA (9:00–10:00) — summarize, next step

**v1 status:** stub — full spec when YouTube goes active.

---

## 5. Long-Form Text

**Platforms:** Newsletter (primary), LinkedIn article (secondary), Blog (future)

**When to use:** Full reasoning posts, post-mortems, deep analysis, framework guides with real depth.

**Structure:**
- Opening (100–200 words) — hook + why this topic now
- Thesis (one paragraph, bolded key claim)
- Supporting sections (2–5) — each with a header, one main argument, at least one data point
- Counterargument + invalidation section
- Conclusion — weighted view, honest about uncertainty
- Optional: personal note / what I'm still working through

**Length:** 1,000–2,500 words for the Newsletter. LinkedIn articles: 800–1,500.

**Pitfalls:**
- Don't pad for length. If the insight is 900 words, publish 900 words.
- Don't hedge into meaninglessness. Have a view.
- Section headers should advance the argument, not just label it.

---

## 6. Short Take

**Platforms:** X (single tweet), Threads, Facebook (short post) — v1 uses this on X only

**When to use:** One sharp observation, a single data callout, a well-framed question, a quote-tweet analysis.

**Structure:**
- Entire post = hook
- Must be self-contained — no setup, no "read to the end"
- If it works, it reads like a closed-circuit observation — complete in itself

**Length:** ≤280 characters (X). Facebook/Threads: ≤500.

**Pitfalls:**
- Don't use Short Take as a weak substitute for a thread. If the idea is big, thread it.
- Don't post Short Takes that need context the reader doesn't have. If setup is required, it's a thread.

---

## Format Selection Heuristic

Given a topic, pick format by answering:

1. **Does it have sequential reasoning or steps?** → Thread (X or LinkedIn)
2. **Does the value hinge on a visual comparison or process?** → Carousel (v2)
3. **Does it need full depth with counterarguments and invalidation?** → Long-Form Text (Newsletter)
4. **Is it one sharp observation that stands alone?** → Short Take (X)
5. **Is it a demo or walk-through that benefits from voice/video?** → Long-Form Video (v2)

When in doubt between Thread and Long-Form Text: if the walk-through takes more than 1,500 words, it belongs in the Newsletter. If it fits in 8–10 tweets, thread it.

## Cross-Platform Format Mapping

For a single topic running through the repurposing chain:

| Platform | Default format | Alt if topic is shorter |
|----------|---------------|--------------------------|
| X | Thread (5–12 tweets) | Short Take (single tweet) |
| LinkedIn | Thread-style long post | Framework post (shorter) |
| Newsletter | Long-Form Text (1,000–2,000 words) | (always long-form here) |

If a topic only has a Short Take on X, it probably doesn't warrant a LinkedIn or Newsletter post. Skip downstream — don't inflate.
