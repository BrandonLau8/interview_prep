"""Patterns 70-73: Bit Manipulation.

Core idea: two facts wearing costumes —
  XOR is self-canceling addition (x ^ x == 0, order irrelevant), and
  n & (n-1) deletes the lowest set bit.
Run: python 11_bits.py
"""


# --------------------------------------------------------------- Pattern 70
def single_number(nums: list[int]) -> int:  # LC 136
    # Pairs annihilate; the singleton survives.
    acc = 0
    for x in nums:
        acc ^= x
    return acc


def missing_number(nums: list[int]) -> int:  # LC 268
    # XOR indices 0..n against all values: everything present cancels.
    acc = len(nums)
    for i, x in enumerate(nums):
        acc ^= i ^ x
    return acc


def single_number_ii(nums: list[int]) -> int:  # LC 137 (others appear thrice)
    # Count each bit position mod 3; the leftover bits belong to the single.
    result = 0
    for bit in range(32):
        count = sum((x >> bit) & 1 for x in nums)
        if count % 3:
            result |= 1 << bit
    if result >= 1 << 31:                  # Python ints aren't 32-bit: fix sign
        result -= 1 << 32
    return result


def find_the_difference(s: str, t: str) -> str:  # LC 389
    acc = 0
    for ch in s + t:                       # every char pairs except the added one
        acc ^= ord(ch)
    return chr(acc)


# --------------------------------------------------------------- Pattern 71
def hamming_weight(n: int) -> int:  # LC 191
    count = 0
    while n:
        n &= n - 1                         # delete lowest set bit
        count += 1                         # loops popcount times, not 32
    return count


def total_hamming_distance(nums: list[int]) -> int:  # LC 477
    # Per bit position: pairs differing there = (count of 1s) * (count of 0s).
    total = 0
    for bit in range(32):
        ones = sum((x >> bit) & 1 for x in nums)
        total += ones * (len(nums) - ones)
    return total


# --------------------------------------------------------------- Pattern 72
def count_bits(n: int) -> list[int]:  # LC 338
    # i is just i//2 shifted left with i's parity appended.
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits


def min_sessions(tasks: list[int], session_time: int) -> int:
    """Bitmask DP demo (family of LC 1494/1986): when n <= ~20, the SUBSET
    of finished items is the DP state."""
    n = len(tasks)
    full = (1 << n) - 1
    # best[mask] = (sessions used, time left in current session) — lexicographic
    best = [(n + 1, 0)] * (full + 1)
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
    return n > 0 and n & (n - 1) == 0      # exactly one set bit


def is_power_of_four(n: int) -> bool:  # LC 342
    # One set bit AND it sits at an even position (mask = ...01010101).
    return n > 0 and n & (n - 1) == 0 and n & 0x55555555 != 0


if __name__ == "__main__":
    assert single_number([4, 1, 2, 1, 2]) == 4
    assert missing_number([3, 0, 1]) == 2
    assert single_number_ii([0, 1, 0, 1, 0, 1, 99]) == 99
    assert single_number_ii([-2, -2, 1, -2]) == 1
    assert find_the_difference("abcd", "abcde") == "e"
    assert hamming_weight(0b1011) == 3
    assert total_hamming_distance([4, 14, 2]) == 6
    assert count_bits(5) == [0, 1, 1, 2, 1, 2]
    assert min_sessions([1, 2, 3], 3) == 2
    assert is_power_of_two(16) and not is_power_of_two(0)
    assert is_power_of_four(16) and not is_power_of_four(8)
    print("11_bits: all checks passed")
