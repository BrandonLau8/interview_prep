import heapq

"""
[3, 5, 9, 6], k=4 -> 9

1 2 3 4 5 6 7 8 9

blocks
3 5 9 6 = 23
1 2 4 3 = 10
1 1 3 2 = 7
0 1 2 1 = 4
0 1 1 1 = 3
0 0 1 1 = 2
0 0 1 0 = 1
0 0 1 0 = 1
0 0 1 0 = 1

silvers
0 0 0 0
1 1 1 0
0 2 0 0
3 1 1 2
3 0 4 1
3 5 3 0
3 5 2 6
3 5 1 6
3 5 0 6

[4, 5, 5, 5]
"""

def secure_max_deliveries(logs, k):
    def score(x):
        blocks = sum(a//x for a in logs)
        silvers = sorted((a%x for a in logs), reverse=True)
        boxes = [x] * min(blocks, k)
        boxes += silvers[:k - len(boxes)]
        boxes += [0] * (k-len(boxes))
        boxes.sort()
        return sum(boxes[:k//2])
        
    return max((score(x) for x in range(1, max(logs)+1)), default=0)
    
def main():
    nums = [7, 3, 4, 5, 6]
    res = three_largest(nums)
    print(res)
if __name__ == "__main__":
    main()
