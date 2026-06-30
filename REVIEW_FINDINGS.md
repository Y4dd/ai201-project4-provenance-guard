# Review Findings — Fix Plan

> Produced 2026-06-30 by a 5-agent relentless review of every milestone against `requirements.md` (each agent independently re-executed code/arithmetic rather than trusting `GOAL.md`'s self-report). This is a **punch list**, not a spec — `planning.md` stays the design doc, `GOAL.md` stays the milestone tracker. Work through items top to bottom; check each off only after the fix is actually verified, same rule as `GOAL.md`.

## CRIT-1 — Implementation never committed to git; no GitHub remote

- [x] Fixed 2026-06-30
- **Found by:** repo-state check (orchestrator) + M6 agent, independently
- **Evidence:** `git ls-files` showed only docs tracked (`CLAUDE.md`, `GOAL.md`, `README.md`, `planning.md`, `requirements.md`, `requirements.txt`, `.gitignore`). `app.py`, `signals.py`, `scoring.py`, `audit_log.py` were all untracked (`??`). `git remote -v` returned nothing.
- **Why it matters:** `requirements.md` (Deliverables & Format) calls committed source code + README "the canonical record graders rely on," and the submission checklist requires a GitHub repo link. With nothing committed and no remote, there's no repo to link.
- **Fix:** add remote `git@github.com:Y4dd/ai201-project4-provenance-guard.git`, commit the implementation files + updated `README.md`/`GOAL.md`/`.gitignore`, push.

## GAP-1 — M1: no false-positive scenario actually traced

- [ ] Open
- **Found by:** Milestone 1&2 review agent
- **Requirements.md checkpoint (verbatim, L137):** "Think through the false positive problem... Trace that scenario through your system — how does the confidence score reflect the uncertainty, what does the label say, and how does the creator appeal? This scenario should inform your decisions in Milestone 2."
- **Evidence:** `planning.md` invokes the false-positive asymmetry abstractly four times (L23, L35–38, L48, L58 — "the false-positive asymmetry called out in the spec's hints," "to make false positives harder to produce") but never walks one concrete example through: specific human text → specific signal scores → combined score → label text → appeal outcome.
- **Fix:** add a short worked example to `planning.md` (new subsection under `## Uncertainty Representation` or a new `## False-Positive Trace`), e.g. using the real `borderline_formal_human` / monetary-policy example already in the repo's test data — llm_score, stylometric_score, combined score, which label fires, and what the creator sees if they appeal.

## GAP-2 — M1: `GET /log` missing from the API surface sketch

- [ ] Open
- **Found by:** Milestone 1&2 review agent
- **Requirements.md checkpoint (verbatim, L138):** "Sketch... your API surface: what endpoints do you need? What does each one accept and return?"
- **Evidence:** `planning.md`'s diagram/narrative only sketches `POST /submit` and `POST /appeal` accept/return shapes. `GET /log` appears exactly once, in the AI Tool Plan (L126), only as a verification *command* — never defined as an endpoint with its own accept/return contract.
- **Fix:** add `GET /log` to `planning.md`'s API surface (no request body; returns `{"entries": [...]}`) — a couple of lines near the `POST /submit` / `POST /appeal` sketch is enough.

## GAP-3 — M6: rate-limit 429 evidence not pasted in README

- [ ] Open
- **Found by:** Milestone 6 review agent
- **Requirements.md (verbatim, L317):** "Capture those 429 responses in your README (paste the status-code output) — that's the evidence graders need."
- **Evidence:** README's "Rate limiting" section only narrates the result in prose ("the first 10 returned 200, the next 2 returned 429") — no pasted command/output block.
- **Fix:** re-run the 12-request burst loop from `requirements.md` Milestone 5 against a live server, paste the literal status-code output (e.g. a fenced code block of `200`×10 then `429`×2) into the README's Rate limiting section.

## GAP-4 — M6: wrong content-ID/timestamp citation in rate-limit section

- [ ] Open
- **Found by:** Milestone 6 review agent
- **Evidence:** README cites the burst-test range as content IDs `abd1913a…` through `e762e23e…`, timestamps `20:27:40.626`–`20:27:43.051`. Actual data: `abd1913a…`'s real timestamp is `20:26:47.347585` — about a minute *before* that window, not part of the burst. The real burst entries run `a847fb22…` through `e762e23e…`.
- **Fix:** re-check `audit_log.json` for the actual 10-entry burst-test range and correct the cited content IDs/timestamps in the README's Rate limiting section. (The underlying claim — 10 logged, 2 silently rejected — is still true; only the citation is wrong.) Doing this alongside GAP-3's re-run is the efficient path — capture fresh, correct evidence in one pass.

## GAP-5 — M3: spec's own curl example 400s against this implementation

- [ ] Open
- **Found by:** Milestone 3 review agent
- **Evidence:** The exact curl command in `requirements.md` Milestone 3 (L186–190) sends `{"text": "..."}` with no `creator_id`. `app.py` correctly requires `creator_id` per `CLAUDE.md`'s locked data contract, so that literal command returns `400 {"error": "text and creator_id are required"}`, not the documented response. This is a `requirements.md` inconsistency (its own prose just above the curl block says the endpoint needs both fields), not a code bug — `GOAL.md` checked M3 off without ever re-running the literal example.
- **Fix (decide before implementing):** document this as a known divergence in the README (e.g. in "Spec reflection" or a one-line note near the curl examples) rather than changing `app.py`'s validation — the locked contract in `CLAUDE.md` is correct and shouldn't bend to a spec typo. Confirm this approach before writing it up.

---

## Confirmed solid (no action needed)

For completeness — these were independently re-verified by the review agents and need no fix:

- M2: all five spec questions, `## Architecture`, `## AI Tool Plan` — all specific and implementation-ready.
- M3: app runs, signal 1 independently correct, audit log structured, `GET /log` round-trips.
- M4: confidence-scoring formula hand-traced and matches `planning.md` exactly, including the strict `>` vs `>=` boundary; GOAL.md's claimed scores reproduced to 3 decimals.
- M5: label text byte-for-byte verified live; appeals append (don't mutate); a **fresh** 12-request burst independently reproduced `[200×10, 429×2]`; zero stray `print()` calls.
- M6 confidence-scoring math: both example submissions' dampening arithmetic redone from scratch, matches README exactly.
- Portfolio walkthrough video: correctly still a TODO — needs the user, not code.
