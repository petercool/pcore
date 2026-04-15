---
name: content-brainstorm
description: Brainstorm content ideas from source material (reports, briefings, research, articles). Generates a comprehensive list of headline, hook, description, and image/chart proposals tailored to a specific platform and audience. Use when asked to brainstorm content, propose post ideas, generate headlines, plan social media content, create content calendars, or extract publishable angles from reports or research. Covers LinkedIn, X/Twitter, Instagram, blog, podcast, and email newsletter formats. Aggressively proposes many alternatives from diverse angles.
metadata:
  author: Algo724
  version: '1.1'
---

# Content Brainstorm

Brainstorm a comprehensive list of content ideas — headline, hook, description, and image/chart plan — from source material, tailored to a specific platform and target audience.

## When to Use This Skill

Use when the user asks to:
- Brainstorm content ideas from a report, briefing, article, or research
- Propose LinkedIn/X/blog post ideas
- Generate headlines, hooks, or descriptions
- Plan social media content from source material
- Extract publishable angles from dense source documents
- Create a content calendar or content pipeline

## Setup

At the start of every invocation, load all reference files upfront so they are available throughout the workflow:

- `references/hooks-and-angles.md` — 12 hook types, 8 post types, 6 angle-generation lenses
- `references/platform-styles.md` — tone, structure, length, fold limits per platform
- `references/image-planning.md` — chart archetypes, decision tree, design standards, carousel guidance
- `references/proposal-template.md` — fully worked example of a single proposal (use as the pattern for Step 3 output)

Loading them once at the start avoids mid-workflow disruption and keeps proposals consistent.

## Step 1: Clarify Platform, Audience, and Constraints

Before brainstorming, ensure you have the six inputs below. **Skip clarifying questions for any input already explicit (or strongly implied) in the user's prompt or attached source material — only ask about genuinely missing fields.** Use `ask_user_question` for the remaining gaps:

1. **Source material** — What document/report/data are we extracting content from? (The user may paste it or provide a file.)
2. **Platform(s)** — Where will this content appear? (LinkedIn, X/Twitter, Instagram, blog, podcast, email newsletter, other)
3. **Target audience** — Who are we writing for? Be specific. Examples:
   - "Board-level financial professionals"
   - "Retail crypto investors"
   - "SaaS founders and PMs"
   - "General tech-literate audience"
4. **Tone / brand voice** — Any specific tone? (institutional, conversational, provocative, educational). If not specified, infer from platform defaults in `references/platform-styles.md`.
5. **Quantity preference** — How many alternatives does the user want? Default: aggressive (7–12 angles). The user may request fewer.
6. **Constraints** — Character limits, topics to avoid, mandatory elements, series/branding requirements.

(Reference files were loaded in Setup — no additional load needed here.)

## Step 2: Extract Angles from Source Material

Read the source material carefully. Then systematically apply the six angle-generation lenses (already loaded from `references/hooks-and-angles.md`):

1. **Audience Perspective Rotation** — Generate one angle per audience segment that would care about this content.
2. **Timeframe Rotation** — Same data viewed through today / this week / this quarter / this cycle horizons.
3. **Contrarian Inversion** — For every consensus view in the source, propose the opposite take.
4. **Cross-Domain Collision** — Find where two narratives in the source material collide or create tension.
5. **Data Surprise Extraction** — Identify the most surprising numbers and build hooks around them.
6. **Emotional Resonance** — Map the data/content to fear, relief, vindication, anxiety, or aspiration.

**Goal: Generate 7–12 distinct angles.** More is better at this stage — the user will select and refine. Do not self-censor or consolidate prematurely.

**Stop criteria — halt angle generation when ANY of these is true:**
- You've reached 12 angles (push to 15 only if source material is unusually rich and the user requested aggressive quantity).
- The next angle would substantially overlap an existing one (same thesis, different wording).
- Source material is genuinely thin and producing more would require fabricating context — in which case stop early and explicitly flag: `source-material-limited: produced N angles`.

Never go below 7 unless the source-material-limited condition applies. Track which Lens (1–6) generated each angle — this is required for citation in Step 3.

## Step 3: Build Each Angle Into a Complete Proposal

**Before drafting, consult the Audience-Specific Calibration section at the bottom of this file** for the audience captured in Step 1, and apply its tone/hook preferences throughout this step.

For each angle, produce ALL of the following components. **Each completed proposal MUST cite three taxonomies: Lens used (1–6 from Step 2), Hook type (1–12), and Post type (1–8).** See `references/proposal-template.md` for a fully worked example to pattern-match against.

### A. Headline
- A concise, publishable title (adapt length to platform)
- For LinkedIn: professional, data-anchored, avoids clickbait
- For X: punchy, under 280 characters, opinionated
- For blog: SEO-friendly, descriptive, includes key terms

### B. Hook
- The opening 1–3 lines that appear before any "see more" truncation
- Must earn the click / scroll-stop
- Select a specific hook type from the 12 hooks (see `references/hooks-and-angles.md`) and note which one you're using
- Ensure it fits within the platform's fold limit (LinkedIn: ~210 chars, Instagram: ~125 chars, X: first tweet)

### C. Description / Body Direction
- A 2–4 sentence summary of what the full post body would cover
- Include the key data points, narrative arc, and conclusion
- Note the post type (Analytical, Contrarian, Observation, etc.)
- Suggest a closing CTA or question

### D. Image / Chart Plan
For each angle, propose ONE primary image option using the decision tree in `references/image-planning.md`:

- **If the angle's value is a unique data framing** → Propose a specific custom chart archetype (scenario tree, divergence chart, three-panel dashboard, heatmap, map infographic, before/after bar, or timeline). Describe the data to plot and the visual concept.
- **If a high-quality institutional chart exists** → Cite the source and describe what it shows.
- **If neither applies** → Propose an AI-generated thematic image or note "no image needed."

Include for each image proposal:
- Type: Generate / Reference / AI-generated
- Concept: 1–2 sentence visual description
- Why it works: How it reinforces the post's thesis

**Optional carousel:** If the angle has multi-part data structure (e.g., probability matrix + scenario timeline + summary card), additionally propose a 2–4 slide carousel using the Carousel Planning section of `references/image-planning.md`. Note this as `Carousel: [slide list]` after the primary image. Do not propose a carousel by default — only when the angle's data genuinely warrants multiple panels.

## Step 4: Organize and Rank

Present the full list of angles in a structured format:

### Summary Table

| # | Angle | Lens | Hook Type | Post Type | Image Type | Engagement Potential |
|---|-------|------|-----------|-----------|------------|---------------------|
| 1 | ... | ... | ... | ... | ... | High / Medium / Low |

### Detailed Proposals
Then present each angle's full details (headline, hook, description, image plan) grouped and numbered.

### Recommendations
End with a ranked top 3–5 recommendation with brief justification:
- Which angles have the highest engagement potential for this specific platform + audience combination
- Which angles are most differentiated (not already being discussed widely)
- Which angles pair well together (for a series or content calendar)

## Step 5: Offer Next Steps

After presenting proposals, offer:
1. **Develop full drafts** — Write complete post copy for selected angles
2. **Generate charts/images** — Produce the visual assets for selected angles
3. **Adapt cross-platform** — Take one angle and adapt it for multiple platforms
4. **Series planning** — Organize selected angles into a recurring content series with cadence recommendations

## Quality Checklist

Before presenting proposals, verify:
- [ ] Every angle has all four components (headline, hook, description, image plan)
- [ ] Every proposal cites Lens (1–6), Hook type (1–12), and Post type (1–8)
- [ ] Summary table includes the Lens column
- [ ] Hooks fit within platform fold limits
- [ ] No two angles are substantially the same thesis repackaged
- [ ] At least 2 contrarian/non-obvious angles are included
- [ ] Data points cited in hooks are specific (numbers, percentages, names) not vague
- [ ] Image proposals match the angle's core value-add (not generic decoration)
- [ ] Carousels are proposed only when multi-part data justifies them, not by default
- [ ] Tone is calibrated to the specified platform and audience (cross-checked against Audience-Specific Calibration)
- [ ] Abbreviations are avoided or expanded for broad audiences
- [ ] Closing CTAs/questions are included for engagement-driving platforms
- [ ] If fewer than 7 angles produced, `source-material-limited` flag is included with reason

## Audience-Specific Calibration

### Finance / Investment Audience
- Lead with precise metrics (basis points, percentage returns, spreads)
- Use Credibility and Value hooks
- Address skepticism directly
- Probability frameworks and scenario trees perform well
- Avoid hype words; use institutional vocabulary

### Tech / SaaS Audience
- Focus on workflow improvement, time saved, integration ease
- Use Curiosity and Counter-intuitive hooks
- Translate technical features into user outcomes

### General Professional Audience
- Balance data density with accessibility
- Expand all abbreviations
- Use Eloquence and Counter-narrative hooks
- End with questions that invite diverse perspectives

### Consumer / Retail Audience
- Lead with emotion and aspiration
- Use Inspiration, Faces, and Identity hooks
- Social proof is critical
- Keep language simple — 10th-grade reading level
