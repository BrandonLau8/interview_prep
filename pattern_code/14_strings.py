"""Patterns 86-92: String Manipulation.

Core idea: careful scanning plus one hashing insight — a CANONICAL FORM
makes equivalent things identical (sorted word / count vector for anagrams,
failure table for repeated structure).
Run: python 14_strings.py
"""
from collections import defaultdict


# --------------------------------------------------------------- Pattern 86
def is_palindrome(s: str) -> bool:  # LC 125
    lo, hi = 0, len(s) - 1
    while lo < hi:
        while lo < hi and not s[lo].isalnum():
            lo += 1
        while lo < hi and not s[hi].isalnum():
            hi -= 1
        if s[lo].lower() != s[hi].lower():
            return False
        lo, hi = lo + 1, hi - 1
    return True


def valid_palindrome_ii(s: str) -> bool:  # LC 680 (one deletion allowed)
    def is_pal(lo: int, hi: int) -> bool:
        while lo < hi:
            if s[lo] != s[hi]:
                return False
            lo, hi = lo + 1, hi - 1
        return True

    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:                 # first mismatch: exactly one branch —
            return is_pal(lo + 1, hi) or is_pal(lo, hi - 1)  # skip either end
        lo, hi = lo + 1, hi - 1
    return True


# --------------------------------------------------------------- Pattern 87
def is_anagram(s: str, t: str) -> bool:  # LC 242
    counts = [0] * 26
    for ch in s:
        counts[ord(ch) - 97] += 1
    for ch in t:
        counts[ord(ch) - 97] -= 1
    return len(s) == len(t) and not any(counts)


def group_anagrams(strs: list[str]) -> list[list[str]]:  # LC 49
    # Canonical key: anagrams collide, non-anagrams don't.
    groups: dict[tuple, list[str]] = defaultdict(list)
    for word in strs:
        key = [0] * 26                     # count vector beats sorting: O(len)
        for ch in word:
            key[ord(ch) - 97] += 1
        groups[tuple(key)].append(word)
    return list(groups.values())


# --------------------------------------------------------------- Pattern 88
def roman_to_int(s: str) -> int:  # LC 13
    # The only rule: a symbol smaller than its RIGHT neighbor subtracts.
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for cur, nxt in zip(s, s[1:] + "\0"):
        total += -vals[cur] if vals.get(nxt, 0) > vals[cur] else vals[cur]
    return total


def int_to_roman(num: int) -> str:  # LC 12
    # Greedy over values with the subtractives listed explicitly.
    table = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
             (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
             (5, "V"), (4, "IV"), (1, "I")]
    out: list[str] = []
    for val, sym in table:
        while num >= val:
            out.append(sym)
            num -= val
    return "".join(out)


# --------------------------------------------------------------- Pattern 89
def my_atoi(s: str) -> int:  # LC 8 — a state machine discipline test
    INT_MAX, INT_MIN = 2**31 - 1, -2**31
    i, n = 0, len(s)
    while i < n and s[i] == " ":           # state 1: whitespace
        i += 1
    sign = 1
    if i < n and s[i] in "+-":             # state 2: one optional sign
        sign = -1 if s[i] == "-" else 1
        i += 1
    num = 0
    while i < n and s[i].isdigit():        # state 3: digits (junk after ignored)
        num = num * 10 + int(s[i])
        if sign * num <= INT_MIN:          # clamp as soon as it happens
            return INT_MIN
        if sign * num >= INT_MAX:
            return INT_MAX
        i += 1
    return sign * num


# --------------------------------------------------------------- Pattern 90
def add_strings(a: str, b: str) -> str:  # LC 415
    i, j, carry = len(a) - 1, len(b) - 1, 0
    out: list[str] = []
    while i >= 0 or j >= 0 or carry:
        total = carry + (int(a[i]) if i >= 0 else 0) + (int(b[j]) if j >= 0 else 0)
        carry, digit = divmod(total, 10)
        out.append(str(digit))
        i, j = i - 1, j - 1
    return "".join(reversed(out))


def multiply_strings(a: str, b: str) -> str:  # LC 43
    # digit i x digit j lands at positions i+j (carry) and i+j+1 (unit).
    if a == "0" or b == "0":
        return "0"
    res = [0] * (len(a) + len(b))
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            total = int(a[i]) * int(b[j]) + res[i + j + 1]
            res[i + j + 1] = total % 10
            res[i + j] += total // 10
    out = "".join(map(str, res)).lstrip("0")
    return out


# --------------------------------------------------------------- Pattern 91
def build_lps(pattern: str) -> list[int]:
    """KMP failure table: lps[i] = length of the longest proper prefix of
    pattern[:i+1] that is also its suffix — i.e., how much match survives
    a mismatch."""
    lps = [0] * len(pattern)
    length = 0
    for i in range(1, len(pattern)):
        while length and pattern[i] != pattern[length]:
            length = lps[length - 1]       # fall back to the next-shorter border
        if pattern[i] == pattern[length]:
            length += 1
        lps[i] = length
    return lps


def str_str(haystack: str, needle: str) -> int:  # LC 28 (KMP)
    if not needle:
        return 0
    lps = build_lps(needle)
    j = 0                                  # chars of needle currently matched
    for i, ch in enumerate(haystack):      # i NEVER moves backward
        while j and ch != needle[j]:
            j = lps[j - 1]                 # reuse the survived prefix
        if ch == needle[j]:
            j += 1
        if j == len(needle):
            return i - j + 1
    return -1


def rotate_string(s: str, goal: str) -> bool:  # LC 796
    # Every rotation of s is a substring of s+s.
    return len(s) == len(goal) and goal in s + s


# --------------------------------------------------------------- Pattern 92
def repeated_substring_pattern(s: str) -> bool:  # LC 459
    # s is periodic <=> s appears inside (s+s) with both ends chopped.
    return s in (s + s)[1:-1]


def repeated_substring_pattern_kmp(s: str) -> bool:  # LC 459 via failure table
    n = len(s)
    border = build_lps(s)[-1]              # longest border of the whole string
    period = n - border
    return border > 0 and n % period == 0


if __name__ == "__main__":
    assert is_palindrome("A man, a plan, a canal: Panama")
    assert valid_palindrome_ii("abca") and not valid_palindrome_ii("abcd")
    assert is_anagram("anagram", "nagaram")
    assert sorted(map(sorted, group_anagrams(
        ["eat", "tea", "tan", "ate", "nat", "bat"]))) == \
        sorted([["ate", "eat", "tea"], ["nat", "tan"], ["bat"]])
    assert roman_to_int("MCMXCIV") == 1994
    assert int_to_roman(1994) == "MCMXCIV"
    assert my_atoi("   -42") == -42
    assert my_atoi("4193 with words") == 4193
    assert my_atoi("-91283472332") == -2**31
    assert add_strings("456", "77") == "533"
    assert multiply_strings("123", "456") == "56088"
    assert build_lps("aabaaab") == [0, 1, 0, 1, 2, 2, 3]
    assert str_str("sadbutsad", "sad") == 0
    assert str_str("leetcode", "leeto") == -1
    assert rotate_string("abcde", "cdeab")
    assert repeated_substring_pattern("abab")
    assert not repeated_substring_pattern("aba")
    assert repeated_substring_pattern_kmp("abcabcabc")
    assert not repeated_substring_pattern_kmp("abac")
    print("14_strings: all checks passed")
