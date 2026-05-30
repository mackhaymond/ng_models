# Agent Review Protocol

For each submitted assignment:

1. Read `ASSIGNMENT.md`.
2. Run the learner's script.
3. Inspect generated outputs.
4. Read the report.
5. Compare against `.agent_private/RUBRIC.md`.
6. Give feedback in this order:
   - blocker issues
   - modeling/data issues
   - interpretation issues
   - code cleanup
   - one next action

## Feedback format

```markdown
## Review

Status: Pass / Revise

### Highest-impact issue
...

### What is correct
...

### What needs revision
...

### Questions for you
1. ...
2. ...

### Next action
...
```

## Iterative review cadence

Review is a loop, not a one-shot grade. Each assignment ends with this exchange:

1. **Learner states the result.** They say what they built and what they think it
   means — in their own words, before the agent runs anything.
2. **Agent inspects and runs.** Run the script from a clean shell, regenerate
   outputs, read the report. Cross-check against the four passes below.
3. **Agent asks 2–3 substantive questions.** Draw them from
   `.agent_private/QUESTION_TAXONOMY.md` (types A–L), choosing the ones this
   submission actually exposes — typically leakage/timing (A), baseline (B),
   target/transformation (D/E), interpretation (G/J), or coverage (L). These are
   decision questions, not syntax; do not answer them for the learner.
4. **Learner revises.** They update code/report in response. Re-inspect.
5. **Grade via RUBRIC.** Apply `.agent_private/RUBRIC.md` and
   `.agent_private/MASTER_GRADING_STANDARD.md`. Status is Pass or Revise.
6. **Record one next skill.** End with exactly one concrete skill to practice next,
   tied to whichever non-negotiable standard was weakest.

The four review passes used in steps 2 and 5:

1. **Reproducibility** — clean-shell run, one-command outputs, raw data untouched.
2. **Data** — dates, units, frequency, lags, missingness, information-availability.
3. **Modeling** — baseline present, time-ordered validation, no leakage, metric
   matches target.
4. **Interpretation** — energy-market meaning, calibrated claims, specific limits.

## Reveal-rules guardrail

- Do not dump the private solution notes, rubric, or `HINTS.md` into chat.
- Deliver help as L1→L2→L3 prompts (see `QUESTION_TAXONOMY.md`), not by pasting
  any `.agent_private/` file.
- Package-API stalls (taxonomy type K) are the only thing answered directly with
  code; modeling decisions stay with the learner.
- Reveal `.agent_private/` contents only when the learner explicitly asks for
  grading or solution details.
