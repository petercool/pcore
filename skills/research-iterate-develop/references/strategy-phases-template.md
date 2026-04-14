# Strategy Phases

Authoritative phase roadmap. Update the "Status" column when a phase
completes. Each phase has a concrete exit criterion.

## Phase 0 — Bootstrap

| Item | Notes |
|---|---|
| Status | {{STATUS: pending / landed}} |
| Deliverables | {{List: project scaffold, config, docs, initial tests}} |
| Exit criterion | {{Concrete check: "uv run pytest passes", "smoke test runs"}} |

## Phase 0.5 — Walking Skeleton

| Item | Notes |
|---|---|
| Status | {{STATUS}} |
| Deliverables | {{List: data layer, minimal runner, CLI entry point}} |
| Exit criterion | {{Concrete check: "end-to-end produces a finite metric"}} |

## Phase 1 — {{First real implementation}}

| Item | Notes |
|---|---|
| Status | {{STATUS}} |
| Deliverables | {{List of modules, tests, experiments}} |
| Exit criterion | {{Metric-based: "Sharpe is finite, trade count > 0"}} |

## Phase 2 — {{Research pivot or iteration}}

| Item | Notes |
|---|---|
| Status | {{STATUS}} |
| Deliverables | {{List}} |
| Exit criterion | {{Walk-forward validated, parameter sweep stable}} |

*(Add more phases as needed. Keep each phase's section short —
5 rows max per table.)*

## How to update this file

When a phase's exit criterion passes:

1. Change "Status" to "Landed"
2. If deliverables drifted from the plan, edit to match reality
3. Commit alongside the phase's code in the same PR
