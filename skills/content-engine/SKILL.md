---
name: content-engine
description: Turn a single topic into platform-native posts for LinkedIn, X, and Newsletter (v1; Instagram, TikTok, YouTube, Threads, Facebook stubbed). Produces publication-ready drafts that each rethink the topic for the platform — never reformatted copies. Use when asked to produce multi-platform content, turn a topic into platform-native posts, run the content engine, execute the repurposing chain, draft posts across platforms, or get publication-ready drafts from a topic.
metadata:
  author: Algo724
  version: '0.1.0'
---

# Content Engine

A full content-production pipeline. Given a topic, this skill produces platform-native posts — each post thinks about the topic differently. Same topic, different angle, hook, voice, structure, and format per platform. The reader following all platforms sees distinct pieces, not reformatted copies.

## When to Use This Skill

Use when the user asks to:
- Turn a topic into posts for multiple platforms
- Produce publication-ready drafts across LinkedIn / X / Newsletter
- Run the repurposing chain on an idea
- Generate platform-native content (not one post reformatted)
- Get drafts ready for scheduling/publishing

## Setup

At the start of every invocation, load the reference files upfront.

**Always load:**
- `references/index.md` — identity, niche, node map, execution instructions
- `references/voice/brand-voice.md` — core voice principles (charisma, respect, trust, never-talk-down) and anti-patterns
- `references/voice/platform-tone.md` — per-platform voice adaptation
- `references/engine/hooks.md` — 8 canonical hook formulas + exclusion list + respect test
- `references/engine/repurpose.md` — chain order, annoyance test, per-platform change table
- `references/engine/scheduling.md` — cadence and peak times
- `references/engine/content-types.md` — 6 format definitions
- `references/audience/builders.md` — primary audience
- `references/audience/casual.md` — secondary audience

**Load for active platforms (v1 = LinkedIn + X + Newsletter):**
- `references/platforms/linkedin.md`
- `references/platforms/x.md`
- `references/platforms/newsletter.md`

**Do NOT load (v1 stubs; reference briefly only when outputting stub placeholders in Step 5):**
- `references/platforms/instagram.md` · `tiktok.md` · `youtube.md` · `threads.md` · `facebook.md`

## Step 1 — Topic Intake

The user provides a topic. Before proceeding:

1. **Niche alignment check** (per `index.md` Identity section). Does the topic fit *"investor-grade judgment applied to AI, trading infrastructure, or market intelligence"*?
   - If NO → stop and explain why the topic is off-niche. Do not produce posts.
   - If YES → proceed.
2. **Skip clarifying questions** for any information already explicit or strongly implied in the user's prompt. Only ask about missing load-bearing inputs (e.g., if the topic is very vague and needs a specific angle first).

## Step 2 — Hook Selection

For each of the 3 active platforms, pick 2–3 candidate hooks from the **approved taxonomy** in `engine/hooks.md` (14 formulas, grouped into three families):

- **Evidence-led:** Data Lead · Proof · Credibility (Grounded) · Value / Resource Drop
- **Insight-led:** Framework · Non-Obvious Angle · Collision · Counter-Intuitive Mechanism · Risk-Aware Warning · Eloquence / Aphorism
- **Invitation-led:** Walk-Through · Honest Correction · Question · Curiosity (Open Loop)

**Rules:**
- Aim for a mix across platforms AND across families — ideally at least two of {Evidence, Insight, Invitation} are represented across the three drafts.
- Explicitly exclude any hook from the "Hooks Explicitly Excluded" list in `hooks.md` (smug, clickbait, or talking-down framings).
- Run the **respect test** on each candidate: *"Would Peter be comfortable saying this out loud, verbatim, to a room of peers he respects?"* If no, pick a different hook.
- Track which hook fits which platform for Step 3.

## Step 3 — Execute Repurposing Chain (v1 = 3 platforms)

Execute in this exact order (per `engine/repurpose.md`):

### Step 3a — X (first)
Forces brevity and finds the core. If the idea can't survive compression to 280 chars (or a tight 5–12 tweet thread), it isn't ready.

- Voice: `voice/platform-tone.md` → X section
- Format: per `platforms/x.md` (single tweet OR thread)
- Hook: from Step 2 selection

### Step 3b — LinkedIn (second)
Different angle from X — not reformatted. Institutional framing, narrative arc, professional warmth.

- Voice: `voice/platform-tone.md` → LinkedIn section
- Format: per `platforms/linkedin.md` (1,300–2,000 char post)
- Hook: different hook family from X, from Step 2 selection

### Step 3c — Newsletter (third)
Deepest version. Full reasoning + counterargument + invalidation condition. Post-mortem element if relevant.

- Voice: `voice/platform-tone.md` → Newsletter section
- Format: per `platforms/newsletter.md` (1,000–2,000 word essay with section headers)
- Hook: often Walk-Through, Honest Correction, or Collision

## Step 4 — Annoyance Test (Mandatory Gate)

Reread all three drafts. Ask:

**"If a reader followed Peter on all three active platforms, would they feel they're seeing substantially the same content reworded?"**

- If YES → at least two of {angle, hook family, structure, depth, voice energy} didn't change enough. Return to the relevant sub-step in Step 3 and rethink.
- If NO → proceed.

Three posts are sufficiently different when **at least three** of these differ meaningfully:
1. Opening angle (which facet of the topic leads)
2. Hook type (from the approved taxonomy)
3. Structure (thread / long post / essay)
4. Depth (surface / walk-through / full mechanism + invalidation)
5. Voice energy (per `platform-tone.md`)

## Step 5 — Stub Output (Phase 2 platforms)

For Instagram, TikTok, YouTube, Threads, Facebook — output a one-line placeholder per platform:

```
[Instagram: STUB — not active in v1. Fill when Instagram goes active.]
[TikTok: STUB — not active in v1. Fill when TikTok goes active.]
[YouTube: STUB — not active in v1. Fill when YouTube goes active.]
[Threads: STUB — not active in v1. Fill when Threads goes active.]
[Facebook: STUB — not active in v1. Fill when Facebook goes active.]
```

Do not attempt full drafts for stub platforms. Doing so violates the design of v1.

## Step 6 — Scheduling Recommendation

For each of the 3 active-platform drafts, include:
- Recommended posting day (per `engine/scheduling.md`)
- Recommended posting time window
- If the drafts belong to the same topic run, note a staggered schedule (default: X Tue 8am → LinkedIn Wed 8am → Newsletter Thu 9am)

## Step 7 — Iteration Prompt

End the run by inviting Peter to refine the system:
1. Which hooks/angles feel strongest to Peter for this topic?
2. Anything new to add to `hooks.md` based on what worked?
3. Any voice calibration to refine in `platform-tone.md`?
4. Any new audience signals to update `audience/*.md`?

This is Shann's "compound interest for content" — the engine gets smarter each week Peter iterates.

## Quality Checklist

Before presenting output, verify:

- [ ] Topic passes niche alignment check (per `index.md`)
- [ ] Each of the 3 active drafts names the hook type used (from the approved 14)
- [ ] Across the 3 drafts, at least 2 of 3 hook families (Evidence / Insight / Invitation) are represented
- [ ] No excluded hooks used (check against `hooks.md` exclusion list)
- [ ] All 3 drafts pass the **respect test** (no talking down, no smug framing, no lecturing)
- [ ] All 3 drafts pass the **annoyance test** (angle/hook/structure/depth/voice all meaningfully differ)
- [ ] Peter's clarity gate holds (smart 13-year-old can follow the language; investors still find it sharp)
- [ ] Peter's non-negotiables applied: hook first, fact before hype, no fluff, never condescending
- [ ] Each draft has at least one counterargument or invalidation condition (non-negotiable for Newsletter; strongly preferred for LinkedIn)
- [ ] Specific numbers with units and timeframes where data is cited
- [ ] 5 stub placeholders present for Phase 2 platforms
- [ ] Scheduling recommendation included per active-platform draft

## Output Format

Present output in this order:

1. **Niche alignment confirmation** (one line: "Topic aligns with [pillar(s)].")
2. **Hook candidates per platform** (2–3 per platform with hook type labeled)
3. **X draft** (hook type + full draft + recommended posting day/time)
4. **LinkedIn draft** (hook type + full draft + recommended posting day/time)
5. **Newsletter draft** (hook type + full draft with section headers + recommended send day/time)
6. **Stub placeholders** (5 one-liners)
7. **Annoyance + respect test confirmation** (one line: "Both tests passed — drafts are platform-native.")
8. **Iteration prompt** (4 questions for Peter)
