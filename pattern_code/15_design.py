"""Patterns 93-94: Design.

Core idea: start from the required operations and their big-O budgets, then
compose structures whose strengths cover each other's gaps. Almost always
ends up as hashmap + something-with-order.
Run: python 15_design.py
"""
import bisect
import random
from collections import deque


# --------------------------------------------------------------- Pattern 93
class LRUCache:  # LC 146
    """Hashmap (O(1) lookup) + doubly linked list (O(1) reorder/evict).
    The map points AT list nodes, so both structures update in O(1).
    (Interview shortcut: OrderedDict / dict.move_to_end — but know this.)"""

    class Node:
        __slots__ = ("key", "val", "prev", "next")

        def __init__(self, key=0, val=0):
            self.key, self.val = key, val
            self.prev = self.next = None

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.map: dict[int, LRUCache.Node] = {}
        self.head = self.Node()            # sentinel: most-recent side
        self.tail = self.Node()            # sentinel: least-recent side
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, node: "LRUCache.Node") -> None:
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node: "LRUCache.Node") -> None:
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self._unlink(node)                 # touching = move to front
        self._push_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._unlink(self.map[key])
        node = self.Node(key, value)
        self.map[key] = node
        self._push_front(node)
        if len(self.map) > self.capacity:
            lru = self.tail.prev           # least recent lives at the tail
            self._unlink(lru)
            del self.map[lru.key]          # node stores its key FOR this delete


class RandomizedSet:  # LC 380
    """Array gives O(1) random; hashmap value->index gives O(1) lookup.
    Delete = swap victim with LAST element, pop — no hole, no shift."""

    def __init__(self):
        self.vals: list[int] = []
        self.index: dict[int, int] = {}

    def insert(self, val: int) -> bool:
        if val in self.index:
            return False
        self.index[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.index:
            return False
        i, last = self.index[val], self.vals[-1]
        self.vals[i] = last                # move last into the hole
        self.index[last] = i
        self.vals.pop()
        del self.index[val]
        return True

    def get_random(self) -> int:
        return random.choice(self.vals)


class TimeMap:  # LC 981
    """Per key: append-only (timestamp, value) list — timestamps arrive
    sorted, so reads are a binary search (pattern 62)."""

    def __init__(self):
        self.store: dict[str, list[tuple[int, str]]] = {}

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store.setdefault(key, []).append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        entries = self.store.get(key, [])
        # rightmost entry with ts <= timestamp: bisect on (timestamp, +inf)
        i = bisect.bisect_right(entries, (timestamp, chr(0x10FFFF)))
        return entries[i - 1][1] if i else ""


class HitCounter:  # LC 362
    """Queue of timestamps; evict what slid out of the 5-minute window."""

    def __init__(self):
        self.hits: deque[int] = deque()

    def hit(self, timestamp: int) -> None:
        self.hits.append(timestamp)

    def get_hits(self, timestamp: int) -> int:
        while self.hits and self.hits[0] <= timestamp - 300:
            self.hits.popleft()
        return len(self.hits)


# --------------------------------------------------------------- Pattern 94
class Trie:  # LC 208
    """Shared prefixes stored once; lookup cost = word length, regardless of
    dictionary size. A hashmap can test membership but not PREFIXES."""

    def __init__(self):
        self.children: dict[str, Trie] = {}
        self.is_word = False

    def insert(self, word: str) -> None:
        node = self
        for ch in word:
            node = node.children.setdefault(ch, Trie())
        node.is_word = True

    def _walk(self, s: str) -> "Trie | None":
        node = self
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None


class WordDictionary:  # LC 211 — wildcard '.' = branch to ALL children
    def __init__(self):
        self.root = Trie()

    def add_word(self, word: str) -> None:
        self.root.insert(word)

    def search(self, word: str) -> bool:
        def dfs(node: Trie, i: int) -> bool:
            if i == len(word):
                return node.is_word
            if word[i] == ".":             # backtracking ON the trie
                return any(dfs(child, i + 1) for child in node.children.values())
            child = node.children.get(word[i])
            return child is not None and dfs(child, i + 1)
        return dfs(self.root, 0)


def replace_words(dictionary: list[str], sentence: str) -> str:  # LC 648
    # Walk the trie until the SHORTEST root ends; that's the replacement.
    trie = Trie()
    for root in dictionary:
        trie.insert(root)

    def shorten(word: str) -> str:
        node = trie
        for i, ch in enumerate(word):
            node = node.children.get(ch)
            if node is None:
                break
            if node.is_word:
                return word[:i + 1]
        return word

    return " ".join(shorten(w) for w in sentence.split())


if __name__ == "__main__":
    lru = LRUCache(2)
    lru.put(1, 1); lru.put(2, 2)
    assert lru.get(1) == 1
    lru.put(3, 3)                          # evicts key 2 (least recent)
    assert lru.get(2) == -1 and lru.get(3) == 3

    rs = RandomizedSet()
    assert rs.insert(1) and not rs.insert(1) and rs.insert(2)
    assert rs.remove(1) and not rs.remove(1)
    assert rs.get_random() == 2

    tm = TimeMap()
    tm.set("foo", "bar", 1)
    assert tm.get("foo", 1) == "bar" and tm.get("foo", 3) == "bar"
    tm.set("foo", "bar2", 4)
    assert tm.get("foo", 4) == "bar2" and tm.get("foo", 3) == "bar"
    assert tm.get("foo", 0) == ""

    hc = HitCounter()
    for t in (1, 2, 3):
        hc.hit(t)
    assert hc.get_hits(4) == 3
    hc.hit(300)
    assert hc.get_hits(300) == 4 and hc.get_hits(301) == 3

    trie = Trie()
    trie.insert("apple")
    assert trie.search("apple") and not trie.search("app")
    assert trie.starts_with("app")

    wd = WordDictionary()
    for w in ("bad", "dad", "mad"):
        wd.add_word(w)
    assert not wd.search("pad") and wd.search("bad")
    assert wd.search(".ad") and wd.search("b..")

    assert replace_words(["cat", "bat", "rat"],
                         "the cattle was rattled by the battery") == \
        "the cat was rat by the bat"
    print("15_design: all checks passed")
