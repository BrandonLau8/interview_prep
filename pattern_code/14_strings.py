"""Patterns 86-92: String Manipulation.

Core idea: careful scanning plus one hashing insight — a CANONICAL FORM
makes equivalent things identical (sorted word / count vector for anagrams,
failure table for repeated structure).
Run: python 14_strings.py
"""
from collections import defaultdict


# --------------------------------------------------------------- Pattern 86
def is_palindrome(s: str) -> bool:  # LC 125
    """Is s a palindrome, ignoring case and non-alphanumerics?
    Converging pointers with the filtering done in place: the inner loops skip
    junk so the outer comparison only ever sees real characters. The `lo < hi`
    guard inside them matters — an all-punctuation string must not run off.

    Naive: build a cleaned lowercase copy, then compare with its reverse —
    O(n) extra space for a check that needs none.

    Real life: reading a sign from both ends at once, ignoring the spaces and
    punctuation, and stopping the moment two letters disagree."""
    lo, hi = 0, len(s) - 1                 # invariant: everything outside [lo, hi] already matched
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
    """Can s become a palindrome by deleting at most one character?
    The budget of one is what keeps this linear: at the FIRST mismatch the
    deletion must be one of those two characters, so there are exactly two
    branches to test and neither can branch again.

    Naive: delete each character in turn and test the rest — O(n^2). The
    single-mismatch argument reduces n candidates to two.

    Real life: a necklace with one bead out of place — the first asymmetric
    pair tells you which two beads to try removing, and no others."""
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
    """Are two strings anagrams of each other?
    One count vector, incremented for s and decremented for t: identical
    multisets cancel to all zeros. The length check is not redundant — it
    catches "a" vs "aa" style cases the running total alone would miss.

    Naive: sort both and compare — O(n log n) to establish an order that
    anagram-ness does not depend on.

    Real life: two bags of Scrabble tiles poured onto a balance one letter at
    a time — if the scales end level, the bags held the same tiles."""
    counts = [0] * 26                      # invariant: per-letter surplus of s over t so far
    for ch in s:
        counts[ord(ch) - 97] += 1
    for ch in t:
        counts[ord(ch) - 97] -= 1
    return len(s) == len(t) and not any(counts)


def group_anagrams(strs: list[str]) -> list[list[str]]:  # LC 49
    """Group words that are anagrams of one another.
    A CANONICAL FORM turns equality-testing into hashing: pick a key that
    anagrams share and nothing else does, and the dict does the grouping. The
    count vector beats a sorted string — O(len) per word rather than O(len log len).

    Naive: compare every pair with is_anagram — O(n^2) comparisons, and the
    result still needs assembling into groups afterwards.

    Real life: filing words by a fingerprint of their letter counts — every
    anagram produces the same fingerprint, so they land in one folder."""
    groups: dict[tuple, list[str]] = defaultdict(list)   # invariant: count-vector key -> all words sharing it
    for word in strs:
        key = [0] * 26                     # count vector beats sorting: O(len)
        for ch in word:
            key[ord(ch) - 97] += 1
        groups[tuple(key)].append(word)
    return list(groups.values())


# --------------------------------------------------------------- Pattern 88
def roman_to_int(s: str) -> int:  # LC 13
    """Convert a Roman numeral to an integer.
    One local rule covers every subtractive case: a symbol smaller than its
    RIGHT neighbour is subtracted, otherwise added. No table of IV, IX, XL is
    needed — the ordering already encodes them, and one pass suffices.

    Naive: scan for each two-character subtractive pair and special-case it —
    six exceptions to maintain where the comparison handles all of them.

    Real life: reading a tally where a mark placed before a bigger one means
    "one short of" — you only ever glance one symbol ahead."""
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0                              # invariant: value of the prefix consumed so far
    for cur, nxt in zip(s, s[1:] + "\0"):
        total += -vals[cur] if vals.get(nxt, 0) > vals[cur] else vals[cur]
    return total


def int_to_roman(num: int) -> str:  # LC 12
    """Convert an integer to a Roman numeral.
    Listing the subtractive forms (900, 400, 90, ...) as ordinary table
    entries is the whole trick: with them present, plain descending greedy is
    correct, and no special-casing survives into the loop.

    Naive: greedy over the seven base symbols only, then post-process runs of
    four into subtractive form — a second pass that the table makes unnecessary.

    Real life: paying an amount with coins that include odd 900 and 400
    denominations — always hand over the largest that still fits."""
    table = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
             (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
             (5, "V"), (4, "IV"), (1, "I")]   # invariant: descending, subtractives included so greedy is exact
    out: list[str] = []
    for val, sym in table:
        while num >= val:
            out.append(sym)
            num -= val
    return "".join(out)


# --------------------------------------------------------------- Pattern 89
def my_atoi(s: str) -> int:  # LC 8 — a state machine discipline test
    """Parse a leading integer from a string, C-style, clamping to int32.
    Not an algorithm — a specification. Write the states down first
    (whitespace, one optional sign, digits, stop) and the code follows.
    Clamping must happen DURING accumulation — checking afterwards assumes the
    very overflow you were avoiding, which is real in C++/Java.

    Naive: strip and call int() — accepts things the spec rejects and rejects
    trailing junk the spec ignores.

    Real life: reading a handwritten form field that may have leading spaces,
    a sign, then digits, then somebody's scribbled note you must ignore."""
    INT_MAX, INT_MIN = 2**31 - 1, -2**31
    i, n = 0, len(s)                       # invariant: i is the next unconsumed character
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
    # Sum of two non-negative decimal strings, without converting to int.
    # Identical schoolbook loop to add_binary in 13_array_matrix.py, base 10:
    # `carry` in the loop condition absorbs unequal lengths and the final carry.
    # Naive: int(a) + int(b) — sidesteps the arbitrary-precision arithmetic
    # that is the entire point of the question.
    # Real life: adding two long numbers on paper, right to left.
    i, j, carry = len(a) - 1, len(b) - 1, 0   # invariant: carry is 0 or 1, owed to the next column
    out: list[str] = []
    while i >= 0 or j >= 0 or carry:
        total = carry + (int(a[i]) if i >= 0 else 0) + (int(b[j]) if j >= 0 else 0)
        carry, digit = divmod(total, 10)
        out.append(str(digit))
        i, j = i - 1, j - 1
    return "".join(reversed(out))


def multiply_strings(a: str, b: str) -> str:  # LC 43
    """Product of two non-negative decimal strings, without big-int conversion.
    The index identity is everything: digit i times digit j always lands in
    positions i+j+1 (units) and i+j (carry). Knowing that, the partial products
    can be accumulated straight into one array — no shifting, no addition pass.

    Naive: form each partial product as a string, pad it with zeros, and add
    them with LC 415 — O(n) separate additions instead of one accumulation.

    Real life: long multiplication where, instead of writing each shifted row
    and summing at the end, you drop every digit straight into its column."""
    if a == "0" or b == "0":
        return "0"                         # without this the result would render as "0000"
    res = [0] * (len(a) + len(b))          # invariant: res[i+j+1] holds units, res[i+j] the carry
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            total = int(a[i]) * int(b[j]) + res[i + j + 1]
            res[i + j + 1] = total % 10
            res[i + j] += total // 10
    out = "".join(map(str, res)).lstrip("0")
    return out


# --------------------------------------------------------------- Pattern 91
def build_lps(pattern: str) -> list[int]:
    """KMP failure table: how much of a match survives a mismatch.
    lps[i] is the longest proper prefix of pattern[:i+1] that is also its
    suffix. On a mismatch that border is exactly what already matched, so the
    search resumes there — built by running the pattern against ITSELF.

    Naive: on a mismatch, back the text pointer up and retry from the next
    start — O(nm), re-reading characters the border proves already match.

    Real life: losing your place mid-word and noticing the last few letters
    you read are also how the word begins — you resume from there."""
    lps = [0] * len(pattern)               # invariant: lps[i] = longest border of pattern[:i+1]
    length = 0                             # invariant: length of the border being extended
    for i in range(1, len(pattern)):
        while length and pattern[i] != pattern[length]:
            length = lps[length - 1]       # fall back to the next-shorter border
        if pattern[i] == pattern[length]:
            length += 1
        lps[i] = length
    return lps


def str_str(haystack: str, needle: str) -> int:  # LC 28 (KMP)
    """Index of the first occurrence of needle in haystack, or -1.
    The failure table earns its keep here: i NEVER moves backward, so the text
    is read once. On a mismatch only j retreats, to the longest border that
    still matches — which is why the total work is O(n + m), not O(nm).

    Naive: try every start position and compare forward — O(nm), worst case on
    inputs like "aaaa...b" where each attempt re-reads almost the whole prefix.

    Real life: scanning a shelf for a title and, on a near-miss, realizing the
    tail of what you just read is itself a valid beginning — no backtracking."""
    if not needle:
        return 0
    lps = build_lps(needle)
    j = 0                                  # invariant: needle[:j] matches the text ending just before i
    for i, ch in enumerate(haystack):      # i NEVER moves backward
        while j and ch != needle[j]:
            j = lps[j - 1]                 # reuse the survived prefix
        if ch == needle[j]:
            j += 1
        if j == len(needle):
            return i - j + 1
    return -1


def rotate_string(s: str, goal: str) -> bool:  # LC 796
    """Is goal a rotation of s?
    s + s contains every rotation of s as a contiguous window, so "is it a
    rotation?" collapses to "is it a substring?". The length check is what
    stops a short string matching as a mere fragment.

    Naive: generate all n rotations and compare — O(n^2). The doubling
    enumerates them all implicitly in one string.

    Real life: laying a bracelet's beads out twice in a row — every way of
    unclasping it appears somewhere along that doubled strip."""
    return len(s) == len(goal) and goal in s + s


# --------------------------------------------------------------- Pattern 92
def repeated_substring_pattern(s: str) -> bool:  # LC 459
    """Is s built by repeating some shorter substring?
    s + s contains s at positions 0 and n trivially. Chopping one character
    off each end destroys exactly those two, so a surviving match can only sit
    at a genuine period — periodicity becomes one substring test.

    Naive: try every divisor length d of n and check each block — O(n * d(n))
    and easy to get the divisor enumeration wrong.

    Real life: sliding a patterned ribbon along a copy of itself — if it lines
    up anywhere other than the obvious ends, the pattern repeats."""
    return s in (s + s)[1:-1]


def repeated_substring_pattern_kmp(s: str) -> bool:  # LC 459 via failure table
    # Same question as above, answered from the failure table.
    # A string's longest border implies its shortest period: period = n -
    # border. The string is periodic exactly when that period divides n and
    # the border is non-empty.
    # Naive: the s in (s+s)[1:-1] one-liner above — shorter, but it builds a
    # 2n string; this reuses the table you already know how to construct.
    # Real life: measuring a repeating wallpaper by how far you can slide it
    # before it lines up with itself again.
    n = len(s)
    border = build_lps(s)[-1]              # invariant: longest proper prefix of s that is also a suffix
    period = n - border                    # invariant: shortest candidate period implied by that border
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
    assert my_atoi("-91283472332") == -2**31   # clamps mid-accumulation, not after
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
