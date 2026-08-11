

def process_commands(matrix, commands):
    for cmd in commands:
        parts = cmd.split()
        
        if parts[0] == 'swapRows':
            r1, r2 = int(parts[1]), int(parts[2])
            matrix[r1], matrix[r2] = matrix[r2], matrix[r1]
            
        elif parts[0] == 'swapCols':
            c1, c2 = int(parts[1]), int(parts[2])
            for row in matrix:
                row[c1], row[c2] = row[c2], row[c1]
        
        elif parts[0] == 'reverseRow':
            r = int(parts[1])
            matrix[r].reverse()
            
        elif parts[0] == 'reverseCol':
            c = int(parts[1])
            top, bottom = 0, len(matrix) - 1
            while top<bottom:
                matrix[top][c], matrix[bottom][c] = matrix[bottom][c], matrix[top][c]
                top += 1
                bottom -= 1
                
        elif parts[0] == 'rotateMatrix90Degree':
            matrix[:] = [list(row) for row in zip(*matrix)]
            for row in matrix:
                row.reverse()
        
    return matrix

# mat = [
#     [1,  2,  3,  4],
#     [5,  6,  7,  8],
#     [9, 10, 11, 12]
# ]

# cmds = [
#     "swapRows 0 2",
#     "swapCols 1 3",
#     "reverseRow 1",
#     "reverseCol 0",
#     "rotateMatrix90Degree"
# ]

# result = process_commands(mat, cmds)

# for row in result:
#     print(row)

def largest_common_prefix(first, second):
    #Convert numbers to strings for prefix comparison
    first_strs = [str(x) for x in first]
    second_strs = [str(x) for x in second]
    
    longest_prefix = ''
    
    for f in first_strs:
        for s in second_strs:
            #Compare character by character
            prefix_len = 0
            for i in range(min(len(f), len(s))):
                if f[i] == s[i]:
                    prefix_len += 1
                else:
                    break
            
            #Update longest prefix if we found a bigger one
            if prefix_len > len(longest_prefix):
                longest_prefix = f[:prefix_len]
                
    return longest_prefix

firstArray = [2, 25, 258, 54843, 390]
secondArray = [2, 255, 3908, 25, 54842, 5]
print(largest_common_prefix(firstArray, secondArray))
            
class TrieNode:
    def __init__(self):
        self.children = {}
        
class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, number: str):
        node = self.root
        for digit in number:
            if digit not in node.children:
                node.children[digit] = TrieNode()
            node = node.children[digit]