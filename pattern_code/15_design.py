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
    """Fixed-capacity cache evicting the least recently used key, all O(1).
    Two questions, two structures: the map answers "where is this key?" and
    the doubly linked list answers "what was touched longest ago?". The map
    points AT list nodes, which is the sync that keeps both updates O(1).

    Naive: a dict plus a timestamp per entry — eviction then costs an O(n)
    scan for the oldest. A list alone makes lookup O(n).

    Real life: a desk where the file you just used goes back on top of the
    pile, plus an index card saying which pile position each file is in."""

    class Node:
        __slots__ = ("key", "val", "prev", "next")

        def __init__(self, key=0, val=0):
            self.key, self.val = key, val
            self.prev = self.next = None

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.map: dict[int, LRUCache.Node] = {}   # invariant: key -> its node; keys match the nodes in the list
        self.head = self.Node()            # invariant: sentinel; head.next is the most recently used
        self.tail = self.Node()            # invariant: sentinel; tail.prev is the eviction candidate
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
    """Insert, remove and get-a-uniform-random-member, all O(1).
    Random sampling needs contiguous storage, membership needs hashing — so
    keep both and sync them. Deletion is the trick: swap the victim with the
    LAST element and pop, leaving no hole and shifting nothing.

    Naive: a set alone has no indexable order, so random sampling degrades to
    building a list each call — O(n). A list alone makes lookup O(n).

    Real life: numbered raffle tickets in a box plus a ledger of who holds
    which number — to withdraw someone, move the last ticket into their slot."""

    def __init__(self):
        self.vals: list[int] = []          # invariant: the members, in no meaningful order, no gaps
        self.index: dict[int, int] = {}    # invariant: value -> its position in vals; always in sync

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
    """Store values under (key, timestamp); read back the latest value at or
    before a given time. Writes arrive in increasing timestamp order, so each
    key's list is sorted for free — which turns the read into a binary search
    for the rightmost entry at or below the query (pattern 62).

    Naive: scan a key's history backwards per read — O(n) per get, where the
    sortedness the writes hand you already permits O(log n).

    Real life: a ledger appended chronologically — to find the price on some
    date you open near where that date falls, not at the first page."""

    def __init__(self):
        self.store: dict[str, list[tuple[int, str]]] = {}   # invariant: key -> (timestamp, value), ascending by timestamp

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store.setdefault(key, []).append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        entries = self.store.get(key, [])
        # rightmost entry with ts <= timestamp: bisect on (timestamp, +inf)
        i = bisect.bisect_right(entries, (timestamp, chr(0x10FFFF)))
        return entries[i - 1][1] if i else ""


class HitCounter:  # LC 362
    """Count hits received in the past 5 minutes.
    A sliding window over time rather than over indices: hits enter at the
    back and expire from the front, so a deque holds exactly the live ones.
    Evicting lazily on read means idle periods cost nothing.

    Naive: keep every hit forever and count those in range per query — O(n)
    per read and unbounded memory on a long-running counter.

    Real life: a doorman's tally slips dropped into a tube — before answering
    "how many lately?", he shakes out the ones older than five minutes."""

    def __init__(self):
        self.hits: deque[int] = deque()    # invariant: timestamps in arrival order; stale ones evicted on read

    def hit(self, timestamp: int) -> None:
        self.hits.append(timestamp)

    def get_hits(self, timestamp: int) -> int:
        while self.hits and self.hits[0] <= timestamp - 300:
            self.hits.popleft()
        return len(self.hits)


# --------------------------------------------------------------- Pattern 94
class Trie:  # LC 208
    """Prefix tree: insert words, then test membership or any prefix.
    The structure IS the shared prefixes — stored once, so lookup costs the
    word's length no matter how large the dictionary grows. is_word is
    separate from having children, because "app" inside "apple" is not a word.

    Naive: a hashmap answers membership in O(1) but cannot answer PREFIXES at
    all; testing every prefix against it is O(len) lookups of growing strings.

    Real life: a filing cabinet where words sharing an opening letter share a
    drawer — you walk letter by letter and never see unrelated words."""

    def __init__(self):
        self.children: dict[str, Trie] = {}   # invariant: next character -> the subtree spelling on from here
        self.is_word = False               # invariant: True iff a complete word ends at this node

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
    """Trie search where '.' matches any single character.
    A wildcard turns lookup from a walk into a SEARCH: at '.' every child is
    a candidate, so this is backtracking over the trie (pattern 46-52) rather
    than a plain descent. Concrete characters still prune to one branch.

    Naive: match the pattern against every stored word — O(words * len),
    where the trie collapses shared prefixes into one traversal.

    Real life: reading a crossword clue with blanks — at each blank you try
    every letter that the grid still allows, and abandon dead branches."""

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
    """Replace each word by the shortest dictionary root that prefixes it.
    Walking the trie visits a word's prefixes in increasing length, so the
    FIRST is_word you meet is already the shortest root — returning there is
    both the answer and the pruning. Falling off the trie means no root exists.

    Naive: for each word test every dictionary entry as a prefix — O(words *
    dict * len). The trie tests all roots simultaneously in one descent.

    Real life: shortening surnames to the first recognized clan prefix — you
    read letters until a known clan name completes, then stop."""
    trie = Trie()                          # invariant: holds every root; is_word marks a root's last letter
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
    assert trie.search("apple") and not trie.search("app")   # "app" is a prefix, not a stored word
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
