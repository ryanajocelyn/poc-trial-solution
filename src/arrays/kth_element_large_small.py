"""
Find the kth Largest / Smallest Element

Input: arr[] = {7, 10, 4, 3, 20, 15}
k = 3
Output: 7

Input: arr[] = {7, 10, 4, 3, 20, 15}
k = 4
Output: 10

"""

import sys


def get_left(i):
    return (2 * i) + 1


def get_right(i):
    return (2 * i) + 2


def get_parent(i):
    return int((i - 1) / 2)


class MinHeap:
    marr = None
    heap_size = 0

    def get_min(self):
        print(self.marr)
        return self.marr[0]

    def __init__(self, marr):
        self.marr = marr
        self.heap_size = len(marr)

        i = int((self.heap_size - 1) / 2)
        while i >= 0:
            self.min_heapify(i)
            i -= 1

    def extract_min(self):
        if self.heap_size == 0:
            return sys.maxsize

        root = self.marr[0]

        if self.heap_size > 1:
            self.marr[0] = self.marr[self.heap_size - 1]
            self.min_heapify(0)

        self.heap_size -= 1

    def min_heapify(self, i):
        left = get_left(i)
        right = get_right(i)
        smallest = i

        if left < self.heap_size and self.marr[left] < self.marr[i]:
            smallest = left
        if right < self.heap_size and self.marr[right] < self.marr[smallest]:
            smallest = right

        if smallest != i:
            tmp = self.marr[smallest]
            self.marr[smallest] = self.marr[i]
            self.marr[i] = tmp

            self.min_heapify(smallest)


def kth_small_element():
    arr.sort()
    return arr[k - 1]


if __name__ == '__main__':
    arr = [7, 10, 4, 3, 20, 15]
    k = 3

    small = kth_small_element()
    print('Small=', small)

    min_heap = MinHeap(arr)
    for i in range(k - 1):
        min_heap.extract_min()

    small = min_heap.get_min()
    print('Min Heap =', small)

