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
    window = 0
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
    # Invariant: window [left, right] never contains a repeat.
    last_seen = {}  # char -> index of its most recent occurrence
    left = 0
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
    # "Shortest valid": expand until valid, then shrink WHILE still valid.
    left = 0
    total = 0
    best = len(nums) + 1  # sentinel: longer than any real window
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
    # need[ch] > 0: window still owes that many of ch.
    # need[ch] < 0: window holds that many surplus ch.
    need = {}
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
    # Valid window: (size - count of majority char) <= k.
    # Trick: max_freq never needs to decrease — window only needs to grow
    # when a NEW higher max_freq appears, so a stale max just freezes growth.
    count = {}
    left = 0
    max_freq = 0
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
    # Reframe: longest window containing at most k zeros.
    left = 0
    zeros = 0
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
    dq = []  # indices, values decreasing from front to back
    head = 0  # dq[head] is the front; "pop front" just advances head
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
    if len(a) != len(b):
        return False
    for key in a:
        if key not in b:
            return False
        if a[key] != b[key]:
            return False
    return True


def find_anagrams(s, p):  # LC 438
    if len(p) > len(s):
        return []
    need = {}
    for i in range(len(p)):
        ch = p[i]
        if ch in need:
            need[ch] = need[ch] + 1
        else:
            need[ch] = 1
    window = {}
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
