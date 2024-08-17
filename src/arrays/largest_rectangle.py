"""
Find the largest rectangle area in an array.

arr = [1, 2, 3, 4, 5]
res = 9
"""


def largest_rectangle_3(h):
    n = len(h)
    max_area = 0

    stack = []
    i = 1
    top = 0
    while i < n:
        if len(stack) == 0 or h[i] > h[i - 1]:
            stack.append(i)
            i += 1
        else:
            top = stack.pop()
            if len(stack) > 0:
                area = h[top] * (i - stack[-1] - 1)
            else:
                area = h[top] * i

            max_area = max(area, max_area)

    while stack:
        top = stack.pop()
        if len(stack) > 0:
            area = h[top] * (i - stack[-1] - 1)
        else:
            area = h[top] * i

        max_area = max(area, max_area)

    return max_area


def largest_rectangle_2(h):
    n = len(h)

    max_area = 0
    stack = [0]
    for i in range(1, n):
        if h[i] > h[i - 1]:
            stack.append(i)
        else:
            top = stack[-1]
            while stack and h[top] > h[i]:
                stack.pop()
                if stack:
                    area = h[top] * (i - stack[-1] - 1)
                    top = stack[-1]
                else:
                    area = h[top] * i

                max_area = max(max_area, area)

            stack.append(i)

    i = 1
    while stack:
        top = stack.pop()
        area = h[top] * i
        i += 1

        max_area = max(max_area, area)

    area = h[top] * n
    max_area = max(area, max_area)

    return max_area


def largest_rectangle_1(h):
    n = len(h)

    max_area = 0
    for i in range(n - 1, 0, -1):
        for j in range(n - i):
            min_h = min(h[j:j+i+1])
            area = min_h * (i + 1)

            if max_area < area:
                max_area = area

    return max_area


def largest_rectangle(arr):
    n = len(arr)
    arr.sort()

    max_area = 0
    for i in range(n):
        area = arr[i] * (n - i)
        if max_area < area:
            max_area = area

    return max_area


if __name__ == '__main__':
    # ar = [1, 2, 3, 4, 5]
    ar = [3, 4, 2, 3, 4]

    res = largest_rectangle_1(ar)
    print(res)

    res = largest_rectangle_2(ar)
    print(res)

    res = largest_rectangle_3(ar)
    print("3=", res)

    res = largest_rectangle(ar)
    print(res)
