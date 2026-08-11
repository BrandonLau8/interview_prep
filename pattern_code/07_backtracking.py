"""Patterns 46-52: Backtracking.

Core idea: exhaustive search as a tree walk — choose, explore, UN-choose.
Power comes from pruning dead branches early and from shaping the decision
tree so duplicates are never generated (not filtered afterwards).
Run: python 07_backtracking.py
"""


# --------------------------------------------------------------- Pattern 46
def subsets(nums: list[int]) -> list[list[int]]:  # LC 78
    res: list[list[int]] = []
    path: list[int] = []

    def dfs(start: int) -> None:
        res.append(path[:])                # EVERY node is an answer, not just leaves
        for i in range(start, len(nums)):  # "choose next index >= start"
            path.append(nums[i])           # -> each subset generated exactly once
            dfs(i + 1)
            path.pop()                     # un-choose
    dfs(0)
    return res


def subsets_with_dup(nums: list[int]) -> list[list[int]]:  # LC 90
    nums.sort()                            # duplicates become adjacent
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
    res: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(nums)

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
    # From the right: find first ascent, swap with its ceiling, reverse suffix.
    i = len(nums) - 2
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
    res: list[list[int]] = []
    path: list[int] = []

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
    candidates.sort()
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
    # Prune by invariant: every prefix is valid by construction.
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
    # Row by row; O(1) conflict checks: r-c and r+c are diagonal invariants.
    res: list[list[str]] = []
    cols: set[int] = set()
    diag1: set[int] = set()                # r - c
    diag2: set[int] = set()                # r + c
    placement: list[int] = []              # placement[r] = chosen column

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
    # Decision at each position: where does the next cut go?
    n = len(s)
    # Precompute is_pal[i][j] so validity checks are O(1).
    is_pal = [[False] * n for _ in range(n)]
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
    assert b == [1, 2, 3]
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
