"""Patterns 70-73: Bit Manipulation.

Core idea: two facts wearing costumes —
  XOR is self-canceling addition (x ^ x == 0, order irrelevant), and
  n & (n-1) deletes the lowest set bit.
Run: python 11_bits.py
"""


# --------------------------------------------------------------- Pattern 70
def single_number(nums: list[int]) -> int:  # LC 136
    """The one value appearing once; every other appears exactly twice.
    XOR is self-cancelling addition: x ^ x is 0 and order does not matter, so
    folding the whole list annihilates every pair regardless of position. The
    accumulator needs no memory of WHICH values it has seen.

    Naive: a hash set toggling membership, or counting — O(n) space to track
    identities the cancellation makes irrelevant.

    Real life: everyone at a dance pairing off and leaving — whoever is still
    standing came alone, and you never had to write down any names."""
    acc = 0                                # invariant: XOR of everything seen; paired values have cancelled
    for x in nums:
        acc ^= x
    return acc


def missing_number(nums: list[int]) -> int:  # LC 268
    """The one value missing from 0..n.
    Manufacture the pairs: XOR every index against every value and each
    present number meets its own index and cancels. Only the absent one is
    left unpaired — the same trick as LC 136 with one side synthesized.

    Naive: sum 0..n and subtract — correct here, but it overflows on fixed-
    width types where XOR never does. A seen-set costs O(n) space.

    Real life: checking a numbered coat rack by ticking each hook against its
    ticket — the hook with no matching ticket is the missing coat."""
    acc = len(nums)                        # invariant: XOR of unmatched indices and values so far
    for i, x in enumerate(nums):
        acc ^= i ^ x
    return acc


def single_number_ii(nums: list[int]) -> int:  # LC 137 (others appear thrice)
    """The one value appearing once; every other appears exactly three times.
    XOR cancels in PAIRS, so it is useless at three. Drop to the bit level:
    each position's count of 1s is a multiple of 3 plus the singleton's bit,
    so count mod 3 rebuilds it. Python's unbounded ints need the sign fixup.

    Naive: a hash map of counts — O(n) space, where per-bit counting needs
    only 32 tallies regardless of input size.

    Real life: a ballot where every candidate got three votes except one —
    you count each column and look for the one that isn't divisible by three."""
    result = 0                             # invariant: bits whose column count isn't a multiple of 3
    for bit in range(32):
        count = sum((x >> bit) & 1 for x in nums)
        if count % 3:
            result |= 1 << bit
    if result >= 1 << 31:                  # Python ints aren't 32-bit: fix sign
        result -= 1 << 32
    return result


def find_the_difference(s: str, t: str) -> str:  # LC 389
    # The single extra character in t, which is s shuffled plus one letter.
    # LC 136 again once you concatenate: every character of s meets its copy
    # in t and cancels, leaving only the addition.
    # Naive: sort both and compare, or count characters — O(n log n) or O(n)
    # space to find something the cancellation surfaces for free.
    # Real life: weighing a parcel before and after — the difference is the
    # item added, without unpacking anything.
    acc = 0                                # invariant: XOR of all codepoints; matched letters have cancelled
    for ch in s + t:                       # every char pairs except the added one
        acc ^= ord(ch)
    return chr(acc)


# --------------------------------------------------------------- Pattern 71
def hamming_weight(n: int) -> int:  # LC 191
    """Count the set bits in n.
    n & (n-1) clears exactly the lowest set bit: subtracting 1 flips that bit
    off and every zero below it on, so the AND keeps only the higher bits.
    The loop therefore runs once per SET bit, not once per bit width.

    Naive: shift right 32 times testing the low bit — fixed 32 iterations
    even for n = 1, and it needs the width known in advance.

    Real life: emptying a coin jar by removing the smallest coin each time —
    you count the coins, not the capacity of the jar."""
    count = 0                              # invariant: set bits already cleared from n
    while n:
        n &= n - 1                         # delete lowest set bit
        count += 1                         # loops popcount times, not 32
    return count


def total_hamming_distance(nums: list[int]) -> int:  # LC 477
    """Sum of Hamming distance over every pair of numbers.
    Bit positions are independent, so swap the loops: instead of comparing
    pairs, ask each COLUMN how many pairs differ in it. That is ones * zeros,
    a product — no pair is ever visited.

    Naive: XOR all O(n^2) pairs and popcount each — quadratic, where the
    per-column count is one pass over 32 positions.

    Real life: counting disagreements across a survey by tallying each
    question's yes/no split, rather than comparing every two respondents."""
    total = 0                              # invariant: differing pairs summed over columns processed
    for bit in range(32):
        ones = sum((x >> bit) & 1 for x in nums)
        total += ones * (len(nums) - ones)
    return total


# --------------------------------------------------------------- Pattern 72
def count_bits(n: int) -> list[int]:  # LC 338
    """Set-bit count for every number from 0 to n.
    i in binary is i >> 1 with one more bit stuck on the end, so its popcount
    is that number's plus the new bit. Every answer is therefore one lookup of
    an already-computed smaller index — DP where the recurrence is a shift.

    Naive: call hamming_weight on each i — O(n log n) total, recomputing the
    shared prefix of every number from scratch.

    Real life: numbering boxes where each label extends a shorter one by a
    digit — you read off the shorter label's tally and add the new digit."""
    bits = [0] * (n + 1)                   # invariant: bits[i] = popcount(i) for every index below the current one
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits


def min_sessions(tasks: list[int], session_time: int) -> int:
    """Fewest sessions of fixed length that fit all tasks (LC 1986 family).
    When n <= ~20 the SUBSET of finished tasks is a legal DP state — 2^n fits
    in memory and an int is the set. The value must be a lexicographic PAIR:
    fewer sessions wins, and ties break on time left, which is the tiebreak
    that makes a greedy fill safe within a session.

    Naive: try every assignment of tasks to sessions — n! orderings, when only
    WHICH tasks are done, not their order, affects what remains.

    Real life: packing errands into fixed-length outings, tracking only which
    errands are behind you and how much of the current outing is left."""
    n = len(tasks)
    full = (1 << n) - 1                    # invariant: bit i set means task i is done
    best = [(n + 1, 0)] * (full + 1)       # invariant: best[mask] = (sessions used, time left), lexicographically minimal
    best[0] = (1, session_time)
    for mask in range(full + 1):
        sessions, left = best[mask]
        for i in range(n):
            if mask >> i & 1:
                continue
            if tasks[i] <= left:           # fits in the open session
                cand = (sessions, left - tasks[i])
            else:                          # open a new session
                cand = (sessions + 1, session_time - tasks[i])
            if cand < best[mask | 1 << i]:
                best[mask | 1 << i] = cand
    return best[full][0]


# --------------------------------------------------------------- Pattern 73
def is_power_of_two(n: int) -> bool:  # LC 231
    """Is n a power of two?
    A power of two has exactly one set bit, and n & (n-1) clears the lowest
    set bit — so the result is zero iff there was only one. The n > 0 guard
    is load-bearing: 0 & -1 is also 0, and zero is not a power of two.

    Naive: divide by two while even and check you land on 1 — O(log n) loop
    for something one AND settles.

    Real life: checking a weight is a single clean doubling of 1kg rather
    than a combination of smaller weights."""
    return n > 0 and n & (n - 1) == 0      # exactly one set bit


def is_power_of_four(n: int) -> bool:  # LC 342
    # Is n a power of four?
    # A power of four is a power of two whose one bit sits at an EVEN
    # position, since each step of four shifts by two. The 0x55555555 mask
    # (binary ...01010101) is exactly the set of even positions.
    # Naive: divide by four repeatedly — O(log n) instead of two ANDs.
    # Real life: telling square tilings from mere doublings — only every
    # second doubling gives you a whole square.
    return n > 0 and n & (n - 1) == 0 and n & 0x55555555 != 0


if __name__ == "__main__":
    assert single_number([4, 1, 2, 1, 2]) == 4
    assert missing_number([3, 0, 1]) == 2
    assert single_number_ii([0, 1, 0, 1, 0, 1, 99]) == 99
    assert single_number_ii([-2, -2, 1, -2]) == 1   # negatives: needs the 32-bit sign fixup
    assert find_the_difference("abcd", "abcde") == "e"
    assert hamming_weight(0b1011) == 3
    assert total_hamming_distance([4, 14, 2]) == 6
    assert count_bits(5) == [0, 1, 1, 2, 1, 2]
    assert min_sessions([1, 2, 3], 3) == 2
    assert is_power_of_two(16) and not is_power_of_two(0)
    assert is_power_of_four(16) and not is_power_of_four(8)
    print("11_bits: all checks passed")
