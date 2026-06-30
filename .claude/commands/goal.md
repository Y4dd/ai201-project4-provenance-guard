---
description: Orient on Provenance Guard progress (GOAL.md + planning.md + requirements.md) and proceed with the next step
---

You are resuming work on the Provenance Guard project (AI201 Project 4). This command is the standard re-entry point, especially right after `/clear`. Follow these steps in order.

## 1. Orient (read-only, do this fully before acting)

1. Read `GOAL.md` in full: the `## Current Status` block, the milestone checklists, and `## Session Handoff Notes`.
2. Identify the next unchecked item. If `## Current Status` already names a specific next step, trust it; otherwise find the first unchecked checkbox in milestone order.
3. Read `planning.md`. If the `## AI Tool Plan` section has a filled-in entry for the milestone the next item belongs to (M3/M4/M5), read it — it specifies which spec sections to use, what to ask for, and how to verify.
4. Read the matching milestone section in `requirements.md` (use the milestone heading to find it) for the full task description and that milestone's verbatim Checkpoint text.
5. If the next item lives in Milestone 1 or 2 (no code yet), there is no AI Tool Plan entry to read — that's expected, those milestones produce the plan rather than consume it.

## 2. Report

Print a short status report:
- What's done so far (one line per completed milestone, or "nothing yet").
- The next unchecked item and which milestone it belongs to.
- That milestone's Checkpoint text, verbatim.
- If applicable, the AI Tool Plan's prescribed spec sections / ask / verification steps for this item.

## 3. Proceed

Immediately continue into implementing the next step — do not stop and wait for confirmation. Follow `planning.md`'s `## AI Tool Plan` guidance when generating code (which spec sections to ground the request in, what to ask for), and follow `CLAUDE.md`'s data-contracts list so field names stay consistent with earlier milestones.

## 4. Verify before checking anything off

Do not check a GOAL.md box just because code was written. Before flipping any checkbox, actually perform that milestone's verification (run the stated curl command, call the new function directly with test inputs, inspect `GET /log` output, run the rate-limit burst test, etc.) and confirm the result matches the Checkpoint text from `requirements.md`. If it doesn't match, fix it before marking anything done.

## 5. Update state

- Check off only the items you just verified.
- If you completed a full milestone (all its Checkpoint criteria verified), update `## Current Status` in `GOAL.md` to point at the next milestone, and write a short `## Session Handoff Notes` entry: what's done, what's in progress (if anything), what broke (if anything), and the exact next action.
- If a milestone boundary was just crossed, tell the user the milestone is complete and suggest they run `/clear`, since the next milestone can be picked up fresh via `/goal`.
- If you're stopping mid-milestone (ran out of room, hit a blocker), still update Session Handoff Notes with precise enough detail that a fresh `/goal` invocation can resume without re-deriving context from the diff.
