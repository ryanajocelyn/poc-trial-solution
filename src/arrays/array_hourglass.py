"""
Given a 6 x 6 2D Array

1 1 1 0 0 0
0 1 0 0 0 0
1 1 1 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0

An hourglass in A is a subset of values with indices falling in this pattern in arr 's graphical representation:

a b c
  d
e f g

"""


import sys


def hourglass_sum(arr):
    rows = len(arr)
    cols = len(arr[0])

    max_val = -sys.maxsize - 1
    for i in range(rows - 2):
        for j in range(cols - 2):
            sum_val = arr[i][j] + arr[i][j + 1] + arr[i][j + 2] \
                    + arr[i + 1][j + 1] \
                    + arr[i + 2][j] + arr[i + 2][j + 1] + arr[i + 2][j + 2]

            if sum_val > max_val:
                max_val = sum_val

    return max_val


if __name__ == '__main__':
    array = [
        [1, 1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [0, 0, 2, 4, 4, 0],
        [0, 0, 0, 2, 0, 0],
        [0, 0, 1, 2, 4, 0]
    ]

    result = hourglass_sum(array)
    print(result)
