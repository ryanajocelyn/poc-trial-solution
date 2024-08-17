"""
Sorted Array

Find the number of rotations in a sorted array

arr = [5, 1, 2, 3, 4]    rotation = 1
arr = [4, 5, 1, 2, 3]    rotation = 2
"""


def rotation_count(arr, start, end):
    if arr[start] < arr[end] or start == end:
        return start

    mid = int((end + start) / 2)
    if arr[start] > arr[mid]:
        return rotation_count(arr, start, mid)
    else:
        return rotation_count(arr, mid + 1, end)


if __name__ == '__main__':
    a = [2, 3, 4, 5, 1]
    rot_count = rotation_count(a, 0, len(a) - 1)

    print(rot_count)
