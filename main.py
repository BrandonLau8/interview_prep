
from collections import deque

class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next
        
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        

def build_list(vals):
    dummy = ListNode(0)
    tail = dummy
    for i in range(len(vals)):
        tail.next = ListNode(vals[i])
        tail = tail.next
    return dummy.next
    
def to_array(head):
    out = []
    cur = head
    while cur is not None:
        out.append(cur.val)
        cur = cur.next
    return out

def build_tree(vals):
    if len(vals) == 0 or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    queue = deque([root])
    i = 1
    while i < len(vals):
        node = queue.popleft()
        if vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root

def length(head):
    count = 0
    cur = head
    
    while cur is not None:
        count += 1
        cur = cur.next
    return count

def remove_value(head, val):
    dummy = ListNode(0)
    dummy.next = head
    prev = dummy
    
    while prev.next is not None:
        if prev.next.val == val:
            prev.next = prev.next.next
        else:
            prev = prev.next
    return dummy.next

def reverse_list(head):
    prev = None
    cur = head
    while cur is not None:
        next = cur.next
        cur.next = prev
        prev = cur
        cur = next
    return prev

def kth_from_end(head, k):
    fast = head
    for i in range(k):
        fast = fast.next
    slow = head
    while fast is not None:
        slow = slow.next
        fast = fast.next
    return slow

def merge_lists(a, b):
    dummy = ListNode(0)
    tail = dummy
    
    while a is not None and b is not None:
        if a.val <= b.val:
            tail.next = a
            a = a.next
            
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    if a is not None:
        tail.next = a
    if b is not None:
        tail.next = b
    return dummy.next

def max_depth(node):
    if node is None:
        return 0
    left= max_depth(node.left)
    right = max_depth(node.right)
    return 1 + max(left, right)

def has_path_sum(node, remaining):
    if node is None:
        return False
    remaining -= node.val
    
    if node.left is None and node.right is None:
        return remaining == 0
    return has_path_sum(node.left, remaining) or has_path_sum(node.right, remaining)

def inorder(root):
    out = []
    stack = []
    cur = root
    while cur is not None or len(stack) > 0:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out

def is_valid_bst(node, lo, hi):
    if node is None:
        return True
    if node.val <= lo or node.val >= hi:
        return False
    return is_valid_bst(node.left, lo, node.val) and is_valid_bst(node.right, node.val, hi)

def topo_sort(n, edges):
    adj = []
    for i in range(n):
        adj.append([])
    indegree = [0] * n
    
    for i in range(len(edges)):
        u = edges[i][0]
        v = edges[i][1]
        adj[u].append(v)
        indegree[v] += 1
        
        
    
def main():
    nums = [3, 0, -1, 2]

if __name__ == "__main__":   
    main()