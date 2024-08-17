"""
Max Hamming Distance

Given an array of n elements, create a new array which is a rotation of given array and
hamming distance between both the arrays is maximum.

Hamming distance between two arrays or strings of equal length is the number of positions
at which the corresponding character(elements) are different.
"""


def max_hamming_dist1(arr):
    n = len(arr)

    max_ham_dist = 0
    for i in range(n):
        ind = 0
        j = i + 1
        ham_dist = 0
        while j <= (i + n):
            if arr[ind] != arr[j % n]:
                ham_dist += 1

            j += 1
            ind += 1

        max_ham_dist = max(max_ham_dist, ham_dist)
        if max_ham_dist == n:
            break

    return max_ham_dist


def max_hamming_dist(arr):
    n = len(arr)
    ar_temp = [0] * 2 * n
    for i in range(n):
        ar_temp[i] = ar_temp[i + n] = arr[i]

    max_ham_dist = 0
    for i in range(n):
        ind = 0
        j = i + 1
        ham_dist = 0
        while j <= (i + n):
            if ar_temp[ind] != ar_temp[j]:
                ham_dist += 1

            j += 1
            ind += 1

        max_ham_dist = max(max_ham_dist, ham_dist)
        if max_ham_dist == n:
            break

    return max_ham_dist


if __name__ == '__main__':
    ar = [2, 4, 8, 0]
    # ar = [1, 4, 1]

    max_dist = max_hamming_dist1(ar)

    print(max_dist)