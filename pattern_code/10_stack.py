"""Patterns 64-69: Stack.

Core idea: LIFO matches "most recent unresolved thing" — open brackets,
pending operators, bars awaiting their boundary. Pairing across nesting or
"nearest X to the left/right" = stack.
Run: python 10_stack.py
"""


# --------------------------------------------------------------- Pattern 64
def is_valid_parentheses(s: str) -> bool:  # LC 20
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False               # closer must match MOST RECENT opener
        else:
            stack.append(ch)
    return not stack


def min_add_to_make_valid(s: str) -> int:  # LC 921
    opened = unmatched_closers = 0         # the "stack" is just a counter here
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
    res = [0] * len(temps)
    stack: list[int] = []                  # indices, temps decreasing
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()                # today is j's next-warmer day
            res[j] = i - j
        stack.append(i)
    return res                             # survivors never got an answer: 0


def next_greater_circular(nums: list[int]) -> list[int]:  # LC 503
    n = len(nums)
    res = [-1] * n
    stack: list[int] = []
    for i in range(2 * n):                 # circular = iterate twice
        while stack and nums[stack[-1]] < nums[i % n]:
            res[stack.pop()] = nums[i % n]
        if i < n:
            stack.append(i)
    return res


def remove_k_digits(num: str, k: int) -> str:  # LC 402
    # Lexicographic greed: pop any digit bigger than the incoming one
    # while deletions remain — keeps the prefix as small as possible.
    stack: list[str] = []
    for d in num:
        while stack and k and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    return "".join(stack[:len(stack) - k]).lstrip("0") or "0"


def sum_subarray_mins(arr: list[int]) -> int:  # LC 907
    # Contribution trick: each element is the min of (left span * right span)
    # subarrays; monotonic stack finds both spans in one pass.
    MOD = 10**9 + 7
    stack: list[int] = []
    total = 0
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
    stack: list[int] = []
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
    # Commit +/- lazily; apply */ immediately to the held previous term.
    stack: list[int] = []
    num, op = 0, "+"
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
    # '(' snapshots (result, sign) — the OUTER context — onto the stack.
    result, sign, num = 0, 1, 0
    stack: list[int] = []
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
    # Entering a scope pushes context; leaving pops and merges.
    stack: list[tuple[str, int]] = []
    cur, num = "", 0
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
    stack: list[str] = []
    for part in path.split("/"):
        if part == "..":
            if stack:
                stack.pop()
        elif part and part != ".":
            stack.append(part)
    return "/" + "/".join(stack)


def asteroid_collision(asteroids: list[int]) -> list[int]:  # LC 735
    stack: list[int] = []                  # survivors so far
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
    """Each frame is self-describing: it stores the min AS OF its push.
    Popping automatically restores history."""

    def __init__(self):
        self.stack: list[tuple[int, int]] = []   # (value, min at this time)

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
    # A bar's best rectangle spans to the nearest SHORTER bar each side —
    # exactly what an increasing stack discovers as it pops.
    stack: list[int] = []                  # indices, heights increasing
    best = 0
    for i in range(len(heights) + 1):      # sentinel 0 flushes the stack
        h = heights[i] if i < len(heights) else 0
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1   # nearest shorter on the left
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best


def maximal_rectangle(matrix: list[list[str]]) -> int:  # LC 85
    # Each row = floor of a histogram of consecutive 1s above; run LC 84 per row.
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
    assert remove_k_digits("10200", 1) == "200"
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
