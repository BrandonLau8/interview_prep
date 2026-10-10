"""The composition skill: one question, one structure.

Core idea: each structure answers exactly ONE question in O(1)/O(log n).
List the questions your main loop asks per step; each distinct question
gets its own structure. The tell you're missing one: an inner loop whose
only job is to re-answer a single question (rescan for a match, rescan
for the min) — that scan IS the structure you should maintain instead.
When you compose, write the sync invariant tying the structures together.

Written deliberately plain (no defaultdict / setdefault / zip idioms) so
the logic ports 1:1 to Java, C++, Go, JS on a whiteboard.
Run: python 16_composing_structures.py
"""


# ------------------------------------------------ the tell: kill the inner loop
def two_sum(nums: list[int], target: int) -> list[int]:  # LC 1
    """Brute force's inner loop asks ONE question: "have I seen target - x,
    and where?" A dict value->index answers it in O(1). One question, one
    structure — the simplest possible instance.

    Naive: for every i, rescan the rest for target - nums[i] — O(n^2). That
    scan re-answers one question every time; the dict remembers the answer.

    Real life: shopping with $9 — for each toy price, check a notepad of
    prices already seen for one costing exactly the rest, instead of walking
    back down the aisle (matching a debit to a credit in reconciliation)."""
    seen = {}                              # invariant: value -> its index, all j < i
    for i in range(len(nums)):
        need = target - nums[i]
        if need in seen:
            return [seen[need], i]
        seen[nums[i]] = i
    return []


# ------------------------------------------- bidirectional: one dict per direction
def is_isomorphic(s: str, t: str) -> bool:  # LC 205
    """True iff s and t are in one-to-one character correspondence.
    One-to-one = TWO questions: "what does a map to?" AND "what maps to b?"
    One dict only checks s->t; it can't catch two different s-chars claiming
    the same t-char. Second dict = the other direction.

    Naive: for each i, rescan 0..i-1 checking both directions held for every
    earlier occurrence — O(n^2). The two dicts cache both directions.

    Real life: a secret code — A must ALWAYS become the same symbol, and no
    other letter may claim that symbol or you can't decode back (anonymizing
    user IDs: same ID -> same pseudonym, and no two IDs share one)."""
    if len(s) != len(t):
        return False
    fwd = {}                               # invariant: s-char -> the t-char it claimed
    bwd = {}                               # invariant: t-char -> the s-char that claimed it
    for i in range(len(s)):
        a = s[i]
        b = t[i]
        if a in fwd:
            if fwd[a] != b:                # a already claimed a different b
                return False
        else:
            fwd[a] = b
        if b in bwd:
            if bwd[b] != a:                # b already claimed by a different a
                return False
        else:
            bwd[b] = a
    return True


def word_pattern(pattern: str, s: str) -> bool:  # LC 290
    # True iff pattern chars and words in s are in bijection.
    # Same signature as 205, different alphabet: chars <-> whole words.
    # Naive: same O(n^2) two-way rescan as 205, one lookback per position.
    # Real life: same secret-code rules, bigger pieces — "a = dog, b = cat"
    # (log template matching: each pattern slot binds to exactly one service).
    words = s.split()
    if len(pattern) != len(words):
        return False
    fwd = {}
    bwd = {}
    for i in range(len(pattern)):
        ch = pattern[i]
        w = words[i]
        if ch in fwd:
            if fwd[ch] != w:
                return False
        else:
            fwd[ch] = w
        if w in bwd:
            if bwd[w] != ch:
                return False
        else:
            bwd[w] = ch
    return True


# ------------------------------------------ running total: prefix sum + seen dict
def subarray_sum_k(nums: list[int], k: int) -> int:  # LC 560
    """Count subarrays summing to exactly k.
    Sliding window fails (negatives break monotonicity — pattern 9 pitfall).
    Question per step: "how many earlier prefixes equal current_prefix - k?"
    A dict counting seen prefix sums answers it in O(1).

    Naive: sum every (start, end) slice — O(n^3), or O(n^2) with a running
    sum per start. The dict collapses that rescan into one lookup.

    Real life: a piggy-bank tape of running totals — if it reads $12 today
    and ever read $7 before, the days between added up to exactly $5 (bank
    audit; refunds go negative, which is exactly why the window fails)."""
    count = 0
    prefix = 0
    seen = {}                              # invariant: prefix sum -> times seen so far
    seen[0] = 1                            # empty prefix: subarrays starting at index 0
    for i in range(len(nums)):
        prefix = prefix + nums[i]
        if prefix - k in seen:
            count = count + seen[prefix - k]   # each hit = one subarray ending here
        if prefix in seen:
            seen[prefix] = seen[prefix] + 1
        else:
            seen[prefix] = 1
    return count


def find_max_length(nums: list[int]) -> int:  # LC 525
    """Longest subarray with equal numbers of 0s and 1s.
    Recast 0 as -1, then "balanced" = "same running sum seen before". Store
    the FIRST index per sum (earliest start = longest span).

    Naive: check every subarray, counting 0s and 1s — O(n^2) with running
    counts. The dict finds the earliest matching start for each end in O(1).

    Real life: sharing cookies with a sibling, +1 for you and -1 for them —
    whenever the score revisits a number, the stretch in between was
    perfectly fair (longest window where two servers split traffic evenly)."""
    first = {}                             # invariant: balance -> earliest index seen
    first[0] = -1
    balance = 0
    best = 0
    for i in range(len(nums)):
        if nums[i] == 1:
            balance = balance + 1
        else:
            balance = balance - 1
        if balance in first:
            length = i - first[balance]
            if length > best:
                best = length
        else:
            first[balance] = i             # only the first sighting — never overwrite
    return best


# ---------------------------- frequency AND recency: freq dict + stack per freq
class FreqStack:  # LC 895
    """Pop the most frequent element, ties broken by recency.
    Two questions per pop: "what's the max frequency?" AND "of those, which
    was pushed last?" The freq dict answers neither alone — add a stack PER
    frequency level, so both answers become one top-of-stack read.

    Naive: keep one flat list of pushes; each pop scans it to count
    frequencies, find the max, then its latest occurrence — O(n) per pop.

    Real life: a teacher calling on whoever raised their hand the most times,
    ties to the most recent raise — a count per kid plus a line-up per count
    level, no scanning the class (LFU cache with LRU tiebreak)."""

    def __init__(self):
        self.freq = {}                     # invariant: value -> its current frequency
        self.group = {}                    # invariant: f -> values that reached freq f, in push order
        self.maxfreq = 0                   # invariant: highest f with a non-empty group
        # sync: an element at freq 3 sits in groups 1, 2 AND 3, so popping it
        # off group[3] leaves it already correct at freq 2.

    def push(self, val: int) -> None:
        if val in self.freq:
            f = self.freq[val] + 1
        else:
            f = 1
        self.freq[val] = f
        if f not in self.group:
            self.group[f] = []
        self.group[f].append(val)
        if f > self.maxfreq:
            self.maxfreq = f

    def pop(self) -> int:
        stack = self.group[self.maxfreq]
        val = stack.pop()
        self.freq[val] = self.freq[val] - 1
        if len(stack) == 0:                # level emptied: max drops by exactly 1
            self.maxfreq = self.maxfreq - 1
        return val


if __name__ == "__main__":
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]

    assert is_isomorphic("egg", "add")
    assert not is_isomorphic("foo", "bar")     # o claims two targets
    assert not is_isomorphic("badc", "baba")   # b and d claim the same target — bwd catches it

    assert word_pattern("abba", "dog cat cat dog")
    assert not word_pattern("abba", "dog cat cat fish")
    assert not word_pattern("abba", "dog dog dog dog")  # a and b claim "dog"

    assert subarray_sum_k([1, 1, 1], 2) == 2
    assert subarray_sum_k([1, 2, 3], 3) == 2
    assert subarray_sum_k([1, -1, 0], 0) == 3  # negatives: window would be WRONG here

    assert find_max_length([0, 1]) == 2
    assert find_max_length([0, 1, 0]) == 2
    assert find_max_length([0, 0, 1, 0, 0, 0, 1, 1]) == 6

    fs = FreqStack()
    for v in (5, 7, 5, 7, 4, 5):
        fs.push(v)
    assert fs.pop() == 5                       # freq 3 wins
    assert fs.pop() == 7                       # tie at freq 2: most recent
    assert fs.pop() == 5
    assert fs.pop() == 4                       # tie at freq 1: most recent
    print("16_composing_structures: all checks passed")
