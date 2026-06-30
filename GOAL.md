# Provenance Guard — Progress

> Live tracker. A checkbox only gets checked after the corresponding milestone's Checkpoint criteria (quoted verbatim below from `requirements.md`) have been verified, not just after code is written. See `CLAUDE.md` for the full rule.

## Current Status

- **Phase:** Milestone 6 README written and verified. Only remaining work on the entire project: record the portfolio walkthrough video.
- **Last session:** 2026-06-30 — wrote `README.md` covering all required M6 sections, sourced directly from `planning.md` and real logged data in `audit_log.json` (no invented numbers): architecture (both flow diagrams + narrative), detection signals (what/why/blind spot for each), confidence scoring (full formula + two real example submissions — 76% `likely_ai` vs. 57% `uncertain` — with the dampening-rule arithmetic traced out explicitly), all three transparency label variants (verified byte-for-byte identical to `planning.md` via direct string-membership check), rate limiting (limits + reasoning + the 10×200/2×429 burst evidence cross-referenced against actual audit log timestamps), known limitations (poem/refrain edge case), spec reflection (the false-positive-asymmetry hint shaping the scoring design; the punctuation-absence calibration as the implementation divergence), and an AI usage section with the two documented M4 stylometric calibration bugs (punctuation-absence cap, all-caps acronym match) in directed/produced/revised form.
- **Next step:** Record the portfolio walkthrough video (a couple of minutes, unpolished — show the system working end-to-end via a few `/submit` calls spanning the three labels, one `/appeal`, and a quick mention of the rate limit). This is the one remaining checkpoint item and isn't something an AI session can do — needs the user to run the app and record themselves. Once recorded, link it in `README.md`'s "Portfolio walkthrough" section (currently a TODO placeholder) and check off the last M6 box + the Milestone 6 checkpoint as a whole — that completes the entire required-features list for the project.

---

## Milestone 1: Understand the System and Define Your Architecture

- [x] Architecture narrative written — the path a single piece of text takes from submission to the label a user sees, naming every component it touches (see `planning.md` → `## Architecture`)
- [x] Two detection signals chosen, each with: what property it measures, why that differs between human/AI writing, and its blind spot (`planning.md` → `## Detection Signals`)
- [x] False-positive scenario traced through the system (confidence score, label, appeal path) — informed the disagreement-dampening + asymmetric AI gate in `## Uncertainty Representation`
- [x] API surface sketched (`POST /submit`, `GET /log`, `POST /appeal` — see `CLAUDE.md` data contracts)
- [x] Diagram drawn: submission flow and appeal flow (`planning.md` → `## Architecture`)

**Checkpoint (verbatim):** "You can describe the path a submitted piece of text takes through your system from start to finish, naming every component. You have chosen 2 detection signals and can explain what each captures and what it misses. You have a rough list of the API endpoints you need to build. You have a diagram showing both the submission and appeal flows."

## Milestone 2: Write Your Spec Before Any Code

- [x] `planning.md` addresses all five questions (detection signals, uncertainty representation, transparency label design, appeals workflow, anticipated edge cases) with specific, implementation-ready answers
- [x] `## Architecture` section added to `planning.md` (diagram from Milestone 1 + narrative)
- [x] `## AI Tool Plan` section added to `planning.md` (M3, M4, M5: which spec sections to provide, what to ask for, how to verify)
- [x] Label variants reviewed/revised before building — three exact-text variants written in `## Transparency Label Design`

**Checkpoint (verbatim):** "`planning.md` addresses all five questions with specific answers. You have written out the three label variants (high-confidence AI, high-confidence human, uncertain). Your confidence scoring approach produces different labels at different score ranges — not a binary flip at 0.5. Your `## Architecture` section includes the diagram from Milestone 1. Your `## AI Tool Plan` section covers all three implementation milestones with specific sections, requests, and verification steps."

## Milestone 3: Build the Submission Endpoint and First Detection Signal

- [x] Flask app set up; `POST /submit` accepts `text` + `creator_id`, returns hardcoded response initially
- [x] First detection signal implemented and tested independently (direct function calls, inspect output)
- [x] First signal wired into `/submit`; response includes `content_id`, `attribution`, `confidence`, `label`
- [x] Audit log set up (structured JSON or SQLite); every submission writes an entry
- [x] `GET /log` endpoint returns recent entries as JSON

**Checkpoint (verbatim):** "Your Flask app runs. `POST /submit` returns a JSON response including `content_id`, attribution result, and a placeholder confidence score. Each submission writes a structured entry to the audit log. `GET /log` returns those entries as JSON. You can inspect the log and see your test submissions."

## Milestone 4: Add the Second Signal and Implement Confidence Scoring

- [x] Second detection signal implemented as a standalone function, tested independently
- [x] Confidence scoring logic implemented, combining both signals per `planning.md`
- [x] Tested with 4+ deliberately chosen inputs (clearly AI, clearly human, 2 borderline) — scores match intuition or discrepancy investigated
- [x] Audit log updated to capture both individual signal scores + combined score

**Checkpoint (verbatim):** "Both detection signals are running and their outputs are combined into a single confidence score. Submitting clearly AI-generated text produces a noticeably different score than clearly human-written text. The audit log now records individual signal scores and the combined result. You have tested at least 4 inputs spanning the confidence range."

## Milestone 5: Implement the Production Layer

- [x] Transparency label: all three variants implemented, label changes based on confidence score, all three reachable via test submissions
- [x] Appeals workflow: `POST /appeal` accepts `content_id` + `creator_reasoning`, sets status to `under_review`, logs the appeal, returns confirmation
- [x] Rate limiting applied to `/submit` via Flask-Limiter (`storage_uri="memory://"`); chosen limits documented with reasoning
- [x] Rate limit verified with the 12-request burst test (10× `200`, then `429`s)
- [x] Audit log complete: timestamp, content ID, attribution, confidence, both signal scores, appeal status — 3+ entries generated

**Checkpoint (verbatim):** "All four production features are working: the transparency label varies by confidence level, appeals can be submitted and are reflected in the audit log, rate limiting triggers when the limit is exceeded, and the audit log has at least 3 structured entries covering submissions and at least one appeal. All of these work end-to-end without workarounds."

## Milestone 6: Document and Walk Through Your Work

- [x] README covers all required sections (architecture, detection signals, confidence scoring, transparency label, rate limiting, known limitations, spec reflection, AI usage)
- [x] Confidence-scoring section includes two example submissions (high-confidence + lower-confidence) with actual scores
- [x] All three label variants typed out verbatim in README
- [x] Known limitations section names a specific content type likely to be misclassified and why
- [x] Spec reflection written (one way spec helped, one way implementation diverged and why)
- [x] AI usage section: 2+ specific instances of what was directed, produced, and revised/overridden
- [ ] Portfolio walkthrough video recorded

**Checkpoint (verbatim):** "README covers all required sections with substantive explanations of design decisions, not just feature descriptions. All three transparency label variants are written out. You've recorded a short portfolio walkthrough giving a quick tour of your system."

---

## Required Features

- [x] Content Submission Endpoint
- [x] Multi-Signal Detection Pipeline (2+ distinct signals)
- [x] Confidence Scoring with Uncertainty
- [x] Transparency Label (3 variants)
- [x] Appeals Workflow
- [x] Rate Limiting
- [x] Audit Log (3+ entries visible)

## Stretch Features

- [ ] Ensemble detection (3+ signals, documented weighting/voting)
- [ ] Provenance certificate ("verified human" credential)
- [ ] Analytics dashboard
- [ ] Multi-modal support (second content type)

---

## Session Handoff Notes

> Updated immediately before every `/clear`. What's in progress, what broke, the exact next action.

- **2026-06-30 (M1-2):** `planning.md` fully written (signals, scoring formula, label text, appeals workflow, edge cases, architecture diagram, AI Tool Plan). Nothing implemented yet.
- **2026-06-30 (M3, complete):** Built and verified the full submission pipeline:
  - `app.py` — `POST /submit` (returns `content_id`, `attribution`, `confidence`, `label`; the latter two are M3 placeholders, not yet the real combined score/label) and `GET /log` (`{"entries": [...]}`).
  - `signals.py` — `groq_ai_score(text) -> float`, Signal 1 (Groq `llama-3.3-70b-versatile`), JSON-mode prompt per `planning.md` → Detection Signals §1. Verified independently against the four M4 example texts: clearly-AI 0.92, clearly-human 0.23, borderline-formal-human 0.85 (correctly reproduces the documented "monetary policy" blind spot), borderline-lightly-edited-AI 0.23.
  - `audit_log.py` — JSON-file-backed log (`audit_log.json`, gitignored) with `append_entry`/`get_entries`; entries match `CLAUDE.md`'s field list exactly (`content_id`, `creator_id`, `timestamp`, `attribution`, `confidence`, `llm_score`, `status`).
  - Verification note: real `curl` against the running dev server is blocked by this session's Bash tool permission settings (denied even with the sandbox restriction lifted — not a sandbox/network-allowlist issue, an explicit permission denial). Verified instead via Flask's in-process `test_client()`, which exercises the identical route code without a real socket. 3 submissions run, `audit_log.json` inspected directly and confirmed correct. If a future session has curl permission available, a real end-to-end curl pass would still be worth doing once, but isn't blocking.
  - Next action: Milestone 4 — implement Signal 2 (stylometric heuristics) as a standalone function tested independently, then replace the M3 placeholder confidence/attribution in `app.py` with the real combined-scoring function from `planning.md` → `## Uncertainty Representation` (disagreement dampening + asymmetric `likely_ai` gate — not a plain average). Test with the same four example texts plus 4+ deliberately chosen inputs per the M4 checkpoint. Update the audit log to also capture `stylometric_score`. Good point to `/clear` before diving into M4.
- **2026-06-30 (M4, complete):** Built and verified Signal 2 + real confidence scoring:
  - `signals.py` — added `stylometric_score(text) -> float`: averages three sub-scores (sentence-length-variance coefficient of variation, type-token ratio, punctuation density/variety), each pure Python, no external libraries. Two calibration bugs found and fixed during independent testing (per `CLAUDE.md`'s "test generated functions against the spec's stated behavior" rule): (1) the all-caps marker was matching the 2-letter acronym "AI" itself in the clearly-AI example, pushing its score the wrong direction — fixed by requiring len≥3 for all-caps detection; (2) the punctuation sub-score mapped "zero expressive punctuation" straight to full AI-confidence (1.0), which is true of nearly all formal prose regardless of authorship — this caused `borderline_formal_human` (the spec's own "monetary policy" trap) to clear the asymmetric gate and produce a false-positive `likely_ai`. Fixed by capping the zero-density case at a mild lean (0.6) instead of full confidence (1.0); absence of markers is weak evidence, presence is strong evidence, so the mapping is now intentionally asymmetric.
  - `scoring.py` — new module, `score_confidence(llm_score, stylometric_score) -> (combined_score, attribution)`, implementing `planning.md`'s exact formula (disagreement dampening when |llm−stylometric| > 0.35, asymmetric gate requiring both signals ≥ 0.55 for `likely_ai`) — verified line-for-line against the spec, not a plain average.
  - Verified against the four M4 example texts plus a fifth extreme/formulaic-AI text to confirm `likely_ai` is actually reachable: clearly-AI → combined 0.588 (`uncertain` — conservative by design, consistent with the project's stated false-positive-avoidance philosophy in `CLAUDE.md`'s Constraints section, since the structural signal alone isn't confident enough to clear the agreement gate); clearly-human → 0.257 (`likely_human`); borderline-formal-human → 0.683 (`uncertain` — confirms the false-positive trap is now avoided); borderline-lightly-edited-AI → 0.287 (`likely_human` — matches the documented Signal 2 blind spot in `planning.md`'s Edge Case 3, not a new bug); extreme-formulaic-AI → 0.842 (`likely_ai`, confirming that label is reachable when both signals genuinely agree). All three attribution categories reachable; clearly-AI vs. clearly-human combined scores are noticeably different (0.588 vs 0.257), satisfying the M4 checkpoint.
  - `app.py` — `/submit` now calls both signals and `score_confidence`; audit log entries include `llm_score`, `stylometric_score`, and combined `confidence`/`attribution`. Verified end-to-end via Flask's in-process `test_client()` (real `curl` still blocked by this session's Bash permission settings) — 4 new submissions run, `audit_log.json` inspected directly, all fields present and correct.
  - Worth carrying into M6's "spec reflection" / "known limitations" sections: the calibration story above (punctuation sub-score's asymmetric treatment, and the conservative `uncertain`-not-`likely_ai` outcome for clearly-AI text) is a concrete, specific example of implementation diverging from a naive reading of the spec and why — good README material.
  - Next action: Milestone 5 — label generator (3 exact-text variants), `POST /appeal`, Flask-Limiter on `/submit` (`storage_uri="memory://"`, document the chosen limits), 12-request burst test (10×200 then 429s), confirm audit log has 3+ entries covering submissions and at least one appeal. Good point to `/clear` before diving into M5.
- **2026-06-30 (M5, complete):** Built and verified all four production features:
  - `scoring.py` — added `generate_label(combined_score, attribution)`, mapping to the three exact-text variants from `planning.md` → `## Transparency Label Design` (including the uncertain variant's appeal invitation). Verified independently across the full 0–1 range (0.1 through 0.95) before wiring in — all three variants reachable, text byte-for-byte matches the spec.
  - `app.py` — `/submit` now returns the real generated label (replacing the M3 placeholder). Added `POST /appeal`: looks up the original entry via `audit_log.find_entry`, appends a *new* log entry (not a mutation) with `status: "under_review"` and `appeal_reasoning`, carrying forward the original `attribution`/`confidence`/signal scores per `planning.md` → `## Appeals Workflow`; returns 404 for an unknown `content_id`. Added Flask-Limiter (`10 per minute;100 per day`, `storage_uri="memory://"`) on `/submit`, with the realistic-usage-vs-abuse reasoning documented as a code comment (also needs to land in the README in M6).
  - `audit_log.py` — added `find_entry(content_id)` (searches most-recent-first, so a re-appealed item resolves to its latest state).
  - Verified end-to-end via `test_client()` (real `curl` against the running dev server confirmed still blocked by this session's Bash permission settings — same denial as M3/M4, not re-investigated further since the in-process route-level verification is equivalent): clearly-AI text → `likely_ai` label at 76%; clearly-human → `likely_human` at 22%; borderline/monetary-policy-style text → `uncertain` at 57%, then appealed successfully (new log entry with `status: under_review`, `appeal_reasoning` populated, original entry left intact); appeal with a nonexistent `content_id` → 404. 12-request burst test against `/submit` produced exactly `[200×10, 429×2]`, matching the spec's documented expected output. `audit_log.json` has 12 entries spanning all three attribution categories plus one appeal.
  - Next action: Milestone 6 (final) — write `README.md` covering architecture, detection signals (what/why/blind spot for each), confidence scoring (include the two M4 example scores: clearly-AI 0.588 vs. clearly-human 0.257), all three label variants typed out verbatim, rate-limiting reasoning + the captured 429 burst-test output, known limitations (the poem/refrain-heavy edge case from `planning.md` is a ready-made answer), spec reflection (the punctuation-sub-score calibration story from the M4 notes above is good material), and an AI usage section with 2+ specific directed/produced/revised instances (the M4 calibration bugs and this milestone's "AI tools default to a plain average, check for that" note are both concrete examples). Then record the portfolio walkthrough video. `/clear` before starting M6 — it's pure documentation, no code dependencies on prior session context.
- **2026-06-30 (REVIEW_FINDINGS.md fix pass):** Implemented the 4 open gap items from a 5-agent review (`REVIEW_FINDINGS.md`), each verified against real data, not asserted:
  - GAP-1: added `### False-Positive Trace` to `planning.md` → `## Uncertainty Representation`, walking the real `borderline_formal_human` audit log entry (`ce05ba47…`) through scores → 68% `uncertain` label → a real `POST /appeal` fired against that same entry via the test client (new `under_review` log entry, original untouched).
  - GAP-2: added an `### API Surface` table to `planning.md` → `## Architecture` covering all three endpoints including `GET /log`.
  - GAP-3/GAP-4: re-ran a fresh 12-request burst against a real running instance of the app (genuine HTTP/socket, real Flask-Limiter, not `test_client()`) and pasted the literal `200`×10/`429`×2 status-code output plus the correct content-ID/timestamp citation into README's Rate limiting section, replacing the old prose-only (and partially wrong) citation.
  - GAP-5: documented the spec's own M3 curl-example/`creator_id` inconsistency as a known divergence in README's Spec reflection section; `app.py`'s validation deliberately left unchanged (the locked `CLAUDE.md` contract is correct).
  - All four checked off in `REVIEW_FINDINGS.md` with evidence notes. **CRIT-1 remains open**: implementation is committed locally (`d7a3143`) and `origin` is set, but nothing has been pushed — needs explicit user go-ahead before `git push` (a visible, hard-to-reverse action), not something to do unprompted.
  - Test runs in this session appended new entries to `audit_log.json` (gitignored, not part of this diff) — harmless, but a future session reading that file should expect a few extra `burst_verify`/appeal entries beyond what M3–M6's handoff notes describe.
  - Next action: ask the user whether to push to GitHub now; if yes, run the push (note in `CLAUDE.md`: git operations needing the SSH agent require the sandbox restriction lifted for that one Bash call). After that, the only remaining work on the entire project is the portfolio walkthrough video (unchanged from before this pass).
- **2026-06-30 (M6, README complete; video still outstanding):** Wrote the full `README.md` directly from `planning.md` + real `audit_log.json` data (no invented examples):
  - Pulled the "two example submissions" for the confidence-scoring section straight from existing logged entries rather than re-running new submissions: `content_id abd1913a…` (llm 0.92, stylometric 0.604, combined 76%, `likely_ai`) and `content_id 4631281e…` (llm 0.92, stylometric 0.367, combined 57%, `uncertain`). Worked out and verified the dampening arithmetic for the second one by hand (`python3 -c`): naive average 0.6433, |diff| 0.5533 > 0.35 threshold, dampened to 0.5717 — matches the logged value exactly, so the README's worked example is provably correct, not just plausible.
  - Verified all three label variants are byte-for-byte identical between `README.md` and `planning.md` via a string-membership check (`python3 -c`) rather than eyeballing — both came back `True`.
  - Rate-limiting section cites the actual burst-test evidence already sitting in `audit_log.json` from M5 (10 entries, `creator_id: "test"`, timestamps `20:27:40.626`–`20:27:43.051`) rather than re-asserting the M5 handoff note's claim unverified.
  - AI usage section uses only the two well-documented M4 stylometric calibration bugs (punctuation-absence cap, all-caps-acronym match) — deliberately did not invent a third instance just to pad the count; two specific, verifiable instances satisfy the "2+" requirement better than a vague third one would.
  - Checked off every M6 GOAL.md box **except** "Portfolio walkthrough video recorded" — that one requires the user to actually run the app and record themselves narrating it; not something this session can do. `README.md`'s walkthrough section currently has a `TODO` placeholder for the video link.
  - Next action: user records the walkthrough video (a couple of minutes, unpolished — a few `/submit` calls spanning the three labels, one `/appeal`, mention the rate limit), links it in `README.md`, then checks off the final GOAL.md box. That closes Milestone 6 and the entire project's required-features checklist. No further `/goal` session is needed unless stretch features get picked up afterward — check `requirements.md` → Stretch Features and update `planning.md` first if so, per `CLAUDE.md`.
