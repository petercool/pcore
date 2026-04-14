# Supervisor Report — {{PROJECT_NAME}}

**Date:** {{DATE}}
**Window:** {{DATA_WINDOW}}
**Status:** Phase {{N}} complete. Champion ready to ship.

---

## 1. Executive summary

{{2-3 paragraphs: what the project set out to do, what the key finding
was, and the champion strategy/model/config with headline metrics.}}

---

## 2. The bottom line

**Run:** `{{CHAMPION_COMMAND}}`

| Metric | Champion | Baseline | Previous best |
|---|---|---|---|
| {{PRIMARY_METRIC}} | **{{VALUE}}** | {{BASELINE}} | {{PREVIOUS}} |
| {{SECONDARY_METRIC}} | **{{VALUE}}** | {{BASELINE}} | {{PREVIOUS}} |
| {{DD_OR_ERROR_METRIC}} | **{{VALUE}}** | {{BASELINE}} | {{PREVIOUS}} |

---

## 3. Experiment trajectory

### Phase {{N}} — {{Phase title}}

- **ENN**: {{hypothesis}} — {{2-sentence result}}
- **ENN**: {{hypothesis}} — {{2-sentence result}}
- **Pivot point**: at experiment {{N}} we learned {{X}}, which changed
  the direction to {{Y}}.

*(Repeat for each phase.)*

---

## 4. Key findings

### What worked

1. {{Finding with evidence (experiment number, metric delta)}}
2. ...

### What didn't work (negative results preserved)

1. {{Finding with evidence}}
2. ...

### Surprises

1. {{Unexpected finding that shaped the outcome}}
2. ...

---

## 5. Walk-forward / cross-validation

| Fold schedule | Champion | Baseline |
|---|---|---|
| {{SCHEDULE_1}} | {{METRIC}} | {{METRIC}} |
| {{SCHEDULE_2}} | {{METRIC}} | {{METRIC}} |

---

## 6. Lessons learned

### Process
1. {{Lesson about how the work was done}}

### Technical
1. {{Lesson about what the data/system taught you}}

---

## 7. What's next (out of scope, flagged)

1. {{Candidate for future work, with rationale}}
2. ...

### Explicitly rejected

1. {{Dead branch, with experiment number and reason}}

---

## 8. Reproduction

```bash
{{Commands to reproduce every experiment in order}}
```
