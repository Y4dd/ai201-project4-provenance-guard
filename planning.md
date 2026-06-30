<!--
Required project deliverable (see requirements.md → Milestone 2 and "Submitting Your Project").
Written before implementation code. Also handed to AI tools as prompting material in Milestones 3-5
(see ## AI Tool Plan). Filled in during Milestone 1-2 work — not pre-fabricated during scaffolding.
-->

# Provenance Guard — Planning

## Detection Signals

Two genuinely independent signals, per the spec's recommended default pairing — one semantic, one structural.

1. **Signal 1 — Groq LLM-based classification** (`llm_score`, float 0–1, probability the text reads as AI-generated).
   Sends the submitted text to Groq (`llama-3.3-70b-versatile`) with a prompt asking it to judge whether the writing reads as human or AI-generated, returning a single calibrated probability.
   - *What it captures:* holistic semantic/stylistic coherence — generic hedging phrases ("it is important to note," "furthermore"), tidy parallel structure, lack of concrete specific detail — the kind of "sounds like an LLM" judgment a careful human reader would notice but raw statistics wouldn't.
   - *Blind spot:* it's itself a black-box model opinion with no ground truth. It can be fooled by AI text a human has lightly edited/paraphrased, and it tends to read polished, formal *human* writing (academic, technical) as more AI-like than it is — the spec's own "monetary policy" borderline example is exactly this trap.

2. **Signal 2 — Stylometric heuristics** (`stylometric_score`, float 0–1, probability AI-generated), pure Python, no external libraries.
   Computes sentence-length variance, type-token ratio (vocabulary diversity), and punctuation density/variety, then combines them into a single normalized score.
   - *What it captures:* measurable structural irregularity. Human writing tends to vary more — uneven sentence lengths, irregular punctuation (em dashes, ALL CAPS, repeated words for emphasis, run-ons), more varied vocabulary; AI text trends more uniform.
   - *Blind spot:* it's purely structural with zero semantic understanding, and it's unreliable on short text (too few sentences for variance to mean anything). A human with a naturally uniform, formal style scores as "uniform" regardless of authorship — it can't tell "formal human" from "AI" on structure alone, and it can be evaded by AI text a human has deliberately roughened up.

**Combination:** see Uncertainty Representation below — not a simple average, because of the false-positive asymmetry called out in the spec's hints.

## Uncertainty Representation

```
combined_score = (llm_score + stylometric_score) / 2

# Disagreement dampening: if the two signals disagree sharply, that disagreement
# IS the signal — pull toward uncertain rather than trusting the average.
if abs(llm_score - stylometric_score) > 0.35:
    combined_score = 0.5 + (combined_score - 0.5) * 0.5   # halve the distance from 0.5

# Asymmetric gate for "likely_ai": a false positive (flagging a human as AI) is worse
# than a false negative, per the spec's hint. Require BOTH signals to independently
# lean AI before allowing the high-confidence-AI label — a high average alone isn't enough.
if combined_score >= 0.7 and llm_score >= 0.55 and stylometric_score >= 0.55:
    attribution = "likely_ai"
elif combined_score <= 0.3:
    attribution = "likely_human"
else:
    attribution = "uncertain"
```

- A confidence of **0.6** means: in the "uncertain" band — the system has a mild lean but not enough agreement/strength to commit to either label. It will surface the uncertain transparency label, not a forced binary call.
- Thresholds: **≥ 0.7** (combined) **and both signals ≥ 0.55** → `likely_ai`. **≤ 0.3** → `likely_human`. Everything else → `uncertain`. This means 0.51 and 0.95 land in clearly different bands (uncertain vs. likely_ai), satisfying the "meaningfully different" requirement.
- The asymmetric AI-gate and disagreement-dampening rule both exist specifically to make false positives harder to produce than false negatives.

## Transparency Label Design

| Variant | Exact text shown to the reader |
|---|---|
| High-confidence AI | `"Likely AI-generated — our system detected strong AI-writing patterns in this content (confidence: {confidence}%)."` |
| High-confidence human | `"Likely human-written — our system found strong indicators of human authorship in this content (confidence: {confidence}%)."` |
| Uncertain | `"Uncertain — we couldn't confidently determine whether this content is AI-generated or human-written (confidence: {confidence}%). If you believe this is misclassified, you can appeal."` |

`{confidence}` is the combined score formatted as a percentage. The uncertain variant explicitly invites an appeal, since that's the band most likely to contain a misclassification either direction.

## Appeals Workflow

- **Who:** the creator who submitted the content (identified by `creator_id` from the original submission).
- **What they provide:** `content_id` (from their original `/submit` response) and `creator_reasoning` (free text explaining why they believe the classification is wrong).
- **What happens on receipt:** the system looks up the original record by `content_id`, sets its `status` to `"under_review"`, and writes a new audit log entry capturing the appeal (`content_id`, `appeal_reasoning`, `status: "under_review"`, `timestamp`) alongside — not replacing — the original classification entry. No automated re-classification.
- **What a human reviewer would see in the appeal queue:** every log entry with `status: "under_review"`, showing the original `attribution`/`confidence`/signal scores next to the creator's `appeal_reasoning`, so they can judge the dispute with full context.

## Anticipated Edge Cases

1. **A poem (or refrain-heavy lyric) with deliberate repetition and simple vocabulary.** Stylometric heuristics will see low type-token ratio and low sentence-length variance — both "AI-like" by this system's structural reading — even though repetition is a common, deliberate *human* poetic device. This is the spec's own flagged example and is a direct consequence of Signal 2's blind spot above.
2. **Very short submissions (a 2–3 sentence caption or excerpt).** Stylometric variance is statistically meaningless over so few sentences, and the LLM signal has little to work with either. Combined confidence on short text should be treated as inherently less reliable than on a full paragraph or more.
3. *(Bonus, not required)* **AI text a human has lightly, deliberately roughened** — uneven sentence lengths and irregular punctuation reintroduced by hand to evade stylometrics, while the underlying content stays semantically AI-generated. Signal 2 gets fooled; Signal 1 may or may not still catch it depending on how much semantic restructuring was done.

## Architecture

**Submission flow** — `POST /submit` → Signal 1 (Groq) → Signal 2 (stylometrics) → Confidence Scorer → Label Generator → Audit Logger → response. **Appeal flow** — `POST /appeal` → Status Updater (`under_review`) → Audit Logger → response. Both flows write through the same audit log, so a content item's full history (original classification + any appeal) lives in one place.

```
SUBMISSION FLOW
================
Creator
  |  POST /submit {text, creator_id}
  v
[Flask route] --(generate content_id, uuid4)-->
  |
  |--raw text--> [Signal 1: Groq LLM classifier]     --> llm_score (0-1)
  |--raw text--> [Signal 2: Stylometric heuristics]   --> stylometric_score (0-1)
  v
[Confidence Scorer] --(llm_score, stylometric_score)--> combined_score, attribution
  v
[Label Generator] --(combined_score, attribution)--> label text
  v
[Audit Logger] --(full record)--> audit log (SQLite/JSON)
  v
Response {content_id, attribution, confidence, label} --> Creator


APPEAL FLOW
===========
Creator
  |  POST /appeal {content_id, creator_reasoning}
  v
[Flask route] --(look up content_id)-->
  v
[Status Updater] --(status = "under_review")-->
  v
[Audit Logger] --(append: appeal_reasoning, status)--> audit log
  v
Response {content_id, status: "under_review", message} --> Creator
```

## AI Tool Plan

- **M3 (submission endpoint + first signal):**
  - Spec sections to provide: `## Detection Signals` (Signal 1 description) + the submission-flow diagram above.
  - What to ask for: a Flask app skeleton with a `POST /submit` route stub, plus the Groq signal function (`text -> float 0-1`, matching the `llm_score` contract).
  - How to verify: call the signal function directly (not through the route) with the spec's four example texts (clearly AI, clearly human, two borderline) from `requirements.md` → Milestone 4, and confirm it returns a single float, not a dict or binary flag, before wiring it into the endpoint.

- **M4 (second signal + confidence scoring):**
  - Spec sections to provide: `## Detection Signals` (Signal 2) + `## Uncertainty Representation` + the diagram.
  - What to ask for: the stylometric heuristic function (`text -> float 0-1`) and a confidence-scoring function implementing the exact formula above (disagreement dampening + asymmetric `likely_ai` gate) — not a generic average.
  - How to verify: run the same four example texts through the combined scorer; confirm the 0.7/0.3 thresholds and the both-signals-≥0.55 gate are implemented exactly as specified, not approximated. AI tools tend to default to a plain average — check for that specifically and correct it if present.

- **M5 (production layer):**
  - Spec sections to provide: `## Transparency Label Design` + `## Appeals Workflow` + the diagram.
  - What to ask for: a label-generation function mapping `(combined_score, attribution)` to the three exact label strings above, and the `POST /appeal` endpoint per the data contract in `CLAUDE.md`.
  - How to verify: call the label function across the full 0–1 range to confirm all three variants are reachable at the documented thresholds; `curl` `/appeal` with a real saved `content_id` and confirm via `GET /log` that `status` flips to `under_review` and `appeal_reasoning` is populated.
