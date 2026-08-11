# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal DSA study repo. The artifacts are *teaching materials*, not a
library — nothing imports anything else, and there is no public API. Two kinds
of file:

    pattern_code/NN_<pattern>.py   annotated reference solutions, one pattern per file
    *.md                           prose explainers (ELI5 -> mechanism -> traps)

Optimize for a human re-deriving the solution months later, not for brevity or
cleverness.

## Verifying changes

Every `.py` file in `pattern_code/` and `amazon_prep/` self-verifies through a
`__main__` block of `assert`s. That is the test suite — run the file you
touched:

```bash
uv run python pattern_code/09_binary_search.py   # prints "09_binary_search: all checks passed"
```

`c1_prep/CapitalOneOA.py` is the exception: no `__main__`, nothing verifies it.

`uv run pytest` collects nothing (there are no `test_*.py` files) and exits 5,
so the `test` job in `.github/workflows/test_pyworkflow.yml` fails on every
push — red CI is structural, not something your change broke. The other
workflow, `python-app.yml`, is commented out in full. Do not add pytest tests
unless asked; extend the `__main__` asserts instead, and give any assert
covering an edge case a trailing `#` comment naming the edge.

## Code conventions in `pattern_code/`

Written **deliberately plain** so the logic ports 1:1 to Java/C++/Go/JS on a
whiteboard: no `defaultdict`/`setdefault`/`zip`/`bisect`, no comprehension
tricks, explicit index loops. Do not "improve" a solution into idiomatic Python.

Comment layers are a fixed format — core insight, `Naive:` baseline, `Real life:`
analogy, plus a right-aligned `# invariant:` on every maintained structure. The
exemplar is `pattern_code/16_composing_structures.py`; the full spec lives in the
project skill `.claude/skills/annotate-pattern/SKILL.md`. Invoke that skill when
annotating or adding a problem.

Module docstrings state the pattern's **tell** (how you recognize it from the
problem statement) and, where relevant, **when the tell lies** — see the
monotonicity warning at the top of `09_binary_search.py`, which points at the
counterexample in `08_greedy.py`. Keep those cross-file pointers accurate when
moving code.

Tag LeetCode numbers on the signature line: `def two_sum(...):  # LC 1`.

## Markdown conventions

Explainers open with a one-line definition, an "Assumes you know" and a "Not
covered" line, then an ELI5 analogy followed by an explicit **"Where the analogy
breaks"** section. Enumerable facts (traps, complexity, checklists) go in
indented aligned blocks, not bullets or tables. `docs/concepts/recursion.md` is
the model.

Prep docs are companion pairs — `amazon_prep/oa/*.md` cross-references
`INTERVIEW_PREP.md` for the shared overflow rules and boundary checklist, and
each OA problem's markdown names the `.py` file holding the verified code. Keep
both sides in sync when either changes.

Target language matters: `INTERVIEW_PREP.md` documents `long`-overflow rules
because the OA reference solutions are Java/C++. Python hides the bug, so flag
overflow-prone accumulators in prose even when the Python code is correct.

## Directory map

    pattern_code/    18 numbered pattern files (two pointers -> prefix sum)
    amazon_prep/     Amazon OA problems; oa/ holds the prose companions
    c1_prep/         Capital One OA
    docs/concepts/   standalone concept explainers
    INTERVIEW_PREP.md  cross-cutting rules: overflow, boundaries, complexity phrasing
    main.py          scratch pad for the problem currently being worked
