---
name: annotate-pattern
description: Annotate a DSA solution file with the layered comment format from pattern_code/16_composing_structures.py — core insight, naive baseline, real-life analogy, and invariant comments. Use when asked to annotate, document, or add comments to a pattern/solution file in this repo.
---

# Annotate a pattern file

Add the repo's standard comment layers to an existing solution file. Do not
rewrite the solutions themselves unless asked — this skill documents code,
it doesn't change logic.

The reference exemplar is `pattern_code/16_composing_structures.py`. When in
doubt about tone, density, or wording, open it and match it.

## Per-problem docstring

Each function or class gets a docstring with three parts, in this order,
separated by blank lines:

1. **Core insight** (no label). State the ONE question the main loop asks
   per step, and which structure answers it in O(1)/O(log n). If the
   problem composes several structures, name the question each one answers
   and the sync invariant tying them together. This is the "why this
   approach" paragraph — it should let the reader re-derive the solution,
   not just follow it.

2. **`Naive:`** — the brute-force approach in one or two sentences, with
   its complexity, then what the chosen structure replaces. Frame it as
   "the inner scan re-answers question X every time; the structure
   remembers the answer." Include intermediate baselines when they exist
   (e.g. "O(n^3), or O(n^2) with a running sum").

3. **`Real life:`** — an ELI5 analogy, then a real-system parallel in
   parentheses. The analogy MUST map to the *mechanism*, not just the
   topic: the everyday object has to play the role of the data structure
   (the notepad IS the dict, the odometer IS the prefix array). If the
   analogy would still work with a different algorithm, it's too generic —
   find a better one. Keep it to 2–4 lines.

For trivial variants of an already-annotated problem in the same file, a
short `#` comment block referring back is fine instead of a full docstring
(see `word_pattern` vs `is_isomorphic` in the exemplar): "same X as above,
different alphabet" plus one-line Naive and Real life comments.

## Other conventions

- Tag the LeetCode number on the signature line: `def two_sum(...):  # LC 1`.
- Every maintained structure gets an inline invariant comment at its
  declaration, aligned to the right: `seen = {}  # invariant: value -> its
  index, all j < i`. State what is true about the structure between
  iterations, not what the line does.
- Inline comments inside the loop only for non-obvious moves (why a
  counter drops by exactly 1, why first sighting is never overwritten).
- Section dividers between pattern groups: `# ----… short label`, dashes
  padded so the line reaches ~80 chars.
- If the file has a module docstring, it states the pattern's core idea
  and the "tell" for recognizing it, and notes that code is written
  deliberately plain (no defaultdict / setdefault / zip idioms) for
  whiteboard portability. Add one if missing; don't duplicate per-problem
  content into it.
- If the file has a `__main__` block with asserts, leave it working and
  add brief comments to asserts that exercise an edge case the docstring
  mentions (e.g. `# negatives: window would be WRONG here`).

## Checklist before finishing

- Run the file (`uv run python <file>`); all asserts must still pass.
- Every problem has all three docstring parts (or the short-variant form).
- Each analogy names an object that plays the data structure's role.
- No solution logic was changed.
