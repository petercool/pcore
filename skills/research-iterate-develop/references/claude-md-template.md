# {{PROJECT_NAME}}

## What this is

{{DESCRIPTION — 2-3 sentences explaining what the project does and why.}}

## Sources of truth

| Document | Role |
|---|---|
| `docs/{{SPEC_FILE}}` | {{ROLE — e.g., "Strategy spec — what the system does and why"}} |
| `docs/{{ADR_FILE}}` | {{ROLE — e.g., "Implementation requirements — how the code is structured"}} |
| `.claude/skills/{{SKILL}}/SKILL.md` | {{ROLE — e.g., "Framework skill — how to use the framework"}} |

**If {{SPEC_FILE}} and {{ADR_FILE}} conflict, stop and ask the user.**

## How to run

```bash
{{INSTALL_COMMAND}}                        # one-time setup
{{DATA_COMMAND}}                           # data preparation (if applicable)
{{RUN_COMMAND}}                            # run the current champion
{{TEST_COMMAND}}                           # run tests
```

## Invariants (do not violate without asking)

{{LIST — project-specific rules. Examples:}}
- All timestamps UTC
- No magic numbers in `.py` files — everything in `config.yaml`
- Dependency rule: lower layers never import from higher layers
- {{FRAMEWORK_RULE_1}}
- {{FRAMEWORK_RULE_2}}

## Repo layout

```
{{PROJECT_NAME}}/
├── src/                          # production modules
├── tests/                        # unit + integration tests
├── research/
│   ├── exp_NN_<topic>.py         # frozen experiment scripts
│   └── REPORT_*.md               # research reports
├── results/                      # (gitignored) experiment outputs
├── docs/
│   ├── {{SPEC_FILE}}
│   ├── {{ADR_FILE}}
│   ├── architecture.md
│   └── strategy-phases.md        # phase roadmap
├── config.yaml                   # all parameters (if applicable)
└── CLAUDE.md                     # (this file)
```

## Current phase

See `docs/strategy-phases.md` for the authoritative status.

**As of {{DATE}}** the project has completed **Phase {{N}}**.
The current champion is {{CHAMPION_CONFIG}}.

### Champion metrics

| Metric | Value |
|---|---|
| {{PRIMARY_METRIC}} | {{VALUE}} |
| {{SECONDARY_METRIC}} | {{VALUE}} |

Run it: `{{RUN_CHAMPION_COMMAND}}`

## What this project is NOT

- {{EXCLUSION_1 — e.g., "Not a live trading system"}}
- {{EXCLUSION_2 — e.g., "Not asynchronous"}}
- {{EXCLUSION_3 — e.g., "Not a web app"}}
