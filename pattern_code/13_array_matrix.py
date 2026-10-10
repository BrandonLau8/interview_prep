"""Patterns 79-85: Array / Matrix Manipulation.

Core idea: index arithmetic and O(1)-space tricks — use the structure
(or the array itself) as your scratch space.
Run: python 13_array_matrix.py
"""


# --------------------------------------------------------------- Pattern 79
def rotate_image(matrix: list[list[int]]) -> None:  # LC 48
    """Rotate a square matrix 90 degrees clockwise, in place.
    A rotation is two reflections: transpose about the main diagonal, then
    reverse each row. Both are plain swaps, so the four-way cell cycle never
    arises. `c` starts at r+1 so no pair is transposed twice and undone.

    Naive: copy into a fresh matrix with dst[c][n-1-r] = src[r][c] — O(n^2)
    space, which the in-place requirement forbids.

    Real life: turning a photo by flipping it along the diagonal, then
    mirroring it left-to-right — two easy flips beat one awkward turn."""
    n = len(matrix)
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix:
        row.reverse()


def rotate_array(nums: list[int], k: int) -> None:  # LC 189
    """Rotate the array right by k, in place.
    Same composition trick as LC 48 in one dimension: reverse everything, then
    reverse each of the two blocks back. The whole-array reversal puts the two
    blocks on the right sides; the inner ones repair their internal order.

    Naive: rotate by one k times — O(nk). Copying to a new array is O(n)
    space, which the in-place requirement rules out.

    Real life: flipping a shelf of books end to end, then straightening each
    of the two sections — the sections have traded places."""
    def rev(lo: int, hi: int) -> None:
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo, hi = lo + 1, hi - 1
    k %= len(nums)                         # invariant: k in [0, n), so a full turn is a no-op
    rev(0, len(nums) - 1)
    rev(0, k - 1)
    rev(k, len(nums) - 1)


# --------------------------------------------------------------- Pattern 80
def spiral_order(matrix: list[list[int]]) -> list[int]:  # LC 54
    """Read a matrix in spiral order, outer ring inward.
    Four boundaries beat a direction-plus-turning-rule: consume one whole
    edge, retract that boundary, repeat. The two guards are the real content —
    on a single remaining row or column, the return legs would re-read cells.

    Naive: track a direction vector and a visited grid, turning on a wall —
    O(rc) extra space and the turn condition is easy to get subtly wrong.

    Real life: peeling an orange in one strip — each pass takes the whole of
    the current edge, and the fruit left behind is a smaller rectangle."""
    res: list[int] = []
    top, bottom = 0, len(matrix) - 1       # invariant: rows [top, bottom] are still unread
    left, right = 0, len(matrix[0]) - 1    # invariant: cols [left, right] are still unread
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
    """If a cell is 0, zero its whole row and column — in O(1) extra space.
    Row 0 and column 0 become the marker arrays, so the matrix stores its own
    bookkeeping. That creates one collision — matrix[0][0] would mean both —
    which `first_col_zero` resolves by holding the column's flag separately.

    Naive: two boolean arrays of size rows and cols — clear and correct, but
    O(r + c) space. Zeroing eagerly is worse: it corrupts cells not yet read.

    Real life: annotating a spreadsheet's own header row and column instead of
    keeping a separate list of what to clear."""
    rows, cols = len(matrix), len(matrix[0])
    first_col_zero = any(matrix[r][0] == 0 for r in range(rows))   # invariant: column 0's own flag, since matrix[0][0] is overloaded
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
    """Advance Conway's Game of Life one generation, in place.
    Every cell must read its neighbours' OLD states while writing its new one.
    Two bits per cell resolve it: bit 0 stays the old state throughout, bit 1
    accumulates the new one, and a final shift discards the past.

    Naive: copy the board and read from the copy — O(rc) space; updating in
    place without the encoding makes later cells read already-updated neighbours.

    Real life: pencilling next year's roster beside this year's on the same
    sheet, then rubbing out the old column once everyone has been assigned."""
    rows, cols = len(board), len(board[0])   # invariant: bit 0 = current generation, bit 1 = next
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
    """Product of all other elements, without division.
    Split the answer at i: everything left of i times everything right of it.
    Each side is a running product, so two sweeps in opposite directions
    suffice — and the output array carries the first sweep, costing no space.

    Naive: total product divided by nums[i] — banned, and it breaks on zeros
    anyway. Recomputing each product is O(n^2).

    Real life: crediting each member of a relay for everyone else's time by
    accumulating the running total from each end, never dividing."""
    n = len(nums)
    res = [1] * n                          # invariant: after sweep 1, res[i] = product strictly left of i
    prefix = 1                             # invariant: product of nums[0:i]
    for i in range(n):                     # first sweep: fold prefixes in
        res[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):         # second sweep: multiply suffixes
        res[i] *= suffix
        suffix *= nums[i]
    return res


def longest_mountain(arr: list[int]) -> int:  # LC 845 — same left/right split
    """Longest strictly-up-then-strictly-down run, peak included.
    Same two-sweep split as LC 238: each index asks one question of its left
    (how far does the climb reach back?) and one of its right. A peak is any
    index where BOTH are non-zero — the `and` is what forbids a flat plateau.

    Naive: for each index, walk outward in both directions — O(n^2), with the
    same slopes re-measured once per candidate peak.

    Real life: finding the longest hill on a walking route by noting, at each
    point, how long you have been climbing and how long you will descend."""
    n = len(arr)
    up = [0] * n                           # invariant: length of the strict climb ending at i
    down = [0] * n                         # invariant: length of the strict descent starting at i
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
    """Add one to a number held as a digit array.
    A carry stops at the first digit below 9, so the early return is the
    common case and the loop is the exception. Only all-nines carries past the
    top — and then the result is always 1 followed by zeros, never anything else.

    Naive: join to an int, add, split back — breaks as soon as the number
    exceeds the word size, which is why it is an array to begin with.

    Real life: clicking an odometer forward one — most clicks touch a single
    wheel, and only 999 rolls the whole row and needs a new column."""
    for i in range(len(digits) - 1, -1, -1):   # invariant: everything right of i has rolled to 0
        if digits[i] < 9:
            digits[i] += 1
            return digits                  # no carry: done early
        digits[i] = 0                      # 9 rolls over, carry continues
    return [1] + digits                    # carried out of the top: 999 -> 1000


def add_binary(a: str, b: str) -> str:  # LC 67
    # Sum of two binary strings, as a binary string.
    # Same schoolbook addition as add_two_numbers in 12_linked_list.py, base 2
    # instead of 10: `carry` in the loop condition folds the unequal lengths
    # and the final carry into one termination test.
    # Naive: int(a, 2) + int(b, 2) — sidesteps the arbitrary-width arithmetic
    # the question is checking.
    # Real life: adding two rows of on/off switches from the right.
    i, j, carry = len(a) - 1, len(b) - 1, 0   # invariant: carry is 0 or 1, owed to the next column
    out: list[str] = []
    while i >= 0 or j >= 0 or carry:
        total = carry + (i >= 0 and a[i] == "1") + (j >= 0 and b[j] == "1")
        out.append(str(total % 2))
        carry = total // 2
        i, j = i - 1, j - 1
    return "".join(reversed(out))


# --------------------------------------------------------------- Pattern 84
def merge_sorted_into(nums1: list[int], m: int, nums2: list[int], n: int) -> None:  # LC 88
    """Merge nums2 into nums1, which has exactly n slots of slack at the end.
    Filling forward would overwrite unread elements of nums1. Writing BACKWARD
    from the largest cannot: the write cursor always sits at or ahead of the
    read cursor, so the free space stays between them.

    Naive: append and sort — O((m+n) log(m+n)) on data already sorted; or
    shift elements right to make room, O(mn) of copying.

    Real life: merging two sorted stacks of paper into a tray by placing the
    largest sheet at the back first — you never disturb what you haven't read."""
    i, j, w = m - 1, n - 1, m + n - 1      # invariant: w >= i, so writes never clobber unread nums1 entries
    while j >= 0:                          # nums1 leftovers are already in place
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[w] = nums1[i]
            i -= 1
        else:
            nums1[w] = nums2[j]
            j -= 1
        w -= 1


def sorted_squares(nums: list[int]) -> list[int]:  # LC 977
    """Squares of a sorted array, sorted, in O(n).
    Squaring destroys the sortedness in the middle but not at the ends: the
    largest square is always at one end or the other. So converge two pointers
    and fill the output from the BACK, where the next value is always known.

    Naive: square then sort — O(n log n), discarding the order you were given.
    Filling forward fails: the smallest square is somewhere in the middle.

    Real life: two teams tied on distance from a start line — you rank from
    the furthest inward, and the furthest is always one of the two extremes."""
    res = [0] * len(nums)                  # invariant: res[w+1:] holds the largest squares, sorted
    lo, hi = 0, len(nums) - 1              # invariant: the next largest square is at lo or hi
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
    """Smallest positive integer absent from the array, O(n) time and O(1) space.
    The answer is always in [1, n+1], so every value that matters has a HOME
    index — v belongs at v-1 — and the array becomes its own hash table. The
    swap loop terminates because each swap puts one value permanently home.

    Naive: a set of the values, then scan 1, 2, 3... — O(n) space, which the
    problem forbids. Sorting is O(n log n).

    Real life: a cloakroom where every ticket has one matching hook — you
    rehang misplaced coats, then walk the row for the first empty hook."""
    n = len(nums)
    for i in range(n):                     # invariant: each completed swap seats one value at its home index
        # Swap nums[i] home (value v lives at index v-1) until settled.
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            home = nums[i] - 1
            nums[i], nums[home] = nums[home], nums[i]
    for i in range(n):
        if nums[i] != i + 1:               # first index not holding its value
            return i + 1
    return n + 1


def find_all_duplicates(nums: list[int]) -> list[int]:  # LC 442
    """Every value appearing twice, in O(1) extra space.
    Same home-index idea as LC 41, but marking instead of swapping: negate the
    slot a value belongs to, and finding it already negative proves a second
    sighting. `abs` on every read is what keeps the values themselves legible.

    Naive: a counter or seen-set — O(n) space to record visits the sign bit
    of each slot can hold for free.

    Real life: ticking names off a numbered register in pencil — a name whose
    box is already ticked has turned up twice."""
    res: list[int] = []                    # invariant: nums[i] < 0 means value i+1 has been seen
    for x in nums:
        home = abs(x) - 1
        if nums[home] < 0:
            res.append(abs(x))
        else:
            nums[home] = -nums[home]
    return res


def find_disappeared_numbers(nums: list[int]) -> list[int]:  # LC 448
    # Every value in [1, n] that never appears.
    # The complement of LC 442 with identical marking: after the pass, a slot
    # still positive was never visited, so its index+1 is missing.
    # Note -abs(...) rather than negation — a slot marked twice must stay
    # marked, which a plain flip would undo.
    # Naive: a seen-set then a scan — O(n) space for the same answer.
    # Real life: reading the register at the end for the boxes never ticked.
    for x in nums:                         # invariant: after this loop, nums[i] > 0 means i+1 never appeared
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
    assert plus_one([9, 9, 9]) == [1, 0, 0, 0]   # all nines: the carry leaves the array
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
