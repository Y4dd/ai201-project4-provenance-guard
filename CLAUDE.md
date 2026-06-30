# Provenance Guard — Project Context

**Project:** AI201 Project 4 ("Provenance Guard") — a Flask backend that classifies submitted text as likely AI-generated, human-written, or uncertain, using at least two independent detection signals, scores its own confidence, surfaces a plain-language transparency label, and lets creators appeal a classification. Production safety infrastructure (rate limiting, structured audit log) is required, not optional.

**Ground truth:** [`requirements.md`](./requirements.md) is a verbatim Markdown conversion of the assignment PDF (mechanical reformatting only, no rewording — see the note at the top of that file). When you need the exact wording of a requirement, a checkpoint, a curl command, or a JSON shape, **read and quote `requirements.md` — do not recall it from memory or from earlier in a conversation.** Memory drifts over a long multi-session build; the file doesn't.

## Tech stack

- API framework: **Flask**
- Detection signal 1: **Groq**, model `llama-3.3-70b-versatile` (same account as Projects 1–3)
- Detection signal 2: **stylometric heuristics**, pure Python (sentence length variance, type-token ratio, punctuation density, etc. — no external libraries)
- Rate limiting: **Flask-Limiter**
- Audit log: **SQLite** or structured **JSON** (never bare `print()` statements)

## Data contracts (don't drift from these field names)

Pulled verbatim from `requirements.md`'s example payloads — reuse these exact names in every milestone so the API stays internally consistent across sessions:

- `POST /submit` request: `text`, `creator_id`
- `POST /submit` response: `content_id`, `attribution`, `confidence`, `label`
- Audit log entry: `content_id`, `creator_id`, `timestamp`, `attribution`, `confidence`, `llm_score` (and the equivalent for signal 2), `status` (`"classified"` or `"under_review"`)
- `GET /log` response: `{"entries": [...]}`
- `POST /appeal` request: `content_id`, `creator_reasoning`
- Appeal-related audit log fields: `status: "under_review"`, `appeal_reasoning`

If a future session is tempted to rename one of these (e.g. `contentId`, `confidence_score`), don't — check this list first.

## Required features (see `requirements.md` → Features for full text)

1. Content Submission Endpoint
2. Multi-Signal Detection Pipeline (2+ distinct signals)
3. Confidence Scoring with Uncertainty (not a binary label)
4. Transparency Label (3 variants, exact text required in README)
5. Appeals Workflow
6. Rate Limiting (documented reasoning)
7. Audit Log (3+ visible entries)

## Stretch features (optional, extra credit)

Ensemble detection · Provenance certificate · Analytics dashboard · Multi-modal support — see `requirements.md` → Stretch Features before starting any of these, and update `planning.md` first.

## Constraints to keep front-of-mind

- A **false positive** (flagging a human's work as AI-generated) is worse than a false negative on a creative-writing platform. Confidence scoring and label design should reflect that asymmetry.
- The confidence score is a **design decision before a technical one** — decide what 0.5 should mean to a user before writing the scoring code.
- **Never paste AI-generated code without testing it independently first.** The spec explicitly warns (Milestone 4) that AI tools can produce scoring logic that looks reasonable but silently diverges from the thresholds in `planning.md`. Test each generated function against the spec's stated behavior before wiring it into the app.
- Don't invent grading point values. The 29-point breakdown lives on a separate course "grading page" that isn't part of our source material — `GOAL.md` tracks feature/milestone completion only.

## Workflow: `planning.md`, `GOAL.md`, and session boundaries

- **`planning.md`** is the project's actual required deliverable (exact filename, repo root) — it's both the design doc (the five questions + `## Architecture` + `## AI Tool Plan`, per `requirements.md` → Milestone 2) and the literal material you hand an AI tool when generating code in Milestones 3–5. Don't generate implementation code for a milestone whose corresponding `planning.md` section isn't filled in yet.
- **`GOAL.md`** is the live progress tracker. Each milestone section's checkboxes only get checked off **after** that milestone's Checkpoint criteria (copied verbatim from `requirements.md`) have actually been verified — a curl command run, the audit log inspected, a rate-limit burst test observed — not merely after code has been written. Generated code is not the same as a completed milestone.
- After a milestone's checkpoint is verified: update `GOAL.md` (checkboxes + the `## Session Handoff Notes` section with what's done / what's next), then tell the user to run `/clear`.
- Start the next session with `/goal` — it reads `GOAL.md`, the relevant slice of `planning.md`, and the matching milestone section of `requirements.md`, reports status, and proceeds with the next step.
