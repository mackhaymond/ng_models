# ng-models — Natural Gas Modeling Curriculum

A guided, AI-tutored path that takes you from raw natural-gas data to a full,
reproducible **Henry Hub price forecast system and research memo** — beating
market and seasonal baselines, with honest uncertainty and a documented failure
analysis.

It assumes you are a capable programmer who is *new* to the specific tools of
applied forecasting (pandas, statsmodels, scikit-learn, lightgbm, …) and whose
stats/time-series/ML intuition is still basic. Concepts are taught from the
ground up, at the point you need them.

## → Start here

**Read [`START_HERE.md`](START_HERE.md) first.** It explains what you are
building, the order to work in, the per-assignment loop, and how to use the AI
tutor.

Then, from the repo root:

```bash
uv run python 00_repo_data_inventory/main.py
```

(Run every module from the repo root so paths resolve. The starters are
intentionally incomplete — you fill in the modeling decisions.)

## Prerequisites

- Python ≥ 3.12 and [`uv`](https://docs.astral.sh/uv/). `uv run …` installs the
  dependencies in `pyproject.toml` automatically on first use.
- The EIA data is already in `data/`. A few later modules (weather, futures,
  power) need data you collect yourself — each says so via a `DATA_COLLECTION.md`.

## Using your AI tutor (Codex, opencode, Claude, …)

The tutoring rules live in [`AGENTS.md`](AGENTS.md) — the open agent-instructions
standard that **Codex and opencode read automatically** from the repo root (Claude
Code reads it too). Nothing here is tied to a specific assistant.

To start a session, point your agent at this repo and say something like:
*"Act as the tutor defined in AGENTS.md. I'm working on `<module>`; review my work
/ give me a hint / explain X."* The agent loads `AGENTS.md`, then reads that
module's `.agent_private/HINTS.md`, `RUBRIC.md`, and `SOLUTION_NOTES.md` on demand
to guide and grade you. Those private files are tutor-facing — `AGENTS.md`
instructs the agent not to reveal them during normal tutoring.

## How it is organized

| Path | What it is |
|---|---|
| [`START_HERE.md`](START_HERE.md) | Learner onboarding — read this first. |
| [`CURRICULUM.md`](CURRICULUM.md) | The full 00→14 sequence, phases, cadence, and standards. |
| `NN_*/` | The 15 assignment modules (00–14), each with `ASSIGNMENT.md`, a runnable `main.py` starter, and a `REPORT_TEMPLATE.md`. |
| `docs/` | [`GLOSSARY_SEED.md`](docs/GLOSSARY_SEED.md) (terms), [`MODELING_PLAYBOOK.md`](docs/MODELING_PLAYBOOK.md) (how-to), [`DATA_SOURCE_NOTES.md`](docs/DATA_SOURCE_NOTES.md) (data + sources). |
| `src/ng_models/` | Shared helpers (data loading, metrics, features, plotting) — you call these, you don't reimplement them. |
| `data/` | Raw EIA series (immutable) + `_metadata.csv` catalog. |
| `AGENTS.md` | Rules the AI tutor follows (how it helps, what it withholds). |

Each module's generated output goes in its own `outputs/` folder. Raw data in
`data/` is never modified.

## The non-negotiable habits

No leakage, ever. Always beat a baseline. Document every feature's timing. State
what would make your model fail. (See `START_HERE.md` for the full version — these
are the point of the curriculum, not busywork.)
