"""Patterns 1-7: Two Pointers.

Core idea: two indices moving with purpose replace a nested loop, because some
structural fact (sortedness, symmetry, a one-pass invariant) proves which
pointer is safe to move — skipped pairs never need revisiting.
Run: python 01_two_pointers.py
"""


# ---------------------------------------------------------------- Pattern 1
# Converging: sorted input, each step PROVABLY eliminates one element.
def two_sum_sorted(nums: list[int], target: int) -> list[int]:  # LC 167
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return [lo + 1, hi + 1]
        if s < target:
            lo += 1   # nums[lo] can't pair with anything (hi was its best shot)
        else:
            hi -= 1   # nums[hi] can't pair with anything (lo was its best shot)
    return []


def three_sum(nums: list[int]) -> list[list[int]]:  # LC 15
    # Sort, fix one element, converge on the remaining pair.
    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:  # skip duplicate anchors
            continue
        if nums[i] > 0:                       # smallest element positive -> done
            break
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                res.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                while lo < hi and nums[lo] == nums[lo - 1]:  # skip dup pairs
                    lo += 1
                hi -= 1
    return res


def max_area(height: list[int]) -> int:  # LC 11
    # The SHORTER wall is the bottleneck: moving the taller wall can only
    # shrink width without raising the bottleneck -> always move the shorter.
    lo, hi, best = 0, len(height) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(height[lo], height[hi]))
        if height[lo] < height[hi]:
            lo += 1
        else:
            hi -= 1
    return best


# ---------------------------------------------------------------- Pattern 2
# Fast & Slow: on a cycle, a 2x runner must lap a 1x runner.
class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def has_cycle(head: ListNode | None) -> bool:  # LC 141
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False


def find_duplicate(nums: list[int]) -> int:  # LC 287
    # n+1 values in [1..n]: treat i -> nums[i] as a linked list; the duplicate
    # value is the node two "pointers" enter -> the cycle entrance.
    slow = fast = nums[0]
    while True:                       # phase 1: meet inside the cycle
        slow, fast = nums[slow], nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]                    # phase 2: both 1x from start & meeting
    while slow != fast:               # they meet exactly at the entrance
        slow, fast = nums[slow], nums[fast]
    return slow


# ---------------------------------------------------------------- Pattern 3
# Fixed separation: a head start of n converts "n from the end" into
# "when the leader hits the end".
def remove_nth_from_end(head: ListNode, n: int) -> ListNode | None:  # LC 19
    dummy = ListNode(0, head)
    lead = follow = dummy
    for _ in range(n + 1):            # +1 so follow stops BEFORE the target
        lead = lead.next
    while lead:
        lead, follow = lead.next, follow.next
    follow.next = follow.next.next
    return dummy.next


def middle_node(head: ListNode) -> ListNode:  # LC 876
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow


# ---------------------------------------------------------------- Pattern 4
# Reader/writer: invariant — [0, write) is always the finished answer.
def remove_duplicates(nums: list[int]) -> int:  # LC 26
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write


def move_zeroes(nums: list[int]) -> None:  # LC 283
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1


def sort_colors(nums: list[int]) -> None:  # LC 75, Dutch national flag
    # Three regions: [0,lo)=0s  [lo,mid)=1s  (hi,end]=2s;  [mid,hi] unknown.
    lo, mid, hi = 0, 0, len(nums) - 1
    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1                   # mid NOT advanced: swapped-in val unknown


# ---------------------------------------------------------------- Pattern 5
# Special characters: scan BACKWARDS so each '#' tells you what it kills.
def backspace_compare(s: str, t: str) -> bool:  # LC 844, O(1) space
    def chars(x: str):
        skip, i = 0, len(x) - 1
        while i >= 0:
            if x[i] == '#':
                skip += 1
            elif skip:
                skip -= 1
            else:
                yield x[i]
            i -= 1
        yield None                    # sentinel: both exhausted together
    return all(a == b for a, b in zip(chars(s), chars(t)))


# ---------------------------------------------------------------- Pattern 6
# Expand from center: 2n-1 centers; each expansion step certifies a
# palindrome for free.
def longest_palindrome(s: str) -> str:  # LC 5
    best = ""
    for center in range(2 * len(s) - 1):
        lo, hi = center // 2, (center + 1) // 2   # odd & even centers
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo, hi = lo - 1, hi + 1
        if hi - lo - 1 > len(best):
            best = s[lo + 1:hi]
    return best


def count_palindromic_substrings(s: str) -> int:  # LC 647
    count = 0
    for center in range(2 * len(s) - 1):
        lo, hi = center // 2, (center + 1) // 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            count += 1
            lo, hi = lo - 1, hi + 1
    return count


# ---------------------------------------------------------------- Pattern 7
# Composite reversal: reverse the whole, then re-reverse the parts.
def reverse_words(s: str) -> str:  # LC 151 (pythonic; the trick matters in C)
    return " ".join(reversed(s.split()))


def reverse_string(s: list[str]) -> None:  # LC 344 — swap-converge IS reversal
    lo, hi = 0, len(s) - 1
    while lo < hi:
        s[lo], s[hi] = s[hi], s[lo]
        lo, hi = lo + 1, hi - 1


if __name__ == "__main__":
    assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert find_duplicate([1, 3, 4, 2, 2]) == 2
    a = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
    assert remove_duplicates(a) == 5 and a[:5] == [0, 1, 2, 3, 4]
    b = [2, 0, 2, 1, 1, 0]
    sort_colors(b)
    assert b == [0, 0, 1, 1, 2, 2]
    assert backspace_compare("ab#c", "ad#c")
    assert not backspace_compare("a#c", "b")
    assert longest_palindrome("babad") in ("bab", "aba")
    assert count_palindromic_substrings("aaa") == 6
    assert reverse_words("  the sky  is blue ") == "blue is sky the"
    print("01_two_pointers: all checks passed")
