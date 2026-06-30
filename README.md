# Provenance Guard

AI201 Project 4 — a Flask backend that classifies submitted text as likely AI-generated, likely human-written, or uncertain, using two independent detection signals, scores its own confidence, surfaces a plain-language transparency label, and lets creators appeal a classification.

Design decisions and the full spec answers (detection signals, uncertainty representation, label design, appeals workflow, edge cases) live in [`planning.md`](./planning.md), written before any code. This README is the record of what was actually built and why.

## Running locally

```bash
pip install -r requirements.txt
# requires GROQ_API_KEY in the environment (e.g. via .env)
python app.py
```

Endpoints: `POST /submit` (`text`, `creator_id`), `POST /appeal` (`content_id`, `creator_reasoning`), `GET /log`.

## Architecture

A submission takes one path from input to label, and an appeal takes a second path that rejoins the same audit log:

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
[Audit Logger] --(full record)--> audit_log.json
  v
Response {content_id, attribution, confidence, label} --> Creator


APPEAL FLOW
===========
Creator
  |  POST /appeal {content_id, creator_reasoning}
  v
[Flask route] --(look up content_id via find_entry)-->
  v
[Audit Logger] --(append NEW entry: status="under_review", appeal_reasoning)--> audit_log.json
  v
Response {content_id, status: "under_review", message} --> Creator
```

The two signals run independently against the raw submitted text — neither sees the other's output. Their scores are combined by the Confidence Scorer into a single `(combined_score, attribution)` pair, which the Label Generator maps to one of three exact-text variants. Every submission and every appeal writes a new entry to the same JSON-file audit log (`audit_log.py`), so a piece of content's full history — original classification plus any later appeal — is reconstructable from one place by filtering on `content_id`. An appeal never mutates the original entry; it appends a new one, so the classification history is never lost.

## Detection signals

**Signal 1 — Groq LLM classifier** (`signals.py` → `groq_ai_score`, `llm_score`, float 0–1). Sends the submitted text to Groq (`llama-3.3-70b-versatile`) with a system prompt asking it to judge, on a calibrated 0–1 scale, how strongly the writing reads as AI-generated.

- *What it measures:* holistic semantic and stylistic coherence — generic hedging phrases ("it is important to note," "furthermore"), tidy parallel structure, lack of concrete specific detail. The kind of "sounds like an LLM" read a careful human reader would notice but raw statistics wouldn't.
- *Why chosen:* it's the only signal in this system that engages with meaning rather than surface structure, so it catches AI text that's been lightly restructured but still reads generically.
- *What it misses:* it's itself a black-box model opinion with no ground truth. It can be fooled by AI text a human has paraphrased, and — the spec's own flagged trap — it tends to read polished, formal *human* writing (academic, technical, policy prose) as more AI-like than it actually is.

**Signal 2 — Stylometric heuristics** (`signals.py` → `stylometric_score`, float 0–1), pure Python, no external libraries. Averages three sub-scores: sentence-length variance (coefficient of variation), type-token ratio (vocabulary diversity), and punctuation density/variety (em dashes, ellipses, repeated `!!`/`??`, ALL-CAPS emphasis).

- *What it measures:* measurable structural irregularity. Human writing tends to vary more — uneven sentence lengths, irregular punctuation, more varied vocabulary; AI text trends uniform.
- *Why chosen:* it's a structural signal that's completely independent of Signal 1 — it has no access to meaning at all, so its errors and Signal 1's errors don't come from the same place. That independence is what makes disagreement between the two informative (see Confidence Scoring below).
- *What it misses:* zero semantic understanding, and it's unreliable on short text (too few sentences for variance to mean anything — the implementation returns a neutral 0.5 for fewer than 3 sentences or 8 words rather than guessing). A human with a naturally uniform, formal style scores as "uniform" regardless of authorship, and it can be evaded by AI text a human has deliberately roughened up.

## Confidence scoring

`scoring.py` → `score_confidence(llm_score, stylometric_score)`. Not a plain average:

```python
combined_score = (llm_score + stylometric_score) / 2

# Disagreement dampening: if the two signals disagree sharply, that disagreement
# IS the signal — pull toward uncertain rather than trusting the average.
if abs(llm_score - stylometric_score) > 0.35:
    combined_score = 0.5 + (combined_score - 0.5) * 0.5

# Asymmetric gate for "likely_ai": a false positive (flagging a human as AI) is
# worse than a false negative. Require BOTH signals to independently lean AI.
if combined_score >= 0.7 and llm_score >= 0.55 and stylometric_score >= 0.55:
    attribution = "likely_ai"
elif combined_score <= 0.3:
    attribution = "likely_human"
else:
    attribution = "uncertain"
```

This is a deliberate response to a constraint named up front in project scope: on a creative-writing platform, wrongly flagging a human's work as AI-generated does more damage to a creator than missing a piece of AI text does. Two mechanisms enforce that asymmetry: disagreement between the signals pulls the score *toward* uncertain instead of being averaged away, and `likely_ai` additionally requires both signals to independently clear 0.55 — a high average alone isn't enough if one signal is unconvinced.

**Two example submissions, actual logged scores** (both inspectable directly in `audit_log.json`):

| | `llm_score` | `stylometric_score` | naive average | dampened? | `confidence` | `attribution` |
|---|---|---|---|---|---|---|
| High-confidence (`content_id` `abd1913a…`) | 0.92 | 0.604 | 0.762 | no (diff 0.316 ≤ 0.35) | **76%** | `likely_ai` |
| Lower-confidence (`content_id` `4631281e…`) | 0.92 | 0.367 | 0.643 | **yes** (diff 0.553 > 0.35) | **57%** | `uncertain` |

The second row is the dampening rule firing on real data: the LLM signal was confident the text was AI-written (0.92), but the structural signal only mildly agreed (0.367) — an 0.553 gap, well past the 0.35 disagreement threshold. A plain average would have produced 64% and the text would have landed just outside the `likely_ai` band anyway, but dampening explicitly halves the distance from 0.5 (0.643 → 0.572), pushing it further into `uncertain` and surfacing the appeal invitation. The two scores are 19 points apart and land in different attribution bands, which is the "meaningfully different, not a constant" property Milestone 4 asked for.

## Transparency label

`scoring.py` → `generate_label(combined_score, attribution)`. Three variants, exact text:

- **High-confidence AI:** `"Likely AI-generated — our system detected strong AI-writing patterns in this content (confidence: {confidence}%)."`
- **High-confidence human:** `"Likely human-written — our system found strong indicators of human authorship in this content (confidence: {confidence}%)."`
- **Uncertain:** `"Uncertain — we couldn't confidently determine whether this content is AI-generated or human-written (confidence: {confidence}%). If you believe this is misclassified, you can appeal."`

`{confidence}` is the combined score formatted as a whole-number percentage. Only the uncertain variant invites an appeal — it's the band most likely to contain a misclassification in either direction, since by definition the signals didn't agree strongly enough to commit.

## Rate limiting

`/submit` is limited via Flask-Limiter to **10 requests per minute and 100 per day per client** (`storage_uri="memory://"`):

> A genuine writer submitting their own work makes a handful of submissions in a sitting, not dozens; a script flooding the system to probe or abuse the Groq-backed pipeline looks very different. 10/minute comfortably covers real usage bursts (e.g. resubmitting after edits) while still capping the damage a flood script can do; 100/day bounds sustained abuse across a session without blocking a prolific creator's normal daily use.

Verified with a 12-request burst against `/submit` from a single client: the first 10 returned `200`, the next 2 returned `429`. `audit_log.json` shows exactly 10 entries from that burst (content IDs `abd1913a…` through `e762e23e…`, timestamps `20:27:40.626` to `20:27:43.051`) — the two `429`s never reached the handler, so they never got an audit entry, which is the expected behavior for a rejection that happens before any classification work occurs.

## Known limitations

**A poem or refrain-heavy lyric with deliberate repetition and simple vocabulary** is likely to be misclassified as AI-generated. Signal 2's type-token ratio and sentence-length-variance sub-scores both read low vocabulary diversity and low structural variance as "AI-like" — but repetition and simple, repeated phrasing are common, deliberate *human* poetic devices (refrains, anaphora). The heuristics have no concept of genre, so they can't distinguish "uniform because generated" from "uniform because that's the form." This is a direct, structural consequence of Signal 2's blind spot, not a tuning issue — fixing it would require a genre-aware adjustment (e.g. detecting verse structure) rather than a threshold change.

## Spec reflection

**Where the spec helped:** the explicit hint that a false positive (flagging a human as AI) is worse than a false negative on a creative-writing platform shaped the scoring logic directly, not just the label text. Without that constraint named up front, the natural implementation is a plain average with a single 0.5 cutoff — symmetric, and exactly the kind of design that would flag the spec's own "monetary policy" example as confidently AI-generated. The disagreement-dampening rule and the both-signals-≥0.55 gate for `likely_ai` both exist specifically because that asymmetry was named before any scoring code was written.

**Where the implementation diverged:** the spec describes the punctuation sub-score generically ("punctuation density/variety") without specifying how *absence* of punctuation should be scored. A first implementation mapped zero expressive punctuation straight to full AI-confidence (1.0) — which seemed reasonable in isolation, but caused the spec's own monetary-policy borderline example to score as confidently AI-generated, since formal academic/policy prose legitimately uses no em dashes, ellipses, or emphasis punctuation either. The fix was to treat the sub-score asymmetrically: absence of expressive punctuation is weak evidence (capped at a mild 0.6 lean), while its presence is strong evidence of a human hand (scales down to 0.0). The spec didn't call this out explicitly — it surfaced from testing against the spec's own example text, which is the scenario the spec's "test before wiring in" guidance is for.

## AI usage

Two specific instances from building Signal 2 (`signals.py` → `_punctuation_score`), both caught by testing the generated function against the four example texts from `requirements.md` → Milestone 4 before wiring it into `/submit`, per `planning.md`'s AI Tool Plan and `CLAUDE.md`'s rule to never paste generated scoring logic in untested:

1. **Punctuation-absence calibration.** Directed: implement the punctuation density/variety sub-score described in `planning.md` → Detection Signals §2. Produced: a function that mapped zero expressive-punctuation density directly to a 1.0 ("fully AI-like") score. Revised: capped the zero-density case at 0.6 instead of 1.0, since absence of expressive punctuation is weak evidence (plenty of careful human prose has none) while presence is strong evidence — the bug was caught because it pushed the spec's own "monetary policy" borderline example (formal, punctuation-light human writing) toward a false `likely_ai` result, exactly the failure mode the project is meant to avoid.
2. **All-caps acronym false match.** Same function, same generation pass. Produced: an ALL-CAPS-word detector (meant to catch stylistic shouting, e.g. "WAY too much sodium") with no minimum length, which matched the two-letter acronym "AI" itself inside the "Clearly AI-generated" test text — adding spurious AI-leaning signal from a word that wasn't emphasis at all. Revised: required a minimum length of 3 characters for a word to count as ALL-CAPS emphasis, excluding short acronyms like "AI," "US," "OK."

## Portfolio walkthrough

_TODO: link the recorded walkthrough video here._
