"""
Create a 2-dimensional array, arr, of n empty arrays. All arrays are zero indexed.
Create an integer, last_answer, and initialize it to 0.
There are 2 types of queries:

Query: 1 x y
Find the list within arr at index idx = ((x xor last_answer) % n).
Append the integer y to the arr[idx].

Query: 2 x y
Find the list within arr at index idx = ((x xor last_answer) % n).
Find the value of element y % size(arr[idx]) where size is the number of elements in arr[idx].
Assign the value to last_answer.

Print the new value of last_answer on a new line
"""


def dynamic_array(n, queries):
    arr = []
    for i in range(n):
        arr.append([])

    last_answer = 0

    for query in queries:
        idx = (query[1] ^ last_answer) % n

        if query[0] == 1:
            arr[idx].append(query[2])
        else:
            la_idx = query[2] % len(arr[idx])
            last_answer = arr[idx][la_idx]
            print(last_answer)


if __name__ == '__main__':
    qrys = [
        [1, 0, 5],
        [1, 1, 7],
        [1, 0, 3],
        [2, 1, 0],
        [2, 1, 1]
    ]

    dynamic_array(2, qrys)
