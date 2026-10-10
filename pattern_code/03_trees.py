"""Patterns 12-17: Tree Traversal.

Core idea: pick the traversal order that delivers information when you need it.
Preorder = parent decides first (pass state DOWN as args).
Postorder = children report first (return state UP).
Inorder on a BST = sorted order.  BFS = process by depth.

Written deliberately plain (no Counter / enumerate / iterator or comprehension
tricks) so the logic ports 1:1 to Java, C++, Go, JS on a whiteboard. Where a
recursive helper needs a shared cursor, it is a one-element list — stand-in for
the by-reference int you would pass in those languages.
Run: python 03_trees.py
"""
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# --------------------------------------------------------------- Pattern 12
# Level order: snapshot len(queue) at loop start = exactly one level.
def level_order(root: TreeNode | None) -> list[list[int]]:  # LC 102
    """Node values level by level, one list per depth.
    The queue holds exactly one level's boundary at a time, so snapshotting
    len(q) at the top of the loop fences off precisely that level — children
    pushed during the sweep fall beyond the fence and wait their turn.

    Naive: find the height, then re-walk the tree once per depth collecting
    the nodes at that depth — O(n * h). The queue emits each level in one pass.

    Real life: a phone tree worked floor by floor — you finish writing down
    this floor's names before anyone they call gets dialled (crawling a site
    one link-hop at a time)."""
    if not root:
        return []
    res, q = [], deque([root])             # invariant: q holds exactly one full level
    while q:
        level = []
        for _ in range(len(q)):  # only the nodes already in the queue
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        res.append(level)
    return res


def right_side_view(root: TreeNode | None) -> list[int]:  # LC 199
    # DEAD CODE: the definition below shadows this one at import time, so
    # nothing ever calls it. Kept as the compact phrasing of the same idea —
    # right side view = last node of each level.
    res = []
    for level in level_order(root):
        res.append(level[len(level) - 1])
    return res


def right_side_view(root: TreeNode | None) -> list[int]:  # LC 199 — the live one
    """The values you see looking at the tree from the right.
    Not the right spine: a deep left subtree shows through wherever the right
    side has run out. Framed by level it is simply the last node of each
    level, which BFS already produces — so the whole problem is the reframing.

    Naive: DFS recording depth -> value for every node, then read the last
    write per depth — same O(n), but correctness now rests on visit order.

    Real life: standing to the right of a hedge and noting the outermost leaf
    at each height — a branch further left still shows if nothing blocks it."""
    def level_order(root):
        if not root:
            return []
        res = []
        q = deque()
        q.append(root)
        while q:
            level = []
            for _ in range(len(q)):
                node = q.popleft()
                level.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)

            res.append(level)
        return res

    res = []
    for level in level_order(root):
        res.append(level[-1])
    return res


def zigzag_level_order(root: TreeNode | None) -> list[list[int]]:  # LC 103
    # Level order with every other level reversed.
    # The traversal itself never changes — only the presentation does, so
    # reverse odd levels afterwards instead of complicating the queue.
    # Naive: alternate which end you push and pop per level — same output,
    # more state to get wrong.
    # Real life: reading a boustrophedon inscription, every second line
    # running right to left.
    levels = level_order(root)
    res = []
    for i in range(len(levels)):
        if i % 2 == 0:
            res.append(levels[i])
        else:
            reversed_level = []
            for j in range(len(levels[i]) - 1, -1, -1):   # explicit walk, not [::-1]
                reversed_level.append(levels[i][j])
            res.append(reversed_level)
    return res


# --------------------------------------------------------------- Pattern 13
# Preorder: everything you need is known BEFORE recursing.
def is_same_tree(p: TreeNode | None, q: TreeNode | None) -> bool:  # LC 100
    """Do two trees match in both shape and values?
    Preorder: the parent settles its own comparison before recursing, so the
    first mismatch aborts the whole walk. `p is q` covers both base cases at
    once — both None is True, exactly one None is False.

    Naive: serialize both trees and compare the strings — still O(n), but it
    builds two full encodings and cannot stop at the first difference.

    Real life: two people reading one recipe aloud in lockstep — the first
    line that differs ends it; nobody finishes the page to be sure."""
    if not p or not q:
        return p is q  # both None -> True, one None -> False
    return (p.val == q.val
            and is_same_tree(p.left, q.left)
            and is_same_tree(p.right, q.right))


def invert_tree(root: TreeNode | None) -> TreeNode | None:  # LC 226
    """Mirror the tree left to right.
    Every node's job is identical and purely local: swap my two children,
    then let them do the same. The tuple assignment is load-bearing — writing
    root.left first would make the second call read what it just overwrote.

    Naive: build a whole new mirrored tree node by node — O(n) extra space
    for a transformation that never needs to look outside one node.

    Real life: holding a mobile up to a mirror — nothing moves relative to
    its own parent, the entire thing simply reads reversed."""
    if root:
        root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


def build_tree(preorder: list[int], inorder: list[int]) -> TreeNode | None:  # LC 105
    """Rebuild a binary tree from its preorder and inorder traversals.
    preorder[0] is always the root, and locating it in inorder splits the rest
    into exactly the left and right subtrees. Preorder hands out roots in the
    same order the recursion wants them, so one shared cursor does the job.

    Naive: search inorder for the root at every level and slice both lists —
    O(n^2) time plus O(n^2) copying. The index dict makes each split a lookup.

    Real life: chapter titles in outline order plus the pages in reading
    order — the first title is the top section, and where it falls in the
    page order says which pages hang under its left and right halves."""
    idx = {}                               # invariant: value -> its position in inorder
    for i in range(len(inorder)):
        idx[inorder[i]] = i
    pre_pos = [0]                          # invariant: next unconsumed preorder index; a list so build() can mutate it

    def build(lo: int, hi: int) -> TreeNode | None:  # inorder slice [lo, hi)
        if lo >= hi:
            return None
        root = TreeNode(preorder[pre_pos[0]])   # preorder feeds roots in order
        pre_pos[0] = pre_pos[0] + 1
        mid = idx[root.val]
        root.left = build(lo, mid)  # left subtree consumed first — same
        root.right = build(mid + 1, hi)  # order preorder emits it
        return root

    return build(0, len(inorder))


def binary_tree_paths(root: TreeNode) -> list[str]:  # LC 257
    """Every root-to-leaf path, arrow-joined.
    Preorder with state flowing DOWN as an argument: each leaf already holds
    its whole history the moment it is reached. Because the path is passed by
    value there is nothing to undo on the way back up — no shared buffer.

    Naive: on reaching a leaf, re-descend from the root to recover how you
    got there (no parent pointers exist here) — O(n * h) of repeated walking.

    Real life: hikers carrying a written trail log and copying it at each
    fork — whoever hits a dead end is already holding the full route."""
    res: list[str] = []

    def dfs(node: TreeNode, path: str) -> None:  # path flows DOWN
        path += str(node.val)
        if not node.left and not node.right:
            res.append(path)
            return
        for child in (node.left, node.right):
            if child:
                dfs(child, path + "->")

    dfs(root, "")
    return res


# --------------------------------------------------------------- Pattern 14
# Inorder on a BST visits values in sorted order -> "sorted array" questions
# become a walk with a prev pointer.
def is_valid_bst(root: TreeNode | None) -> bool:  # LC 98
    """Is this a valid BST — every left descendant smaller, every right larger?
    Inorder on a BST emits sorted values, so validity collapses to "is this
    sequence strictly rising?", which one prev variable answers. Checking a
    node only against its parent is the classic wrong answer — it misses the
    ancestor bounds a grandchild can violate.

    Naive: for every node, scan its left subtree for a max and right for a
    min — O(n^2). The inorder walk gets the same guarantee in one pass.

    Real life: verifying a filing cabinet is truly alphabetized by reading
    front to back — one folder out of order condemns it, however tidy each
    drawer looks on its own."""
    prev = None                            # invariant: value of the last node inorder, or None

    def inorder(node: TreeNode | None) -> bool:
        nonlocal prev
        if not node:
            return True
        if not inorder(node.left):
            return False
        if prev is not None and node.val <= prev:  # must be strictly rising
            return False
        prev = node.val
        return inorder(node.right)

    return inorder(root)


def kth_smallest(root: TreeNode, k: int) -> int:  # LC 230
    """kth smallest value in a BST, 1-indexed.
    Inorder is sorted order, so this is "walk sorted, stop after k". The
    explicit stack exists purely to make that early exit possible — recursive
    inorder would visit everything or thread a stop flag back through frames.

    Naive: collect all values inorder, then index — O(n) time and space even
    when k is 1. The stack pays only for the nodes it actually reaches.

    Real life: counting to the kth name in an alphabetized ledger and shutting
    the book — the remaining pages never get read."""
    stack: list[TreeNode] = []             # invariant: ancestors of node whose values are still unvisited
    node = root
    while True:  # iterative inorder: stop early at k
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right


# --------------------------------------------------------------- Pattern 15
# Postorder: children report, parent combines.
def max_depth(root: TreeNode | None) -> int:  # LC 104
    """Postorder at its simplest: a node cannot know its depth until both
    children have reported theirs, so the answer flows UP. One line, because
    the combine step is just max plus one for the current level.

    Naive: BFS counting levels — the same O(n), but it needs an explicit
    queue; the recursion reuses the call stack you already have.

    Real life: asking each manager "how many levels report below you?" and
    answering one more than your deepest report."""
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def diameter_of_binary_tree(root: TreeNode | None) -> int:  # LC 543
    """Longest path between any two nodes, counted in edges.
    The trap is that the answer usually does not pass through the root. So
    return the CONSTRAINED value a parent can use — downward height — and
    track the UNCONSTRAINED answer, the path bending here (lh + rh), aside.

    Naive: at every node compute left and right height with separate walks —
    O(n^2), since each height call re-walks what its caller just walked.

    Real life: the longest corridor in an office runs wing to wing through
    some junction, not through the front door — but each wing still reports
    only its own depth to whoever is measuring."""
    best = 0                               # invariant: longest path seen bending through any node so far

    def height(node: TreeNode | None) -> int:
        nonlocal best
        if not node:
            return 0
        lh, rh = height(node.left), height(node.right)
        best = max(best, lh + rh)  # path bends through this node
        return 1 + max(lh, rh)  # only one arm continues upward

    height(root)
    return best


def max_path_sum(root: TreeNode) -> int:  # LC 124 — same skeleton as diameter
    """Largest sum along any path between two nodes; values may be negative.
    Same return-constrained / track-unconstrained shape as LC 543, plus one
    move: max(gain, 0) means a branch that costs you is simply not entered.
    That clamp is what encodes "the path may start and end anywhere".

    Naive: enumerate all O(n^2) node pairs and sum the path between each —
    O(n^3) with no preprocessing.

    Real life: the most profitable route through a chain of shops when some
    lose money — you stop before the loss-making wing rather than pay to
    pass through it."""
    best = float("-inf")                   # invariant: best path seen bending through any node so far

    def gain(node: TreeNode | None) -> int:
        nonlocal best
        if not node:
            return 0
        lg = max(gain(node.left), 0)  # negative branch: don't take it
        rg = max(gain(node.right), 0)
        best = max(best, node.val + lg + rg)
        return node.val + max(lg, rg)

    gain(root)
    return best


def rob_tree(root: TreeNode | None) -> int:  # LC 337 House Robber III
    """Max loot from a tree where robbing a node forbids robbing its children.
    One number per subtree is not enough — the parent's choice depends on
    whether the child was taken. Return BOTH, best-if-robbed and
    best-if-skipped, and the conflict resolves locally with no global search.

    Naive: enumerate every independent set of nodes and score it —
    exponential. Splitting the report by "was the root taken?" gives two numbers.

    Real life: deciding which relatives to ask for money when no two directly
    related people will both say yes — each branch reports its best answer
    under both assumptions, and you choose after hearing them."""
    def dfs(node: TreeNode | None) -> tuple[int, int]:  # invariant: returns (best if robbed, best if skipped)
        if not node:
            return 0, 0
        l_rob, l_skip = dfs(node.left)
        r_rob, r_skip = dfs(node.right)
        rob = node.val + l_skip + r_skip  # robbing here forbids children
        skip = max(l_rob, l_skip) + max(r_rob, r_skip)
        return rob, skip

    return max(dfs(root))


# --------------------------------------------------------------- Pattern 16
def lca_bst(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:  # LC 235
    """Lowest common ancestor of two nodes in a BST.
    The ordering answers "which subtree holds both?" in one comparison: above
    both, go left; below both, go right; between them, this node is the split
    point and therefore the LCA. No recursion and no return trip needed.

    Naive: the general LC 236 postorder search — correct, but O(n) and it
    throws away the ordering the BST is handing you.

    Real life: finding where two family lines meet in a surname-sorted
    register — you keep narrowing until one page holds both names."""
    lo, hi = min(p.val, q.val), max(p.val, q.val)   # invariant: the LCA's value lies in [lo, hi]
    node = root
    while node:
        if node.val < lo:
            node = node.right
        elif node.val > hi:
            node = node.left
        else:
            return node
    raise ValueError


def lca(root: TreeNode | None, p: TreeNode, q: TreeNode) -> TreeNode | None:  # LC 236
    """Lowest common ancestor in a plain binary tree — no ordering to exploit.
    Postorder: each subtree reports "did you find either target?" A node
    hearing from BOTH sides is the meeting point; a node hearing from one
    forwards it up untouched. The returned node is both the flag and the answer.

    Naive: build the root-to-node path for each target, then compare the two
    paths for their last shared entry — two passes and O(h) extra space.

    Real life: two hikers sending word back up a trail network — the first
    junction that hears from both is where their routes joined."""
    if root is None or root is p or root is q:
        return root
    left = lca(root.left, p, q)
    right = lca(root.right, p, q)
    if left and right:
        return root
    return left or right


# --------------------------------------------------------------- Pattern 17
# Preorder WITH null markers uniquely encodes a tree.
def serialize(root: TreeNode | None) -> str:  # LC 297
    """Encode a tree as a string deserialize can rebuild exactly.
    Preorder alone is ambiguous — many shapes produce the same value sequence.
    Writing "#" for every absent child pins the shape down, because the null
    markers record exactly where each subtree ended, making the encoding 1:1.

    Naive: emit preorder and inorder and rebuild via LC 105 — works, but only
    when all values are distinct, and it doubles the output.

    Real life: dictating an outline and saying "nothing under this heading"
    out loud — the empty slots are what let the listener restore the indenting."""
    parts: list[str] = []                  # invariant: preorder tokens, "#" for every missing child

    def dfs(node: TreeNode | None) -> None:
        if not node:
            parts.append("#")  # nulls pin the shape
            return
        parts.append(str(node.val))
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return ",".join(parts)


def deserialize(data: str) -> TreeNode | None:  # LC 297
    # Rebuild the tree from serialize's output.
    # Mirror image of serialize: the same preorder, one token consumed per
    # call, so the recursion's own shape reproduces the shape "#" recorded.
    # Naive: rescan the string for the next unconsumed token at every node —
    # O(n) per node, O(n^2) overall; the cursor just never looks backward.
    # Real life: taking that dictated outline back down, indenting as you hear it.
    vals = data.split(",")                 # invariant: preorder tokens, "#" for every missing child
    pos = [0]                              # invariant: next unconsumed token; a list so dfs() can mutate it

    def dfs() -> TreeNode | None:
        v = vals[pos[0]]
        pos[0] = pos[0] + 1
        if v == "#":
            return None
        node = TreeNode(int(v))
        node.left = dfs()  # consume in the same preorder
        node.right = dfs()
        return node

    return dfs()


def find_duplicate_subtrees(root: TreeNode | None) -> list[TreeNode]:  # LC 652
    """One representative root per subtree shape that occurs more than once.
    "Are these two subtrees identical?" becomes "do their canonical strings
    match?" — LC 297's encoding reused as a hash key. Reporting when the count
    hits exactly 2 emits each duplicate once, however many copies exist.

    Naive: compare every pair of subtrees node by node — O(n^2) comparisons
    at O(n) each. The encoding turns each comparison into a dict lookup.

    Real life: spotting repeated LEGO sub-assemblies by writing each one's
    build steps on a card and looking for two cards that read the same."""
    seen: dict[str, int] = {}              # invariant: encoding -> how many subtrees produced it
    res: list[TreeNode] = []

    def encode(node: TreeNode | None) -> str:
        if not node:
            return "#"
        left = encode(node.left)
        right = encode(node.right)
        key = str(node.val) + "," + left + "," + right
        if key in seen:
            seen[key] = seen[key] + 1
        else:
            seen[key] = 1
        if seen[key] == 2:  # report each duplicate once
            res.append(node)
        return key

    encode(root)
    return res


if __name__ == "__main__":
    #        3
    #       / \
    #      9  20
    #         / \
    #        15  7
    t = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert level_order(t) == [[3], [9, 20], [15, 7]]
    assert right_side_view(t) == [3, 20, 7]
    assert zigzag_level_order(t) == [[3], [20, 9], [15, 7]]
    assert max_depth(t) == 3
    assert diameter_of_binary_tree(t) == 3

    built = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    assert is_same_tree(t, built)
    assert serialize(deserialize(serialize(t))) == serialize(t)  # round trip: "#" makes the encoding 1:1

    bst = TreeNode(5, TreeNode(3, TreeNode(2), TreeNode(4)),
                   TreeNode(8, TreeNode(7), TreeNode(9)))
    assert is_valid_bst(bst)
    assert kth_smallest(bst, 3) == 4
    assert lca_bst(bst, bst.left.left, bst.left.right).val == 3

    neg = TreeNode(-10, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert max_path_sum(neg) == 42             # root is -10: the best path skips it entirely
    assert rob_tree(TreeNode(3, TreeNode(2, None, TreeNode(3)),
                             TreeNode(3, None, TreeNode(1)))) == 7
    assert binary_tree_paths(TreeNode(1, TreeNode(2, None, TreeNode(5)),
                                      TreeNode(3))) == ["1->2->5", "1->3"]
    dup = TreeNode(1, TreeNode(2, TreeNode(4)),
                   TreeNode(3, TreeNode(2, TreeNode(4)), TreeNode(4)))
    assert sorted(n.val for n in find_duplicate_subtrees(dup)) == [2, 4]
    print("03_trees: all checks passed")
