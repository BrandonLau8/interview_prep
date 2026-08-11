# Counting by maximal runs

**In one line:** Chop the string into blocks of identical characters, then count
how many substrings each block contributes with a formula instead of looping
over substrings.

**Assumes you know:** Python, nested loops, and that `C(n,2) = n*(n-1)/2` counts
the ways to pick 2 items from n. You have written the O(n²) version of this
problem and want to know why the O(n) version is correct.

**Not covered:** Palindrome counting proper (Manacher, expand-around-center).
This code looks like it counts palindromes. It does not — see Example 3.

## What this code actually counts

`findUniquePatterns` returns the number of index pairs `i < j` where

    signal[i] == signal[j]     and     signal[i+1 : j]  is all one character
                                       (empty counts)

Equivalently: substrings of length ≥ 2 that look like `cccc` or `d cccc d`.

I verified this against a brute-force enumerator on 3000 random strings over
`abc` — zero mismatches. The brute force is in [Gotchas](#gotchas).

The function name is misleading twice: nothing is deduplicated (`"aaa"` → 3, not
2), and nothing is "unique."

## ELI5

You have a shelf of colored books. Someone asks: how many ways can you pick two
books of the same color such that everything between them is a single color?

You do not check all pairs. You notice the shelf is already grouped into stretches
of one color — `RR GGGG B RR`. Two books in the same stretch always qualify, and
you know how many pairs a stretch of 4 has without pointing at them. The only
other way to qualify is to reach *across* a whole stretch and find the same color
on both sides.

**Where the analogy breaks:** the "reach across" case is only allowed to skip
**one entire** stretch, and it must be the whole stretch — not part of it, not two
of them. The books don't tell you that; the maximal-run boundaries do. That single
constraint is the whole reason the third bucket in the code is `+= 1` and never
`+= something`.

## Actually

Scan the string once into **maximal runs**: `[l, r]` such that all of
`signal[l..r]` are equal and the neighbors on both sides differ (or don't exist).
`"aabaa"` → `[0,1]`, `[2,2]`, `[3,4]`.

Every qualifying pair `(i, j)` falls in exactly one of two shapes:

    both endpoints inside one run    the middle is that same character
    endpoints straddle one run       the middle IS the run, i = l-1, j = r+1

That "exactly one" is what makes summing over runs safe: no pair is counted
twice, none is missed. The straddle case can't be off-by-a-bit because if the
middle is all one character and the endpoints sit outside it, the middle stretches
exactly to the run's boundaries — by definition of maximal.

The three buckets in the code, for a run of length `L`:

    bucket 1    L - 1              endpoints in-run, distance 1 → substrings "cc"
    bucket 2    (L-1)(L-2)/2       endpoints in-run, distance ≥ 2 → "ccc" and longer
    bucket 3    0 or 1             straddle: signal[l-1] == signal[r+1]

Bucket 2 is `C(L-1, 2)`, which is where the substring count of length ≥ 3 lands:
`(L-2) + (L-3) + ... + 1`.

And the algebra worth carrying away:

    (L-1) + (L-1)(L-2)/2  =  (L-1) · (2 + L - 2)/2  =  L(L-1)/2  =  C(L, 2)

Buckets 1 and 2 are one thing split in half. `total += L*(L-1)//2` is the same
function. The split is presentational — it's how someone *derived* it (length-2
substrings first, then everything longer), not something the algorithm needs.

Cost: O(n) time, O(1) space. `k` only ever moves forward and `j = k` hands the
outer loop the next run, so the inner `while` does n steps of work across the
entire outer loop — not n per iteration.

## The picture

```
signal =  a  a  b  a  a
index     0  1  2  3  4
         [ run 0 ][r1][ run 2 ]
          L = 2    L=1   L = 2

  run 0:  C(2,2) = 1  ->  (0,1) "aa"
          straddle? l-1 = -1, no left neighbor      -> 0
  run 1:  C(1,2) = 0
          straddle? signal[1]=='a' == signal[3]=='a' -> 1   (1,3) "aba"
  run 2:  C(2,2) = 1  ->  (3,4) "aa"
          straddle? r+1 = 5, past the end            -> 0
                                                    ----
                                            total =    3
```

Each run is charged for the pairs *inside* it, plus the one pair that *jumps
over* it.

## Example 1 — the smallest thing that works

```python
def count_in_one_run(L):
    """A string that is a single run of length L, e.g. 'aaaa' for L=4."""
    return L * (L - 1) // 2

print(count_in_one_run(4))   # 6
```

`"aaaa"` has 6 qualifying pairs: `(0,1) (0,2) (0,3) (1,2) (1,3) (2,3)` —
substrings `aa aaa aaaa aa aaa aa`. Every pair inside a run qualifies, because
the middle is always the same character. No scanning needed, just `C(4,2)`.

## Example 2 — the version you'll actually write

```python
def find_patterns(signal):
    n = len(signal)
    total = 0
    j = 0
    while j < n:
        k = j
        while k < n and signal[k] == signal[j]:   # walk to the end of the run
            k += 1
        l, r = j, k - 1
        L = r - l + 1

        total += L * (L - 1) // 2                 # pairs inside the run

        if 0 <= l - 1 and r + 1 < n and signal[l - 1] == signal[r + 1]:
            total += 1                            # the pair that jumps the run

        j = k                                     # O(n): never re-scan the run
    return total

print(find_patterns("aabaa"))    # 3
print(find_patterns("aabbaa"))   # 4
```

**Adds:** the run scan itself, and the merge of buckets 1 and 2 into one
`C(L,2)`. This is the same function as the original — same output on every input
— with the derivation collapsed.

`"aabbaa"` is the case that shows bucket 3 is not just about single characters:
the four pairs are `aa`, `bb`, `aa`, and `abba` — that last one jumps the entire
`bb` run, length 2.

## Example 3 — where it gets subtle

```python
print(find_patterns("abcba"))   # 1, not 2
```

`"abcba"` is a palindrome. It is not counted. The only pair found is `(1,3)`,
`"bcb"`.

`"aabaa"` is also a palindrome, also not counted — the whole string needs the
middle `"aba"`, which is not one repeated character.

**Adds:** the boundary of what this counts. Everything it finds *is* a
palindrome, so pattern-matching on the output suggests "count palindromic
substrings." The converse fails: it only finds palindromes whose interior is a
single repeated character. Real palindrome counting on `"abcba"` returns 2 for
length ≥ 2 (`bcb`, `abcba`) and needs expand-around-center or Manacher.

## Gotchas

- **`(L-1)*(L-2)//2` when `L == 1`** — that's `0 * -1 // 2`. Python gives 0
  because one factor is 0, so it's harmless here. Port this to C with `size_t`
  and `L - 2` underflows to a huge unsigned value; the zero factor still saves
  you, but `(L-2)*(L-1)/2` with any reordering or intermediate cast will not.
  Write `L*(L-1)/2` and the trap disappears.

- **`j = k`, not `j += 1`** — advancing by one re-enters the same run, which both
  makes it O(n²) and counts every run once per character in it. This is the bug
  to check first if your total is too high.

- **Bucket 3 needs the run to be maximal** — if you produced runs some other way
  (say, fixed-size chunks), `signal[l-1]` could equal the run's own character and
  you'd count a pair that the inside-the-run bucket already counted. Maximality is
  what guarantees `signal[l-1] != signal[l]`.

- **It counts occurrences, not distinct substrings** — `"aaa"` returns 3, but
  there are only 2 distinct substrings (`"aa"`, `"aaa"`). Despite the name.

- **Check yourself against brute force, not against intuition** — this is the
  enumerator I used, and it is worth keeping:

  ```python
  def brute(s):
      return sum(
          1
          for i in range(len(s))
          for j in range(i + 1, len(s))
          if s[i] == s[j] and len(set(s[i+1:j])) <= 1
      )

  import random
  random.seed(0)
  for _ in range(3000):
      s = "".join(random.choice("abc") for _ in range(random.randint(0, 9)))
      assert find_patterns(s) == brute(s), s
  print("ok")
  ```

  Small alphabet, short strings. Random 200-character strings over 26 letters
  would almost never produce a run of length 3, and the bug you're hunting lives
  there.

## Related

- **Run-length encoding** — same scan, but it stores `(char, length)` pairs
  instead of accumulating a count. If the pattern is hard to see here, write the
  RLE first and do the arithmetic over the list.
- **LeetCode 1759, Count Number of Homogenous Substrings** — the same run scan
  with `L*(L+1)/2`, counting length ≥ 1 instead of ≥ 2. Difference is only that
  single characters count as substrings there.
- **LeetCode 647, Palindromic Substrings** — what this problem is *not*. Runs
  don't get you there; you need centers.

## Sources

- Brute-force differential test above, run on 3000 random strings over `abc`,
  lengths 0–9. That's the evidence for the "what this counts" claim, not a
  citation.
- LeetCode 1759 "Count Number of Homogenous Substrings" — the canonical
  statement of the run-scan half of this.
