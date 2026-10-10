# Stack

**In one line:** A pile you can only touch from the top — the last thing you put
in is the first thing you take out.

**Assumes you know:** Python lists, `append` and `pop`, big-O. You have written
`is_valid_parentheses` and want to know what makes it a stack problem rather
than a counting problem, and what else has that shape.

**Not covered:** the monotonic stack — a stack you keep sorted by discarding, a
different idea built on this one; see
[monotonic-stack.md](monotonic-stack.md). Nor the queue, which is this structure
with the other end open; see [Related](#related).

## ELI5

A stack of plates in a cupboard. You put a clean plate on top, you take the top
plate off, and the plate you used most recently is the one you meet first. The
plate at the bottom is the one that has been waiting longest, and it leaves last.

**Where the analogy breaks:** in two places, and both matter.

Nothing physically stops you reading the middle of a Python list — `stack[3]`
works fine. The restriction is a discipline you impose, and the discipline is
what buys you the guarantee. The moment you index into the middle, you no longer
have a stack, you have a list, and none of the reasoning below applies.

And plates only ever hold plates. Stack entries hold whatever the problem needs
to *resume later*: a character, an index, a `(string, count)` pair, a whole
suspended computation. Choosing what one entry carries is most of the work in
these problems — Examples 1 to 3 climb exactly that axis.

## Actually

A stack is a container with three operations, all O(1), and one rule:

    push(x)     add x to the top
    pop()       remove and return the top item
    peek()      read the top item without removing it

The rule is **LIFO**: last in, first out. That is the whole definition. Every
stack problem is a problem where "the most recent unresolved thing" is exactly
the thing you need next.

In Python a plain `list` is the stack — there is no separate type to import:

    push        stack.append(x)      O(1) amortized
    pop         stack.pop()          O(1)
    peek        stack[-1]            O(1), does NOT remove
    is empty    if not stack:        never `len(stack) == 0`

`pop()` and `append()` act on the *end* of the list, which is why they are cheap.
`pop(0)` and `insert(0, x)` act on the front, cost O(n) each because every other
element shifts, and mean you wanted a queue — use `collections.deque`.

The tell, in a problem statement:

    "matching" / "balanced" / "nested"    pairs resolve innermost-first
    "most recent" / "last" / "undo"       LIFO stated outright
    "nearest X to the left/right"         monotonic stack (separate page)
    "evaluate this expression"            operators pend until their operands land

Depth is the other half. A stack's *height* is how deeply nested you currently
are, so anything that must know "how far in am I" reads `len(stack)`, and
anything that unwinds one level reads a `pop`.

The call stack is the same structure, run by the interpreter: each pending
function call is a frame pushed on entry and popped on return. That is not an
analogy — it is why any recursive solution can be rewritten with an explicit
stack, and why `RecursionError` at ~1000 frames has no counterpart in a stack
you manage yourself (see [recursion.md](recursion.md)).

## The picture

```
push a    push b    push c     pop       pop       push d
                    +---+
          +---+     | c | <-top
          | b |     | b |     +---+
+---+     | b |     | a |     | b | <-t  +---+     +---+
| a |<-t  | a |<-t  | a |     | a |      | a |<-t  | d |<-t
+---+     +---+     +---+     +---+      +---+     | a |
                                                   +---+
  a         ab        abc       ab         a         ad
```

Only the top face is reachable. `c` was pushed after `b` and left before it.

```
s =  3 [ a 2 [ c ] ]
     ^   ^     ^ ^ ^
     |   |     | | +-- pop: level 0 resumes, "" + "acc"*3
     |   |     | +---- pop: level 1 resumes, "a" + "c"*2
     |   |     +------ deepest point, len(stack) == 2
     |   +------------ push ("a", 2): level 1 suspended
     +---------------- push ("", 3):  level 0 suspended
```

Stack height *is* nesting depth. Each `[` suspends a level, each `]` resumes one,
and the entries are the levels waiting — this is Example 3.

## Example 1 — the smallest thing that works

```python
stack = []
stack.append("a")
stack.append("b")
stack.append("c")

print(stack[-1])        # c      peek: top, still on the stack
print(stack.pop())      # c      pop: top, now gone
print(stack.pop())      # b
print(stack)            # ['a']  a has waited the whole time
```

Three pushes and two pops. `c` arrived last and left first; `a` arrived first
and is still sitting there. An entry here is a raw value — nothing is remembered
about it beyond itself.

## Example 2 — the version you'll actually write

`pattern_code/10_stack.py:11`:

```python
def is_valid_parentheses(s: str) -> bool:  # LC 20
    pairs = {")": "(", "]": "[", "}": "{"}  # invariant: closer -> the opener it demands
    stack: list[str] = []                   # invariant: openers still unclosed, innermost last
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False                # closer must match MOST RECENT opener
        else:
            stack.append(ch)
    return not stack                        # leftovers = openers never closed

print(is_valid_parentheses("([{}])"))       # True
print(is_valid_parentheses("([)]"))         # False   counts match, nesting does not
print(is_valid_parentheses("((("))          # False   stack not empty at the end
```

**Adds:** an entry is now an *obligation*, not a value — every `(` on the stack
is a promise still owed a `)`. That reframing is what makes the stack mandatory:
counting openers and closers accepts `"([)]"`, because a count cannot say which
opener a closer is standing in front of. LIFO can, and it is the definition of
correct nesting.

Three ways the function returns, and each is a different failure:

    stack.pop() != pairs[ch]   closer met the wrong opener      "([)]"
    not stack                  closer met nothing at all        ")("
    not (return not stack)     openers left owed at the end     "((("

Miss the last line and `"((("` passes. It is the most common LC 20 bug and it
survives every test case that ends balanced.

## Example 3 — where it gets subtle

`pattern_code/10_stack.py:228`:

```python
def decode_string(s: str) -> str:  # LC 394
    stack: list[tuple[str, int]] = []   # invariant: (string before this group, its repeat count)
    cur, num = "", 0                    # invariant: cur = text built at this nesting level
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)    # multi-digit: 12[a] not 1,2[a]
        elif ch == "[":
            stack.append((cur, num))    # snapshot outer string + multiplier
            cur, num = "", 0
        elif ch == "]":
            outer, k = stack.pop()
            cur = outer + cur * k
        else:
            cur += ch
    return cur

print(decode_string("3[a2[c]]"))        # accaccacc
print(decode_string("2[abc]3[cd]ef"))   # abcabccdcdcdef
```

**Adds:** the entry is a *suspended computation* — the work you had half-finished
when you were interrupted. Two details follow that Example 2 never forced.

What gets pushed is the **outer** state, not the inner one. At `[` you park the
string built so far along with the multiplier that will apply to what comes next,
then start the inner level from empty. Pushing `cur` after clearing it, or
pushing `num` without `cur`, both typecheck and both produce garbage.

The thing you are building — `cur` — is deliberately *not* on the stack. It lives
in a local, and the pop is what merges it back into the level below. A stack
holds what is waiting; the active level is not waiting.

Trace `3[a2[c]]`:

```
ch   action                         stack                cur           num
3    num = 3                        []                   ""            3
[    push ("", 3), reset            [("",3)]             ""            0
a    cur += "a"                     [("",3)]             "a"           0
2    num = 2                        [("",3)]             "a"           2
[    push ("a", 2), reset           [("",3), ("a",2)]    ""            0
c    cur += "c"                     [("",3), ("a",2)]    "c"           0
]    pop ("a",2) -> "a" + "c"*2     [("",3)]             "acc"         0
]    pop ("",3)  -> "" + "acc"*3    []                   "accaccacc"   0
```

The same shape drives LC 224 (`:197`, sums instead of strings) and LC 71
(`:255`, where `..` pops a directory). Recognizing "snapshot, descend, merge on
the way out" is worth more than any one of them.

## Gotchas

- **Popping an empty stack** — `IndexError: pop from empty list`. Guard with
  `if not stack` *before* the pop, never after. In these problems the empty pop
  is almost always meaningful rather than exceptional: LC 921 counts it as a
  repair needed (`pattern_code/10_stack.py:33`), LC 71 ignores it because `..`
  at the root stays at the root (`:255`).

- **`stack.pop()` where you meant `stack[-1]`** — peek reads, pop consumes, and
  a stray pop corrupts the structure for every later iteration rather than
  failing where you wrote it. Reach for `stack[-1]` whenever the entry still has
  work left to do.

- **`pop(0)` or `insert(0, x)`** — O(n) per call, so an O(n) loop silently
  becomes O(n²), and the LIFO reasoning no longer holds because you are taking
  from the wrong end. If you actually want FIFO, `collections.deque` with
  `append` / `popleft` is O(1).

- **Forgetting the end-of-loop check** — the stack is rarely empty when the loop
  ends, and its leftovers mean something specific every time: unclosed openers
  (LC 20), unanswered elements (LC 739), unmeasured bars (LC 84). Decide what
  survivors mean before you write the loop.

- **Pushing values when the answer needs a position** — `stack.append(nums[i])`
  works right up until the question is "how far" rather than "which", and there
  is no way back. Push `i`, read `nums[stack[-1]]`; see
  [monotonic-stack.md](monotonic-stack.md).

- **Porting to Java or C++ from muscle memory** — `java.util.Stack` is a legacy
  synchronized class; use `ArrayDeque` with `push` / `pop` / `peek`. In C++,
  `std::stack::pop()` returns `void` — read `top()` first, then `pop()`. Both
  bite on a whiteboard, neither shows up in Python.

## Where to practice

In this order, all in `pattern_code/10_stack.py`:

    LC 20    Valid Parentheses      :11    the pattern, undisguised
    LC 921   Min Add to Make Valid  :33    one bracket type -> a counter suffices
    LC 150   Evaluate RPN           :145   entries are operands awaiting an operator
    LC 394   Decode String          :228   entries are suspended contexts
    LC 71    Simplify Path          :255   the surviving stack IS the answer
    LC 155   MinStack               :304   each frame stores its own min
    LC 224   Basic Calculator       :197   LC 394's shape, arithmetic instead of text

LC 20 is in the daily core (`docs/daily_warmup.md:26`); LC 224 is its escalation
(`docs/daily_warmup.md:213`). LC 921 is the one to notice: it proves a stack of
identical symbols is a counter, and knowing when *not* to reach for the structure
is the same skill as knowing when to.

## Related

- **Monotonic stack** (`docs/concepts/monotonic-stack.md`) — a stack with an
  extra invariant: entries stay sorted, and you discard whatever the newest
  element makes irrelevant. Everything on this page still holds; the pops just
  carry answers with them.

- **Queue** — the same container with the *other* end open: FIFO, first in first
  out. Stack for "most recent unresolved", queue for "oldest unserved" (BFS level
  order, `pattern_code/03_trees.py`). `collections.deque` is both.

- **Recursion** (`docs/concepts/recursion.md`) — the call stack is a stack you
  do not manage. Any recursive traversal converts to an explicit one; do it when
  depth would blow the recursion limit, or when you need to inspect the pending
  frames, which recursion will not let you do.

- **`MinStack`** (`pattern_code/10_stack.py:304`) — a stack whose entries carry
  a running minimum, so `get_min` is O(1) and popping restores history for free.
  The clean demonstration that an entry can be anything you want.

- **Backtracking** (`pattern_code/07_backtracking.py`) — the choose / explore /
  un-choose loop is a stack of decisions, usually the call stack plus a `path`
  list that pushes and pops in lockstep with it.

## Sources

- `pattern_code/10_stack.py` — the verified reference implementations this page
  cites, each with its own naive baseline and invariants.
- Python tutorial, section 5.1.1 "Using Lists as Stacks" — `append` / `pop` as
  the stack API, and 5.1.2 for why the front of a list is the wrong end:
  https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks
- CLRS, section 10.1 "Stacks and queues" — `PUSH` / `POP` with the underflow
  condition stated as part of the definition.
