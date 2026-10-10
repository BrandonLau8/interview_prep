# Tells

A tell is a phrase or constraint in a problem statement that names the
technique for you. This page maps tells to techniques, then techniques to the
idioms in the three warmup files.

Assumes you know: the idioms in `docs/array_warmup.md`,
`docs/structure_warmup.md`, and `docs/search_warmup.md`, or at least their
summary blocks.
Not covered: how each idiom works. Look up its name in the warmup file listed
next to it.


## ELI5

A doctor doesn't run every test on every patient. A fever plus a rash narrows
the cause to a handful of possibilities before any test is ordered, and the
test then confirms one of them. Tells are the symptoms. "Contiguous,"
"sorted," "k-th largest," and "n <= 20" each narrow the field to a few
techniques before you've written a line.

## Where the analogy breaks

A symptom points to a disease whether or not you check it. A tell only points
to a technique if its precondition holds. "Longest contiguous subarray" means
a sliding window only when the values can't be negative. Missing that check
doesn't slow you down. It gives you a confident wrong answer. That's why every
tell below has a precondition, and the last section lists the ones that fail
most often.


## The three steps

Before you write any code, answer these in order:

    1. budget        what does n allow?                    section "Constraints"
    2. tell          which phrase names a technique?       sections "Arrays" .. "Counting"
    3. precondition  does the technique's assumption hold? section "When the tell lies"

Then write it. Inside the technique, the idioms come from questions about the
next line (section "Choosing the idiom").

If you can't find a tell, write the brute force first. Its wasted work usually
names the technique:

    nested loop over all pairs              hash map, or opposite ends if sorted
    re-summing the same range               prefix with sentinel
    rescanning to the right for each i      monotonic stack, or a right-to-left pass
    re-finding the max of each window       monotonic deque
    re-sorting after each insert            heap
    recomputing the same subproblem         memo check first
    trying every value of the answer        binary search on the answer


## Constraints

n tells you the complexity you're allowed. Read it before the story.

    n <= 10           O(n!)         permutations: used array
    n <= 20           O(2^n)        subsets: bitmask, copy on record
    n <= 500          O(n^3)        triple loops, interval DP
    n <= 5,000        O(n^2)        all pairs, DP table
    n <= 10^5         O(n log n)    sort first, heap, lower bound
    n <= 10^6         O(n)          pointers, windows, prefix, hash map, monotonic stack
    values up to 10^9 O(log V)      binary search on the answer
    answer mod 1e9+7  the count is huge: DP or counting, never enumeration


## Arrays

    tell                                       technique              idioms (array_warmup.md)
    contiguous, longest/shortest, values >= 0  variable-size window   variable-size window
    contiguous, at most k distinct / no repeat variable-size window   window with counts
    exactly k consecutive elements             fixed-size window      fixed-size window
    subarray sum equals k, negatives allowed   prefix sum + map       frequency count, prefix sum + map
    many range-sum queries                     prefix sum             prefix with sentinel
    many range updates, read once at the end   difference array       running sum, inclusive
    answer at i uses everything left and right prefix + suffix passes running sum, exclusive; right-to-left pass
    best contiguous sum                        Kadane                 running sum, inclusive; running best
    buy before sell, pair i with an earlier j  min so far             min so far
    sorted, pair or triplet with a target      opposite ends          opposite ends
    in place, remove, keep relative order      reader / writer        reader / writer, swap with tmp
    only 2 or 3 distinct values, one pass      partition              Dutch flag
    shift or rotate with O(1) space            three reversals        opposite ends
    values in 1..n, O(1) extra space           index marking          index marking
    values in 1..n, read-only, find duplicate  fast / slow on indices fast / slow on indices
    merge into an array with spare room        overwrite from back    merge two sorted, right-to-left pass
    groups of equal neighbours                 run grouping           run grouping
    next greater/smaller, days until warmer    monotonic stack        monotonic stack
    max/min of every window of size k          monotonic deque        fixed-size window + monotonic stack
    complement seen earlier (two sum)          hash map               frequency count
    rotate or transpose a grid                 matrix in place        grid neighbours, opposite ends

## Linked lists and trees

    tell                                       technique              idioms (structure_warmup.md)
    the head might be removed or replaced      dummy head             dummy head
    reverse all or part of a list              pointer rewiring       reverse in place
    middle, halves, palindrome list            fast / slow            fast / slow middle, reverse in place
    cycle in a list                            fast / slow            fast / slow middle
    nth from the end, one pass                 gap                    kth from end
    combine sorted lists                       tail pointer           merge two sorted
    depth, size, sum of a tree                 return up              base case first
    root-to-leaf path condition                pass down              pass down
    longest path anywhere, may skip the root   return up, record both return up
    level by level, zigzag, right side view    BFS by level           BFS by level
    BST, sorted order, k-th smallest           inorder                iterative inorder
    validate BST                               bounds passed down     BST bounds

## Graphs and grids

    tell                                       technique              idioms (structure_warmup.md)
    islands, regions, flood fill               grid DFS               grid DFS
    connected components, provinces            DFS or union-find      mark before you recurse, union-find
    fewest steps, unweighted, minimum moves    BFS                    BFS shortest path
    edges added over time, redundant edge      union-find             union-find
    prerequisites, build order, schedule       topological sort       topological sort
    can all courses finish, directed cycle     cycle check            three colours, topological sort
    weighted edges, cheapest path              Dijkstra               Dijkstra (search_warmup.md)

## Search and ordering

    tell                                       technique              idioms (search_warmup.md)
    sorted, O(log n), insert position          binary search          lower bound (array_warmup.md)
    first and last position, count of x        two bounds             upper bound
    minimum X such that, minimize the maximum  binary search on answer lower bound + a can(x) check
    k-th largest, top k, k closest             heap of size k         heap (array_warmup.md)
    merge k sorted, repeatedly take the best   heap of tuples         heap of tuples, max-heap
    intervals: combine overlapping ones        sort by start          sort first (array_warmup.md)
    intervals: keep the most, remove fewest    sort by end            sort by end, overlap test
    sort by several fields                     tuple key              custom sort key
    reach the end, gas station                 greedy scan            greedy scan (array_warmup.md)

## Exploring and counting

    tell                                       technique              idioms (search_warmup.md)
    all subsets, combinations                  backtracking           choose/recurse/pop, copy on record
    all orderings                              backtracking           used array
    input has duplicates, distinct results     backtracking           skip duplicates
    unlimited use of each item                 backtracking           reuse and prune
    number of ways                             DP                     memo check first, memo key
    minimum cost or count, may be impossible   DP                     impossible sentinel
    two strings, edit / common subsequence     2-D DP                 DP table (structure_warmup.md)
    take or skip neighbours (house robber)     1-D DP                 DP over indices (array_warmup.md)
    count of ways to choose k from n           formula                n choose k
    every value appears twice except one       XOR                    XOR (array_warmup.md)
    count bits, power of two                   bit tricks             clear lowest bit
    n <= 20 and subsets as states              bitmask                get / set / clear, bitmask
    prefix search over a word list             trie                   insert / search

## Strings

    tell                                       technique              idioms (structure_warmup.md)
    anagram, permutation of, same letters      letter counts          char to index
    compress, encode, build an output string   build then join        build then join, run grouping
    counts written as digits in the input      parse numbers          multi-digit parse
    digits of an integer                       % 10, // 10            digit extraction
    longest substring with a condition         window with counts     window with counts (array_warmup.md)


## When the tell lies

Each technique assumes something. Check it before you commit:

    variable-size window   values >= 0; with negatives, shrinking can raise the sum: use prefix sum + map
    greedy scan            the local choice must be provably safe; if a counterexample exists, use DP
    binary search          the condition must flip exactly once; "sorted" alone isn't enough
    binary search on answer  can(x) must be monotone: if x works, x + 1 works
    BFS shortest path      every edge costs the same; weighted edges need Dijkstra
    Dijkstra               weights >= 0; a negative edge breaks "final when popped"
    union-find             undirected only; directed cycles need three colours
    break in backtracking  input must be sorted; otherwise use continue
    opposite ends          input must be sorted, or sorting must not lose the indices you return
    XOR                    exactly the pairs cancel; three copies of a value don't
    n choose k             no mod; under mod 1e9+7, use Pascal's rule in a DP table


## Choosing the idiom

Once you've chosen the technique, ask what the next line needs:

    do I need the previous element?                    adjacent pairs
    does out[i] include nums[i]?                       running sum, inclusive vs exclusive
    does the answer need both sides of i?              prefix + suffix passes
    may i pair with itself?                            min so far: use then update
    am I counting occurrences?                         frequency count, char to index, window with counts
    do I overwrite a value I still need?               swap with tmp, reverse in place (save next)
    is the output "past the end" possible?             lower bound: hi = n
    can the head of the list change?                   dummy head
    do I need to know which level I'm on?              BFS by level
    does the parent need something different
      from what I record?                              return up
    will a node be reached twice?                      mark before you recurse, mark on push
    can the same value be chosen at the same depth?    skip duplicates
    is "impossible" a possible answer?                 impossible sentinel
    will I use a mutable list as a result?             copy on record, 2-D init
    is a number accumulating across digits?            multi-digit parse
    might this overflow in Java?                       running sum (long), ceil division, n choose k


## Worked example

"Given an integer array `nums` (values may be negative, length up to 2·10^4)
and an integer k, return the number of contiguous subarrays whose sum equals
k."

    budget        n = 2·10^4: O(n^2) is 4·10^8, too slow; aim for O(n)
    tell          "contiguous subarrays" + "sum equals k": window, or prefix sum + map
    precondition  "may be negative": the window's shrink step fails, so prefix sum + map
    idioms        frequency count (the map), running sum inclusive (prefix),
                  check before insert (the k = 0 case)

The tell offered two techniques, and the precondition picked between them.
That happens most of the time: tells narrow the field, and preconditions
decide.
