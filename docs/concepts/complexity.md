# Data Structure Complexity

**In one line:** How the cost of each operation on each data structure grows as
the structure holds more items — the numbers you quote when an interviewer asks
"what's the runtime?"

**Assumes you know:** Big-O notation, and what each structure is. You want the
numbers in one place, plus the Python operations that are secretly slower than
they look.

**Not covered:** Sorting and graph-algorithm complexities, and deriving
recurrences (master theorem) — this sheet is per-operation costs only.

## ELI5

Each data structure is a different way of shelving books. A numbered shelf
(array) lets you grab book #500 instantly, but squeezing a new book into the
middle means sliding every book after it over one slot. A card catalog (hash
map) tells you exactly where any title is, but can't tell you "the next title
alphabetically". A library sorted by title (balanced BST) can answer that, but
every lookup takes a few steps of "left half or right half?". Complexity is
just counting those steps as the library grows.

**Where the analogy breaks:** in two places.

A librarian's steps cost the same every time. A computer's don't: a Python
`list` occasionally copies the whole shelf to a bigger one when it fills up.
That one append is O(n), but it happens rarely enough that the average stays
O(1) — that is what "amortized" means below.

And a real catalog never collides. A hash map can: if many keys land in the
same bucket, lookup degrades to O(n). Interviews accept O(1) "average"; say
"O(n) worst case" if asked.

## Core operations

`n` = items stored. `a` = amortized. `avg` = average case, worst in brackets.

    Structure             Access    Search    Insert         Delete         Space
    Array (fixed)         O(1)      O(n)      O(n)           O(n)           O(n)
    Dynamic array / list  O(1)      O(n)      O(1)a end      O(1) end       O(n)
                                              O(n) middle    O(n) middle
    Sorted array          O(1)      O(log n)  O(n)           O(n)           O(n)
    Singly linked list    O(n)      O(n)      O(1) at head   O(1) at head   O(n)
    Doubly linked list    O(n)      O(n)      O(1) at node   O(1) at node   O(n)
    Stack                 O(1) top  O(n)      O(1) push      O(1) pop       O(n)
    Queue / deque         O(1) ends O(n)      O(1) ends      O(1) ends      O(n)
    Hash map / set        n/a       O(1) avg  O(1) avg       O(1) avg       O(n)
                                    [O(n)]    [O(n)]         [O(n)]
    Binary heap           O(1) top  O(n)      O(log n)       O(log n) top   O(n)
    BST, balanced         O(log n)  O(log n)  O(log n)       O(log n)       O(n)
    BST, unbalanced       O(n)      O(n)      O(n)           O(n)           O(n)
    Trie                  n/a       O(L)      O(L)           O(L)           O(total chars)
    Union-Find            n/a       O(α(n))   O(α(n)) union  n/a            O(n)
    Segment tree          O(log n)  n/a       O(log n) upd   n/a            O(n)
    Fenwick tree (BIT)    O(log n)  n/a       O(log n) upd   n/a            O(n)
    Prefix sum array      O(1)      n/a       O(n) rebuild   O(n) rebuild   O(n)

    L       length of the key/word, independent of how many words are stored
    α(n)    inverse Ackermann; ≤ 4 for any real input, say "effectively O(1)"
            — only with BOTH path compression and union by rank/size
    "at node"  O(1) only if you already hold a pointer to the node;
               finding it first is O(n)

## Build costs

Building is not always n × insert. Two of these beat the naive bound.

    Heap from n items (heapify)     O(n)        not O(n log n)
    Segment tree from n items       O(n)
    Fenwick tree from n items       O(n log n)  O(n) with the parent-push trick
    Prefix sum array                O(n)
    Hash map from n items           O(n) avg
    Balanced BST from n items       O(n log n)  O(n) if input already sorted
    Sorted array                    O(n log n)  that's the sort

## Range and order queries

What each structure can answer beyond "is x here?".

    Min/max                 heap O(1) peek; balanced BST O(log n); hash map O(n)
    k-th smallest           sorted array O(1); heap O(k log n); BST O(log n) with sizes
    Successor / floor       sorted array O(log n); balanced BST O(log n); hash map no
    Range sum, static       prefix sum O(1) per query
    Range sum, with updates segment tree or BIT, O(log n) query and update
    Range min, static       sparse table O(1) query, O(n log n) build
    Sliding window max      monotonic deque, O(1) amortized per step
    Next greater element    monotonic stack, O(n) total — see monotonic-stack.md

## Graph representations

`V` = vertices, `E` = edges.

                        Adjacency list    Adjacency matrix
    Space               O(V + E)          O(V²)
    Edge (u,v) exists?  O(deg u)          O(1)
    All neighbors of u  O(deg u)          O(V)
    Add edge            O(1)              O(1)
    BFS / DFS           O(V + E)          O(V²)

    Grid of R×C         V = R·C, E ≈ 4·R·C, so BFS/DFS is O(R·C)

Default to the list. The matrix only wins on dense graphs (E near V²) or
when you need constant-time edge lookup, e.g. Floyd-Warshall.

## Python traps

Operations that look O(1) but are not. These are the ones that turn an O(n)
solution into O(n²) in an OA.

    list.pop(0)              O(n)   shifts everything; use deque.popleft()
    list.insert(0, x)        O(n)   use deque.appendleft()
    x in list                O(n)   use a set if you check repeatedly
    list.remove(x)           O(n)   searches, then shifts
    list.index(x)            O(n)
    a[i:j] slicing           O(j-i) copies; recursion on slices is O(n²) total
    a + b                    O(len a + len b) builds a new list
    s += c in a loop         O(n²)  strings are immutable; append to a list, "".join
    deque[i] in the middle   O(n)   deque is a linked list of blocks
    min(list), max(list)     O(n)   a heap if you need it more than once
    sorted(x), list.sort()   O(n log n)
    len(x)                   O(1)   stored, never counted
    heapq.heappush / pop     O(log n)
    heapq.heapify            O(n)
    dict / set iteration     O(n)   plus capacity; fine in practice
    set(a) & set(b)          O(min(len a, len b)) avg

Python has no built-in balanced BST. `heapq` is a min-heap only — push `-x`
for a max-heap. `sortedcontainers.SortedList` gives O(log n) insert and is
usually unavailable in OAs.

## Java / C++ names

The OA reference solutions are Java/C++, so the same costs under their names:

    Concept            Java                    C++
    Dynamic array      ArrayList               vector
    Deque              ArrayDeque              deque
    Hash map / set     HashMap / HashSet       unordered_map / unordered_set
    Balanced BST       TreeMap / TreeSet       map / set
    Heap               PriorityQueue (min)     priority_queue (max!)
    Linked list        LinkedList              list

    TreeMap / std::map give floor/ceiling/successor in O(log n) —
    the operation Python has no built-in for.
    C++ priority_queue is a MAX-heap by default; Java's is a MIN-heap.
    Java String += in a loop is O(n²) for the same reason as Python; use
    StringBuilder.

## Saying it out loud

    State the variable:   "O(n) where n is the length of nums", not just "O(n)"
    Two inputs:           O(n + m), not O(n) — don't merge them
    Amortized:            "O(1) amortized" for list append and monotonic stacks
    Hash maps:            "O(1) average" — say it before they ask
    Space:                count the output separately if asked; recursion
                          depth counts as space (O(h) for a tree DFS)

## Related

    docs/concepts/recursion.md         call-stack depth as space cost
    docs/concepts/monotonic-stack.md   why O(n) total despite a nested loop
    docs/concepts/prefix-suffix.md     prefix sum build and query
