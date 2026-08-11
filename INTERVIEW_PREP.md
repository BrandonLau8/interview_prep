# Interview Prep: Greedy + Difference/Classification

Decoding the brief: two problems, Easy→Medium, on strings/arrays. One will
reward a greedy choice you can justify; one will reward stamping ranges onto a
difference array (or splitting the answer axis into constant-cost cases). The
overflow warning means the expected answer is an accumulated sum or a pair
count, and the reference solution in Java/C++ needs `long`.

Code: `pattern_code/08_greedy.py`, `pattern_code/17_difference_array.py`.

## The overflow rule

`int` in Java/C++ tops out at 2,147,483,647. These shapes cross it:

    pair / subarray counts    n=1e5 -> n*(n-1)/2 ~ 5e9
    sum of array values       1e5 elements * 1e9 each -> 1e14
    range-update accumulator  2e4 updates * 1e5 each -> 2e9
    prefix sums of values     any values >= 1e5 over 1e5 cells

Rules that cover almost every case:

- Return type `long`, and every accumulator feeding it `long`.
- `long` the FIRST operand: `(long) a * b`, not `(long)(a * b)` — the cast
  after the multiply is too late, the wrap already happened.
- Loop counters, indices, and array lengths stay `int`.
- `mid = left + (right - left) / 2`, never `(left + right) / 2`.

Python hides all of this — ints are arbitrary precision. If you drill only in
Python you will not feel the bug, so say the `long` decision out loud while
coding and note where the cast goes.

## Boundary checklist

Run this list before you say "done" — it's what the brief means by boundary
condition handling.

    empty input           n == 0, s == "", and n == 1
    all-same values       no strict inequality ever fires
    already sorted / reversed
    inclusive vs half-open  diff[end+1] for [start,end], diff[end] for a drop-off
    off-by-one on edges   is the band [lo+1, hi] or [lo, hi]?
    duplicates            do ties break the greedy exchange argument?
    negative numbers      does the greedy assume positives?
    k > n, k == 0         clamp before indexing
    single-char / single-element string ops

## Greedy: prove it in one sentence

Don't just assert the choice — say the exchange argument out loud. "Any
optimal solution can be rewritten to make my choice first without getting
worse." If you can't say it, the problem is probably DP.

    Jump Game II (45)         farthest reach per level = BFS layers
    Gas Station (134)         a failing prefix can't be the start
    Candy (135)               two independent passes, take the max
    Partition Labels (763)    extend the block to the last index of each char
    Task Scheduler (621)      the most frequent char sets the skeleton
    Merge Intervals (56)      sort by start makes overlap local
    Non-overlapping (435)     keep the earliest end
    Remove K Digits (402)     monotonic stack = greedy with undo

## Difference array: the tell

If the problem says "apply these k updates to a range" or "for each candidate
answer T, compute a cost", stop writing the nested loop.

    Range Addition (370)          the primitive
    Flight Bookings (1109)        1-indexed, overflow-prone
    Car Pooling (1094)            half-open: drop-off at `to`, not `to+1`
    Shifting Letters II (2381)    string + mod 26
    Min Moves Complementary (1674) the hard one: 5 cost bands per pair
    2D Range Increment (2536)     four corner stamps

## Complexity: say it unprompted

State it in this order — time, then space, then why it's optimal.

    "O(n + k) time: one pass over the updates, one prefix sum. O(n) space for
     the diff array. Can't beat O(n) since we output n values."

Note the brute force you skipped and its complexity — interviewers grade the
comparison, not just the final number. Sorting-based greedy is O(n log n) and
the sort usually dominates; say so.

## 45-minute drill

Two problems, timed, one from each column. Write the complexity before the
code, run the boundary checklist after.

    1109 + 763      warm-up pair
    1094 + 134      half-open edges + greedy proof
    2381 + 402      string manipulation both sides
    1674 + 135      hardest pair: classification + two-pass greedy
