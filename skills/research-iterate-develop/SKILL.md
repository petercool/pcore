---
name: research-iterate-develop
description: |
  Research-iterate-develop workflow for empirical projects. Guides numbered
  experiment scripts, leaderboard-driven iteration, supervisor reports, and
  walk-forward validation. Use when: starting a research project, running
  experiments, iterating on strategy/model performance, "research mode",
  "run experiments", "iterate on results", "find the best config",
  "experiment-driven development", "empirical workflow", "numbered experiments".
---

# Research-Iterate-Develop Methodology

A battle-tested workflow for empirical projects where you don't know the
answer upfront and must discover it through structured experimentation.
Derived from a real 4-phase backtest project that pivoted from a complex
adaptive grid strategy to a simple trend follower after 25 experiments
proved the original thesis wrong.

## Core Principles

### 1. Research on main, commit at phase boundaries

Experiments live in `research/exp_NN_<topic>.py` as self-contained scripts.
Each script loads data, runs one hypothesis, writes a CSV to `results/`,
and prints a leaderboard. Don't refactor `exp_01` when you write `exp_02`
— frozen experiments are the audit trail.

### 2. Numbered sequentially, named by hypothesis

`exp_01_simulator_and_direction.py`, `exp_02_slow_fair_value.py`, etc. The
number preserves the chronological learning path; the name captures the
question. Never rename; if an experiment is superseded, write a new numbered
one that explains why.

### 3. One hypothesis per experiment, one answer per run

If you want to sweep parameters, that's a sweep experiment (e.g., `exp_08`).
If you want to A/B two variants, that's a comparison experiment. Don't mix
"is this profitable?" with "what's the optimal parameter?" in one script —
you can't read the results cleanly.

### 4. Leaderboard-driven iteration

Every experiment prints a sorted leaderboard by the domain metric (Sharpe,
accuracy, F1, loss, etc.) at the end. The next experiment starts from
whatever won. If the winner surprises you, chase that surprise — most of the
alpha in this methodology came from chasing surprises.

### 5. Pivot when evidence demands it

If empirical evidence contradicts the original spec, **pivot and document
the deviation** in `research/REPORT_SUPERVISOR.md`. The spec is a starting
hypothesis, not a constraint. Keep the legacy path working for A/B
comparison, but make the new winner the default.

### 6. Walk-forward / cross-validate the winner

The leaderboard picks the in-sample champion. Walk-forward validation (or
k-fold CV) is mandatory before declaring victory. If the winner doesn't
survive out-of-sample, go back to the leaderboard and pick the next one.

### 7. Negative results are deliverables, not failures

Document what didn't work and why. In a research report, a section titled
"Why alternatives lost" saves the next developer from re-running dead
branches. Include the failed experiment numbers so readers can check the
CSVs.

### 8. Keep the test suite green at every checkpoint

Even in research mode, `pytest` must pass. Unit tests catch bugs immediately
(e.g., off-by-one errors in rolling calculations). Write the test when you
ship the code, not at the end of the phase.

## Directory Layout

```
project/
├── src/                    # production modules only
├── tests/                  # unit tests for src/
├── research/
│   ├── exp_NN_<topic>.py   # frozen experiments (never renamed)
│   └── REPORT_*.md         # narrative reports (supervisor, per-topic)
├── results/                # CSV outputs + HTML plots (gitignored)
├── docs/
│   ├── adr-*.md            # original requirements (may be superseded)
│   ├── strategy-phases.md  # living status doc
│   └── architecture.md     # module layers
├── config.yaml             # all parameters (if applicable)
└── CLAUDE.md               # project brief + invariants + current phase
```

**Key gitignore entries:** `results/`, `data/`, `.venv/`, `__pycache__/`.
Experiment CSVs are ephemeral outputs, not source code.

## CLAUDE.md Pattern

Tell Claude three things upfront:

### 1. Source-of-truth table

```markdown
| Document | Role |
|---|---|
| `docs/adr-1.md` | Requirements — how the code is structured |
| `docs/prd-1.md` | Strategy spec — what the system does, why |
| `.claude/skills/...` | Framework skill (if applicable) |

**If the ADR and PRD conflict, stop and ask the user.**
```

### 2. Inviolable invariants

Framework rules, naming conventions, and boundaries that must never be
violated without asking:

```markdown
## Invariants (do not violate without asking)
- Always validate inputs at system boundaries
- All timestamps UTC
- No magic numbers in .py files — everything in config.yaml
- Dependency rule: lower layers never import from higher layers
```

### 3. Current phase section

Updated as phases land, with the champion config and headline metrics:

```markdown
## Current phase
See `docs/strategy-phases.md`.

**As of YYYY-MM-DD** the project has completed Phase N. The current
champion is [config]. Metrics: [headline numbers].

Run it: `command here`
```

This is how a fresh Claude Code session orients in 30 seconds.

## Permission Grant for Research Mode

The single biggest unlock is explicit user permission to deviate from the
spec when evidence demands it. Save this as a feedback memory:

```
When empirical evidence contradicts the spec, pivot and document the
deviation in research/REPORT_*.md. The user cares about outcomes, not
compliance. Keep the legacy path working for A/B comparison, but make
the new winner the default.
```

Without this, Claude defaults to spec-following. With it, Claude can chase
surprises and discover genuinely better approaches.

## Supervisor Report Pattern

Every research campaign should produce a `research/REPORT_SUPERVISOR.md`
that narrates:

1. **Trajectory** — numbered list of experiments, 2 sentences each, in order
2. **Pivot points** — explicit "at experiment N we learned X, which changed
   the direction"
3. **Final champion** — config, metrics, how to run, walk-forward validation
4. **Why alternatives lost** — a negative-results table so readers don't
   re-run dead branches
5. **What's next** — out-of-scope candidates flagged for follow-up sessions

The narrative matters because in six months you'll forget why the original
approach failed.

## Experiment Script Template

Every `research/exp_NN_<topic>.py` follows this skeleton:

```python
"""Experiment ENN: <hypothesis in one sentence>.

<2-3 sentences of context: what we learned from the previous experiment
that led to this one, and what we're testing now.>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# 1. Load data
# 2. Define variants to compare
# 3. Run each variant
# 4. Collect metrics into rows[]
# 5. Build a DataFrame
# 6. Save to results/exp_NN_<topic>.csv
# 7. Print sorted leaderboard
```

**Rules:**
- Self-contained — no imports from other experiment scripts
- Deterministic — same data + params → same output
- Leaderboard at the end — always sorted by the primary metric
- CSV saved — the audit trail lives in `results/`, not in the console

## Parallel Agents — Lessons Learned

The parallel-agent pattern sounds great but has real pitfalls:

1. **Default to doing it yourself on main** for research that requires
   iteration. One mind iterating fast beats three minds that can't
   coordinate.
2. **Reserve parallel agents** for truly independent, self-contained work
   with clear deliverables ("implement X, write tests, return a CSV") and
   even then verify they can execute.
3. **Always brief the agent with the current champion state**, not just the
   task. Agents that don't know the context produce work optimised for the
   wrong target.
4. **Agent plans are valuable** even when agents can't execute. Their
   thinking about implementation details (e.g., OLS formulations, slicing
   strategies) can be cribbed directly.

## Test Discipline

Even in research mode, keep the test suite green at every checkpoint:

- Unit tests catch bugs immediately (e.g., cascading cooldown bug)
- A green suite means you can aggressively refactor between experiments
- Integration tests on seeded synthetic fixtures run in seconds
- Write the test when you ship the code, not at the end of the phase

## Checkpoint Rhythm

Don't commit per-experiment — it's too noisy. Commit at phase boundaries
with a coherent message:

```
Phase 0: bootstrap — uv, pyproject, config, docs
Phase 0.5: walking skeleton — data layer + buy-hold
Phase 1: Keltner grid MVP (later rejected — see REPORT_SUPERVISOR)
Phase 2: trend-follower pivot (new champion: EMA 2000, Sharpe 1.53)
```

Each phase commit should leave the repo in a runnable state with tests green.

## Memory Discipline

Three memory types pay off across sessions:

1. **`feedback_*`** — how the user wants you to work (autonomy grants,
   commit policy, communication style)
2. **`project_*_findings`** — empirical results ("X works, Y doesn't,
   here's why") so you don't re-run dead experiments
3. **`project_pivot_notes`** — why the current approach diverges from the
   original spec

Skip writing memories about the spec itself — that's in `docs/`. Memories
are for what the docs don't say.

## The One-Line Summary

**Fail fast in small numbered experiments. Leaderboard decides the next
experiment. Narrative accumulates in REPORT_SUPERVISOR.md. Champion lands
in src/ and CLAUDE.md. Agents are a power tool, not a default.**

If you adopt one thing from this methodology, make it the numbered
`research/exp_NN_*.py` + leaderboard convention. Everything else is
scaffolding around that core loop.

## Reference Templates

This skill includes fill-in-the-blank templates in `references/`:

- `claude-md-template.md` — CLAUDE.md skeleton for new projects
- `exp-script-template.py` — canonical experiment script skeleton
- `supervisor-report-template.md` — REPORT_SUPERVISOR.md structure
- `strategy-phases-template.md` — docs/strategy-phases.md structure

Read these templates when starting a new project to bootstrap the
directory layout and documentation in minutes.
