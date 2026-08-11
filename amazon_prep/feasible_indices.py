"""
Feasible Indices After Prefix/Suffix Reduction (Amazon OA, Medium)

Two moves on an array of distinct integers:
  Move A: pick any prefix; only its MINIMUM survives, the rest are deleted.
  Move B: pick any suffix; only its MAXIMUM survives, the rest are deleted.
Apply the moves any number of times, in any order. For each index, output 1 if
that element can be the last one remaining, else 0. Return the flags as a
string.

Core insight
------------
Index i is feasible iff nothing before it is smaller OR nothing after it is
bigger — a prefix-minimum or a suffix-maximum.

Why: to delete the elements in front of you, some Move A must cover them. But
that prefix also covers you, and the move keeps only the minimum, so a smaller
element in front survives instead of you. Symmetrically, a bigger element
behind you survives every Move B that would clear the tail. Smaller-in-front
AND bigger-behind is a permanent trap; missing either one gives you a legal
clearing sequence.

Complexity: O(n) time, O(1) extra space beyond the output. Two passes.

More examples, as reference:
    arr             out     why
    [5]             "1"     the only element, both min and max
    [1, 2, 3]       "101"   2 is trapped: 1 in front is smaller, 3 behind is
                            bigger
    [3, 2, 1]       "111"   descending, so every element is a prefix minimum
    [2, 1, 3]       "111"   2 is a prefix-min, 1 a prefix-min, 3 a suffix-max
    [1, 2, 4, 3]    "1011"  2 has 1 in front and 4 behind -> trapped
"""

from typing import List

"""
1 2 4 3
0 0 0 0
1 0 0 0
0 0 1 1  
"""
def feasible_indices(arr: List[int]) -> str:
    """Return a '0'/'1' string flagging which indices can survive alone."""
    n = len(arr)
    res = [0] * n

    # Pass 1: prefix minima. Invariant: `run` is min(arr[0..i]) after the
    # update, so arr[i] == run means nobody in front of i is smaller.
    run = float("inf")
    for i in range(n):
        run = min(run, arr[i])
        if arr[i] == run:
            res[i] = 1

    # Pass 2: suffix maxima. Invariant: `run` is max(arr[i..n-1]).
    run = float("-inf")
    for i in range(n - 1, -1, -1):
        run = max(run, arr[i])
        if arr[i] == run:
            res[i] = 1

    return "".join(map(str, res))



if __name__ == "__main__":
    # Single element: it is simultaneously the global min and the global max.
    assert feasible_indices([5]) == "1"

    # Sorted ascending: only arr[0] is a prefix min and only arr[-1] is a
    # suffix max, so everything in the middle is trapped.
    assert feasible_indices([1, 2, 3]) == "101"

    # Sorted descending: arr[0] is the global max, and every arr[i] is the min
    # of arr[0..i], so all are feasible.
    assert feasible_indices([3, 2, 1]) == "111"

    # The trapped case: 2 has 1 in front (smaller) and 4 behind (bigger).
    assert feasible_indices([1, 2, 4, 3]) == "1011"

    # The global min and global max are always feasible.
    flags = feasible_indices([7, 3, 9, 1, 8])
    assert flags[3] == "1"  # value 1, the global minimum
    assert flags[2] == "1"  # value 9, the global maximum

    # The answer is never all zeros.
    assert "1" in feasible_indices([4, 1, 5, 2, 6, 3])

    # Empty input degrades to the empty string rather than crashing.
    assert feasible_indices([]) == ""

    print("all tests passed")
