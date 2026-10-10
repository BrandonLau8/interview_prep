"""Patterns 1-7: Two Pointers.

Core idea: two indices moving with purpose replace a nested loop, because some
structural fact (sortedness, symmetry, a one-pass invariant) proves which
pointer is safe to move — skipped pairs never need revisiting.
Run: python 01_two_pointers.py
"""


# ---------------------------------------------------------------- Pattern 1
# Converging: sorted input, each step PROVABLY eliminates one element.
def two_sum_sorted(nums: list[int], target: int) -> list[int]:  # LC 167
    """Sortedness makes hi the best partner lo will ever get: if their sum is
    still too small, nums[lo] can pair with nothing — discard it. Every
    comparison provably eliminates one element, so one pass suffices.

    Naive: test all pairs — O(n^2). Sortedness turns "is there a partner?"
    from a rescan into one comparison against the current extreme.

    Real life: two fingers on a price list sorted cheap-to-dear, hunting a
    pair totalling $50 — too cheap, slide the left finger up; too dear, slide
    the right one down (matching bids against asks in an order book)."""
    lo, hi = 0, len(nums) - 1              # invariant: answer, if any, lies in [lo, hi]
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return [lo + 1, hi + 1]        # LC 167 wants 1-indexed positions
        if s < target:
            lo += 1   # nums[lo] can't pair with anything (hi was its best shot)
        else:
            hi -= 1   # nums[hi] can't pair with anything (lo was its best shot)
    return []


def three_sum(nums: list[int]) -> list[list[int]]:  # LC 15
    """All unique triplets summing to zero.
    Fix one element and the rest is exactly LC 167 with target -nums[i], so
    the converging pair runs in O(n). Sorting buys both that convergence
    proof and cheap deduping — equal values land next to each other.

    Naive: three nested loops plus a set to dedupe — O(n^3). Sorting makes
    duplicates adjacent, so comparing to the previous element replaces the set.

    Real life: coins laid out smallest to largest; pin one, then sweep two
    fingers inward for a pair that cancels it — identical coins sit together
    so you skip them at a glance (netting a ledger to zero, three entries)."""
    nums.sort()
    res = []
    for i in range(len(nums) - 2):         # invariant: nums[i] is the smallest of the triplet
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
    """Pick two lines that, with the x-axis, hold the most water.
    Area = width x the SHORTER wall. Moving the taller wall keeps the same
    bottleneck and loses width, so it can never improve — only the shorter
    wall can, which makes discarding it provably safe.

    Naive: compute the area for every pair — O(n^2). The bottleneck argument
    replaces that scan with one forced move per step.

    Real life: two people holding a sagging tarp — the lower hand decides how
    much rain it catches, so raising the higher hand is wasted effort; step
    the lower one inward (a pipe run capped by its narrowest segment)."""
    lo, hi, best = 0, len(height) - 1, 0   # invariant: best area using any pair outside [lo,hi] is already beaten
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
    """A 2x runner gains exactly one node per step on a 1x runner, so once
    both are inside a loop the gap shrinks by one each step and can never be
    jumped over — they must land on the same node. No memory needed.

    Naive: record every visited node in a set and stop on a repeat — correct
    but O(n) space. The speed difference is what replaces the set.

    Real life: two runners on a track, one twice as fast — on a loop the fast
    one eventually laps the slow one; on a straight road he just finishes and
    leaves (spotting a symlink loop without keeping a visited table)."""
    slow = fast = head                     # invariant: fast has taken exactly 2x slow's steps
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False


def find_duplicate(nums: list[int]) -> int:  # LC 287
    """n+1 values in [1..n]; find the repeated one without modifying nums.
    Read i -> nums[i] as next-pointers. Two indices holding the same value
    means two nodes point at one successor, so the duplicate IS the cycle
    entrance — and Floyd finds an entrance in O(1) space.

    Naive: sort and scan for neighbours (destroys the input), or a seen-set —
    O(n) space. The cycle reframing needs neither.

    Real life: a phone tree where two people list the same next contact —
    calling down the chain always funnels you into the same loop, and the
    person everyone converges on is the duplicate."""
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
    """A fixed gap of n+1 converts "n from the end" — which needs the length —
    into "the leader fell off the end", a local check. The +1 is what leaves
    follow on the predecessor, the node you actually have to mutate.

    Naive: walk once to measure the length, then walk again to length - n —
    two passes. The gap carries the same information through one pass.

    Real life: two people hauling a rope hand over hand a fixed span apart —
    when the leader reaches the frayed end, the follower is already standing
    on the spot to cut (keeping the last n lines of a stream unbuffered)."""
    dummy = ListNode(0, head)              # invariant: gap between lead and follow stays n+1
    lead = follow = dummy
    for _ in range(n + 1):            # +1 so follow stops BEFORE the target
        lead = lead.next
    while lead:
        lead, follow = lead.next, follow.next
    follow.next = follow.next.next
    return dummy.next


def middle_node(head: ListNode) -> ListNode:  # LC 876
    """Same 2x runner as LC 141, no cycle — here the ratio itself is the
    answer: when fast falls off the end, slow has covered exactly half.
    On even length this lands on the second middle, which LC 876 wants.

    Naive: count the nodes, then walk half the count again — two passes.

    Real life: pacing a hallway beside a friend taking two steps per your one
    — when they hit the far wall, you are standing at the midpoint."""
    slow = fast = head                     # invariant: slow is at floor(fast/2) nodes in
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow


# ---------------------------------------------------------------- Pattern 4
# Reader/writer: invariant — [0, write) is always the finished answer.
def remove_duplicates(nums: list[int]) -> int:  # LC 26
    """Sorted array, dedupe in place; return the new length.
    Two cursors on one array: read runs ahead over the garbage while write
    marks the end of the finished answer. Comparing against nums[write-1] —
    the last value KEPT, not the last value read — collapses runs of any length.

    Naive: build a fresh list, then copy it back — O(n) extra space for a
    result that provably fits inside the input.

    Real life: recopying a guest list onto a clean sheet and skipping a name
    when it matches the one you just wrote (compacting repeated status pings)."""
    write = 1                              # invariant: nums[0:write] is the deduped answer
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write


def move_zeroes(nums: list[int]) -> None:  # LC 283
    """Push every zero to the end, keeping the non-zeroes in their order.
    Same reader/writer as LC 26, but swapping instead of overwriting: the
    swap drops the zero into the slot the non-zero just vacated, so the
    zeroes pile up at the back for free and relative order survives.

    Naive: build a list of the non-zeroes, then pad with zeroes — O(n) space.

    Real life: sweeping leaves down a hallway — every clean tile you step on
    trades places with the pile you have been pushing behind you."""
    write = 0                              # invariant: nums[0:write] is non-zero, in original order
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1


def sort_colors(nums: list[int]) -> None:  # LC 75, Dutch national flag
    """Sort an array of 0/1/2 in place, one pass.
    Three known regions and one unknown gap: [0,lo)=0s, [lo,mid)=1s,
    [mid,hi]=unknown, (hi,end]=2s. Every value has exactly one destination,
    so a single look places it and the gap shrinks by one each step.

    Naive: counting sort — correct but two passes; a general sort is O(n log n)
    for data with only three distinct keys.

    Real life: sorting laundry into whites, colours and darks with one hand —
    each garment goes straight to its pile, but one tossed back from the far
    pile has not been looked at yet, which is why mid holds still on a 2."""
    lo, mid, hi = 0, 0, len(nums) - 1      # invariant: [0,lo)=0s  [lo,mid)=1s  (hi,end]=2s
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
    """Do two strings match after '#' is applied as a backspace?
    Forward you cannot tell whether a char survives — a later '#' may still
    kill it. Backwards, each '#' is a credit spent on the next char, so a
    char's fate is decided the moment you see it. One pass, O(1) space.

    Naive: rebuild both strings with a stack, then compare — O(n) space to
    learn something the reverse scan settles as it goes.

    Real life: proofreading a message from the end, where each "scratch that"
    cancels the word just before it (replaying an edit log in reverse)."""
    i = len(s) - 1                         # invariant: next index of s not yet compared
    j = len(t) - 1                         # invariant: next index of t not yet compared
    skip_s = 0                             # invariant: deletions owed, one per '#' passed
    skip_t = 0
    while i >= 0 or j >= 0:
        while i >= 0:                      # walk i back to the next SURVIVING char
            if s[i] == '#':
                skip_s += 1
                i -= 1
            elif skip_s > 0:
                skip_s -= 1
                i -= 1
            else:
                break
        while j >= 0:
            if t[j] == '#':
                skip_t += 1
                j -= 1
            elif skip_t > 0:
                skip_t -= 1
                j -= 1
            else:
                break
        if i >= 0 and j >= 0:
            if s[i] != t[j]:
                return False
        elif i >= 0 or j >= 0:             # one ran out first: different lengths
            return False
        i -= 1
        j -= 1
    return True


# ---------------------------------------------------------------- Pattern 6
# Expand from center: 2n-1 centers; each expansion step certifies a
# palindrome for free.
def longest_palindrome(s: str) -> str:  # LC 5
    """Longest palindromic substring — contiguous, not a subsequence.
    Every palindrome has a center, and there are only 2n-1 of them: n chars
    plus n-1 gaps. Expanding outward certifies each longer palindrome in O(1)
    from the verified one inside it, so nothing is ever rechecked.

    Naive: test all O(n^2) substrings at O(n) each — O(n^3). Expansion reuses
    the inside it already proved instead of re-scanning it.

    Real life: pinching one bead of a necklace and feeling outward pair by
    pair to test symmetry — the first mismatched pair ends that center."""
    best = ""
    for center in range(2 * len(s) - 1):   # invariant: 2n-1 centers = n chars + n-1 gaps
        lo, hi = center // 2, (center + 1) // 2   # odd & even centers
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo, hi = lo - 1, hi + 1
        if hi - lo - 1 > len(best):
            best = s[lo + 1:hi]
    return best


def count_palindromic_substrings(s: str) -> int:  # LC 647
    # Count every palindromic substring; equal strings at different positions
    # count separately.
    # Same 2n-1 centers as LC 5 — but tally each successful expansion instead
    # of tracking the longest, because every expansion step IS one palindrome.
    # Naive: test all O(n^2) substrings at O(n) each — O(n^3).
    # Real life: same necklace pinch, counting every symmetric stretch found.
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
    """Reverse the word order, trimming and collapsing whitespace.
    Word order flips but the letters inside a word do not — so reverse the
    whole string, then reverse each word back. Python's split/join hides
    that; on a char array it is the only route to O(1) extra space.

    Naive: split into a list and emit it backwards — O(n) space, which is
    exactly what this Python version does; the two-reversal trick avoids it.

    Real life: flipping a shelf of books end to end, then turning each book
    upright again (reversing a path's segments in the buffer you have)."""
    return " ".join(reversed(s.split()))


def reverse_string(s: list[str]) -> None:  # LC 344 — swap-converge IS reversal
    """Converging pointers where the swap is the entire job: each step
    finalizes two positions at once, so lo < hi is the whole termination
    condition — a lone middle character is already in its right place.

    Naive: copy into a second array back to front — O(n) space.

    Real life: two people at opposite ends of a row of chairs trading seats
    and stepping inward until they meet."""
    lo, hi = 0, len(s) - 1                 # invariant: everything outside [lo,hi] is reversed
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
