"""
Shift all zeros in a array to the end.

Example:
    A = [1, 4, -1, 0, 5, 0, 0, 3]

Return
    A = [1, 4, -1, 5, 3, 0, 0, 0]
"""


def shift_zeros(arr):
    index = 0
    for i in range(len(arr)):
        if arr[i] != 0:
            arr[index] = arr[i]
            index += 1

    while index < len(arr):
        arr[index] = 0
        index += 1

    return arr


def shift_zeros1(arr):
    zero_start = -1
    for i in range(len(arr)):
        if arr[i] == 0 and zero_start == -1:
            zero_start = i
            continue

        if arr[i] != 0 and zero_start >= 0:
            arr[zero_start] = arr[i]
            arr[i] = 0
            zero_start += 1

    return arr


if __name__ == '__main__':
    array = [1, 4, -1, 0, 5, 0, 0, 3]

    shift_array = shift_zeros(array)
    print(shift_array)

    shift_array = shift_zeros1(array)
    print(shift_array)
