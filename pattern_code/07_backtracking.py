"""Patterns 46-52: Backtracking.

Core idea: exhaustive search as a tree walk — choose, explore, UN-choose.
Power comes from pruning dead branches early and from shaping the decision
tree so duplicates are never generated (not filtered afterwards).
Run: python 07_backtracking.py
"""


# --------------------------------------------------------------- Pattern 46
def subsets(nums: list[int]) -> list[list[int]]:  # LC 78
    """Every subset of a list with distinct values.
    Two things make this the base case of the whole file: EVERY node of the
    tree is an answer, not just leaves; and "only choose indices >= start"
    fixes one order per subset, so each is generated once by construction.

    Naive: build all 2^n subsets by iterating bitmasks, or generate freely and
    dedupe with a set — the same count, but dedup work the shape avoids.

    Real life: walking a buffet once, deciding take-or-skip per dish and
    photographing your tray at every step — you never double back for dish 2."""
    res: list[list[int]] = []
    path: list[int] = []                   # invariant: the choices on the current root-to-node branch

    def dfs(start: int) -> None:
        res.append(path[:])                # EVERY node is an answer, not just leaves
        for i in range(start, len(nums)):  # "choose next index >= start"
            path.append(nums[i])           # -> each subset generated exactly once
            dfs(i + 1)
            path.pop()                     # un-choose
    dfs(0)
    return res


def subsets_with_dup(nums: list[int]) -> list[list[int]]:  # LC 90
    """Every distinct subset when the input may repeat values.
    The duplicate rule is subtle: skip equal SIBLINGS (same depth, i > start)
    but allow equal parent-child chains. Two 2s at the same level would build
    the identical subset twice; a 2 under a 2 is the legitimate [2,2].

    Naive: generate all subsets and dedupe via a set of sorted tuples — the
    tree still does the duplicate work, you just pay again to throw it away.

    Real life: choosing from a fruit bowl with three identical apples — how
    MANY apples you take matters, which apple you grabbed does not."""
    nums.sort()                            # invariant: equal values are adjacent, so siblings are comparable
    res: list[list[int]] = []
    path: list[int] = []

    def dfs(start: int) -> None:
        res.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                   # skip equal SIBLINGS (same depth),
            path.append(nums[i])           # equal parent-child chains are fine
            dfs(i + 1)
            path.pop()
    dfs(0)
    return res


def letter_combinations(digits: str) -> list[str]:  # LC 17
    # Every string spellable on a phone keypad from a digit sequence.
    # Fixed depth, no pruning, nothing to un-choose: passing path by value
    # means each branch owns its own copy, so the "un-choose" step disappears.
    # Naive: nested loops — but the nesting depth is len(digits), unknown
    # until runtime, which is exactly what the recursion supplies.
    # Real life: reading a phone number to someone and listing every word it
    # could spell, one digit's worth of letters at a time.
    if not digits:
        return []
    keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
            "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    res: list[str] = []

    def dfs(i: int, path: str) -> None:
        if i == len(digits):
            res.append(path)
            return
        for ch in keys[digits[i]]:
            dfs(i + 1, path + ch)
    dfs(0, "")
    return res


# --------------------------------------------------------------- Pattern 47
def permutations(nums: list[int]) -> list[list[int]]:  # LC 46
    """Every ordering of a list with distinct values.
    Order matters here, so unlike subsets there is no `start` — every unused
    element is a candidate at every depth. The used[] flags are what replace
    it, and only leaves are answers because a permutation must be complete.

    Naive: generate all n^n index tuples and discard those with repeats —
    n^n work for n! answers. The used[] check prunes those branches at entry.

    Real life: seating n guests in n chairs — at each chair you consider
    everyone still standing, and they sit back down when you backtrack."""
    res: list[list[int]] = []
    path: list[int] = []                   # invariant: the prefix chosen so far
    used = [False] * len(nums)             # invariant: used[i] iff nums[i] is somewhere in path

    def dfs() -> None:
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True                 # choose
            path.append(x)
            dfs()                          # explore
            path.pop()                     # un-choose
            used[i] = False
    dfs()
    return res


def next_permutation(nums: list[int]) -> None:  # LC 31 — one-shot construction
    """Next lexicographic permutation, in place, wrapping to sorted at the end.
    The odd one out in this file: no search at all. A descending suffix is
    already the largest arrangement of those values, so the first ascent from
    the right is the only digit worth raising — then minimize the suffix.

    Naive: generate permutations in order and take the one after this — up to
    O(n!) work for a step the structure of the number already determines.

    Real life: turning an odometer to the next-highest reading you can make
    from the same digits — you bump the rightmost digit that can rise and
    make everything after it as small as possible."""
    i = len(nums) - 2                      # invariant: nums[i+1:] is non-increasing when the loop stops
    while i >= 0 and nums[i] >= nums[i + 1]:   # suffix is descending = maxed out
        i -= 1
    if i >= 0:
        j = len(nums) - 1
        while nums[j] <= nums[i]:          # smallest suffix value > nums[i]
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])  # minimize the suffix


# --------------------------------------------------------------- Pattern 48
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:  # LC 39
    """All multisets of candidates summing to target; each may be reused freely.
    Recursing on `i` rather than `i + 1` is the entire difference from subsets:
    staying put permits reuse, while never going backwards still fixes one
    order per combination. `remaining` prunes a branch the moment it overshoots.

    Naive: enumerate all length-<=k sequences and filter by sum — it generates
    the same multiset in every order, then throws away all but one.

    Real life: making change from unlimited coins of each denomination, never
    reaching back for a smaller coin once you have moved past it."""
    res: list[list[int]] = []
    path: list[int] = []                   # invariant: current combination; sum(path) + remaining == target

    def dfs(start: int, remaining: int) -> None:
        if remaining == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:  # prune (needs sorted input to break)
                continue
            path.append(candidates[i])
            dfs(i, remaining - candidates[i])   # same i: reuse allowed
            path.pop()
    candidates.sort()
    dfs(0, target)
    return res


def combination_sum2(candidates: list[int], target: int) -> list[list[int]]:  # LC 40
    """Distinct combinations summing to target, each item usable once.
    Both constraints from earlier problems at once: i + 1 spends each item
    once (LC 39 used i), and the sibling skip suppresses duplicate values at
    one depth (LC 90). Sorting is what earns `break` instead of `continue`.

    Naive: take all subsets and filter by sum — 2^n branches explored where
    the sorted prune abandons a branch as soon as the smallest item overshoots.

    Real life: paying an exact amount from the coins in your pocket — each
    physical coin is spent once, but two identical dimes are interchangeable."""
    candidates.sort()                      # invariant: ascending, so an overshoot means every later one overshoots
    res: list[list[int]] = []
    path: list[int] = []

    def dfs(start: int, remaining: int) -> None:
        if remaining == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break
            if i > start and candidates[i] == candidates[i - 1]:
                continue                   # same sibling-skip as Subsets II
            path.append(candidates[i])
            dfs(i + 1, remaining - candidates[i])  # i+1: each item once
            path.pop()
    dfs(0, target)
    return res


# --------------------------------------------------------------- Pattern 49
def generate_parenthesis(n: int) -> list[str]:  # LC 22
    """All well-formed strings of n pairs of parentheses.
    Pruning by invariant instead of by test: the two guards (opened < n, and
    closed < opened) make every prefix valid by construction, so no branch is
    ever explored and rejected — the invalid ones are never entered.

    Naive: generate all 2^(2n) bracket strings and validate each with a
    counter — Catalan-many survive, so almost everything built is discarded.

    Real life: a bouncer letting people in and out of a room — you cannot let
    out more than went in, so an impossible sequence never starts."""
    res: list[str] = []

    def dfs(path: str, opened: int, closed: int) -> None:
        if len(path) == 2 * n:
            res.append(path)
            return
        if opened < n:
            dfs(path + "(", opened + 1, closed)
        if closed < opened:                # never more ) than (
            dfs(path + ")", opened, closed + 1)
    dfs("", 0, 0)
    return res


# --------------------------------------------------------------- Pattern 50
def word_search(board: list[list[str]], word: str) -> bool:  # LC 79
    """Does word trace a path through adjacent cells, no cell reused?
    Backtracking on a grid: the board itself is the visited set, marked "#"
    while a cell is on the CURRENT path and restored on the way out. Restoring
    is what distinguishes this from island-sinking — other paths still need it.

    Naive: enumerate all paths of len(word) and compare — 4^L branches, where
    matching char by char abandons a branch at the first wrong letter.

    Real life: tracing a word in a letter grid with your finger, keeping a
    thumb on the cells you are standing on and lifting it when you back up."""
    rows, cols = len(board), len(board[0])

    def dfs(r: int, c: int, i: int) -> bool:
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False
        board[r][c] = "#"                  # mark: cell is on the current path
        found = any(dfs(r + dr, c + dc, i + 1)
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = word[i]              # un-choose: restore for other paths
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))


# --------------------------------------------------------------- Pattern 51
def solve_n_queens(n: int) -> list[list[str]]:  # LC 51
    """All ways to place n non-attacking queens on an n x n board.
    Going row by row removes the row conflict for free. The other three
    questions each get a set: column, r - c and r + c are constant along the
    two diagonals, which turns every conflict test into an O(1) lookup.

    Naive: place queens anywhere and check all pairs — C(n^2, n) placements
    at O(n^2) each. The row-by-row shape plus three sets prunes at every level.

    Real life: seating guests who refuse to share a row, column or sight line
    — you keep three lists of what is already spoken for, not a seating chart."""
    res: list[list[str]] = []
    cols: set[int] = set()                 # invariant: columns occupied by rows above r
    diag1: set[int] = set()                # invariant: r - c values taken (constant along one diagonal)
    diag2: set[int] = set()                # invariant: r + c values taken (constant along the other)
    placement: list[int] = []              # invariant: placement[r] = column chosen for row r

    def dfs(r: int) -> None:
        if r == n:
            res.append(["." * c + "Q" + "." * (n - c - 1) for c in placement])
            return
        for c in range(n):
            if c in cols or (r - c) in diag1 or (r + c) in diag2:
                continue
            cols.add(c); diag1.add(r - c); diag2.add(r + c)
            placement.append(c)
            dfs(r + 1)
            placement.pop()
            cols.discard(c); diag1.discard(r - c); diag2.discard(r + c)
    dfs(0)
    return res


# --------------------------------------------------------------- Pattern 52
def partition_palindromes(s: str) -> list[list[str]]:  # LC 131
    """All ways to cut s so every piece is a palindrome.
    The decision at each step is "where does the next cut go?", which makes
    this subsets over cut positions. Two structures: the DP table answers "is
    s[i:j+1] a palindrome?" in O(1), and the backtracker walks the cut choices.

    Naive: try all 2^(n-1) cut sets and test each piece at O(n) — the table
    turns every one of those tests into a lookup instead.

    Real life: slicing a bead string into symmetric runs — you check a chart
    of which stretches read the same both ways rather than re-reading each."""
    n = len(s)
    # Precompute is_pal[i][j] so validity checks are O(1).
    is_pal = [[False] * n for _ in range(n)]   # invariant: True iff s[i:j+1] reads the same both ways
    for j in range(n):
        for i in range(j + 1):
            if s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
    res: list[list[str]] = []
    path: list[str] = []

    def dfs(start: int) -> None:
        if start == n:
            res.append(path[:])
            return
        for end in range(start, n):
            if is_pal[start][end]:
                path.append(s[start:end + 1])
                dfs(end + 1)
                path.pop()
    dfs(0)
    return res


if __name__ == "__main__":
    assert len(subsets([1, 2, 3])) == 8
    assert subsets_with_dup([1, 2, 2]) == \
        [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]
    assert sorted(letter_combinations("23")) == \
        sorted(["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"])
    assert len(permutations([1, 2, 3])) == 6
    a = [1, 2, 3]
    next_permutation(a)
    assert a == [1, 3, 2]
    b = [3, 2, 1]
    next_permutation(b)
    assert b == [1, 2, 3]                      # fully descending: no ascent, so it wraps
    assert sorted(combination_sum([2, 3, 6, 7], 7)) == [[2, 2, 3], [7]]
    assert sorted(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)) == \
        [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
    assert sorted(generate_parenthesis(3)) == \
        sorted(["((()))", "(()())", "(())()", "()(())", "()()()"])
    board = [list("ABCE"), list("SFCS"), list("ADEE")]
    assert word_search(board, "ABCCED") and not word_search(board, "ABCB")
    assert len(solve_n_queens(4)) == 2 and len(solve_n_queens(8)) == 92
    assert sorted(partition_palindromes("aab")) == [["a", "a", "b"], ["aa", "b"]]
    print("07_backtracking: all checks passed")
