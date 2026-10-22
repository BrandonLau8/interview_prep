# Cells and fences

**In one line:** A cell index names an element. A fence index names a gap between
elements. An array of `n` elements has `n` cells and `n + 1` fences.

**Assumes you know:** Arrays, Python slicing, and that off-by-one bugs exist. You
have written a binary search or prefix sum and had to guess at a `+1` or `- 1`.

**Not covered:** The prefix-sum technique itself (see `prefix-suffix.md`), and
binary search predicates (see `pattern_code/09_binary_search.py`).

## ELI5

Look at a ruler. The numbered tick marks are fences, and the one-centimeter
spaces between them are cells. A 4 cm ruler has 4 spaces but 5 marks, 0 through
4. To find how long a stretch is, you subtract the marks at its ends: from mark 1
to mark 3 is `3 - 1 = 2` cm. You don't count marks, because that gives 3 and is
wrong.

**Where the analogy breaks:** on a ruler, you can stand on any mark. In an array,
fences have no memory behind them. Fence 4 is a valid boundary of a length-4
array, but `a[4]` is still out of bounds. A fence index can be a length, a slice
endpoint or an insertion point, but you can never read `a[...]` at it.

## Actually

Every index variable is one of two kinds, and most off-by-one bugs come from
treating one kind as the other:

    cell    names an element          valid range 0 .. n-1    a[i] is legal
    fence   names a gap/boundary      valid range 0 .. n      a[i] may crash

The one fact that connects the two:

    cell i sits between fence i (its left edge) and fence i+1 (its right edge)

Every rule below follows from it.

    question                          kind     why
    "what's at position i"            cell     reads an element
    "slice from here to there"        fence    a[i:j] takes two fences
    "where would x be inserted"       fence    insertion happens in a gap
    "sum of everything before here"   fence    "before" is a boundary
    "window between L and R"          fence    if half-open [L, R)

## The picture

```
  fence:   0   1   2   3   4
           |   |   |   |   |
           | A | B | C | D |
           |   |   |   |   |
  cell:      0   1   2   3
```

To draw it by hand:

    1. draw the cells as boxes
    2. write cell numbers under the boxes
    3. write fence numbers on the vertical lines, starting at 0 on the far left
    4. for each index variable, ask: does it name a box or a line?
    5. put that variable's pointer on the matching row

If you can't answer step 4 for a variable, that's usually where the bug is.

## Example 1 — counting between fences

The range from fence `i` to fence `j` holds `j - i` cells, with no `+1`.

```
  fence:   0   1   2   3   4
           | A | B | C | D |
               ^-------^
           fence 1 .. fence 3   ->   3 - 1 = 2 cells (B, C)
```

Python slicing works this way. `a[1:3]` takes two fences and returns `B, C`,
which is why `len(a[i:j]) == j - i`.

Inclusive cell ranges ("from index i to index j inclusive") need converting
first. Cell `i` starts at fence `i`, and cell `j` ends at fence `j + 1`:

    cells i..j inclusive   =   fence i .. fence j+1
    count                  =   (j + 1) - i            <- the familiar "j - i + 1"

That `+1` isn't a fudge. It moves from the last cell to the fence on its right.

## Example 2 — prefix sums

`pre[k]` is the sum of every cell to the left of fence `k`. It is stored on
fences, so it has `n + 1` entries.

```
  fence:   0   1   2   3   4
           | 2 | 4 | 6 | 8 |
  pre:     0   2   6  12  20
```

    pre[0] = 0       nothing is left of fence 0
    pre[n] = total   everything is left of the last fence

Sum of cells `l..r` inclusive: convert to fences `l` and `r + 1`, then subtract.

```
  cells 1..2  ->  fences 1, 3  ->  pre[3] - pre[1] = 12 - 2 = 10   (4 + 6)
```

This is `range_sum` in `pattern_code/18_prefix_sum.py`. Getting `pre[r] - pre[l]`
instead is the classic bug: it treats `r` as a fence when it's a cell, so the
last element is dropped.

## Example 3 — where it gets subtle: lower bound

"Where does 5 go in `[1, 3, 7, 9]`?" The answer is a gap, so it's a fence:

```
  fence:   0   1   2   3   4
           | 1 | 3 | 7 | 9 |
                   ^
              5 goes at fence 2
```

The answer can be `n`. Inserting 10 goes at fence 4, past the last cell. So
`lower_bound` in `pattern_code/09_binary_search.py:40` searches fences `0..n`:

```python
lo, hi = 0, len(nums)        # hi = n, not n - 1: fence n is a valid answer
while lo < hi:               # half-open [lo, hi): stop when the range is empty
```

Compare the two binary search shapes:

    closed     [lo, hi]   searches cells    hi = n - 1   while lo <= hi
    half-open  [lo, hi)   searches fences   hi = n       while lo < hi

Mixing them up, for example `hi = n - 1` with `while lo < hi`, means fence `n`
is never returned. Searching for a target bigger than everything then gives the
wrong answer.

## Sliding windows on fences

Put `L` and `R` on fences, so the window is the cells between them:

```
  fence:   0   1   2   3   4
           | A | B | C | D |
               L       R
  window = B, C      size = R - L = 2      empty when L == R
```

With fences, the empty window is just `L == R`. With inclusive cell pointers it
becomes `R = L - 1`, which is awkward to start from and easy to get wrong.

## Gotchas

    a[result] after lower_bound   result can be n; check result < n first
    pre[r] - pre[l]               drops a[r]; inclusive r needs pre[r + 1]
    len(pre) == n                 should be n + 1; pre[0] = 0 is the empty prefix
    hi = n - 1 with lo < hi       half-open loop over a closed range; misses n
    R - L + 1 on a [L, R) window  that's the inclusive formula; half-open is R - L
    "the 3rd element"             is cell 2, the cell between fences 2 and 3

## Related

- **Prefix sums** — `prefix-suffix.md`. Every `pre` array is a value stored on
  each fence.
- **Difference arrays** — `pattern_code/17_difference_array.py`. Range updates
  mark fence `l` and fence `r + 1`, the same inclusive-to-fence conversion.
- **Binary search** — `pattern_code/09_binary_search.py`. `lower_bound` is a
  fence search; `search_rotated` is a cell search, with `lo <= hi`.

## Sources

- Dijkstra, EWD831 "Why numbering should start at zero" — the argument for
  half-open ranges `[lo, hi)`: length is `hi - lo` and empty ranges are `lo == hi`.
- "Fencepost error" — the standard name for this bug class, after the
  posts-vs-sections puzzle the ruler analogy is based on.
