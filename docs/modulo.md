# Modulo warmup

`a % k` is the remainder left after taking as many whole k's out of `a` as
fit. In other words, it tells you where `a` lands inside a cycle of length k.

Assumes you know: Python basics, Big-O, and hashmap counting.
Not covered: modular inverse, Fermat, and CRT (contest math that rarely shows
up in interviews). For the mixed daily rotation, see `docs/daily_warmup.md`.

How to use it: read the tell, cover the code, and write it yourself. Then
compare, and read "Why it works." Every block ends with an `assert`, so you can
paste it into `main.py` and run it. The `Next:` line lists harder problems that
use the same mechanism, with their answer keys in `pattern_code/`.


## ELI5

A clock has 12 positions. Seventeen hours after midnight, the hand points at
5, because 17 % 12 = 5. `%` gives you the position on the clock face, and `//`
counts how many full laps the hand has made (17 // 12 = 1).

So whenever a problem talks about cycles, wrapping around, leftovers, or "every
kth" item, you're working on a clock face, and `%` is the tool.

### Where the analogy breaks

    negatives     a clock never shows -1, but Java/C++ return -1 for -1 % 5.
                  Python returns 4. Same math, different sign convention
    k == 0        a clock with 0 positions doesn't exist, and x % 0 throws
    divisibility  "is x a multiple of k" is about whether the hand lands
                  exactly on 12. You check one position; nothing wraps


## 1. Divisibility and parity

### Divisible-by check — LC 412 Fizz Buzz

Tell: the problem says "divisible by," "multiple of," "every kth," or
"even/odd."

```python
def fizz_buzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:                # check the combined case FIRST
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out

assert fizz_buzz(15)[-1] == "FizzBuzz"
assert fizz_buzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
```

ELI5: deal i candies into bags of 3. If none are left over, i is a multiple
of 3. The 15 check goes first because every number that fills bags of 15 also
fills bags of 3 exactly, so "Fizz" would get to it before "FizzBuzz" did.

Why it works: `i % k == 0` means k divides i with nothing left over. 15 is
checked first because any multiple of 15 is also a multiple of 3, so checking
3 first would print "Fizz" and the "FizzBuzz" branch would never run.

Time O(n), space O(1) extra.

Next: LC 416 `05_dp.py:199` (an odd total can't split into two equal halves),
LC 494 `05_dp.py:221`, LC 103 `03_trees.py:100` (alternate direction on odd
levels)

### Euclid's GCD — LC 1979 Find GCD of Array

Tell: the problem asks for the "greatest common divisor," for "the largest
unit that tiles both," or to "reduce a fraction."

```python
def gcd(a, b):
    while b != 0:
        r = a % b                      # invariant: gcd(a, b) never changes
        a = b
        b = r
    return a

def find_gcd(nums):
    lo = nums[0]
    hi = nums[0]
    for x in nums:
        if x < lo:
            lo = x
        if x > hi:
            hi = x
    return gcd(lo, hi)

assert find_gcd([2, 5, 6, 9, 10]) == 2
assert find_gcd([7, 5, 6, 8, 3]) == 1
assert gcd(12, 18) == 6
assert gcd(5, 0) == 5                  # b == 0: everything divides 0
```

ELI5: you want the biggest square tile that fits a 12 x 18 floor exactly.
Lay 12-wide tiles along the 18 side and a 6-wide strip is left over. Any tile
that fits the whole floor must also fit that strip, so the question becomes
the 12 x 6 floor. 6 goes into 12 with nothing left, so the answer is 6.

Why it works: any number that divides both a and b also divides `a - b`,
`a - 2b`, and so on down to `a % b`. That means `gcd(a, b) == gcd(b, a % b)`.
The remainder is always smaller than b, so the pair keeps shrinking until b
reaches 0, and at that point a is the answer.

Time O(log min(a, b)) for gcd, plus O(n) for the scan. Space O(1).

Next: LC 1071 GCD of Strings, LC 459 `14_strings.py:278` (n % period == 0)


## 2. Digit extraction

### Peel digits off the right — LC 9 Palindrome Number

Tell: the problem works on "the digits of an integer" and says not to convert
it to a string.

```python
def is_palindrome_number(x):
    if x < 0:
        return False                   # "-121" reads "121-" backwards
    original = x
    rev = 0
    while x > 0:
        rev = rev * 10 + x % 10        # x % 10 = last digit
        x = x // 10                    # x // 10 = drop last digit
    return rev == original

assert is_palindrome_number(121)
assert not is_palindrome_number(-121)  # negative
assert not is_palindrome_number(10)    # trailing zero
assert is_palindrome_number(0)         # zero
```

ELI5: the number is a stack of digit blocks. `% 10` reads the block on the
right end and `// 10` takes it off. Put each block you remove onto a second
stack and that stack comes out backwards. If backwards matches the original,
the number is a palindrome.

Why it works: in base 10, `x % 10` is the ones digit and `x // 10` shifts
everything one place right. `rev * 10 + d` does the reverse, shifting left and
appending d. The loop moves digits one at a time from the right end of x onto
the right end of rev, which reverses their order.

`rev` can overflow a 32-bit int in Java when x is near INT_MAX. Use `long`,
or only reverse half the digits.

Time O(digits), space O(1).

### Carry — LC 415 Add Strings

Tell: the problem asks for "big number arithmetic as strings" or "add digit by
digit."

```python
def add_strings(a, b):
    i = len(a) - 1
    j = len(b) - 1
    carry = 0
    out = []
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += ord(a[i]) - 48
            i -= 1
        if j >= 0:
            total += ord(b[j]) - 48
            j -= 1
        out.append(str(total % 10))    # digit that stays
        carry = total // 10            # invariant: carry is 0 or 1
    out.reverse()
    return "".join(out)

assert add_strings("11", "123") == "134"
assert add_strings("999", "1") == "1000"   # carry creates a new digit
assert add_strings("0", "0") == "0"
```

ELI5: a column can hold only one digit, like a bowl that holds at most 9
marbles. If 7 + 5 puts 12 marbles in the bowl, 2 stay (`12 % 10`) and the
full ten turns into 1 marble for the next bowl to the left (`12 // 10`).

Why it works: `%` and `//` split `total` into the digit that stays in this
column and the amount carried to the next column. The pair is the same as
"position on the clock" and "laps completed." For binary, change 10 to 2.

Time O(max(m, n)), space O(max(m, n)).

Next: LC 67 `13_array_matrix.py:207`, LC 43 `14_strings.py:192`


## 3. Wraparound

### Circular index — LC 1652 Defuse the Bomb

Tell: the problem says "circular array," "wraps around," "the next element
after the last is the first," or "ring."

```python
def decrypt(code, k):
    n = len(code)
    res = [0] * n
    if k == 0:
        return res
    for i in range(n):
        s = 0
        if k > 0:
            for step in range(1, k + 1):
                s += code[(i + step) % n]          # forward wrap
        else:
            for step in range(1, -k + 1):
                s += code[(i - step + n) % n]      # backward wrap: +n keeps it >= 0 in Java
        res[i] = s
    return res

assert decrypt([5, 7, 1, 4], 3) == [12, 10, 16, 13]
assert decrypt([2, 4, 9, 3], -2) == [12, 5, 6, 13]
assert decrypt([1, 2, 3, 4], 0) == [0, 0, 0, 0]    # k == 0
```

ELI5: kids sitting in a circle. Count 3 seats to your right, and when the
count passes the last kid it carries on from the first one. `% n` handles
that wrap. Counting to the left can drop below seat 0, so add one full circle
(`+ n`) before you count and you never land on a negative seat.

Why it works: `(i + step) % n` maps any index past the end back into
`[0, n)`. You don't need an `if idx >= n: idx -= n` branch, and it still works
when step is large. Going backward, `i - step` can go negative, so add n
before taking `%`. Python doesn't need the `+ n`, but Java and C++ do.

Time O(n·|k|), space O(n). A sliding window brings this down to O(n), but
it's the same `%`.

Next: LC 503 `10_stack.py:78` (loop i to 2n, read `nums[i % n]`)

### Reduce the shift first — LC 189 Rotate Array

Tell: the problem says "rotate by k," and k can be larger than n.

```python
def rotate(nums, k):
    n = len(nums)
    k = k % n                          # invariant: 0 <= k < n; n full turns = no-op
    out = [0] * n
    for i in range(n):
        out[(i + k) % n] = nums[i]     # element at i lands k slots right, wrapping
    for i in range(n):
        nums[i] = out[i]
    return nums

assert rotate([1, 2, 3, 4, 5, 6, 7], 3) == [5, 6, 7, 1, 2, 3, 4]
assert rotate([1, 2], 5) == [2, 1]     # k > n
assert rotate([1, 2, 3], 3) == [1, 2, 3]  # k == n: full turn
```

ELI5: spin a 7-seat merry-go-round 10 seats. The first 7 just bring everyone
back to where they started, so only the last 3 matter (10 % 7 = 3). After
that, each kid moves 3 seats over and wraps past the end, like the circle
from the previous warmup.

Why it works: rotating n times returns the original array, so only `k % n`
of the rotations do anything. Destination `(i + k) % n` is the circular-index
trick from the previous warmup, used to place elements instead of read them.

Time O(n), space O(n). The O(1)-space three-reversal version is in the file
below, and it needs `k %= n` even more, because otherwise it reverses past the
end of the array.

Next: LC 189 in place `13_array_matrix.py:29`, LC 2381 `17_difference_array.py:88`
(`% 26` on letters)


## 4. 1D to 2D index mapping

### Flat index to (row, col) — LC 566 Reshape the Matrix

Tell: the problem says to "treat the grid as one long array," "reshape," or
"binary search a sorted matrix."

```python
def matrix_reshape(mat, r, c):
    m = len(mat)
    n = len(mat[0])
    if m * n != r * c:
        return mat
    out = []
    for _ in range(r):
        out.append([0] * c)
    for i in range(m * n):
        out[i // c][i % c] = mat[i // n][i % n]   # row = laps, col = position in lap
    return out

assert matrix_reshape([[1, 2], [3, 4]], 1, 4) == [[1, 2, 3, 4]]
assert matrix_reshape([[1, 2], [3, 4]], 4, 1) == [[1], [2], [3], [4]]
assert matrix_reshape([[1, 2], [3, 4]], 2, 4) == [[1, 2], [3, 4]]  # size mismatch
```

ELI5: a cinema with 10 seats per row, where tickets are numbered 0, 1, 2 and
so on across each row. Ticket 23 is in row 2 (`23 // 10`), because two full
rows come before it, and in seat 3 of that row (`23 % 10`).

Why it works: in row-major order, each row is one lap of length `cols`. So
`i // cols` counts the completed laps, which is the row, and `i % cols` is
your position in the current lap, which is the column. Going the other way,
`i = row * cols + col`.

Divide by the number of columns, not rows. Swapping them is the classic bug,
and square test cases hide it.

Time O(m·n), space O(m·n).

Next: LC 74 `09_binary_search.py:80` (binary search on 0..m·n-1, decode mid)


## 5. Remainder buckets

### Pairs that sum to a multiple of k — LC 1010 Pairs of Songs

Tell: the problem says "pairs whose sum is divisible by k."

```python
def num_pairs_divisible_by_60(time):
    seen = [0] * 60                    # invariant: seen[r] = earlier songs with t % 60 == r
    count = 0
    for t in time:
        r = t % 60
        need = (60 - r) % 60           # outer % maps r == 0 to need 0, not 60
        count += seen[need]
        seen[r] += 1
    return count

assert num_pairs_divisible_by_60([30, 20, 150, 100, 40]) == 3
assert num_pairs_divisible_by_60([60, 60, 60]) == 3     # r == 0 pairs with itself
assert num_pairs_divisible_by_60([1, 2]) == 0
```

ELI5: only the minutes past the hour matter. A song at :20 pairs with one at
:40, and a song at :00 pairs with another at :00. So sort the songs into 60
boxes by their leftover minutes. Each new song checks how many songs already
sit in the box that completes its hour.

Why it works: `(a + b) % 60 == 0` depends only on `a % 60` and `b % 60`. That
lets you replace each song with its remainder and count complements, as in
Two Sum. The extra `% 60` on `need` handles the r == 0 case, where the
complement of 0 is 0, not 60.

Time O(n), space O(k).

### Subarray sum divisible by k — LC 974

Tell: the problem asks about a "subarray (contiguous) sum divisible by k."
That's the same bucket idea as the previous warmup, applied to prefix sums.

```python
def subarrays_div_by_k(nums, k):
    bucket = [0] * k                   # invariant: bucket[r] = prefixes seen with sum % k == r
    bucket[0] = 1                      # empty prefix: lets a subarray start at index 0
    running = 0
    count = 0
    for x in nums:
        running = (running + x) % k    # Java: ((running + x) % k + k) % k
        count += bucket[running]
        bucket[running] += 1
    return count

assert subarrays_div_by_k([4, 5, 0, -2, -3, 1], 5) == 7
assert subarrays_div_by_k([5], 9) == 0
assert subarrays_div_by_k([-1, 2, 9], 2) == 2           # negatives
```

ELI5: walk along a running track with laps of length k and write down where
on the lap you are after each number. If you were at the same spot at two
different times, everything you walked between them was a whole number of
laps, so that stretch sums to a multiple of k.

Why it works: `sum(i..j) = pre[j+1] - pre[i]`. If both prefixes leave the
same remainder, the remainders cancel in the subtraction, so the subarray sum
is a multiple of k. Each new prefix pairs with every earlier prefix in its
bucket.

A negative x is where Java breaks. With `-1 % 5 == -1`, the remainders -1 and
4 land in different buckets even though they mean the same thing.

Time O(n), space O(k).

Next: LC 974 `18_prefix_sum.py:94`, LC 523 `18_prefix_sum.py:130` (length >= 2,
so store the first index per remainder instead of a count)


## 6. Big answers mod 1e9+7

### Fast power with reduction at every step — LC 1922 Count Good Numbers

Tell: the problem says "return the answer modulo 10^9 + 7," and the answer
grows exponentially.

```python
MOD = 10**9 + 7

def pow_mod(base, exp):
    result = 1
    base = base % MOD
    while exp > 0:
        if exp % 2 == 1:               # odd exponent: peel off one factor
            result = result * base % MOD
        base = base * base % MOD       # square, then reduce immediately
        exp = exp // 2
    return result

def count_good_numbers(n):
    evens = (n + 1) // 2               # positions 0, 2, 4...: 5 choices (0,2,4,6,8)
    odds = n // 2                      # positions 1, 3, 5...: 4 choices (2,3,5,7)
    return pow_mod(5, evens) * pow_mod(4, odds) % MOD

assert count_good_numbers(1) == 5
assert count_good_numbers(4) == 400
assert count_good_numbers(50) == 564908303
assert pow_mod(2, 0) == 1              # exp == 0
assert pow_mod(2, 10) == pow(2, 10, MOD)
```

ELI5: you only care where the clock hand ends up, not how many laps it made.
Throw the laps away after every step and the hand still lands in the same
place, but your numbers never get too big to hold. For fast power, 5^8 is
just 5^4 squared, so you square instead of multiplying 8 times.

Why it works: `(a * b) % M == ((a % M) * (b % M)) % M`. Reducing after every
multiply gives the same final answer while keeping each value below M. In
Java, two values below about 1e9 multiply to about 1e18, which fits in a
`long`, but a third multiply without reducing in between overflows. That's
why every `*` line ends with `% MOD`.

The `exp % 2` / `exp // 2` pair reads the exponent's binary digits, which is
the digit-peeling warmup with base 2.

Time O(log n), space O(1).

Next: LC 907 `10_stack.py:120` (the sum is reduced mod 1e9+7), LC 70
`05_dp.py:12` (if asked "mod 1e9+7," reduce inside the loop)


## 7. Negative remainders

### Write Java's % and then fix it

Tell: you're about to run `%` on a value that can be negative, and the
interview is in Java, C++, Go, or JS.

```python
def trunc_mod(a, k):
    # what Java/C++/Go/JS compute: remainder takes the sign of a
    q = abs(a) // abs(k)
    if (a < 0) != (k < 0):
        q = -q
    return a - k * q

def safe_mod(a, k):
    return (trunc_mod(a, k) + k) % k   # the portable fix (k > 0)

assert trunc_mod(-1, 5) == -1          # Java answer
assert -1 % 5 == 4                     # Python answer
assert safe_mod(-1, 5) == 4            # fixed
assert safe_mod(-10, 5) == 0           # exact multiple
assert safe_mod(7, 5) == 2             # positive input unchanged
```

ELI5: ask Java where 1 hour before midnight is on the clock and it answers
"-1 o'clock," which isn't on the dial. Add one full turn (k) to get onto the
dial, then take `% k` again in case you went past the top.

Why it works: truncating division rounds toward zero, so for negative a the
remainder comes out between -(k-1) and 0. Adding k shifts that range into
1..k, and one more `% k` brings it back into `[0, k)` without breaking
positive inputs. Python floors instead of truncating, so its `%` already
returns a non-negative result for k > 0.

Time O(1).

Next: LC 974 in Java, as shown in the bucket warmup.


## Traps

    precedence      a + b % k  is  a + (b % k).  Write (a + b) % k
    reduce late     with MOD, reduce after EVERY + and *; Java long overflows otherwise
    k > n           rotation/shift: k %= n first, or you index past the end
    k == 0          x % 0 throws; guard when k is an input
    negatives       Java/C++/Go/JS: ((x % k) + k) % k
    r == 0 pairs    complement of 0 is 0, not k: need = (k - r) % k
    rows vs cols    flat index: i // COLS, i % COLS; square tests hide the swap
    % 2 vs & 1      equal for x >= 0; -3 % 2 is -1 in Java, so x % 2 == 1 misses
                    negative odds. Test x % 2 != 0
