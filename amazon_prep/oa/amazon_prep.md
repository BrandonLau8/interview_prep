# Amazon OA Prep — Coding Warm-Up (ELI5)

Four problems, four different shapes. Read the ELI5, cover the code, redo it
from scratch, then check the traps. ~40 minutes.

Three are below. The fourth, **Secure Maximum Deliveries**, lives in
`secure_maximum_deliveries.md` — it needs diagrams, so it got its own file.

All code here is verified against the sample tests.
Companion: `../../INTERVIEW_PREP.md` (overflow rules, boundary checklist).

---

## 1. Feasible Indices After Prefix/Suffix Reduction

### ELI5

A line of kids, each holding a different number.

- **Move A:** pick some kids from the *front* of the line. Only the one with the
  smallest number stays. The rest go home.
- **Move B:** pick some kids from the *back* of the line. Only the one with the
  biggest number stays.

For each kid, ask: could that kid be the last one standing?

A kid survives to the end only if they are already special in one of two ways:
**nobody in front of them is smaller**, or **nobody behind them is bigger**.

Why? To clear out the kids in front of you, you must use Move A on a group that
includes them. But if any of those kids is smaller than you, *they* stay and
*you* go home. Same story behind you with Move B and bigger kids. So if there's
a smaller kid in front AND a bigger kid behind, you're trapped forever.

### Code

```python
def feasible_indices(arr: list[int]) -> str:
    n = len(arr)
    res = [0] * n

    run = float("inf")
    for i in range(n):                      # nobody in front is smaller
        run = min(run, arr[i])
        if arr[i] == run:
            res[i] = 1

    run = float("-inf")
    for i in range(n - 1, -1, -1):          # nobody behind is bigger
        run = max(run, arr[i])
        if arr[i] == run:
            res[i] = 1

    return "".join(map(str, res))
```

O(n) time, O(1) extra space. Two passes, no sorting.

### Traps

    n == 1                  answer "1" — that kid is both smallest and biggest
    the global minimum      always "1"
    the global maximum      always "1"
    the answer is never all zeros — those two rules always hit something
    simulating the moves    exponential, times out instantly at n = 2e5

### The pattern

**Prefix/suffix scan.** Whenever a question asks "is element `i` special
relative to everything before/after it," precompute running min/max in two
passes instead of looking left and right for each `i`.

---

## 2. Frequency Sort (expanded)

### ELI5

Count how many of each thing you have. Then dump them out, most-common pile
first.

`[1,1,2,2,2,3]` → you own two 1s, three 2s, one 3 → biggest pile is the 2s →
`2 2 2 1 1 3`.

### Code

```python
from collections import Counter

def frequency_sort(nums: list[int]) -> list[int]:
    count = Counter(nums)
    order = sorted(count, key=lambda v: -count[v])
    out = []
    for v in order:
        out.extend([v] * count[v])
    return out
```

O(n log n) time — the sort dominates; counting is O(n). O(n) space.

### The tie-break, stated

The problem says ties can go in any order. This code picks a rule and it's
worth saying out loud: **ties keep first-appearance order.** You get it for
free from two Python guarantees — `Counter` iterates in insertion order, and
`sorted` is stable. That rule happens to reproduce every sample output exactly,
including Test 4 (`-1` before `3`, both count 2) and Test 5 (all counts 1, so
the original order survives).

In Java or C++ you get no such guarantee. Sort explicitly on
`(-count, firstIndex)` or the ties come out scrambled.

### Traps

    n == 1                  single element, nothing to sort
    all distinct            every count is 1, output = input under a stable sort
    negative numbers        fine as hash keys — don't try to index an array by value
    values up to 1e9        a count array of size 1e9 blows memory; you need a hash map
    "descending frequency"  key is -count, not the value itself

### The pattern

**Count then sort.** Hash map for the counts, sort the *distinct* keys (there
may be far fewer than n), expand back out.

---

## 3. Course Schedule II (topological order)

### ELI5

You're getting dressed. Socks before shoes, shirt before jacket. What's a valid
order to put everything on?

Do it greedily: **repeatedly grab anything that has nothing left blocking it.**
Put it on, then cross it off everyone else's blocker list. Anything that just
dropped to zero blockers joins the pile of things you can grab next.

If you run out of grabbable items but still have clothes left, there's a
deadlock — a loop like "socks before shoes, shoes before socks." Impossible,
return empty.

### Code

```python
from collections import deque

def find_order(n: int, prerequisites: list[list[int]]) -> list[int]:
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for course, need in prerequisites:      # [a, b] = take b BEFORE a
        graph[need].append(course)          # edge points need -> course
        indegree[course] += 1

    q = deque(i for i in range(n) if indegree[i] == 0)
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:          # last blocker just cleared
                q.append(nxt)

    return order if len(order) == n else []  # short = cycle
```

O(n + m) time — each node dequeued once, each edge relaxed once. O(n + m) space.

### Traps

    edge direction          [a, b] means b -> a. Reversing it is THE bug here.
    cycle detection         it's just `len(order) != n`. No extra bookkeeping.
    no prerequisites        every node has indegree 0, any order works
    disconnected pieces     the initial queue seeds ALL zero-indegree nodes, so
                            islands are handled with no special case
    self-loop [a, a]        indegree never hits 0 -> correctly returns []
    n = 2e5 with recursion  a DFS version hits Python's recursion limit; BFS
                            (Kahn's) has no such problem

### The pattern

**Kahn's algorithm / topological sort.** The giveaway phrasing is "X must come
before Y" plus "return any valid ordering" or "detect if it's impossible."

---

## What these four have in common

    problem 1    two-pass scan          O(n)
    problem 2    hash map + sort        O(n log n)
    problem 3    BFS on a graph         O(n + m)
    problem 4    scan + greedy          O(max(v) · n log n)   see companion file

Same three habits pass all of them:

1. **Check `n == 1` and the empty case before you submit.** Every one of these
   has a degenerate input that a natural-looking loop gets wrong.
2. **State the complexity unprompted**, and name the brute force you avoided.
3. **Don't simulate.** Problems 1, 3, and 4 all have an obvious
   simulate-every-move solution that is exponential or O(n·m). The intended
   answer is always the one-pass reformulation.

One calibration note: none of these actually overflow — the outputs are a
string, a permutation of the input, a list of indices, and a bounded sum. That
warning in your brief is aimed at a *different* problem, the kind that returns a
count of pairs. And problem 3 is a graph problem, which the brief didn't mention
at all, so don't treat that brief as an exhaustive syllabus.
