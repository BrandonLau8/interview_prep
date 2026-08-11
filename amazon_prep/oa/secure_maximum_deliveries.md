# Secure Maximum Deliveries (Amazon OA)

Problem 4 of the warm-up set — companion to `amazon_prep.md`, split out because
it needs the diagrams.

You receive `deliveryLogs` (deliveries per log) and an even `k` (warehouses).
Each warehouse stores deliveries from one log only; a log may be split across
warehouses; you may leave deliveries unstored. Afterward the `k/2` fullest
warehouses are compromised. Maximize the deliveries in the rest.

    deliveryLogs = [3, 5, 9, 6], k = 4   ->   9
    deliveryLogs = [6],          k = 2   ->   3

Constraints: `1 <= n <= 1000`, `2 <= k <= 1000`, k even, `0 <= logs[i] <= 1000`.

The code below is verified against both samples plus 300 random cases checked
against a brute force that enumerates every possible split.

---


## ELI5

You have piles of candy and `k` boxes. A bully will take the **fullest half** of
the boxes; you keep the rest.

- A box may hold candy from **one pile only** — no mixing.
- A pile **may** be spread across several boxes.
- You may throw candy on the floor.

With `piles = [3, 5, 9, 6]` and `k = 4`, the bully takes the 2 fullest boxes.
How much do you keep?

The instinct "make every box equal so it doesn't matter which he takes" gets you
`4 4 4 4` → **8**. But some piles don't chop evenly, and the awkward leftovers
are small — which means they land in the boxes you *keep*. Exploiting that gets
you **9**.

## The insight

Let `x` be the size of your biggest **secure** box. Every box the bully takes is
already `≥ x`, and anything above `x` in them is candy you'll never see — so
shrink them all to exactly `x`. Now every box holds `≤ x`, and the problem is
just: *chop the piles into pieces of size `x` and keep the best `k` pieces.*

`x` is not binary-searchable. Scan it.

## One pass, drawn out (x = 5)

```
┌─ CHOP ──────────────────────────────────────────────┐
│  pile 3   ▓▓▓                                       │
│           └─┘ 3 // 5 = 0 blocks    3 % 5 = 3 sliver │
│                                                     │
│  pile 5   █████                                     │
│           └───┘ 1 block            5 % 5 = 0        │
│                                                     │
│  pile 9   █████▓▓▓▓                                 │
│           └───┘└──┘ 1 block        9 % 5 = 4 sliver │
│                                                     │
│  pile 6   █████▓                                    │
│           └───┘└┘ 1 block          6 % 5 = 1 sliver │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─ POOL ──────────────────────────────────────────────┐
│  blocks  = 3          (just a number — all worth 5) │
│  slivers = ▓▓▓▓  ▓▓▓  ▓        sorted big→small     │
│              4     3   1                            │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─ FILL  k = 4 boxes ─────────────────────────────────┐
│  box 1  █████   5   block                           │
│  box 2  █████   5   block                           │
│  box 3  █████   5   block                           │
│  box 4  ▓▓▓▓    4   blocks ran out → fattest sliver │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─ SORT & SEIZE ──────────────────────────────────────┐
│       4     5     5     5                           │
│     ▓▓▓▓  █████ █████ █████                         │
│     └───────────┘└───────────┘                      │
│        YOURS         BULLY                          │
│                                                     │
│        score = 4 + 5 = 9                            │
└─────────────────────────────────────────────────────┘
```

`a // x` never builds a list — it *counts*. Summing counts across piles is legal
because every block is worth exactly `x` regardless of which pile it came from,
so they're interchangeable. Slivers stay a list because they're all different
sizes and you need the biggest ones.

The "one pile per box" rule never appears in the code: a block or sliver is
carved from exactly one pile, so a mixed box is impossible by construction.

## Where the candy leaks

All 23 deliveries exist at every `x`. Only the leak moves.

```
x=1   23 blocks, boxes hold 1 each
      ▪▪▪▪ │ ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
      kept │ 19 pieces never fit in a box   ← leak at FILL
      score 2

x=5   ▓▓▓▓ █████ │ █████ █████
      yours       │ bully                   ← small leak both ends
      score 9

x=9   ▓▓▓ ▓▓▓▓▓ │ ▓▓▓▓▓▓ █████████
      yours     │ bully takes 15            ← leak at SEIZE
      score 8
```

Small `x`: your boxes are too small to carry the candy. Large `x`: the bully's
half is enormous. The best `x` is where both leaks are jointly smallest.

## Every x, and why binary search fails

```
x   boxes                 score
1    1   1   1  1           2
2    2   2   2  2           4
3    3   3   3  3           6
4    4   4   4  4           8
5   [4]  5   5  5           9   ← best
6   [3] [5]  6  6           8
7   [3] [5] [6] 7           8
8   [3] [5] [6] 8           8
9   [3] [5] [6] 9           8

[n] = sliver (a leftover < x), everything else is a full block
```

Read down the bracket column: as `x` grows, blocks run out and slivers creep in
from the left. Rows 6-9 are the failure mode — two slivers stuck in *your* half
at 3 and 5 forever, while only the bully's boxes get bigger.

```
score
  9 |                 ●
  8 |             ●   │   ●   ●   ●   ●
  6 |         ●
  4 |     ●
  2 | ●
    +───────────────────────────────────
      1   2   3   4   5   6   7   8   9    x
      └── leak at FILL ──┘└─ leak at SEIZE ─┘
```

A hill, not a cliff. Binary search needs `N N N Y Y Y` — one clean flip — so
`check(mid)` here can't tell you which half to keep. Two costs pulling opposite
directions always give you a peak.

## Code

```python
def secure_max_deliveries(logs: list[int], k: int) -> int:
    def score(x: int) -> int:                   # best haul if every box is capped at x
        blocks = sum(a // x for a in logs)      # CHOP: pieces worth a full x
        slivers = sorted((a % x for a in logs), reverse=True)
        boxes = [x] * min(blocks, k)            # FILL: blocks first, always fatter
        boxes += slivers[:k - len(boxes)]       #       top up with the biggest slivers
        boxes += [0] * (k - len(boxes))         #       any box left over holds 0
        boxes.sort()                            # SORT: bully takes the fullest half
        return sum(boxes[:k // 2])              # SCORE: you keep the smaller half

    return max((score(x) for x in range(1, max(logs) + 1)), default=0)
```

O(max(logs) · n log n) — about 10^7 at the stated limits (n ≤ 1000, values ≤
1000), comfortably fast. O(n) space.

## Traps

    binary search on x      the tell fits ("maximize...") but the score PEAKS.
                            Confirm monotonicity before reaching for the template.
    forgetting the pad      `boxes += [0] * (k - len(boxes))` — if the piles
                            can't fill k boxes, the empties are real boxes
                            holding 0, and zeros sort into YOUR half. Skipping
                            this silently inflates the answer.
    slivers before blocks   a sliver is < x by definition, so taking one over an
                            available block always loses. Blocks first, always.
    all-zero piles          `range(1, 0 + 1)` is empty -> `max()` raises.
                            `default=0` covers it.
    equal split instinct    `4 4 4 4` scores 8, not 9. Uneven wins when a fat
                            sliver lands in the secure half.
    k not fully used        you never want fewer than k boxes — an unused box
                            is a 0 in your own half.

## The pattern

**Greedy under a scanned parameter.** Fix the one number that makes the
structure collapse (here: the cap on every box), solve the rest greedily, then
try every value of that number. Lives in `pattern_code/08_greedy.py`; the
"looks like binary search but isn't" warning is in
`pattern_code/09_binary_search.py`.


---

Back to the rest of the set: `amazon_prep.md`.
