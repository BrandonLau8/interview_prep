# Daily warmup

A fixed core you redo every day, plus an 8-day rotation. Every problem here has
a verified reference solution in `pattern_code/` — the `file:line` is the answer
key, opened only after you've written yours.

Assumes you know: the 18 patterns in `pattern_code/`.
Not covered: hard problems, contest-style tricks, anything without a reference
in this repo. This is finger memory, not new material.

Rule: warmup problems are written from scratch, no editor autocomplete, no
peeking. If one takes more than 10 minutes, that's the signal — it moves into
the next day's rotation too until it doesn't.


## The core sixteen (~50 min, every single day)

One representative of every high-frequency pattern — the cheapest problem that
still forces you to write the mechanism. Coverage is the goal, so each slot is
the *easiest* member of its family, not the most interesting one.

    LC 1     Two Sum                       hash map kills the inner loop     16_composing_structures.py:17
    LC 125   Valid Palindrome              two pointers converging           14_strings.py:12
    LC 3     Longest Substring No Repeat   window grow/shrink invariant      02_sliding_window.py:40
    LC 724   Find Pivot Index              running total, single pass        18_prefix_sum.py:202
    LC 20    Valid Parentheses             stack = most recent unresolved    10_stack.py:11
    LC 739   Daily Temperatures            monotonic stack = pending answers 10_stack.py:57
    LC 206   Reverse Linked List           save next before rewiring         12_linked_list.py:33
    LC 35    Search Insert Position        lo/hi boundary discipline         09_binary_search.py:50
    LC 104   Maximum Depth of Binary Tree  postorder: children report up     03_trees.py:271
    LC 102   Binary Tree Level Order       BFS with a level snapshot         03_trees.py:26
    LC 200   Number of Islands             flood fill = visit and sink       04_graphs.py:15
    LC 207   Course Schedule               3-color DFS = cycle detection     04_graphs.py:145
    LC 215   Kth Largest Element           size-k heap is the answer state   06_heap.py:14
    LC 78    Subsets                       choose / recurse / undo           07_backtracking.py:11
    LC 53    Maximum Subarray              1-D DP: extend or restart         05_dp.py:83
    LC 56    Merge Intervals               sort, then one-pass merge         08_greedy.py:27

Target after two weeks: all sixteen in 35 minutes, first-try correct.

Deliberately not in the core, because they are lower frequency or you would
never be asked them cold: design (LC 146), bit tricks (LC 136), difference
arrays (LC 1109), matrix manipulation (LC 48, 54). They live in the rotation.


## The rotation (3-4 problems, ~30 min)

Second-tier problems only — nothing here repeats a core slot.

### Day 1 — arrays, prefix, difference

    LC 167   Two Sum II (sorted)           01_two_pointers.py:12
    LC 238   Product of Array Except Self  13_array_matrix.py:139
    LC 560   Subarray Sum Equals K         18_prefix_sum.py:60
    LC 1109  Corporate Flight Bookings     17_difference_array.py:45

Point of the day: 238 is the left/right-pass form of the core's 724; 1109 is
the inverse (range writes, point reads). 560 is the one that must become
automatic — prefix + hash map, and a sliding window is *wrong* on it because
negatives break the monotonicity the shrink step assumes.

### Day 2 — sliding window, strings

    LC 209   Minimum Size Subarray Sum     02_sliding_window.py:67
    LC 424   Longest Repeating Char Repl.  02_sliding_window.py:140
    LC 438   Find All Anagrams             02_sliding_window.py:239

Point of the day: 209 shrinks on a feasible window, 424 shrinks on an
infeasible one, 438 never shrinks at all (fixed width). Know which direction
the condition is monotone in before you write the while.

### Day 3 — trees

    LC 226   Invert Binary Tree            03_trees.py:141
    LC 98    Validate BST                  03_trees.py:216
    LC 236   Lowest Common Ancestor        03_trees.py:387

Point of the day: 226 is postorder, 98 is preorder passing bounds DOWN, 236
is postorder passing findings UP. Three information flows through one shape.

### Day 4 — graphs

    LC 994   Rotting Oranges               04_graphs.py:80
    LC 133   Clone Graph                   04_graphs.py:249
    LC 743   Network Delay Time            04_graphs.py:276

Point of the day: 994 is multi-source BFS (seed the queue with every source,
not one), 743 is Dijkstra — a heap replacing the queue the moment edges carry
weight.

### Day 5 — heap, greedy, intervals

    LC 347   Top K Frequent Elements       06_heap.py:33
    LC 253   Meeting Rooms II              06_heap.py:196
    LC 55    Jump Game                     08_greedy.py:92

Point of the day: say out loud why the greedy choice is safe before coding it.
If you can't state the exchange argument, it's a DP problem.

### Day 6 — stack, binary search, design

    LC 394   Decode String                 10_stack.py:228
    LC 153   Find Minimum in Rotated Array 09_binary_search.py:137
    LC 146   LRU Cache                     15_design.py:14

Point of the day: 153 has no target — the predicate is "am I right of the
pivot?". 146 is the one design problem worth having memorized cold.

### Day 7 — DP, backtracking, bits

    LC 322   Coin Change                   05_dp.py:143
    LC 46    Permutations                  07_backtracking.py:87
    LC 136   Single Number                 11_bits.py:11

Point of the day: state the DP state in one sentence before writing the loop.
46 differs from the core's 78 in one line — a used-check instead of a start
index — and that line is the whole permutation-vs-combination distinction.

### Day 8 — hash maps

    LC 49    Group Anagrams                14_strings.py:81
    LC 205   Isomorphic Strings            16_composing_structures.py:38
    LC 525   Contiguous Array              18_prefix_sum.py:164

Point of the day: three different jobs for one dict. 49 keys a bucket by a
canonical form — pick something anagrams share and nothing else does, and the
dict does the grouping for free. 205 needs TWO dicts, because a bijection has
two directions and one map only ever checks one of them. 525 stores the first
index a prefix state was seen at, not a count, because the answer is a length;
it is 560's sibling, and the 0 -> -1 remap is the only step that turns "equal
counts" into a sum condition the map can key on.


## When you blank on the optimal

Write the fallback and move on. A correct slow solution beats ten minutes of
staring, and in an interview it is the sentence that usually hands you the
optimization: say the brute force, name what it wastes, then fix that waste.

Every fallback below is written out in `pattern_code/19_fallbacks.py`, grouped
by the file its optimal version lives in. The complexity and the LeetCode
constraint that makes it safe are in the two comment lines above each one —
read them there, not here, so the two can't drift apart.

These fallbacks submit green — the constraint is small enough, or the trick was
only ever buying O(1) space.

    LC 1    Two Sum            double loop, rescan for target - nums[i]   19_fallbacks.py:568
    LC 125  Valid Palindrome   cleaned lowercase copy vs its reverse      19_fallbacks.py:526
    LC 206  Reverse List       copy values to an array, rewrite them      19_fallbacks.py:491
    LC 35   Search Insert      linear scan for the first index >= target  19_fallbacks.py:442
    LC 102  Level Order        DFS carrying depth, append to res[depth]   19_fallbacks.py:159
    LC 207  Course Schedule    Kahn's indegree BFS, not 3-color DFS      19_fallbacks.py:255
    LC 215  Kth Largest        sort, return nums[n-k]                     19_fallbacks.py:344
    LC 78   Subsets            iterative: per num, duplicate every        19_fallbacks.py:390
                               subset so far and append num to it
    LC 98   Validate BST       inorder into a list, check increasing      19_fallbacks.py:178
    LC 236  LCA                root-to-node path for each, walk to        19_fallbacks.py:197
                               the last shared node
    LC 743  Network Delay      Bellman-Ford, no heap                      19_fallbacks.py:281
    LC 153  Find Minimum       min(nums)                                  19_fallbacks.py:451
    LC 347  Top K Frequent     count, sort by count, take k               19_fallbacks.py:351
    LC 136  Single Number      count in a hash map                        19_fallbacks.py:475
    LC 238  Product Except Self prefix and suffix arrays                  19_fallbacks.py:508
    LC 994  Rotting Oranges    rescan the grid until nothing rots         19_fallbacks.py:226
    LC 322  Coin Change        memoized recursion, top down               19_fallbacks.py:319
    LC 46   Permutations       backtracking IS the accepted answer        07_backtracking.py:87
    LC 253  Meeting Rooms II   sort starts and ends separately, sweep     19_fallbacks.py:365

LC 46 is the exception with no separate entry: the pointer is the real solution,
because there is nothing simpler to fall back to.

These are correct but TLE — full credit in an interview, red on LeetCode.

    LC 3    Longest Substring  per start, extend with a seen-set          19_fallbacks.py:80
    LC 739  Daily Temperatures per i, scan right for a warmer day         19_fallbacks.py:462
    LC 53   Maximum Subarray   every (start, end) with a running sum      19_fallbacks.py:306
    LC 56   Merge Intervals    merge any overlapping pair, repeat         19_fallbacks.py:403
    LC 724  Pivot Index        sum left and right at every i              19_fallbacks.py:590
    LC 167  Two Sum II         ignore sortedness, double loop             19_fallbacks.py:69
    LC 560  Subarray Sum K     every (start, end) with a running sum      19_fallbacks.py:605
    LC 209  Min Subarray Sum   every start, extend until feasible         19_fallbacks.py:95
    LC 424  Longest Char Repl. every start, count the majority char       19_fallbacks.py:111
    LC 438  Find All Anagrams  rebuild the window's counts per start      19_fallbacks.py:134
    LC 1109 Flight Bookings    loop each booking over its whole range     19_fallbacks.py:579
    LC 55   Jump Game          DP over which indices are reachable        19_fallbacks.py:427
    LC 146  LRU Cache          dict plus a list, move-to-front on get     19_fallbacks.py:537

No fallback exists for the rest — the standard solution already is the simplest
thing, so blanking on it means reviewing it, not routing around it.

    LC 104  Maximum Depth       the recursion is three lines
    LC 200  Number of Islands   DFS flood fill; union-find is harder, not easier
    LC 20   Valid Parentheses   the stack beats repeatedly deleting "()"
    LC 226  Invert Binary Tree  swap and recurse, nothing to strip out
    LC 133  Clone Graph         traversal plus a visited map either way
    LC 394  Decode String       a recursive parser is the same work as the stack

Constraint claims in those comments are LeetCode limits as of writing. If a
green one starts TLEing, they retuned it — move it down a block.


## When the core gets easy

Swap in the harder sibling, keep the same slot. Only ever swap two or three at
a time — the core's job is speed, and a core of all-hard problems stops being a
warmup.

    LC 1   -> LC 895   Freq Stack                    16_composing_structures.py:155
    LC 125 -> LC 15    Three Sum                     01_two_pointers.py:35
    LC 3   -> LC 76    Minimum Window Substring      02_sliding_window.py:95
    LC 724 -> LC 974   Subarray Sums Divisible by K  18_prefix_sum.py:94
    LC 20  -> LC 224   Basic Calculator              10_stack.py:197
    LC 739 -> LC 84    Largest Rectangle Histogram   10_stack.py:334
    LC 206 -> LC 25    Reverse Nodes in k-Group      12_linked_list.py:75
    LC 35  -> LC 875   Koko Eating Bananas           09_binary_search.py:183
    LC 104 -> LC 124   Binary Tree Maximum Path Sum  03_trees.py:312
    LC 102 -> LC 297   Serialize/Deserialize Tree    03_trees.py:409
    LC 200 -> LC 417   Pacific Atlantic Water Flow   04_graphs.py:44
    LC 207 -> LC 269   Alien Dictionary              04_graphs.py:206
    LC 215 -> LC 295   Find Median from Stream       06_heap.py:95
    LC 78  -> LC 51    N-Queens                      07_backtracking.py:257
    LC 53  -> LC 152   Maximum Product Subarray      05_dp.py:101
    LC 56  -> LC 2406  Divide Intervals into Groups  08_greedy.py:71

Rotation problems escalate on their own: when a day is easy, take the next
problem down in the same `pattern_code/` file. The files are ordered easy to
hard for exactly this.
