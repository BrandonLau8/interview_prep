"""Patterns 74-78: Linked List Manipulation.

Core idea: pointer choreography — know which pointers you need BEFORE the
operation destroys them. Two tools remove most pain: a dummy head (kills
empty-result / delete-first edge cases) and saving next before rewiring.
Run: python 12_linked_list.py
"""


class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def from_list(vals: list[int]) -> ListNode | None:
    dummy = tail = ListNode()
    for v in vals:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def to_list(head: ListNode | None) -> list[int]:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


# --------------------------------------------------------------- Pattern 74
def reverse_list(head: ListNode | None) -> ListNode | None:  # LC 206
    """Reverse a singly linked list in place.
    The one hazard: overwriting head.next destroys the only route to the rest
    of the list. The tuple assignment snapshots all three values before any
    is written, which is why this fits on one line without a temp variable.

    Naive: copy the values into an array, reverse it, and rewrite them —
    O(n) extra space to avoid pointer bookkeeping.

    Real life: reversing a conga line by having each person turn to face the
    one behind — you must know who that is before you let go of the front."""
    prev = None                            # invariant: head of the already-reversed prefix
    while head:
        head.next, prev, head = prev, head, head.next   # snapshot-and-rewire
    return prev


def reverse_between(head: ListNode, left: int, right: int) -> ListNode:  # LC 92
    """Reverse only positions left..right, one pass.
    Head-insertion rather than pointer-flipping: repeatedly unlink the node
    AFTER cur and splice it just past wall. Each move pulls one node to the
    front of the window, so the window reverses without any suffix rewiring.

    Naive: cut the sublist out, call LC 206 on it, then stitch three pieces —
    correct, but the boundary bookkeeping is where the bugs live.

    Real life: dealing cards off a deck onto the top of a pile — the pile
    ends up in the opposite order without ever handling the whole deck."""
    dummy = ListNode(0, head)              # invariant: kills the "window starts at position 1" special case
    wall = dummy                           # invariant: the node immediately before the window
    for _ in range(left - 1):              # wall = node before the window
        wall = wall.next
    cur = wall.next
    # Head-insertion: repeatedly unlink cur's NEXT node, plug it after wall.
    for _ in range(right - left):
        moved = cur.next
        cur.next = moved.next
        moved.next = wall.next
        wall.next = moved
    return dummy.next


def reverse_k_group(head: ListNode | None, k: int) -> ListNode | None:  # LC 25
    """Reverse every full group of k nodes; leave a short tail alone.
    Check FIRST, reverse second — walking k nodes before touching anything is
    what protects the short tail. Recursing before the local reversal means
    `prev` already points at the finished remainder, so the stitch is free.

    Naive: reverse a group, then hunt for the new tail to attach the next
    one — the same work with the joins done by hand and easy to misplace.

    Real life: flipping a bookshelf shelf by shelf, but only where a full
    shelf's worth of books is present — you count before you lift."""
    node = head                            # invariant: probe walking k ahead to prove a full group exists
    for _ in range(k):
        if not node:
            return head                    # short tail stays as-is
        node = node.next
    prev = reverse_k_group(node, k)        # prev = head of reversed remainder
    cur = head
    for _ in range(k):
        cur.next, prev, cur = prev, cur, cur.next
    return prev


def is_palindrome_list(head: ListNode | None) -> bool:  # LC 234
    """Is the list a palindrome, in O(1) extra space?
    Composition of two primitives you already have: fast/slow finds the middle
    (pattern 3), then LC 206 reverses the back half so both halves can be
    walked forward together. Stopping when `back` runs out handles odd lengths.

    Naive: copy the values to an array and two-point it — O(n) space, which
    is the only thing the problem actually asks you to avoid.

    Real life: checking a train's carriages read the same both ways by
    uncoupling at the middle and turning the rear half around."""
    slow = fast = head                     # invariant: slow reaches the midpoint as fast reaches the end
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    back = reverse_list(slow)
    front = head
    while back:                            # back half is <= front half
        if front.val != back.val:
            return False
        front, back = front.next, back.next
    return True


# --------------------------------------------------------------- Pattern 75
def merge_two_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:  # LC 21
    """Merge two sorted lists into one sorted list, reusing the nodes.
    The dummy head is the point: without it every append needs an "is the
    result empty?" branch. `<=` rather than `<` keeps equal values in their
    original relative order, which is what makes the merge stable.

    Naive: collect all values, sort, rebuild — O(n log n) plus new nodes, for
    input that was already sorted.

    Real life: interleaving two sorted card piles into one by always taking
    the smaller top card, onto a placeholder that starts the new pile."""
    dummy = tail = ListNode()              # invariant: dummy.next is the result; tail is its last node
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next, l1 = l1, l1.next
        else:
            tail.next, l2 = l2, l2.next
        tail = tail.next
    tail.next = l1 or l2                   # attach whichever survives
    return dummy.next


# --------------------------------------------------------------- Pattern 76
def add_two_numbers(l1: ListNode | None, l2: ListNode | None) -> ListNode:  # LC 2
    """Add two numbers stored least-significant digit first.
    The digit order is a gift — least significant first is exactly the order
    long addition wants, so no reversal is needed. Putting `carry` in the loop
    condition folds three end cases (l1 longer, l2 longer, final carry) into one.

    Naive: convert both lists to ints, add, rebuild — fails the moment the
    numbers exceed the word size, which is the whole reason they are lists.

    Real life: adding two columns of figures on paper from the right, carrying
    into a column that may not exist until you create it."""
    dummy = tail = ListNode()              # invariant: dummy.next is the result; tail is its last digit
    carry = 0                              # invariant: 0 or 1, owed to the next digit
    while l1 or l2 or carry:               # carry keeps the loop honest
        total = (l1.val if l1 else 0) + (l2.val if l2 else 0) + carry
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    return dummy.next


# --------------------------------------------------------------- Pattern 77
def get_intersection_node(a: ListNode | None, b: ListNode | None) -> ListNode | None:  # LC 160
    """The node where two lists merge, or None.
    The lists have different lengths, so equalize by construction: send each
    walker to the OTHER head on finishing. Both then cover exactly
    len(a) + len(b) + shared, meeting at the junction — or at None together.

    Naive: measure both lengths, advance the longer by the difference, then
    walk in step — same O(n) but three passes and an explicit offset.

    Real life: two people walking each other's routes in turn — having covered
    identical ground, they arrive at the shared stretch at the same moment."""
    pa, pb = a, b                          # invariant: each has walked the same total distance
    while pa is not pb:                    # terminates: both hit None if there is no junction
        pa = pa.next if pa else b
        pb = pb.next if pb else a
    return pa


# --------------------------------------------------------------- Pattern 78
def reorder_list(head: ListNode | None) -> None:  # LC 143
    """Reorder to first, last, second, second-last, ... in place.
    Three primitives composed, none new: find the middle, reverse the back
    half, interleave. Cutting with `slow.next = None` is essential — leave it
    joined and the interleave walks into the reversed half and loops forever.

    Naive: index the nodes into an array and rewire by position — O(n) space,
    and the array is only used to simulate walking backwards.

    Real life: folding a queue in half so the last person stands beside the
    first — you cut the line at the midpoint and turn the back half around."""
    if not head or not head.next:
        return
    slow = fast = head                     # invariant: slow lands on the end of the FRONT half
    while fast.next and fast.next.next:
        slow, fast = slow.next, fast.next.next
    back = reverse_list(slow.next)
    slow.next = None                       # cut the list in two
    front = head
    while back:
        front.next, back.next, front, back = back, front.next, front.next, back.next


def partition_list(head: ListNode | None, x: int) -> ListNode | None:  # LC 86
    """Move all nodes < x before all nodes >= x, keeping relative order.
    Two output lists, each with its own dummy, then concatenate — appending
    preserves order for free. `at.next = None` is mandatory: the last "after"
    node still points into the original list, so leaving it makes a cycle.

    Naive: swap node values to compact in place — breaks stability, and
    swapping values sidesteps the pointer work the problem is about.

    Real life: sorting mail into two trays as you walk the pile, then
    stacking one tray on the other — nothing inside a tray gets reordered."""
    before = bt = ListNode()               # invariant: chain of nodes with val < x, in original order
    after = at = ListNode()                # invariant: chain of nodes with val >= x, in original order
    while head:
        if head.val < x:
            bt.next = head
            bt = bt.next
        else:
            at.next = head
            at = at.next
        head = head.next
    at.next = None                         # don't leave a dangling tail
    bt.next = after.next
    return before.next


def odd_even_list(head: ListNode | None) -> ListNode | None:  # LC 328
    """Group nodes at odd positions before those at even positions.
    Two chains woven through one list rather than built separately: each
    pointer hops over its neighbour, so both are extended in lockstep.
    even_head must be saved up front — the join needs it after the weave.

    Naive: build two fresh lists and concatenate, as in LC 86 — correct, but
    here the alternation lets you rewire without a second traversal.

    Real life: splitting a deck by dealing alternately into two piles, then
    setting one pile on top of the other."""
    if not head:
        return None
    odd, even = head, head.next            # invariant: tails of the odd and even chains
    even_head = even                       # invariant: where the even chain starts, needed for the final join
    while even and even.next:
        odd.next = even.next               # odd hops over even
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head


def swap_pairs(head: ListNode | None) -> ListNode | None:  # LC 24
    """Swap every two adjacent nodes.
    LC 25 with k fixed at 2, so the reversal collapses to one rewiring. Three
    pointers change at once and each is read by another — the simultaneous
    assignment is what removes the temp variables and the ordering trap.

    Naive: swap the values instead of the nodes — passes these tests, but
    dodges the pointer work the question exists to check.

    Real life: two dancers in a line trading places while everyone else
    stands still — the person in front must be told who now leads."""
    dummy = ListNode(0, head)              # invariant: removes the "the head itself moves" special case
    prev = dummy                           # invariant: last node of the already-swapped prefix
    while prev.next and prev.next.next:
        a, b = prev.next, prev.next.next
        a.next, b.next, prev.next = b.next, a, b   # prev -> b -> a -> rest
        prev = a
    return dummy.next


if __name__ == "__main__":
    assert to_list(reverse_list(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert to_list(reverse_between(from_list([1, 2, 3, 4, 5]), 2, 4)) == \
        [1, 4, 3, 2, 5]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 2)) == \
        [2, 1, 4, 3, 5]
    assert is_palindrome_list(from_list([1, 2, 2, 1]))
    assert not is_palindrome_list(from_list([1, 2]))   # even length: halves must not overlap
    assert to_list(merge_two_lists(from_list([1, 2, 4]), from_list([1, 3, 4]))) == \
        [1, 1, 2, 3, 4, 4]
    assert to_list(add_two_numbers(from_list([2, 4, 3]), from_list([5, 6, 4]))) == \
        [7, 0, 8]
    shared = from_list([8, 4, 5])
    a = from_list([4, 1])
    a.next.next = shared
    b = from_list([5, 6, 1])
    b.next.next.next = shared
    assert get_intersection_node(a, b) is shared
    lst = from_list([1, 2, 3, 4, 5])
    reorder_list(lst)
    assert to_list(lst) == [1, 5, 2, 4, 3]
    assert to_list(partition_list(from_list([1, 4, 3, 2, 5, 2]), 3)) == \
        [1, 2, 2, 4, 3, 5]
    assert to_list(odd_even_list(from_list([1, 2, 3, 4, 5]))) == [1, 3, 5, 2, 4]
    assert to_list(swap_pairs(from_list([1, 2, 3, 4]))) == [2, 1, 4, 3]
    print("12_linked_list: all checks passed")
