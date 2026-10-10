"""Patterns 64-69: Stack.

Core idea: LIFO matches "most recent unresolved thing" — open brackets,
pending operators, bars awaiting their boundary. Pairing across nesting or
"nearest X to the left/right" = stack.
Run: python 10_stack.py
"""


# --------------------------------------------------------------- Pattern 64
def is_valid_parentheses(s: str) -> bool:  # LC 20
    """Are the brackets balanced and correctly nested?
    A closer can only match the MOST RECENT unclosed opener, which is the
    definition of LIFO — so the stack isn't an optimization, it's the problem
    restated. Counting alone fails: "([)]" has equal counts and is invalid.

    Naive: repeatedly delete adjacent matching pairs until nothing changes —
    O(n^2) rescans of a string the stack settles in one pass.

    Real life: a stack of nested Russian dolls — the one you close must be
    the one you most recently opened, or the halves don't fit."""
    pairs = {")": "(", "]": "[", "}": "{"}   # invariant: closer -> the opener it demands
    stack: list[str] = []                  # invariant: openers still unclosed, innermost last
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False               # closer must match MOST RECENT opener
        else:
            stack.append(ch)
    return not stack


def min_add_to_make_valid(s: str) -> int:  # LC 921
    """Fewest parentheses to insert to make the string valid.
    With ONE bracket type the stack's contents carry no information beyond
    their count — every entry is "(" — so a counter replaces it. Popping when
    empty is the signal that a "(" must be inserted before this point.

    Naive: run LC 20's stack and count failures — same answer, but it stores
    a stack of identical symbols to learn a number.

    Real life: tallying how many doors you left open and how many you tried
    to close that were never open — the repairs needed are the two sums."""
    opened = unmatched_closers = 0         # invariant: openers still unclosed / closers that found nothing
    for ch in s:
        if ch == "(":
            opened += 1
        elif opened:
            opened -= 1
        else:
            unmatched_closers += 1         # pop from empty = must insert a (
    return opened + unmatched_closers


# --------------------------------------------------------------- Pattern 65
# Monotonic stack: a new larger element ANSWERS every smaller one waiting.
def daily_temperatures(temps: list[int]) -> list[int]:  # LC 739
    """Days until a warmer temperature, per day; 0 if none comes.
    One warm day answers EVERY colder day still waiting, in one sweep — that
    is what makes the monotonic stack linear. A day only waits while colder
    days sit above it, so the stack stays decreasing by construction.

    Naive: for each day, scan forward for the next warmer one — O(n^2), and
    that scan repeats work the stack does once for all pending days.

    Real life: a queue of people waiting for someone taller to walk past —
    when a tall person arrives, everyone shorter gets their answer at once."""
    res = [0] * len(temps)                 # invariant: 0 until a warmer day is found; survivors keep 0
    stack: list[int] = []                  # invariant: indices awaiting an answer, temperatures decreasing
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()                # today is j's next-warmer day
            res[j] = i - j
        stack.append(i)
    return res                             # survivors never got an answer: 0


def next_greater_circular(nums: list[int]) -> list[int]:  # LC 503
    """Next greater element for each position, wrapping around the end.
    Same monotonic stack as LC 739; the circle is handled by walking the array
    twice and taking i % n. Only the first pass PUSHES — the second exists
    solely to answer indices still waiting, never to create new waiters.

    Naive: for each element scan the whole circle — O(n^2), re-walking the
    same wrap-around for every unanswered index.

    Real life: a carousel of bidders where each waits for a higher bid — one
    more full turn is enough to know nobody will outbid you."""
    n = len(nums)
    res = [-1] * n                         # invariant: -1 until answered; never answered = no greater exists
    stack: list[int] = []                  # invariant: indices awaiting an answer, values decreasing
    for i in range(2 * n):                 # circular = iterate twice
        while stack and nums[stack[-1]] < nums[i % n]:
            res[stack.pop()] = nums[i % n]
        if i < n:
            stack.append(i)
    return res


def remove_k_digits(num: str, k: int) -> str:  # LC 402
    """Smallest number obtainable by deleting exactly k digits, order kept.
    Earlier digits dominate lexicographically, so a digit larger than the one
    arriving is always worth deleting while deletions remain. That is a
    monotonic stack — the result is kept non-decreasing wherever k allows.

    Naive: try all C(n, k) deletion sets and compare — combinatorial, when
    the leftmost improvable digit is decidable on sight.

    Real life: crossing out digits on a price tag to make the number as small
    as possible — you strike a big digit the moment a smaller one follows it."""
    stack: list[str] = []                  # invariant: kept digits, non-decreasing while deletions remain
    for d in num:
        while stack and k and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    return "".join(stack[:len(stack) - k]).lstrip("0") or "0"


def sum_subarray_mins(arr: list[int]) -> int:  # LC 907
    """Sum of min(subarray) over every subarray, modulo 1e9+7.
    Invert the loop: instead of asking each subarray for its min, ask each
    element how many subarrays it MINIMIZES — that count is (span left) *
    (span right), and both spans are what a monotonic stack pops out.

    Naive: enumerate all O(n^2) subarrays tracking a running min — quadratic,
    where the contribution view makes each element's total a single product.

    Real life: costing a fleet by its weakest vehicle — rather than pricing
    every convoy, ask each vehicle how many convoys it is the weak link in."""
    MOD = 10**9 + 7
    stack: list[int] = []                  # invariant: indices with increasing values (>= pops one side only)
    total = 0                              # invariant: contributions of all elements popped so far
    for i in range(len(arr) + 1):          # sentinel flush at the end
        cur = arr[i] if i < len(arr) else float("-inf")
        while stack and arr[stack[-1]] >= cur:   # >= one side only: no double count
            j = stack.pop()
            left = stack[-1] if stack else -1
            total += arr[j] * (j - left) * (i - j)
        stack.append(i)
    return total % MOD


# --------------------------------------------------------------- Pattern 66
def eval_rpn(tokens: list[str]) -> int:  # LC 150
    """Evaluate an expression in reverse Polish notation.
    RPN exists precisely so no precedence or parens are needed: an operator's
    arguments are always the two most recent unconsumed values. Popping order
    matters — b comes off first, so `a - b` needs b popped before a.

    Naive: convert to infix and parse with precedence rules — reintroducing
    exactly the ambiguity RPN was designed to remove.

    Real life: an old HP calculator where you key both numbers then the
    operation — the display always holds the values still awaiting an operator."""
    stack: list[int] = []                  # invariant: operands not yet consumed by an operator
    ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
           "*": lambda a, b: a * b, "/": lambda a, b: int(a / b)}  # trunc to 0
    for tok in tokens:
        if tok in ops:
            b, a = stack.pop(), stack.pop()
            stack.append(ops[tok](a, b))
        else:
            stack.append(int(tok))
    return stack[0]


def calculate_ii(s: str) -> int:  # LC 227 (+ - * / no parens)
    """Evaluate a + - * / expression with precedence but no parentheses.
    Precedence handled without a parser: push +/- terms unresolved, but apply
    */ immediately to the term on top, because a higher-precedence operator
    can always finish before its neighbours. Summing at the end resolves +/-.

    Naive: two passes, one collapsing */ then one summing — the stack does
    both at once, and generalizes to the parenthesized LC 224 below.

    Real life: totting up a receipt where quantities multiply their unit price
    on the spot, but the running total is only added up at the till."""
    stack: list[int] = []                  # invariant: signed terms awaiting a final sum
    num, op = 0, "+"                       # invariant: op is the operator PRECEDING num
    for i, ch in enumerate(s):
        if ch.isdigit():
            num = num * 10 + int(ch)
        if ch in "+-*/" or i == len(s) - 1:
            if op == "+":
                stack.append(num)
            elif op == "-":
                stack.append(-num)
            elif op == "*":
                stack.append(stack.pop() * num)
            else:
                stack.append(int(stack.pop() / num))
            num, op = 0, ch
    return sum(stack)


def calculate_i(s: str) -> int:  # LC 224 (+ - and parens)
    """Evaluate a + - expression containing parentheses.
    A '(' means "start a fresh sum", so the stack stores what to RESUME with:
    the outer result and the sign in front of the group. On ')' the inner sum
    is folded back in — which is why the pops read sign first, then result.

    Naive: recursive descent parsing — the same idea with the interpreter's
    call stack instead of an explicit one, and harder to write under pressure.

    Real life: totalling a bill with bracketed sub-totals — you set the
    running figure aside, add up the bracket, then bring the two together."""
    result, sign, num = 0, 1, 0            # invariant: result = sum committed at this nesting level
    stack: list[int] = []                  # invariant: pairs of (outer result, sign before the group)
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch in "+-":
            result += sign * num
            num, sign = 0, 1 if ch == "+" else -1
        elif ch == "(":
            stack.append(result)
            stack.append(sign)
            result, sign = 0, 1
        elif ch == ")":
            result += sign * num
            num = 0
            result = stack.pop() * result + stack.pop()   # sign, then outer
    return result + sign * num


# --------------------------------------------------------------- Pattern 67
def decode_string(s: str) -> str:  # LC 394
    """Expand strings like 3[a2[c]] into accaccacc.
    Same shape as LC 224 with strings instead of sums: '[' snapshots the outer
    context and starts fresh, ']' multiplies the inner result and rejoins it.
    The multiplier must be pushed WITH the outer string — it belongs to the group.

    Naive: find the innermost bracket by regex and expand repeatedly — O(n^2)
    rescans of a string one left-to-right pass already resolves.

    Real life: reading nested knitting instructions — you park the row so far,
    work the bracketed motif, repeat it, then carry on where you left off."""
    stack: list[tuple[str, int]] = []      # invariant: (string before this group, its repeat count)
    cur, num = "", 0                       # invariant: cur = text built at this nesting level
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((cur, num))       # snapshot outer string + multiplier
            cur, num = "", 0
        elif ch == "]":
            outer, k = stack.pop()
            cur = outer + cur * k
        else:
            cur += ch
    return cur


def simplify_path(path: str) -> str:  # LC 71
    """Canonicalize a Unix absolute path.
    ".." undoes the most recent directory entered, which is a pop — so the
    stack of surviving components IS the answer, not a means to it. The edge
    cases are all "pop from empty": ".." at root stays at root.

    Naive: rewrite the string with repeated substitutions until stable —
    O(n^2) and easy to get wrong on "..." or empty components.

    Real life: walking a corridor and doubling back — the rooms you are
    actually inside are whatever remains after each backtrack cancels one."""
    stack: list[str] = []                  # invariant: directory names currently entered, root-first
    for part in path.split("/"):
        if part == "..":
            if stack:
                stack.pop()
        elif part and part != ".":
            stack.append(part)
    return "/" + "/".join(stack)


def asteroid_collision(asteroids: list[int]) -> list[int]:  # LC 735
    """Surviving asteroids; positive move right, negative left, bigger wins.
    Only one arrangement collides — a right-mover with a left-mover arriving
    after it — so the test is exactly `stack[-1] > 0 and a < 0`. A newcomer
    may destroy several survivors, hence the loop rather than one comparison.

    Naive: simulate positions over time — unbounded steps for a question
    settled by the order alone.

    Real life: a one-lane bridge where oncoming trucks meet — the lighter one
    is pushed off, and the winner keeps meeting whoever is next in line."""
    stack: list[int] = []                  # invariant: survivors so far, in original order
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:  # only ->  <- collide
            if stack[-1] < -a:
                stack.pop()                # top explodes, keep fighting
            elif stack[-1] == -a:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(a)
    return stack


# --------------------------------------------------------------- Pattern 68
class MinStack:  # LC 155
    """Stack with push, pop, top and get_min all in O(1).
    Each frame is self-describing: it stores the minimum AS OF its own push.
    That makes popping free — history is restored automatically, with no
    recomputation, because the frame below already recorded its own answer.

    Naive: one min variable survives pushes but not pops — removing the
    minimum leaves nothing that knows the old one; rescanning is O(n).

    Real life: writing the current record score on every page as you fill a
    logbook — tear a page out and the one beneath still shows the old record."""

    def __init__(self):
        self.stack: list[tuple[int, int]] = []   # invariant: (value, min of everything at or below this frame)

    def push(self, val: int) -> None:
        cur_min = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, cur_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def get_min(self) -> int:
        return self.stack[-1][1]


# --------------------------------------------------------------- Pattern 69
def largest_rectangle_area(heights: list[int]) -> int:  # LC 84
    """Largest rectangle fitting under a histogram.
    Fix the rectangle's HEIGHT to some bar: it then stretches until the first
    shorter bar on each side. An increasing stack discovers both boundaries
    on the pop — the popper is the right wall, the new top is the left one.

    Naive: for every pair of bars, take the min height across the span —
    O(n^2) or O(n^3), re-deriving boundaries the stack already holds.

    Real life: hanging the widest possible banner at a fixed height along a
    fence of uneven posts — a shorter post on either side ends the run."""
    stack: list[int] = []                  # invariant: indices with strictly increasing heights
    best = 0                               # invariant: largest rectangle whose height-bar has been popped
    for i in range(len(heights) + 1):      # sentinel 0 flushes the stack
        h = heights[i] if i < len(heights) else 0
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1   # nearest shorter on the left
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best


def maximal_rectangle(matrix: list[list[str]]) -> int:  # LC 85
    """Largest all-1 rectangle in a binary matrix.
    Every rectangle sits on some row, so treat each row as the floor of a
    histogram whose bars are the runs of 1s above it. That reduces a 2-D
    search to r calls of LC 84 — the reduction is the entire problem.

    Naive: try every pair of corners and verify the rectangle —
    O(r^2 c^2 * rc). The rolling heights reuse each row's work for the next.

    Real life: finding the biggest clear floor area in a warehouse by
    measuring, at each aisle, how far back the shelving stays empty."""
    if not matrix:
        return 0
    heights = [0] * len(matrix[0])
    best = 0
    for row in matrix:
        for c, ch in enumerate(row):
            heights[c] = heights[c] + 1 if ch == "1" else 0
        best = max(best, largest_rectangle_area(heights))
    return best


if __name__ == "__main__":
    assert is_valid_parentheses("()[]{}") and not is_valid_parentheses("(]")
    assert min_add_to_make_valid("())") == 1 and min_add_to_make_valid("(((") == 3
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == \
        [1, 1, 4, 2, 1, 1, 0, 0]
    assert next_greater_circular([1, 2, 1]) == [2, -1, 2]
    assert remove_k_digits("1432219", 3) == "1219"
    assert remove_k_digits("10200", 1) == "200"   # leading zeros stripped after the deletions
    assert sum_subarray_mins([3, 1, 2, 4]) == 17
    assert eval_rpn(["2", "1", "+", "3", "*"]) == 9
    assert calculate_ii("3+2*2") == 7 and calculate_ii(" 3/2 ") == 1
    assert calculate_i("(1+(4+5+2)-3)+(6+8)") == 23
    assert decode_string("3[a2[c]]") == "accaccacc"
    assert simplify_path("/a/./b/../../c/") == "/c"
    assert asteroid_collision([10, 2, -5]) == [10]
    ms = MinStack()
    ms.push(-2); ms.push(0); ms.push(-3)
    assert ms.get_min() == -3
    ms.pop()
    assert ms.top() == 0 and ms.get_min() == -2
    assert largest_rectangle_area([2, 1, 5, 6, 2, 3]) == 10
    assert maximal_rectangle([list("10100"), list("10111"),
                              list("11111"), list("10010")]) == 6
    print("10_stack: all checks passed")
