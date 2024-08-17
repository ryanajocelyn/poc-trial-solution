"""
A left rotation operation on an array of size n shifts each of the
array's elements 1 unit to the left.

Given an integer, d, rotate the array that many steps left and return the result

Example

d = 2
arr = [1, 2, 3, 4, 5]

After 2 rotations, [3, 4, 5, 1, 2]
"""
# 3 2 1 4 5
# 3 4 1 2 5
# 3 4 5 2 1


def rotate_left (d, arr):
    n = len(arr)
    rotated_arr = []

    for i in range(len(arr)):
        rotated_arr.append(arr[(i + d) % n])

    return rotated_arr


if __name__ == '__main__':
    array = [1, 2, 3, 4, 5]
    rotated = rotate_left(2, array)
    print(rotated)

    array = [1, 2, 3, 4, 5]
    rotated = rotate_left(3, array)
    print(rotated)

    array = [1, 2, 3, 4, 5]
    rotated = rotate_left(4, array)
    print(rotated)

    array = [1, 2, 3, 4, 5, 6]
    rotated = rotate_left(2, array)
    print(rotated)
