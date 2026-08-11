"""Patterns 79-85: Array / Matrix Manipulation.

Core idea: index arithmetic and O(1)-space tricks — use the structure
(or the array itself) as your scratch space.
Run: python 13_array_matrix.py
"""


# --------------------------------------------------------------- Pattern 79
def rotate_image(matrix: list[list[int]]) -> None:  # LC 48
    # Compose reflections: rotate 90 clockwise = transpose + reverse rows.
    n = len(matrix)
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix:
        row.reverse()


def rotate_array(nums: list[int], k: int) -> None:  # LC 189
    # Reverse whole, reverse first k, reverse rest.
    def rev(lo: int, hi: int) -> None:
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo, hi = lo + 1, hi - 1
    k %= len(nums)
    rev(0, len(nums) - 1)
    rev(0, k - 1)
    rev(k, len(nums) - 1)


# --------------------------------------------------------------- Pattern 80
def spiral_order(matrix: list[list[int]]) -> list[int]:  # LC 54
    # Four boundaries; consume a full edge, shrink it, stop when they cross.
    res: list[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            res.append(matrix[r][right])
        right -= 1
        if top <= bottom:                  # guard: single row remaining
            for c in range(right, left - 1, -1):
                res.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:                  # guard: single column remaining
            for r in range(bottom, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    return res


# --------------------------------------------------------------- Pattern 81
def set_zeroes(matrix: list[list[int]]) -> None:  # LC 73
    # Repurpose row 0 / col 0 as the marker arrays (O(1) extra space).
    rows, cols = len(matrix), len(matrix[0])
    first_col_zero = any(matrix[r][0] == 0 for r in range(rows))
    for r in range(rows):
        for c in range(1, cols):
            if matrix[r][c] == 0:
                matrix[r][0] = 0           # mark this row...
                matrix[0][c] = 0           # ...and this column
    for r in range(rows - 1, -1, -1):      # bottom-up: don't clobber markers
        for c in range(cols - 1, 0, -1):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0
        if first_col_zero:
            matrix[r][0] = 0


def game_of_life(board: list[list[int]]) -> None:  # LC 289
    # Encode old AND new state in one cell: bit 0 = now, bit 1 = next.
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            live = sum(board[nr][nc] & 1   # bit 0 still holds the OLD state
                       for nr in range(r - 1, r + 2)
                       for nc in range(c - 1, c + 2)
                       if (nr, nc) != (r, c) and 0 <= nr < rows and 0 <= nc < cols)
            if board[r][c] & 1:
                if live in (2, 3):
                    board[r][c] |= 2       # survives into bit 1
            elif live == 3:
                board[r][c] |= 2           # birth
    for r in range(rows):
        for c in range(cols):
            board[r][c] >>= 1              # decode: keep only the NEXT state


# --------------------------------------------------------------- Pattern 82
def product_except_self(nums: list[int]) -> list[int]:  # LC 238
    # answer[i] = (product of everything left of i) * (right of i).
    n = len(nums)
    res = [1] * n
    prefix = 1
    for i in range(n):                     # first sweep: fold prefixes in
        res[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):         # second sweep: multiply suffixes
        res[i] *= suffix
        suffix *= nums[i]
    return res


def longest_mountain(arr: list[int]) -> int:  # LC 845 — same left/right split
    n = len(arr)
    up = [0] * n                           # rising run ending at i
    down = [0] * n                         # falling run starting at i
    for i in range(1, n):
        if arr[i] > arr[i - 1]:
            up[i] = up[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if arr[i] > arr[i + 1]:
            down[i] = down[i + 1] + 1
    return max((up[i] + down[i] + 1 for i in range(n) if up[i] and down[i]),
               default=0)


# --------------------------------------------------------------- Pattern 83
def plus_one(digits: list[int]) -> list[int]:  # LC 66
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits                  # no carry: done early
        digits[i] = 0                      # 9 rolls over, carry continues
    return [1] + digits                    # carried out of the top: 999 -> 1000


def add_binary(a: str, b: str) -> str:  # LC 67
    i, j, carry = len(a) - 1, len(b) - 1, 0
    out: list[str] = []
    while i >= 0 or j >= 0 or carry:
        total = carry + (i >= 0 and a[i] == "1") + (j >= 0 and b[j] == "1")
        out.append(str(total % 2))
        carry = total // 2
        i, j = i - 1, j - 1
    return "".join(reversed(out))


# --------------------------------------------------------------- Pattern 84
def merge_sorted_into(nums1: list[int], m: int, nums2: list[int], n: int) -> None:  # LC 88
    # Write BACKWARD from the largest: never collides with unread elements.
    i, j, w = m - 1, n - 1, m + n - 1
    while j >= 0:                          # nums1 leftovers are already in place
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[w] = nums1[i]
            i -= 1
        else:
            nums1[w] = nums2[j]
            j -= 1
        w -= 1


def sorted_squares(nums: list[int]) -> list[int]:  # LC 977
    # Largest square is at one END of a sorted array; fill output from the back.
    res = [0] * len(nums)
    lo, hi = 0, len(nums) - 1
    for w in range(len(nums) - 1, -1, -1):
        if abs(nums[lo]) > abs(nums[hi]):
            res[w] = nums[lo] ** 2
            lo += 1
        else:
            res[w] = nums[hi] ** 2
            hi -= 1
    return res


# --------------------------------------------------------------- Pattern 85
# Values in [1..n]: every value has a HOME index — the array is its own
# hash table.
def first_missing_positive(nums: list[int]) -> int:  # LC 41
    n = len(nums)
    for i in range(n):
        # Swap nums[i] home (value v lives at index v-1) until settled.
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            home = nums[i] - 1
            nums[i], nums[home] = nums[home], nums[i]
    for i in range(n):
        if nums[i] != i + 1:               # first index not holding its value
            return i + 1
    return n + 1


def find_all_duplicates(nums: list[int]) -> list[int]:  # LC 442
    # Mark presence by negating the value's home slot; a second visit finds
    # it already negative.
    res: list[int] = []
    for x in nums:
        home = abs(x) - 1
        if nums[home] < 0:
            res.append(abs(x))
        else:
            nums[home] = -nums[home]
    return res


def find_disappeared_numbers(nums: list[int]) -> list[int]:  # LC 448
    for x in nums:
        home = abs(x) - 1
        nums[home] = -abs(nums[home])
    return [i + 1 for i, x in enumerate(nums) if x > 0]   # never visited


if __name__ == "__main__":
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    rotate_image(m)
    assert m == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    a = [1, 2, 3, 4, 5, 6, 7]
    rotate_array(a, 3)
    assert a == [5, 6, 7, 1, 2, 3, 4]
    assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == \
        [1, 2, 3, 6, 9, 8, 7, 4, 5]
    z = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    set_zeroes(z)
    assert z == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    g = [[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]]
    game_of_life(g)
    assert g == [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert longest_mountain([2, 1, 4, 7, 3, 2, 5]) == 5
    assert plus_one([9, 9, 9]) == [1, 0, 0, 0]
    assert add_binary("1010", "1011") == "10101"
    n1 = [1, 2, 3, 0, 0, 0]
    merge_sorted_into(n1, 3, [2, 5, 6], 3)
    assert n1 == [1, 2, 2, 3, 5, 6]
    assert sorted_squares([-4, -1, 0, 3, 10]) == [0, 1, 9, 16, 100]
    assert first_missing_positive([3, 4, -1, 1]) == 2
    assert first_missing_positive([1, 2, 0]) == 3
    assert find_all_duplicates([4, 3, 2, 7, 8, 2, 3, 1]) == [2, 3]
    assert find_disappeared_numbers([4, 3, 2, 7, 8, 2, 3, 1]) == [5, 6]
    print("13_array_matrix: all checks passed")
