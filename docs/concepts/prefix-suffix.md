# Prefix and suffix

**In one line:** Store the running total at every index — prefix from the left,
suffix from the right — and the loop you would have written to re-add those
numbers becomes one lookup.

**Assumes you know:** Python lists and `for` loops, and that a *subarray* is a
contiguous stretch `nums[l..r]`, not any subset.

**Not covered:** difference arrays (the mirror image), the prefix + hash map
reframe that solves LC 560, and 2-D prefix sums — all three in
[Related](#related).

## ELI5

A bank statement has a running balance column. To find what you spent between
March 3 and March 20 you do not add up every transaction in between — you look
up two balances and subtract. The column was filled in once, on the way down,
and it answers every "how much between these two dates" question forever after.

A suffix is the same statement totalled from the bottom up: each row answering
"how much is still to come after this one".

**Where the analogy breaks:** in two places, and the second is the one that
costs you.

The balance column is real money at a real moment. `pre[0] = 0` is not — it is a
bookkeeping slot standing for "the empty prefix", holding a row that does not
correspond to any transaction. It exists so that index 0 needs no special case,
and forgetting it is where the off-by-one bugs come from.

More important: subtraction works only because addition has an *inverse*.
Balances always subtract, so the analogy quietly suggests every running total
does. It does not. A running `max` cannot be undone — knowing the max of the
first 7 and the max of the first 3 tells you nothing about the max of items 4
through 7. Prefix arrays work for `+`, `XOR`, and `*` (no zeros), and fail
outright for `min`, `max`, and `gcd`.

## Actually

Two arrays, both built in one pass:

    pre[i]    the fold of the FIRST i elements — everything strictly left of
              index i. Sized n+1, because "the first 0 elements" is a real
              case and needs a slot
    suf[i]    the fold of elements i through the end — everything from i
              rightward, built by walking backwards

The payoff formula, for `+`:

    sum(nums[l..r]) == pre[r + 1] - pre[l]

Read it as "everything up to r, minus everything before l". The `r + 1` is the
inclusive-range adjustment, not a fudge — `pre[r + 1]` means "the first r+1
items", which is items `0..r`.

The operation must be **associative and have an inverse**. That is the entire
requirement, and it is what the last paragraph of the ELI5 was about.

These show up in two distinct shapes, and conflating them is most of the
confusion:

    range queries   one prefix array, then any (l, r) pair answered in O(1)
                    by subtracting two entries. LC 303
    split at i      prefix AND suffix, meeting at index i, so each position
                    knows "everything left of me" and "everything right of
                    me" at once. LC 238, LC 724, LC 845

Shape one is about answering many questions cheaply. Shape two is about giving
every index two facts it would otherwise have to scan for. Same primitive,
different reason to reach for it.

## The picture

Range queries — the n+1 sizing and the subtraction:

```
nums          [  2,   4,   1,   7,   3 ]
index            0    1    2    3    4

pre        [  0,   2,   6,   7,  14,  17 ]
index         0    1    2    3    4    5
              ^                        ^
              |                        +-- pre[5] = all five items
              +-- pre[0] = the empty prefix; 0 is the identity for +

sum(nums[1..3]) = 4 + 1 + 7 = 12
                = pre[4] - pre[1]
                = 14 - 2 = 12
                  ^^^^   ^^^
                  first  first
                  four   one
```

Split at i — the shape where prefix and suffix are used together:

```
                        i = 2
nums          [  2,   4,   1,   7,   3 ]
                \______/    \________/
                 left of i   right of i
                 prefix = 6  suffix = 10

               index 2 itself belongs to NEITHER side
```

## Example 1 — the smallest thing that works

```python
nums = [2, 4, 1, 7, 3]

pre = [0] * (len(nums) + 1)
for i in range(len(nums)):
    pre[i + 1] = pre[i] + nums[i]

print(pre)                 # [0, 2, 6, 7, 14, 17]
print(pre[4] - pre[1])     # 12  — sum of nums[1..3]
print(pre[5] - pre[0])     # 17  — the whole array, no special case
```

One pass fills the array. After that every range sum costs one subtraction, no
matter how many you ask for. The third line is the point of `pre[0]`: the whole
array is just another range.

## Example 2 — the version you'll actually write

`pattern_code/18_prefix_sum.py:202`, LC 724 — find the index where the sum to
its left equals the sum to its right:

```python
def pivot_index(nums: list[int]) -> int:
    total, left = sum(nums), 0             # invariant: left = sum strictly before i
    for i, num in enumerate(nums):
        if left == total - left - num:
            return i
        left += num                        # add AFTER the test: i is excluded
    return -1

print(pivot_index([1, 7, 3, 6, 5, 6]))     # 3
```

**Adds:** no array. You need the prefix at exactly one index at a time, so a
scalar carries it — and once you know the total, the suffix is free:
`right == total - left - nums[i]`. Materialize the array only when you have to
answer queries out of order.

The `left += num` placement is the whole correctness argument. Update after the
test and `left` means "strictly before i"; update before it and the pivot counts
itself.

## Example 3 — where it gets subtle

`pattern_code/13_array_matrix.py:139`, LC 238 — product of all elements except
the one at each index, without division:

```python
def product_except_self(nums: list[int]) -> list[int]:
    n = len(nums)
    res = [1] * n                          # invariant: after sweep 1, res[i] = product strictly left of i
    prefix = 1                             # invariant: product of nums[0:i]
    for i in range(n):                     # first sweep: fold prefixes in
        res[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):         # second sweep: multiply suffixes
        res[i] *= suffix
        suffix *= nums[i]
    return res

print(product_except_self([1, 2, 3, 4]))   # [24, 12, 8, 6]
print(product_except_self([1, 0, 3, 4]))   # [0, 12, 0, 0]  — zeros just work
```

**Adds:** both directions at once, and the output array doing double duty — it
holds the prefixes after sweep one, then gets multiplied by the suffixes in
place, so the extra space is O(1).

The banned division is not an arbitrary interview rule. `total // nums[i]` is
exactly the "undo the fold" move, and `*` loses its inverse the moment a zero
appears — which is the failure named in *Where the analogy breaks*, showing up
as a real constraint. The two-sweep version never divides, so the second `print`
needs no zero-counting special case at all.

## Gotchas

- **Sizing `pre` at n instead of n+1** — then index 0 has no "before me" slot
  and every formula needs an `if l == 0` branch. Size it `n + 1`, set
  `pre[0]` to the operation's identity (0 for `+`, 1 for `*`), and the branch
  disappears.

- **Writing `pre[r] - pre[l]` for an inclusive range** — that is `sum(l..r-1)`.
  Inclusive is `pre[r + 1] - pre[l]`. Check it once against a two-element array
  rather than trusting the shape.

- **Reaching for a prefix array on min / max / gcd** — no inverse, so there is
  nothing to subtract. That is a sparse table or a segment tree, not this.

- **Using a sliding window when the array has negatives** — see
  `pattern_code/18_prefix_sum.py:60` (LC 560). Shrinking a window assumes
  removing an element lowers the sum; a negative element breaks that, and prefix
  + hash map is the correct tool. The assert at
  `16_composing_structures.py`'s `subarray_sum_k([1, -1, 0], 0) == 3` is there
  to catch exactly this.

- **Overflow in Java or C++** — the accumulator is not the same width as the
  elements. `int` values summing across a large `n` need a `long` prefix array.
  Python hides this entirely, so the reference solutions here look safe and the
  ported version is not.

- **Building the suffix forwards** — the second loop runs `n - 1` down to `0`.
  Written ascending it computes a second prefix, and the tests still pass on
  palindromic inputs like `[1, 2, 1]`.

## Where it lives in this repo

    18_prefix_sum.py:20      build_prefix — the primitive everything else uses
    18_prefix_sum.py:38      LC 303, the range-query shape
    18_prefix_sum.py:202     LC 724, the scalar-not-array form (Example 2)
    18_prefix_sum.py:256     2-D, four lookups by inclusion-exclusion
    13_array_matrix.py:139   LC 238, prefix and suffix together (Example 3)
    13_array_matrix.py:163   LC 845, the same split with "how far up / down"
    18_prefix_sum.py:60      LC 560, prefix paired with a hash map
    17_difference_array.py   the inverse: range writes, point reads

`docs/daily_warmup.md` Day 1 drills the first group; LC 724 is in the daily core.

## Related

- **Difference array** (`pattern_code/17_difference_array.py`) — the exact
  mirror. Prefix sums are point writes and range reads; difference arrays are
  range writes and point reads, and a prefix sum is what converts one back into
  the other.
- **Prefix + hash map** (`pattern_code/18_prefix_sum.py:60`) — once every
  subarray is a *difference* of two prefixes, "is there a subarray summing to
  k?" becomes "have I already seen a prefix equal to `cur - k`?". This is where
  most of the interview value is.
- **Sliding window** — also O(n) over subarrays, but needs the sum to move
  monotonically as the window grows. Prefix sums have no such requirement, which
  is why they survive negative numbers.
- **Sparse table / segment tree** — what you use when the operation has no
  inverse (`min`, `max`, `gcd`) and you still want fast range queries.

## Sources

- Guy Blelloch, *Prefix Sums and Their Applications*, CMU-CS-90-190 (1990) —
  the general treatment: any associative operator, and the parallel scan.
- `pattern_code/18_prefix_sum.py` module docstring — the inverse-of-difference-
  array framing and the list of operators this works for.
