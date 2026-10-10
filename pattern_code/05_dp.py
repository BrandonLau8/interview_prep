"""Patterns 30-41: Dynamic Programming.

Core idea: finding the STATE is the hard part. Ask: "processing left to
right, what minimal summary of the past determines the future?" That summary
is your state; the transition writes itself.
Run: python 05_dp.py
"""


# --------------------------------------------------------------- Pattern 30
# Fibonacci style: each position depends on the previous 1-2 positions.
def climb_stairs(n: int) -> int:  # LC 70
    """Ways to climb n stairs taking 1 or 2 steps at a time.
    The state is "how many ways reach step i", and the last move was either a
    1 or a 2 — so the answer is the sum of the two before it. Nothing else
    about the path survives, which is why two variables replace the array.

    Naive: enumerate every sequence of steps — exponential, re-deriving the
    ways to reach step 3 once per path that passes through it.

    Real life: counting routes up a staircase where you can only remember the
    last two landings — the tally at each landing is all you carry."""
    a, b = 1, 1                            # invariant: ways to reach steps i-2 and i-1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def rob(nums: list[int]) -> int:  # LC 198
    """Max loot from a row of houses when no two adjacent may be robbed.
    One number is not enough state — whether the NEXT house is allowed depends
    on what you did here. Carrying both answers, best-if-robbed and
    best-if-skipped, makes the transition local. Same split as LC 337 on a tree.

    Naive: enumerate every subset with no two adjacent — exponential, when the
    only thing the future needs is those two running numbers.

    Real life: walking a street deciding house by house, remembering only your
    best total under "I just took one" and "I just walked past one"."""
    rob_here, skip_here = 0, 0             # invariant: best totals ending with this house robbed / skipped
    for x in nums:
        rob_here, skip_here = skip_here + x, max(rob_here, skip_here)
    return max(rob_here, skip_here)


def rob_circular(nums: list[int]) -> int:  # LC 213
    # Max loot when the houses form a circle.
    # The circle adds exactly one constraint: first and last are now adjacent.
    # Rather than encode it in the state, drop one end and solve LC 198 twice —
    # every valid plan omits at least one end, so the max of the two is right.
    # Naive: add "did I rob the first house?" to the state, doubling the DP.
    # Real life: a ring road of houses — commit to skipping one end, then the
    # ring is just a street again.
    if len(nums) == 1:
        return nums[0]
    return max(rob(nums[1:]), rob(nums[:-1]))


def num_decodings(s: str) -> int:  # LC 91
    """Ways to decode a digit string where A=1 ... Z=26.
    Same two-back recurrence as LC 70, but each edge is now conditional: the
    last letter used one digit (illegal if "0") or two (legal only in 10..26).
    The traps are all zeros — "0" alone decodes to nothing, "06" is not 6.

    Naive: generate every split of the string and validate — exponential, and
    it re-decodes shared prefixes once per suffix.

    Real life: reading a run-together phone keypad code where some pairs of
    digits form one letter — you count readings, not letters."""
    prev2, prev1 = 1, 1                    # invariant: ways to decode prefixes of length i-2 and i-1
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
    """Largest sum of any contiguous subarray.
    Kadane: the only question per element is "extend the best run ending at
    the previous element, or start fresh here?" A prefix with negative sum is
    dead weight, so a running total that never goes negative-first suffices.

    Naive: sum every (start, end) pair — O(n^2) with a running sum. The
    constrained/unconstrained split (ending_here vs best) removes the outer loop.

    Real life: a road trip logging daily net gain — the moment your running
    total goes negative, you would have been better starting from today."""
    best = ending_here = nums[0]           # invariant: ending_here = best sum of a run ending at i
    for x in nums[1:]:
        ending_here = max(x, ending_here + x)   # negative prefix = dead weight
        best = max(best, ending_here)
    return best


def max_product(nums: list[int]) -> int:  # LC 152
    """Largest product of any contiguous subarray.
    Kadane's state is not enough: multiplying by a negative turns the SMALLEST
    running product into the largest, so the most negative value is a live
    candidate. Track both extremes and let a negative swap their roles.

    Naive: multiply out every subarray — O(n^2). Keeping the min alongside the
    max is what preserves the one fact a sign flip can promote.

    Real life: compounding returns where two bad months cancel — you have to
    remember your worst run as well as your best, because it may turn."""
    best = hi = lo = nums[0]               # invariant: hi/lo = largest and smallest product of a run ending at i
    for x in nums[1:]:
        hi, lo = max(x, hi * x, lo * x), min(x, hi * x, lo * x)
        best = max(best, hi)
    return best


def max_subarray_circular(nums: list[int]) -> int:  # LC 918
    """Largest contiguous sum when the array wraps around.
    A wrapping subarray is the complement of a non-wrapping one, so its sum is
    total - (minimum middle) — one extra Kadane for the min. The all-negative
    case is the trap: the complement would be empty, which is not allowed.

    Naive: concatenate the array with itself and run Kadane on windows of at
    most n — O(n) but fiddly to bound; the complement identity needs no bound.

    Real life: a circular railway where the best stretch may run through
    midnight — either it doesn't wrap, or it is everything except the worst run."""
    total, best, worst, cur_hi, cur_lo = 0, nums[0], nums[0], 0, 0   # invariant: best/worst = max and min non-wrapping sums
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
    """Fewest coins summing to amount, unlimited copies of each, or -1.
    State is just the amount left — which coins got you there does not affect
    what remains. Trying every coin as the LAST one covers all cases, and
    reusing dp[a - c] is what makes unlimited copies free.

    Naive: greedy largest-coin-first is simply wrong (coins [1,3,4], amount 6
    gives 4+1+1 instead of 3+3). Exhaustive search is exponential.

    Real life: making change at a till with an odd currency — you work up from
    small amounts, and the answer for 6p is built from the answer for 6-c."""
    INF = amount + 1                       # sentinel: more coins than any real answer needs
    dp = [0] + [INF] * amount              # invariant: dp[a] = fewest coins making exactly a
    for a in range(1, amount + 1):
        for c in coins:                    # try every coin as the LAST coin
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return -1 if dp[amount] == INF else dp[amount]


def coin_change_ways(coins: list[int], amount: int) -> int:  # LC 518
    """Number of distinct coin COMBINATIONS summing to amount.
    Loop order is the entire answer. Coins outer means each combination is
    built in one fixed coin order, so {1,2} is counted once. Swap the loops
    and you get LC 377 instead — same array, same updates, different meaning.

    Naive: enumerate combinations and dedupe by sorting each — exponential
    generation plus dedup work the loop order avoids entirely.

    Real life: counting the ways to pay a price when the order you hand over
    the coins is irrelevant — you fix an order once and never revisit it."""
    dp = [1] + [0] * amount                # invariant: dp[a] = combinations of coins processed so far making a
    for c in coins:                        # coins OUTER -> each combination
        for a in range(c, amount + 1):     # counted once (order fixed)
            dp[a] += dp[a - c]
    return dp[amount]


def combination_sum_iv(nums: list[int], target: int) -> int:  # LC 377
    # Number of ORDERED sequences summing to target (misnamed on LeetCode).
    # Identical array and updates to LC 518 with the loops swapped: amount
    # outer means each amount considers every number as its last step, so
    # 1+2 and 2+1 are counted separately.
    # Naive: enumerate sequences — exponential, and the count is often huge.
    # Real life: counting the distinct orders you could climb to a total,
    # where taking the 2 first is a different climb from taking the 1 first.
    dp = [1] + [0] * target                # invariant: dp[a] = ordered sequences summing to a
    for a in range(1, target + 1):         # amount OUTER -> order matters:
        for c in nums:                     # counts PERMUTATIONS
            if c <= a:
                dp[a] += dp[a - c]
    return dp[target]


# --------------------------------------------------------------- Pattern 33
# 0/1 knapsack: iterate sums DOWNWARD so each item counts once.
def can_partition(nums: list[int]) -> bool:  # LC 416
    """Can the list be split into two subsets of equal sum?
    Reframe first: equal halves means "is total/2 reachable as a subset sum?",
    so a boolean per sum is enough state. Iterating sums DOWNWARD is what
    makes it 0/1 — upward would read a slot this same item already updated.

    Naive: try all 2^n subsets and sum each — exponential; the dp collapses
    every subset reaching the same sum into one bit.

    Real life: splitting a shopping trolley evenly between two people — you
    only care which totals are achievable, not who carries which item."""
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
    """Ways to assign + or - to every number so the result is target.
    Do the algebra before the DP: with P the positives and N the negatives,
    P - N = target and P + N = total give P = (total + target) / 2. The sign
    problem is now subset-sum counting — the same downward 0/1 loop as LC 416.

    Naive: try all 2^n sign assignments — exponential, and it never notices
    that only the positive subset's SUM matters.

    Real life: settling debts where each amount is paid or received — you
    solve for how much must be on the paying side, then count the ways."""
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
    """Can s be cut into a sequence of dictionary words?
    The state is one boolean per prefix length: a prefix is breakable if some
    earlier breakable prefix is followed by a dictionary word. Only the
    breakability of prefixes matters — which words were used never does.

    Naive: backtrack over cut positions — exponential on strings like
    "aaaa...b", re-solving the same suffix once per way of reaching it.

    Real life: reading a sign with the spaces rubbed out — you mark how far
    you can read cleanly, and extend from the furthest clean point."""
    words = set(word_dict)                 # invariant: membership test in O(1)
    dp = [True] + [False] * len(s)         # invariant: dp[i] = the first i chars split into words
    for i in range(1, len(s) + 1):
        dp[i] = any(dp[j] and s[j:i] in words for j in range(i))
    return dp[-1]


# --------------------------------------------------------------- Pattern 35
def longest_common_subsequence(a: str, b: str) -> int:  # LC 1143
    """Length of the longest subsequence common to both strings.
    Two strings means two indices, so the state is a grid. At each cell one
    question: do the current chars match? If so the answer extends the
    diagonal; if not, one of the two chars must be dropped — try both.

    Naive: enumerate all 2^|a| subsequences of a and test each against b —
    exponential, when every pair of prefixes has just one best answer.

    Real life: aligning two editions of a document to find the text they
    share — you walk both in step, taking matches and skipping insertions."""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]   # invariant: dp[i][j] = LCS of a[:i] and b[:j]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1    # match: extend diagonal
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # drop one char
    return dp[-1][-1]


def min_insertions_palindrome(s: str) -> int:  # LC 1312 — reduces to LCS
    # Fewest characters to insert anywhere to make s a palindrome.
    # The reduction is the whole problem: characters you never touch form a
    # palindromic subsequence, and the longest of those is LCS(s, reversed s).
    # Everything else must be paired by an insertion.
    # Naive: DP over intervals of s — correct and O(n^2), but it re-derives a
    # table LCS already gives you.
    # Real life: making a bead string symmetric by adding beads, never
    # removing — you keep the longest symmetric run and mirror the rest.
    return len(s) - longest_common_subsequence(s, s[::-1])


# --------------------------------------------------------------- Pattern 36
def edit_distance(a: str, b: str) -> int:  # LC 72
    """Fewest insert/delete/replace operations turning a into b.
    Same prefix grid as LC 1143, but now every cell has three predecessors,
    one per operation — replace comes from the diagonal, delete from above,
    insert from the left. The base row and column are pure delete/insert.

    Naive: BFS over all strings reachable by one edit — the branching factor
    is the alphabet size, and the same intermediate strings recur constantly.

    Real life: a spell checker scoring how far a typo is from a real word,
    counting the cheapest sequence of keystrokes that fixes it."""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]   # invariant: dp[i][j] = edits turning a[:i] into b[:j]
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
    """Paths across an m x n grid moving only right or down.
    Each cell is reached from above or from the left, so its count is their
    sum. Because a row only ever reads the row above and the cell to its left,
    one rolling array suffices — `row[j] += row[j-1]` IS the 2-D recurrence.

    Naive: recurse over both moves — exponential, revisiting each cell once
    per path through it. (A closed form C(m+n-2, m-1) also exists.)

    Real life: counting routes through a city grid where you may only walk
    east and south — each corner tallies the two corners feeding it."""
    row = [1] * n                          # invariant: row[j] = paths to column j of the row processed so far
    for _ in range(m - 1):
        for j in range(1, n):
            row[j] += row[j - 1]           # up + left
    return row[-1]


def min_path_sum(grid: list[list[int]]) -> int:  # LC 64
    """Cheapest top-left to bottom-right path moving only right or down.
    Same recurrence as LC 62 with min replacing sum. The grid is overwritten
    in place — safe only because a cell is read exactly once, by its right and
    lower neighbours, both visited after it.

    Naive: explore every path — exponential, when each cell has a single best
    arrival cost regardless of how the rest of the route continues.

    Real life: driving a toll grid where you may only head east or south,
    writing on each junction the cheapest fare that reaches it."""
    rows, cols = len(grid), len(grid[0])   # invariant: grid[r][c] becomes the cheapest cost to reach (r, c)
    for r in range(rows):
        for c in range(cols):
            if r or c:
                best_in = min(grid[r - 1][c] if r else float("inf"),
                              grid[r][c - 1] if c else float("inf"))
                grid[r][c] += best_in
    return grid[-1][-1]


def maximal_square(matrix: list[list[str]]) -> int:  # LC 221
    """Area of the largest all-1 square in a binary matrix.
    The constrained/unconstrained split again: dp holds the largest square
    ENDING at a cell, and the answer is tracked aside. A square of side k+1
    needs all three neighbours at k, so the WEAKEST of them caps you.

    Naive: for every cell and every side length, verify the square —
    O(rc * min(r,c)^2). The three-way min reuses the checks already done.

    Real life: laying the biggest square rug against a corner — how far it
    fits is set by whichever of the two walls and the diagonal runs out first."""
    rows, cols = len(matrix), len(matrix[0])
    dp = [[0] * (cols + 1) for _ in range(rows + 1)]   # invariant: dp[r+1][c+1] = side of the largest square ending at (r,c)
    side = 0                               # invariant: largest side seen anywhere so far
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == "1":
                dp[r + 1][c + 1] = 1 + min(dp[r][c], dp[r][c + 1], dp[r + 1][c])
                side = max(side, dp[r + 1][c + 1])
    return side * side


# --------------------------------------------------------------- Pattern 38
def max_coins(nums: list[int]) -> int:  # LC 312 Burst Balloons
    """Max coins from bursting balloons, each paying left * self * right.
    Asking which balloon pops FIRST fails — it changes who neighbours whom, so
    the two sides stay entangled. Ask which pops LAST instead: it still has
    walls i and j when it goes, and the sides become independent subproblems.

    Naive: try every burst order — n! sequences, with no shared substructure
    at all under the first-burst framing.

    Real life: demolishing a row of buildings where each payout depends on its
    standing neighbours — you plan by deciding what falls last, not first."""
    vals = [1] + nums + [1]                # invariant: sentinel walls so edge balloons have neighbours
    n = len(vals)
    dp = [[0] * n for _ in range(n)]       # invariant: dp[i][j] = best from the OPEN interval (i, j)
    for length in range(2, n):             # increasing interval length
        for i in range(n - length):
            j = i + length
            dp[i][j] = max(
                dp[i][k] + vals[i] * vals[k] * vals[j] + dp[k][j]
                for k in range(i + 1, j))  # k pops last, sees walls i and j
    return dp[0][n - 1]


# --------------------------------------------------------------- Pattern 39
def num_trees(n: int) -> int:  # LC 96 — Catalan
    """How many structurally distinct BSTs hold values 1..n?
    Fix the root: with k values below it, the left subtree has k shapes' worth
    of choices and the right n-1-k, independently — so multiply, then sum over
    every root. Only the SIZE of each side matters, never the actual values.

    Naive: build every BST and count — Catalan-many trees, each constructed
    node by node, when the count needs no trees at all.

    Real life: counting tournament bracket shapes — pick the final match, and
    the two halves are decided separately."""
    dp = [1] * (n + 1)                     # invariant: dp[k] = distinct BST shapes holding k values
    for total in range(2, n + 1):
        dp[total] = sum(dp[left] * dp[total - 1 - left] for left in range(total))
    return dp[n]


# --------------------------------------------------------------- Pattern 40
def length_of_lis(nums: list[int]) -> int:  # LC 300, O(n log n)
    """Length of the longest strictly increasing subsequence.
    Keep, per length k, the SMALLEST tail achieving it — a smaller tail is
    never worse, since anything extending a larger one extends it too. Those
    tails stay sorted, so each element binary-searches the slot it improves.

    Naive: O(n^2) DP asking, for each i, the best subsequence ending at i by
    scanning all j < i. The sorted tails replace that scan with a lookup.

    Real life: stacking rings by width where only the narrowest ring of each
    height matters — swapping in a narrower one never blocks a future ring."""
    tails: list[int] = []                  # invariant: tails[k] = smallest tail of an increasing subseq of length k+1; sorted
    for x in nums:
        lo = 0                             # invariant: lower_bound — leftmost tail >= x
        hi = len(tails)                    # hi exclusive; same template as 09_binary_search.lower_bound
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < x:
                lo = mid + 1               # mid is too small to be the slot
            else:
                hi = mid                   # mid could be the slot: keep it
        if lo == len(tails):
            tails.append(x)                # extends the longest subsequence
        else:
            tails[lo] = x                  # same length, better (smaller) tail
    return len(tails)


def max_envelopes(envelopes: list[list[int]]) -> int:  # LC 354 Russian Doll
    """Longest chain of envelopes each fitting strictly inside the next.
    Sorting by width reduces a 2-D nesting question to LIS on heights. The
    load-bearing detail is the tie-break: heights DESCENDING within one width,
    so two equal widths can never both be picked by the increasing scan.

    Naive: O(n^2) DP over pairs asking "does i fit inside j?" — correct, but
    it re-derives the ordering the sort establishes once.

    Real life: nesting suitcases sorted by footprint, where same-footprint
    cases are stacked tallest-first so you cannot fool yourself into pairing them."""
    envelopes.sort(key=lambda e: (e[0], -e[1]))   # invariant: width ascending, height descending within a width
    return length_of_lis([h for _, h in envelopes])


# --------------------------------------------------------------- Pattern 41
# Stock problems = one state machine with different edges.
def max_profit_one(prices: list[int]) -> int:  # LC 121
    # Best profit from a single buy and a later sell.
    # Same running-minimum argument as the copy in 08_greedy.py; it appears
    # here as the degenerate state machine — one buy, one sell, no loop back.
    # Naive: check every (buy, sell) pair — O(n^2).
    # Real life: watching a ticker and remembering only the lowest price seen.
    best, low = 0, prices[0]               # invariant: low = cheapest price strictly before today
    for p in prices[1:]:
        best = max(best, p - low)
        low = min(low, p)
    return best


def max_profit_unlimited(prices: list[int]) -> int:  # LC 122
    """Best profit with unlimited trades, holding at most one share.
    The template the rest of this section varies: two states, holding and not,
    each carrying the best cash reachable in it. Every day offers rest or
    transition, so `max(stay, switch)` is the whole recurrence.

    Naive: the telescoping sum in 08_greedy.py is shorter for THIS problem,
    but it does not extend to cooldowns or trade limits — this shape does.

    Real life: a trader who each morning either sits still or flips position,
    tracking only the best balance consistent with each posture."""
    hold, cash = -prices[0], 0             # invariant: best cash while holding a share / while flat
    for p in prices[1:]:
        hold = max(hold, cash - p)         # rest, or buy today
        cash = max(cash, hold + p)         # rest, or sell today
    return cash


def max_profit_cooldown(prices: list[int]) -> int:  # LC 309
    """Unlimited trades, but you may not buy the day after selling.
    The cooldown is a THIRD state, not a flag: selling lands in `cooling`,
    which can only rest into `cash`, and only `cash` may buy. Adding the
    state is what keeps every transition a plain max over the previous day.

    Naive: DP over (day, holding, days since sale) — the same thing with a
    redundant axis, since only one day of history ever matters.

    Real life: a trader barred from re-entering for one session after selling
    — the bench is a distinct place to be, not a note on being flat."""
    hold, cash, cooling = -prices[0], 0, 0   # invariant: best cash while holding / free to buy / benched today
    for p in prices[1:]:
        hold, cooling, cash = (max(hold, cash - p),  # buy needs a rested day
                               hold + p,             # selling triggers cooldown
                               max(cash, cooling))   # cooldown expires
    return max(cash, cooling)


def max_profit_k(k: int, prices: list[int]) -> int:  # LC 188
    """Best profit with at most k transactions.
    The trade budget becomes an axis: the same two states as LC 122, indexed
    by transactions used. hold[t] draws from cash[t-1] — buying is what spends
    a transaction — so the two arrays advance together each day.

    Naive: enumerate which k disjoint intervals to trade — combinatorial,
    when the budget only ever enters as "which row do I read from".

    Real life: a trading account capped at k round trips a year — you track
    your best balance separately for each number of trips already spent."""
    if not prices:
        return 0
    hold = [float("-inf")] * (k + 1)       # invariant: hold[t] = best cash holding a share, t buys spent
    cash = [0] * (k + 1)                   # invariant: cash[t] = best cash while flat, t buys spent
    for p in prices:
        for t in range(1, k + 1):
            hold[t] = max(hold[t], cash[t - 1] - p)
            cash[t] = max(cash[t], hold[t] + p)
    return cash[k]


if __name__ == "__main__":
    assert climb_stairs(5) == 8
    assert rob([2, 7, 9, 3, 1]) == 12
    assert rob_circular([2, 3, 2]) == 3
    assert num_decodings("226") == 3 and num_decodings("06") == 0   # leading zero decodes to nothing
    assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert max_product([2, 3, -2, 4]) == 6 and max_product([-2, 3, -4]) == 24
    assert max_subarray_circular([5, -3, 5]) == 10
    assert max_subarray_circular([-3, -2, -3]) == -2   # all negative: the complement would be empty
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
