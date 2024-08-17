"""
Reverse an array of integers.

Example:
    A = [1,2,3]
Return
    [3,2,1]
"""


def reverse_array(a):
    n = len(a) - 1
    for i in range(int(len(a) / 2)):
        tmp = a[i]
        a[i] = a[n]
        a[n] = tmp
        n -= 1


if __name__ == '__main__':
    a = [1, 2, 3]
    reverse_array(a)
    print (a)
