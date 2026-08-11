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
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next   # snapshot-and-rewire
    return prev


def reverse_between(head: ListNode, left: int, right: int) -> ListNode:  # LC 92
    dummy = ListNode(0, head)
    wall = dummy
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
    # Check a full group exists, reverse it, recurse on the rest, stitch.
    node = head
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
    # Middle (pattern 3) + reverse back half in place + compare.
    slow = fast = head
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
    dummy = tail = ListNode()
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
    dummy = tail = ListNode()
    carry = 0
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
    # Redirect each finished walker to the OTHER head: both travel a+b+shared,
    # arriving at the junction in sync (or at None together).
    pa, pb = a, b
    while pa is not pb:
        pa = pa.next if pa else b
        pb = pb.next if pb else a
    return pa


# --------------------------------------------------------------- Pattern 78
def reorder_list(head: ListNode | None) -> None:  # LC 143
    # Compose primitives: find middle + reverse back half + interleave.
    if not head or not head.next:
        return
    slow = fast = head
    while fast.next and fast.next.next:
        slow, fast = slow.next, fast.next.next
    back = reverse_list(slow.next)
    slow.next = None                       # cut the list in two
    front = head
    while back:
        front.next, back.next, front, back = back, front.next, front.next, back.next


def partition_list(head: ListNode | None, x: int) -> ListNode | None:  # LC 86
    # Two sublists with dummy heads, then concatenate — order preserved.
    before = bt = ListNode()
    after = at = ListNode()
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
    if not head:
        return None
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next               # odd hops over even
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head


def swap_pairs(head: ListNode | None) -> ListNode | None:  # LC 24
    dummy = ListNode(0, head)
    prev = dummy
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
    assert not is_palindrome_list(from_list([1, 2]))
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
