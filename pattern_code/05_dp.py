"""Patterns 30-41: Dynamic Programming.

Core idea: finding the STATE is the hard part. Ask: "processing left to
right, what minimal summary of the past determines the future?" That summary
is your state; the transition writes itself.
Run: python 05_dp.py
"""


# --------------------------------------------------------------- Pattern 30
# Fibonacci style: each position depends on the previous 1-2 positions.
def climb_stairs(n: int) -> int:  # LC 70
    a, b = 1, 1                            # ways to reach steps i-2, i-1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def rob(nums: list[int]) -> int:  # LC 198
    rob_here, skip_here = 0, 0             # best if last house robbed / skipped
    for x in nums:
        rob_here, skip_here = skip_here + x, max(rob_here, skip_here)
    return max(rob_here, skip_here)


def rob_circular(nums: list[int]) -> int:  # LC 213
    # Circle = can't rob both ends -> solve twice, excluding each end.
    if len(nums) == 1:
        return nums[0]
    return max(rob(nums[1:]), rob(nums[:-1]))


def num_decodings(s: str) -> int:  # LC 91
    # dp over prefixes: last char alone (1-9) or last two together (10-26).
    prev2, prev1 = 1, 1                    # empty prefix, first char handled below
    for i, ch in enumerate(s):
        cur = 0
        if ch != "0":
            cur += prev1
        if i > 0 and "10" <= s[i - 1:i + 1] <= "26":
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1


# --------------------------------------------------------------- Pattern 31
# Kadane: extend the best subarray ending here, or start fresh.
def max_subarray(nums: list[int]) -> int:  # LC 53
    best = ending_here = nums[0]
    for x in nums[1:]:
        ending_here = max(x, ending_here + x)   # negative prefix = dead weight
        best = max(best, ending_here)
    return best


def max_product(nums: list[int]) -> int:  # LC 152
    # Track max AND min ending here: negative * negative flips min into max.
    best = hi = lo = nums[0]
    for x in nums[1:]:
        hi, lo = max(x, hi * x, lo * x), min(x, hi * x, lo * x)
        best = max(best, hi)
    return best


def max_subarray_circular(nums: list[int]) -> int:  # LC 918
    total, best, worst, cur_hi, cur_lo = 0, nums[0], nums[0], 0, 0
    for x in nums:
        total += x
        cur_hi = max(x, cur_hi + x)
        best = max(best, cur_hi)
        cur_lo = min(x, cur_lo + x)
        worst = min(worst, cur_lo)
    # wrap-around max = total - (minimum middle); all-negative edge case
    return best if best < 0 else max(best, total - worst)


# --------------------------------------------------------------- Pattern 32
# Unbounded knapsack. LOOP ORDER decides combinations vs permutations.
def coin_change(coins: list[int], amount: int) -> int:  # LC 322
    INF = amount + 1
    dp = [0] + [INF] * amount              # dp[a] = fewest coins for amount a
    for a in range(1, amount + 1):
        for c in coins:                    # try every coin as the LAST coin
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return -1 if dp[amount] == INF else dp[amount]


def coin_change_ways(coins: list[int], amount: int) -> int:  # LC 518
    dp = [1] + [0] * amount
    for c in coins:                        # coins OUTER -> each combination
        for a in range(c, amount + 1):     # counted once (order fixed)
            dp[a] += dp[a - c]
    return dp[amount]


def combination_sum_iv(nums: list[int], target: int) -> int:  # LC 377
    dp = [1] + [0] * target
    for a in range(1, target + 1):         # amount OUTER -> order matters:
        for c in nums:                     # counts PERMUTATIONS
            if c <= a:
                dp[a] += dp[a - c]
    return dp[target]


# --------------------------------------------------------------- Pattern 33
# 0/1 knapsack: iterate sums DOWNWARD so each item counts once.
def can_partition(nums: list[int]) -> bool:  # LC 416
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    dp = [True] + [False] * target         # dp[s] = "sum s reachable"
    for x in nums:
        for s in range(target, x - 1, -1):  # downward = x used at most once
            dp[s] = dp[s] or dp[s - x]
    return dp[target]


def find_target_sum_ways(nums: list[int], target: int) -> int:  # LC 494
    # Algebra first: P - N = target, P + N = total -> P = (total+target)/2.
    total = sum(nums)
    if (total + target) % 2 or abs(target) > total:
        return 0
    goal = (total + target) // 2
    dp = [1] + [0] * goal
    for x in nums:
        for s in range(goal, x - 1, -1):
            dp[s] += dp[s - x]
    return dp[goal]


# --------------------------------------------------------------- Pattern 34
def word_break(s: str, word_dict: list[str]) -> bool:  # LC 139
    words = set(word_dict)
    dp = [True] + [False] * len(s)         # dp[i] = prefix of length i breakable
    for i in range(1, len(s) + 1):
        dp[i] = any(dp[j] and s[j:i] in words for j in range(i))
    return dp[-1]


# --------------------------------------------------------------- Pattern 35
def longest_common_subsequence(a: str, b: str) -> int:  # LC 1143
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1    # match: extend diagonal
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # drop one char
    return dp[-1][-1]


def min_insertions_palindrome(s: str) -> int:  # LC 1312 — reduces to LCS
    return len(s) - longest_common_subsequence(s, s[::-1])


# --------------------------------------------------------------- Pattern 36
def edit_distance(a: str, b: str) -> int:  # LC 72
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i                       # delete everything
    for j in range(len(b) + 1):
        dp[0][j] = j                       # insert everything
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]         # match is free
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1],  # replace
                                   dp[i - 1][j],      # delete from a
                                   dp[i][j - 1])      # insert into a
    return dp[-1][-1]


# --------------------------------------------------------------- Pattern 37
def unique_paths(m: int, n: int) -> int:  # LC 62
    row = [1] * n                          # 1-D rolling row
    for _ in range(m - 1):
        for j in range(1, n):
            row[j] += row[j - 1]           # up + left
    return row[-1]


def min_path_sum(grid: list[list[int]]) -> int:  # LC 64
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if r or c:
                best_in = min(grid[r - 1][c] if r else float("inf"),
                              grid[r][c - 1] if c else float("inf"))
                grid[r][c] += best_in
    return grid[-1][-1]


def maximal_square(matrix: list[list[str]]) -> int:  # LC 221
    # dp = biggest square ENDING here; weakest of 3 neighbors caps you.
    rows, cols = len(matrix), len(matrix[0])
    dp = [[0] * (cols + 1) for _ in range(rows + 1)]
    side = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == "1":
                dp[r + 1][c + 1] = 1 + min(dp[r][c], dp[r][c + 1], dp[r + 1][c])
                side = max(side, dp[r + 1][c + 1])
    return side * side


# --------------------------------------------------------------- Pattern 38
def max_coins(nums: list[int]) -> int:  # LC 312 Burst Balloons
    # Inversion: pick which balloon pops LAST in (i, j) — it walls off the
    # two sides, making them independent.
    vals = [1] + nums + [1]
    n = len(vals)
    dp = [[0] * n for _ in range(n)]       # dp[i][j]: open interval (i, j)
    for length in range(2, n):             # increasing interval length
        for i in range(n - length):
            j = i + length
            dp[i][j] = max(
                dp[i][k] + vals[i] * vals[k] * vals[j] + dp[k][j]
                for k in range(i + 1, j))  # k pops last, sees walls i and j
    return dp[0][n - 1]


# --------------------------------------------------------------- Pattern 39
def num_trees(n: int) -> int:  # LC 96 — Catalan
    # Fix the root: left and right subtrees are independent subproblems.
    dp = [1] * (n + 1)
    for total in range(2, n + 1):
        dp[total] = sum(dp[left] * dp[total - 1 - left] for left in range(total))
    return dp[n]


# --------------------------------------------------------------- Pattern 40
def length_of_lis(nums: list[int]) -> int:  # LC 300, O(n log n)
    import bisect
    # tails[k] = smallest possible tail of an increasing subseq of length k+1.
    # Stays sorted -> each element binary-searches its slot.
    tails: list[int] = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)                # extends the longest subsequence
        else:
            tails[i] = x                   # same length, better (smaller) tail
    return len(tails)


def max_envelopes(envelopes: list[list[int]]) -> int:  # LC 354 Russian Doll
    # Sort width asc, height DESC within ties (blocks same-width chains),
    # then the problem is exactly LIS on heights.
    envelopes.sort(key=lambda e: (e[0], -e[1]))
    return length_of_lis([h for _, h in envelopes])


# --------------------------------------------------------------- Pattern 41
# Stock problems = one state machine with different edges.
def max_profit_one(prices: list[int]) -> int:  # LC 121
    best, low = 0, prices[0]
    for p in prices[1:]:
        best = max(best, p - low)
        low = min(low, p)
    return best


def max_profit_unlimited(prices: list[int]) -> int:  # LC 122
    hold, cash = -prices[0], 0             # best cash in each state
    for p in prices[1:]:
        hold = max(hold, cash - p)         # rest, or buy today
        cash = max(cash, hold + p)         # rest, or sell today
    return cash


def max_profit_cooldown(prices: list[int]) -> int:  # LC 309
    hold, cash, cooling = -prices[0], 0, 0
    for p in prices[1:]:
        hold, cooling, cash = (max(hold, cash - p),  # buy needs a rested day
                               hold + p,             # selling triggers cooldown
                               max(cash, cooling))   # cooldown expires
    return max(cash, cooling)


def max_profit_k(k: int, prices: list[int]) -> int:  # LC 188
    if not prices:
        return 0
    hold = [float("-inf")] * (k + 1)       # hold[t]: holding, t buys used
    cash = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            hold[t] = max(hold[t], cash[t - 1] - p)
            cash[t] = max(cash[t], hold[t] + p)
    return cash[k]


if __name__ == "__main__":
    assert climb_stairs(5) == 8
    assert rob([2, 7, 9, 3, 1]) == 12
    assert rob_circular([2, 3, 2]) == 3
    assert num_decodings("226") == 3 and num_decodings("06") == 0
    assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert max_product([2, 3, -2, 4]) == 6 and max_product([-2, 3, -4]) == 24
    assert max_subarray_circular([5, -3, 5]) == 10
    assert max_subarray_circular([-3, -2, -3]) == -2
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change_ways([1, 2, 5], 5) == 4
    assert combination_sum_iv([1, 2, 3], 4) == 7
    assert can_partition([1, 5, 11, 5]) and not can_partition([1, 2, 3, 5])
    assert find_target_sum_ways([1, 1, 1, 1, 1], 3) == 5
    assert word_break("leetcode", ["leet", "code"])
    assert longest_common_subsequence("abcde", "ace") == 3
    assert min_insertions_palindrome("mbadm") == 2
    assert edit_distance("horse", "ros") == 3
    assert unique_paths(3, 7) == 28
    assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert maximal_square([list("10100"), list("10111"),
                           list("11111"), list("10010")]) == 4
    assert max_coins([3, 1, 5, 8]) == 167
    assert num_trees(3) == 5
    assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert max_envelopes([[5, 4], [6, 4], [6, 7], [2, 3]]) == 3
    assert max_profit_one([7, 1, 5, 3, 6, 4]) == 5
    assert max_profit_unlimited([7, 1, 5, 3, 6, 4]) == 7
    assert max_profit_cooldown([1, 2, 3, 0, 2]) == 3
    assert max_profit_k(2, [3, 2, 6, 5, 0, 3]) == 7
    print("05_dp: all checks passed")
