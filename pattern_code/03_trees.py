"""Patterns 12-17: Tree Traversal.

Core idea: pick the traversal order that delivers information when you need it.
Preorder = parent decides first (pass state DOWN as args).
Postorder = children report first (return state UP).
Inorder on a BST = sorted order.  BFS = process by depth.
Run: python 03_trees.py
"""
from collections import Counter, deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# --------------------------------------------------------------- Pattern 12
# Level order: snapshot len(queue) at loop start = exactly one level.
def level_order(root: TreeNode | None) -> list[list[int]]:  # LC 102
    if not root:
        return []
    res, q = [], deque([root])
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
    # Right side view = last node of each level.
    return [level[-1] for level in level_order(root)]


def right_side_view(root: TreeNode | None) -> list[int]:
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
                level.append(node)
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
    return [level if i % 2 == 0 else level[::-1]
            for i, level in enumerate(level_order(root))]


# --------------------------------------------------------------- Pattern 13
# Preorder: everything you need is known BEFORE recursing.
def is_same_tree(p: TreeNode | None, q: TreeNode | None) -> bool:  # LC 100
    if not p or not q:
        return p is q  # both None -> True, one None -> False
    return (p.val == q.val
            and is_same_tree(p.left, q.left)
            and is_same_tree(p.right, q.right))


def invert_tree(root: TreeNode | None) -> TreeNode | None:  # LC 226
    if root:
        root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


def build_tree(preorder: list[int], inorder: list[int]) -> TreeNode | None:  # LC 105
    # preorder[0] is ALWAYS the root; inorder splits left/right around it.
    idx = {v: i for i, v in enumerate(inorder)}
    pre_it = iter(preorder)

    def build(lo: int, hi: int) -> TreeNode | None:  # inorder slice [lo, hi)
        if lo >= hi:
            return None
        root = TreeNode(next(pre_it))  # preorder feeds roots in order
        mid = idx[root.val]
        root.left = build(lo, mid)  # left subtree consumed first — same
        root.right = build(mid + 1, hi)  # order preorder emits it
        return root

    return build(0, len(inorder))


def binary_tree_paths(root: TreeNode) -> list[str]:  # LC 257
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
    prev = None

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
    stack: list[TreeNode] = []
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
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def diameter_of_binary_tree(root: TreeNode | None) -> int:  # LC 543
    # Return the CONSTRAINED value (downward height, usable by parent);
    # track the UNCONSTRAINED answer (path bending here) on the side.
    best = 0

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
    best = float("-inf")

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
    # Each subtree reports two numbers: best if root robbed / not robbed.
    def dfs(node: TreeNode | None) -> tuple[int, int]:
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
    # LCA = first node whose value falls BETWEEN p and q (the split point).
    lo, hi = min(p.val, q.val), max(p.val, q.val)
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
    # Postorder: if p and q surface from DIFFERENT subtrees, this is the LCA;
    # a single signal is forwarded up unchanged.
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
    parts: list[str] = []

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
    vals = iter(data.split(","))

    def dfs() -> TreeNode | None:
        v = next(vals)
        if v == "#":
            return None
        node = TreeNode(int(v))
        node.left = dfs()  # consume in the same preorder
        node.right = dfs()
        return node

    return dfs()


def find_duplicate_subtrees(root: TreeNode | None) -> list[TreeNode]:  # LC 652
    # Canonical encoding as hash key: identical subtrees collide.
    seen: Counter[str] = Counter()
    res: list[TreeNode] = []

    def encode(node: TreeNode | None) -> str:
        if not node:
            return "#"
        key = f"{node.val},{encode(node.left)},{encode(node.right)}"
        seen[key] += 1
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
    assert serialize(deserialize(serialize(t))) == serialize(t)

    bst = TreeNode(5, TreeNode(3, TreeNode(2), TreeNode(4)),
                   TreeNode(8, TreeNode(7), TreeNode(9)))
    assert is_valid_bst(bst)
    assert kth_smallest(bst, 3) == 4
    assert lca_bst(bst, bst.left.left, bst.left.right).val == 3

    neg = TreeNode(-10, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert max_path_sum(neg) == 42
    assert rob_tree(TreeNode(3, TreeNode(2, None, TreeNode(3)),
                             TreeNode(3, None, TreeNode(1)))) == 7
    assert binary_tree_paths(TreeNode(1, TreeNode(2, None, TreeNode(5)),
                                      TreeNode(3))) == ["1->2->5", "1->3"]
    dup = TreeNode(1, TreeNode(2, TreeNode(4)),
                   TreeNode(3, TreeNode(2, TreeNode(4)), TreeNode(4)))
    assert sorted(n.val for n in find_duplicate_subtrees(dup)) == [2, 4]
    print("03_trees: all checks passed")
