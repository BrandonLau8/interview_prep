# Monotonic stack

**In one line:** A stack you keep sorted by throwing out every entry the newest
element makes irrelevant — and each thing you throw out is one answer.

**Assumes you know:** Python lists used as stacks, LIFO, big-O. You have written
`is_valid_parentheses` (`pattern_code/10_stack.py:11`) and want to know why the
next six problems in that file look nothing like it.

**Not covered:** the monotonic *deque* (sliding-window maximum) — see
[Related](#related). Also not the amortized-analysis proof, only its statement.

## ELI5

A line of people waiting to be told "who is the next person taller than me?"
Nobody in the line can see past someone taller, so anyone shorter than the person
in front of them has already given up looking — the line is always tallest at
the back.

When a tall person walks up, everyone shorter than them gets their answer at the
same moment and leaves. One arrival can clear half the line.

**Where the analogy breaks:** the line is not a queue. People leave from the
*back*, the end they joined at — which is what makes it a stack, and why the
person still standing behind the one who leaves is that leaver's other neighbour.
That second fact is invisible in the analogy and is the whole of LC 84.

And "taller" is doing more work than it looks. Swap it for "shorter" and the same
loop answers the opposite question; make it "taller or equal" and ties change
hands. Three different problems, one character apart.

## Actually

A monotonic stack maintains this invariant: **the values in the stack are sorted**
(increasing or decreasing) at all times. You restore it before every push by
popping everything that would violate it.

The payload is what happens *during the pop*, not what is left in the stack. When
index `j` is popped by the arrival of index `i`:

    nums[i]      is the nearest element to j's RIGHT that broke the order
    stack[-1]    (read AFTER popping j) is the nearest one to j's LEFT
    i - left - 1 is how far j's value extends before hitting either

So a pop hands you both boundaries of a range that `j` dominates. Every
"next greater / previous smaller / how far does this element reach" problem is
that sentence with different words.

Which order to keep is decided by the question, not by taste:

    decreasing stack   pops on a LARGER arrival   -> next greater element
    increasing stack   pops on a SMALLER arrival  -> next smaller element
    strict (<)         ties stay on the stack     -> nearest STRICTLY greater
    non-strict (<=)    ties get popped            -> nearest greater-or-equal

Cost is O(n) even though the loop is nested: each index is pushed exactly once
and popped at most once, so the inner `while` runs at most `n` times *in total*
across the whole outer loop. Amortized, not per-iteration — a single arrival may
pop `n-1` entries, and that is fine.

Store **indices**, not values. Values answer "what", indices answer "how far",
and you can always recover the value with `nums[stack[-1]]`.

## The picture

```
nums = [3, 1, 4, 2]         stack holds indices; VALUES kept decreasing

i=0  v=3   push                    stack: [3]
i=1  v=1   1 < 3, order holds      stack: [3, 1]
i=2  v=4   4 > 1  pop -> ans[1]=4
           4 > 3  pop -> ans[0]=4
           push                    stack: [4]
i=3  v=2   2 < 4, order holds      stack: [4, 2]
end        4 and 2 never popped -> no greater element exists -> -1
```

One arrival (`4`) answered two waiters. The two survivors are not a leftover to
clean up — being unanswered *is* their answer.

```
              popped j              arrival i
                 |                      |
   stack:  ... [ 2 ] [ 5 ]             [ 1 ]
                 ^^^   ^                ^^^
          left boundary   the element   right boundary
          (stack[-1]       being         (nums[i] broke
           after the pop)   answered      the order)
```

Anatomy of a single pop: three values, two of which most people forget are
sitting right there.

## Example 1 — the smallest thing that works

```python
def next_greater(nums):
    res = [-1] * len(nums)              # unanswered = no greater element
    stack = []                          # indices; values decreasing
    for i in range(len(nums)):
        while stack and nums[stack[-1]] < nums[i]:
            res[stack.pop()] = nums[i]
        stack.append(i)
    return res

print(next_greater([3, 1, 4, 2]))       # [4, 4, -1, -1]
```

Four lines of body. The `while` is the whole pattern: keep answering waiters
while the arrival outranks them, then join the line yourself.

## Example 2 — the version you'll actually write

`pattern_code/10_stack.py:57`:

```python
def daily_temperatures(temps: list[int]) -> list[int]:  # LC 739
    res = [0] * len(temps)              # invariant: 0 until a warmer day is found
    stack: list[int] = []               # invariant: indices awaiting an answer, temps decreasing
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()             # today is j's next-warmer day
            res[j] = i - j
        stack.append(i)
    return res                          # survivors never got an answer: 0

print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
# [1, 1, 4, 2, 1, 1, 0, 0]
```

The trace on that input — stack shown as temperatures, but the entries are the
indices next to them:

```
temps = [73, 74, 75, 71, 69, 72, 76, 73]        values kept decreasing

i=0  t=73  stack empty, push                    stack: [73]
i=1  t=74  74 > 73  pop 0 -> res[0] = 1-0 = 1   stack: [74]
i=2  t=75  75 > 74  pop 1 -> res[1] = 2-1 = 1   stack: [75]
i=3  t=71  71 < 75, order holds                 stack: [75, 71]
i=4  t=69  69 < 71, order holds                 stack: [75, 71, 69]
i=5  t=72  72 > 69  pop 4 -> res[4] = 5-4 = 1
           72 > 71  pop 3 -> res[3] = 5-3 = 2
           72 < 75, stop and push               stack: [75, 72]
i=6  t=76  76 > 72  pop 5 -> res[5] = 6-5 = 1
           76 > 75  pop 2 -> res[2] = 6-2 = 4   stack: [76]
i=7  t=73  73 < 76, order holds                 stack: [76, 73]
end        indices 6, 7 never popped            res[6] = res[7] = 0

res = [1, 1, 4, 2, 1, 1, 0, 0]
```

Index 2 (`75`) sits on the stack from `i=2` to `i=6` while four warmer-looking
days come and go, and is popped holding a wait of `4`. A stack of temperatures
pairs `75 -> 76` correctly and still cannot produce that number.

**Adds:** the answer is a *distance*, `i - j`, not a value. That is the reason
the stack holds indices — a stack of temperatures would produce the right
`73 -> 76` pairing and be unable to say it took four days.

Note the default. `res` is pre-filled with `0`, so the survivors need no cleanup
pass; picking a default that means "never answered" is how you avoid a flush.

## Example 3 — where it gets subtle

`pattern_code/10_stack.py:334`:

```python
def largest_rectangle_area(heights: list[int]) -> int:  # LC 84
    stack: list[int] = []               # invariant: indices with increasing heights
    best = 0
    for i in range(len(heights) + 1):   # one extra iteration: the sentinel
        h = heights[i] if i < len(heights) else 0
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1        # nearest shorter on the LEFT
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best

print(largest_rectangle_area([2, 1, 5, 6, 2, 3]))    # 10
print(largest_rectangle_area([2, 2, 2]))             # 6
```

**Adds:** the pop is now read for *both* boundaries, and three details follow
that Examples 1 and 2 never forced you to confront.

`left = stack[-1]` is read **after** the pop, so it is the entry that was buried
underneath — the nearest shorter bar on the left. `-1` when the stack empties
means "nothing shorter on the left, so the rectangle runs to the wall". Width is
`i - left - 1` because both boundaries are *exclusive*: the rectangle sits
strictly between them.

The sentinel `h = 0` on the extra iteration exists because survivors matter here.
In LC 739 an unanswered day is a `0` you already wrote down; here an unpopped bar
is a rectangle you never measured. A height of `0` is shorter than everything, so
it flushes the stack through the same `while`, with no second loop.

`>=` instead of `>` pops on ties, which looks like a bug and is not. With
`[2, 2, 2]` the first `2` is popped by the second and gets a width of 1 — too
narrow. But the last `2` is popped by the sentinel, finds an empty stack, and
computes width 3. The undercounted rectangles are always dominated by the
rightmost member of the tie, so `max` is still right. `sum_subarray_mins`
(`pattern_code/10_stack.py:120`) relies on that asymmetry deliberately: its
single `>=` makes the left span stop at a strictly smaller element while the
right span stops at a smaller-or-equal one, and that mismatch is exactly what
stops equal minimums being counted twice.

## Gotchas

- **Storing values instead of indices** — works for LC 496, silently fails the
  moment the answer is a distance or a width. Push `i`, read `nums[stack[-1]]`.
  There is no cost to indices and no way back from values.

- **Forgetting the survivors** — the stack is not empty when the loop ends, and
  those entries are real answers. Two fixes, and you pick one: pre-fill the
  result with the "never answered" value (LC 739's `0`, LC 503's `-1`), or run a
  sentinel iteration that pops everything (LC 84's trailing `0`). Writing a
  second loop after the main one to drain the stack means you missed that the
  sentinel does it for free.

- **`left` read before the pop** — `stack[-1]` before popping is the element
  itself, not its neighbour. The left boundary only becomes visible once the
  element on top of it is gone.

- **Reaching for it when the array is not scanned once left-to-right** — a
  monotonic stack answers questions about *nearest on one side*. "Nearest on
  either side" is two passes (or one pass plus the `stack[-1]` trick); "any
  element anywhere" is not this pattern at all.

- **Assuming the nested loop is O(n²)** — it is O(n), and in an interview you say
  why unprompted: `n` pushes, at most `n` pops, the inner `while` is bounded
  across the whole run rather than per iteration. Not saying it reads as not
  knowing it.

- **Circular input handled with a second array** — LC 503 iterates `2n` times
  with `i % n` and pushes only while `i < n`. The second pass exists to answer
  waiters, never to create them; pushing in it is the bug that makes the wrap
  answer itself (`pattern_code/10_stack.py:78`).

## Related

- **Monotonic deque** (`pattern_code/02_sliding_window.py:194`) — same
  keep-it-sorted-by-discarding idea, but pops from *both* ends: the back for
  order, the front for elements that fell out of the window. Use it when the
  question has a fixed span; use a stack when it has a boundary to find.

- **`MinStack`** (`pattern_code/10_stack.py:304`) — stores a running minimum
  alongside each entry. Often confused with this pattern because both are "a
  stack that knows about order", but nothing is ever discarded there; it is
  bookkeeping, not pruning.

- **Binary search on a monotone predicate** (`pattern_code/09_binary_search.py:15`)
  — same word, unrelated technique. There, monotonicity is a property of the
  *problem* you must verify; here, it is an invariant *you enforce* on a
  structure. Nothing transfers.

- **Contribution counting** (`pattern_code/10_stack.py:120`) — the trick that
  turns "aggregate over all subarrays" into "per element, how many subarrays does
  it dominate". A monotonic stack is what supplies the two spans that product
  needs, which is why LC 907 lives in the stack file rather than the DP one.

## Where to practice

In this order, all in `pattern_code/10_stack.py`:

    LC 739   Daily Temperatures            :57    the pattern, undisguised
    LC 503   Next Greater Circular         :78    wrap-around, push guard
    LC 402   Remove K Digits               :100   the "value" is lexicographic
    LC 84    Largest Rectangle Histogram   :334   both boundaries, sentinel
    LC 907   Sum of Subarray Minimums      :120   spans as a contribution count

LC 739 is in the daily core (`docs/daily_warmup.md:27`); LC 84 is its escalation.

## Sources

- `pattern_code/10_stack.py` — the verified reference implementations this page
  cites, each with its own naive baseline and invariants.
- Laaksonen, *Competitive Programmer's Handbook*, ch. 8 "Amortized analysis" —
  the "nearest smaller elements" section is this pattern with the amortized
  argument written out properly.
