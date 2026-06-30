<!--
This file is a required project deliverable (see requirements.md → Milestone 2 and "Submitting Your Project").
It must be written BEFORE implementation code, and is also handed to AI tools as prompting material in
Milestones 3-5 (see the ## AI Tool Plan section below). Every section below is a TODO scaffold only —
content gets filled in during Milestone 1-2 work, deliberately, not pre-filled here.
-->

# Provenance Guard — Planning

## Detection Signals

TODO — answer with specific, implementation-ready detail:
- What are your 2+ signals?
- What does each one measure?
- What does each signal's output look like (a score between 0–1? a binary flag?)
- How will you combine them into a single confidence score?

## Uncertainty Representation

TODO:
- What does a confidence score of 0.6 mean to your system?
- How will you map raw signal outputs to a calibrated score?
- What threshold separates "likely AI" from "uncertain" from "likely human"?

## Transparency Label Design

TODO — write out the exact text for all three variants now, before building the UI:
- High-confidence AI result:
- High-confidence human result:
- Uncertain result:

## Appeals Workflow

TODO:
- Who can submit an appeal?
- What information do they provide?
- What does the system do when an appeal is received — what status changes, what gets logged?
- What would a human reviewer see when they open the appeal queue?

## Anticipated Edge Cases

TODO — name at least two *specific* scenarios (not generic risks like "inaccurate detection"):
1.
2.

## Architecture

TODO:
- Diagram (ASCII art is fine) covering both flows:
  - Submission flow: `POST /submit` → signal 1 → signal 2 → confidence scoring → transparency label → audit log → response
  - Appeal flow: `POST /appeal` → status update → audit log → response
- 2–3 sentence narrative describing both flows

## AI Tool Plan

TODO — for each implementation milestone, specify which spec sections to provide, what to ask for, and how to verify the output:

- **M3 (submission endpoint + first signal):**
  - Spec sections to provide:
  - What to ask for:
  - How to verify:

- **M4 (second signal + confidence scoring):**
  - Spec sections to provide:
  - What to ask for:
  - How to verify:

- **M5 (production layer):**
  - Spec sections to provide:
  - What to ask for:
  - How to verify:
