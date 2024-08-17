"""
Given an array A of n elements, sort the array according to the following relations :

a[i] >= a[i-1], if i is even
a[i] <= a[i-1], if i is odd

"""


def greater_odd_arr(arr):
    n = len(arr)
    for i in range(1, n):
        if i % 2 == 0:
            # Even
            if arr[i] > arr[i - 1]:
                tmp = arr[i]
                arr[i] = arr[i - 1]
                arr[i - 1] = tmp
        else:
            # Odd
            if arr[i] < arr[i - 1]:
                tmp = arr[i]
                arr[i] = arr[i - 1]
                arr[i - 1] = tmp

    return arr


if __name__ == '__main__':
    ar = [1, 2, 2, 1]

    res_ar = greater_odd_arr(ar)
    print(res_ar)
