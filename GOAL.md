# Provenance Guard — Progress

> Live tracker. A checkbox only gets checked after the corresponding milestone's Checkpoint criteria (quoted verbatim below from `requirements.md`) have been verified, not just after code is written. See `CLAUDE.md` for the full rule.

## Current Status

- **Phase:** Not started
- **Last session:** 2026-06-30 — repo scaffolded (`requirements.md`, `CLAUDE.md`, `GOAL.md`, `planning.md` skeleton, `/goal` command, repo bootstrap).
- **Next step:** Milestone 1 — read the required features list, write the architecture narrative, choose the two detection signals, trace the false-positive scenario, sketch the API surface, draw the submission/appeal flow diagram.

---

## Milestone 1: Understand the System and Define Your Architecture

- [ ] Architecture narrative written — the path a single piece of text takes from submission to the label a user sees, naming every component it touches
- [ ] Two detection signals chosen, each with: what property it measures, why that differs between human/AI writing, and its blind spot
- [ ] False-positive scenario traced through the system (confidence score, label, appeal path)
- [ ] API surface sketched (endpoints, what each accepts/returns)
- [ ] Diagram drawn: submission flow (`POST /submit` → signal 1 → signal 2 → confidence scoring → transparency label → audit log → response) and appeal flow (`POST /appeal` → status update → audit log → response)

**Checkpoint (verbatim):** "You can describe the path a submitted piece of text takes through your system from start to finish, naming every component. You have chosen 2 detection signals and can explain what each captures and what it misses. You have a rough list of the API endpoints you need to build. You have a diagram showing both the submission and appeal flows."

## Milestone 2: Write Your Spec Before Any Code

- [ ] `planning.md` addresses all five questions (detection signals, uncertainty representation, transparency label design, appeals workflow, anticipated edge cases) with specific, implementation-ready answers
- [ ] `## Architecture` section added to `planning.md` (diagram from Milestone 1 + 2–3 sentence narrative)
- [ ] `## AI Tool Plan` section added to `planning.md` (M3, M4, M5: which spec sections to provide, what to ask for, how to verify)
- [ ] Label variants reviewed/revised before building

**Checkpoint (verbatim):** "`planning.md` addresses all five questions with specific answers. You have written out the three label variants (high-confidence AI, high-confidence human, uncertain). Your confidence scoring approach produces different labels at different score ranges — not a binary flip at 0.5. Your `## Architecture` section includes the diagram from Milestone 1. Your `## AI Tool Plan` section covers all three implementation milestones with specific sections, requests, and verification steps."

## Milestone 3: Build the Submission Endpoint and First Detection Signal

- [ ] Flask app set up; `POST /submit` accepts `text` + `creator_id`, returns hardcoded response initially
- [ ] First detection signal implemented and tested independently (direct function calls, inspect output)
- [ ] First signal wired into `/submit`; response includes `content_id`, `attribution`, `confidence`, `label`
- [ ] Audit log set up (structured JSON or SQLite); every submission writes an entry
- [ ] `GET /log` endpoint returns recent entries as JSON

**Checkpoint (verbatim):** "Your Flask app runs. `POST /submit` returns a JSON response including `content_id`, attribution result, and a placeholder confidence score. Each submission writes a structured entry to the audit log. `GET /log` returns those entries as JSON. You can inspect the log and see your test submissions."

## Milestone 4: Add the Second Signal and Implement Confidence Scoring

- [ ] Second detection signal implemented as a standalone function, tested independently
- [ ] Confidence scoring logic implemented, combining both signals per `planning.md`
- [ ] Tested with 4+ deliberately chosen inputs (clearly AI, clearly human, 2 borderline) — scores match intuition or discrepancy investigated
- [ ] Audit log updated to capture both individual signal scores + combined score

**Checkpoint (verbatim):** "Both detection signals are running and their outputs are combined into a single confidence score. Submitting clearly AI-generated text produces a noticeably different score than clearly human-written text. The audit log now records individual signal scores and the combined result. You have tested at least 4 inputs spanning the confidence range."

## Milestone 5: Implement the Production Layer

- [ ] Transparency label: all three variants implemented, label changes based on confidence score, all three reachable via test submissions
- [ ] Appeals workflow: `POST /appeal` accepts `content_id` + `creator_reasoning`, sets status to `under_review`, logs the appeal, returns confirmation
- [ ] Rate limiting applied to `/submit` via Flask-Limiter (`storage_uri="memory://"`); chosen limits documented with reasoning
- [ ] Rate limit verified with the 12-request burst test (10× `200`, then `429`s)
- [ ] Audit log complete: timestamp, content ID, attribution, confidence, both signal scores, appeal status — 3+ entries generated

**Checkpoint (verbatim):** "All four production features are working: the transparency label varies by confidence level, appeals can be submitted and are reflected in the audit log, rate limiting triggers when the limit is exceeded, and the audit log has at least 3 structured entries covering submissions and at least one appeal. All of these work end-to-end without workarounds."

## Milestone 6: Document and Walk Through Your Work

- [ ] README covers all required sections (architecture, detection signals, confidence scoring, transparency label, rate limiting, known limitations, spec reflection, AI usage)
- [ ] Confidence-scoring section includes two example submissions (high-confidence + lower-confidence) with actual scores
- [ ] All three label variants typed out verbatim in README
- [ ] Known limitations section names a specific content type likely to be misclassified and why
- [ ] Spec reflection written (one way spec helped, one way implementation diverged and why)
- [ ] AI usage section: 2+ specific instances of what was directed, produced, and revised/overridden
- [ ] Portfolio walkthrough video recorded

**Checkpoint (verbatim):** "README covers all required sections with substantive explanations of design decisions, not just feature descriptions. All three transparency label variants are written out. You've recorded a short portfolio walkthrough giving a quick tour of your system."

---

## Required Features

- [ ] Content Submission Endpoint
- [ ] Multi-Signal Detection Pipeline (2+ distinct signals)
- [ ] Confidence Scoring with Uncertainty
- [ ] Transparency Label (3 variants)
- [ ] Appeals Workflow
- [ ] Rate Limiting
- [ ] Audit Log (3+ entries visible)

## Stretch Features

- [ ] Ensemble detection (3+ signals, documented weighting/voting)
- [ ] Provenance certificate ("verified human" credential)
- [ ] Analytics dashboard
- [ ] Multi-modal support (second content type)

---

## Session Handoff Notes

> Updated immediately before every `/clear`. What's in progress, what broke, the exact next action.

- (none yet — scaffolding session only)
