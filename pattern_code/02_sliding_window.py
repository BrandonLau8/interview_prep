"""Patterns 8-11: Sliding Window.

Core idea: for CONTIGUOUS subarray/substring problems, don't recompute
overlapping windows — update state incrementally (one element in, one out).
Requires the window condition to be monotone under growth/shrink.

Written in deliberately explicit (non-idiomatic) style: index-based loops,
plain dicts with membership checks, no Counter/enumerate/boolean tricks —
each line should translate 1:1 to C++/Java.
Run: python 02_sliding_window.py
"""


# ---------------------------------------------------------------- Pattern 8
# Fixed size: slide = +entering element, -leaving element.
def max_average_subarray(nums, k):  # LC 643
    """Largest average over any k consecutive elements.
    Neighbouring windows overlap in k-1 elements, so their sums differ by
    exactly two terms. Add the entering element, subtract the leaving one,
    and each slide costs O(1) instead of a re-sum. Max sum = max average.

    Naive: sum each of the n-k+1 windows from scratch — O(nk), re-adding the
    same overlap every time; the running total remembers it instead.

    Real life: a 4-day rolling weather average — you don't re-add four
    temperatures daily, you add today's and drop the one from four days ago."""
    window = 0                             # invariant: sum of the k elements ending at i
    for i in range(k):
        window = window + nums[i]
    best = window
    for i in range(k, len(nums)):
        window = window + nums[i] - nums[i - k]
        if window > best:
            best = window
    return best / k


# ---------------------------------------------------------------- Pattern 9
# Variable size. The invariant IS the solution — state it before coding.
def longest_substring_no_repeat(s):  # LC 3
    """Longest substring with no repeated character.
    Question per step: "where was s[right] last seen?" A dict answers it in
    O(1), and left jumps straight past that index rather than creeping. The
    `>= left` guard matters — a sighting behind left already left the window.

    Naive: for each start, extend while chars stay unique — O(n^2), and the
    inner scan re-answers "have I seen this char?" the dict already knows.

    Real life: reading a shelf of books and keeping the longest stretch with
    no title twice — spotting a repeat, you restart just past the earlier copy
    rather than walking back to the shelf's start (dedup window in a log)."""
    last_seen = {}                         # invariant: char -> index of its most recent occurrence
    left = 0                               # invariant: s[left:right+1] holds no repeat
    best = 0
    for right in range(len(s)):
        ch = s[right]
        if ch in last_seen:
            if last_seen[ch] >= left:
                left = last_seen[ch] + 1  # jump past the previous occurrence
        last_seen[ch] = right
        length = right - left + 1
        if length > best:
            best = length
    return best


def min_subarray_len(target, nums):  # LC 209
    """Shortest subarray of positive numbers summing to at least target.
    "Shortest valid" means expand until valid, then shrink WHILE still valid —
    the opposite shape from "longest valid". Positivity is what makes the sum
    monotone under both moves; with negatives this is wrong (see LC 560).

    Naive: sum every (start, end) pair — O(n^2) with a running sum. Each
    element enters and leaves the window once here, so the whole thing is O(n).

    Real life: buying the fewest days of groceries to hit a $100 delivery
    minimum — once you clear it, drop items off the front while you still
    qualify (smallest burst of requests that trips a rate limit)."""
    left = 0
    total = 0                              # invariant: sum of nums[left:right+1]
    best = len(nums) + 1                   # sentinel: longer than any real window
    for right in range(len(nums)):
        total = total + nums[right]
        while total >= target:  # shrink while valid
            length = right - left + 1
            if length < best:
                best = length
            total = total - nums[left]
            left = left + 1
    if best == len(nums) + 1:
        return 0
    return best


def min_window_substring(s, t):  # LC 76
    """Shortest substring of s containing every char of t, multiplicity included.
    One signed dict answers both questions: need[ch] > 0 means the window
    still owes that many, need[ch] < 0 means it holds that many surplus. A
    single counter `missing` collapses "am I valid yet?" into one comparison.

    Naive: for every start, extend and re-count the window against t —
    O(n^2 * |t|). The signed counts turn each move into one increment.

    Real life: gathering a recipe's ingredients down one market aisle —
    duplicates of what you already hold don't help, so once the basket is
    complete you shed them off the back (smallest log slice with every error)."""
    need = {}                              # invariant: >0 = still owed, <0 = surplus held
    for i in range(len(t)):
        ch = t[i]
        if ch in need:
            need[ch] = need[ch] + 1
        else:
            need[ch] = 1
    missing = len(t)  # chars still needed, counted with multiplicity
    left = 0
    start = 0
    end = 0  # end == 0 means "no window found yet"
    for r in range(len(s)):
        right = r + 1  # exclusive bound of the window
        ch = s[r]
        if ch in need:
            if need[ch] > 0:  # only chars we still owe reduce missing
                missing = missing - 1
            need[ch] = need[ch] - 1
        else:
            need[ch] = -1  # char t never asked for: pure surplus
        if missing == 0:  # valid -> shrink to minimal
            while need[s[left]] < 0:  # surplus char at left edge
                need[s[left]] = need[s[left]] + 1
                left = left + 1
            if end == 0 or right - left < end - start:
                start = left
                end = right
            need[s[left]] = need[s[left]] + 1  # break validity, resume expanding
            missing = missing + 1
            left = left + 1
    return s[start:end]


def longest_repeating_char_replacement(s, k):  # LC 424
    """Longest substring made uniform by replacing at most k characters.
    Valid window: size - (count of its majority char) <= k, since anything not
    the majority is a replacement you pay for. max_freq may go stale — a
    too-large max only freezes growth, so shrinking never has to recompute it.

    Naive: for each start, extend and recount the majority char — O(n^2 * 26).
    The count dict plus the never-decreasing max keeps every move O(1).

    Real life: a row of coloured tiles and k pots of paint — the cheapest
    stretch to make one colour is the one already mostly that colour, and you
    only care when some colour beats your current best run."""
    count = {}                             # invariant: char -> its count inside the window
    left = 0
    max_freq = 0                           # invariant: >= the true max count when the answer grows
    for right in range(len(s)):
        ch = s[right]
        if ch in count:
            count[ch] = count[ch] + 1
        else:
            count[ch] = 1
        if count[ch] > max_freq:
            max_freq = count[ch]
        window_size = right - left + 1
        if window_size - max_freq > k:  # invalid: slide (never shrink)
            count[s[left]] = count[s[left]] - 1
            left = left + 1
    return len(s) - left


def max_consecutive_ones_iii(nums, k):  # LC 1004
    """Longest run of 1s after flipping at most k zeros.
    "Flip k zeros" is a disguise — the window never needs to know WHICH zeros
    it flipped, only how many it contains, so one counter replaces the whole
    choice. Same never-shrink slide as LC 424 with a two-symbol alphabet.

    Naive: try every subset of k zero positions to flip, then measure —
    exponential. Counting zeros in the window collapses the choice entirely.

    Real life: the longest stretch of a road trip you can call "on schedule"
    if you're allowed k late days — you only count the late days, not which."""
    left = 0
    zeros = 0                              # invariant: zeros inside nums[left:right+1]
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros = zeros + 1
        if zeros > k:  # invalid: slide (never shrink)
            if nums[left] == 0:
                zeros = zeros - 1
            left = left + 1
    return len(nums) - left


# --------------------------------------------------------------- Pattern 10
# Monotonic deque: an element smaller AND older than a newcomer can never
# be the max again — evict it. Front of deque = current max.
def sliding_window_maximum(nums, k):  # LC 239
    """Maximum of every window of size k.
    An element that is both smaller AND older than the newcomer can never be
    a future max — the newcomer outlives and outranks it — so evict it on
    sight. What survives is a decreasing queue whose front is today's max.

    Naive: rescan all k elements per window — O(nk). The deque remembers the
    only candidates that scan could ever return; each index enters and leaves once.

    Real life: a leaderboard where a younger, higher scorer permanently
    retires everyone below them — the board self-trims to the only players
    who could still lead (max latency over a rolling minute)."""
    dq = []                                # invariant: indices, their values strictly decreasing
    head = 0                               # invariant: dq[head] is the window's max; pop-front = head += 1
    out = []
    for i in range(len(nums)):
        while len(dq) > head and nums[dq[len(dq) - 1]] <= nums[i]:
            dq.pop()  # newcomer dominates these
        dq.append(i)
        if dq[head] <= i - k:  # front expired out of the window
            head = head + 1
        if i >= k - 1:
            out.append(nums[dq[head]])
    return out


# --------------------------------------------------------------- Pattern 11
# Frequency matching: an anagram is exactly a count-vector match in a
# fixed window; zero-count keys are deleted so dicts stay comparable.
def same_counts(a, b):
    # Helper: do two count dicts describe the same multiset?
    # Only sound because callers delete zero-count keys — a lingering {'x': 0}
    # would make two equal windows compare unequal.
    if len(a) != len(b):
        return False
    for key in a:
        if key not in b:
            return False
        if a[key] != b[key]:
            return False
    return True


def find_anagrams(s, p):  # LC 438
    """Every start index where a substring of s is an anagram of p.
    "Is this an anagram?" is exactly "do the count vectors match?", and order
    never enters into it. Since |p| is fixed, the window is fixed too: one
    char in, one char out, so each slide is two updates and a compare.

    Naive: sort each of the n windows and compare — O(n * m log m). The count
    dict carries the previous window's answer across the slide instead.

    Real life: checking each handful of Scrabble tiles against a target word —
    you don't re-sort the handful, you swap one tile and glance at the tally
    (spotting a fixed multiset of event types in a rolling window)."""
    if len(p) > len(s):
        return []
    need = {}                              # invariant: char -> count in p, zero keys deleted
    for i in range(len(p)):
        ch = p[i]
        if ch in need:
            need[ch] = need[ch] + 1
        else:
            need[ch] = 1
    window = {}                            # invariant: char -> count in the current window, zero keys deleted
    for i in range(len(p)):
        ch = s[i]
        if ch in window:
            window[ch] = window[ch] + 1
        else:
            window[ch] = 1
    res = []
    if same_counts(window, need):
        res.append(0)
    for i in range(len(p), len(s)):
        entering = s[i]
        if entering in window:
            window[entering] = window[entering] + 1
        else:
            window[entering] = 1
        leaving = s[i - len(p)]
        window[leaving] = window[leaving] - 1
        if window[leaving] == 0:
            del window[leaving]  # keep dicts comparable
        if same_counts(window, need):
            res.append(i - len(p) + 1)
    return res


if __name__ == "__main__":
    assert max_average_subarray([1, 12, -5, -6, 50, 3], 4) == 12.75
    assert longest_substring_no_repeat("abcabcbb") == 3
    assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2
    assert min_window_substring("ADOBECODEBANC", "ABC") == "BANC"
    assert longest_repeating_char_replacement("AABABBA", 1) == 4
    assert max_consecutive_ones_iii([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2) == 6
    assert sliding_window_maximum([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert find_anagrams("cbaebabacd", "abc") == [0, 6]
    print("02_sliding_window: all checks passed")
