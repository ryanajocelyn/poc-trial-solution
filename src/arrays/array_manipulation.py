"""
Starting with a 1-indexed array of zeros and a list of operations, for each operation
add a value to each the array element between two given indices, inclusive.
Once all operations have been performed, return the maximum value in the array.

Example
n = 10
queries = [[1, 5, 3], [4, 8, 7], [6, 9, 1]]

queries are interpreted as follows
    a b k
    1 5 3
    4 8 7
    6 9 1

Add the values of k between the indices a and b inclusive:

index->	 1 2 3  4  5 6 7 8 9 10
   [0,0,0, 0, 0,0,0,0,0, 0]
   [3,3,3, 3, 3,0,0,0,0, 0]
   [3,3,3,10,10,7,7,7,0, 0]
   [3,3,3,10,10,8,8,8,1, 0]
"""


def array_manipulation1(n, queries):
    max_v = 0;
    arr_list = [0] * (n + 1)

    for qry in queries:
        arr_list[qry[0]] += qry[2]

        if qry[1] + 1 <= n:
            arr_list[qry[1] + 1] -= qry[2]

    cum_sum = 0
    for i in arr_list:
        cum_sum += i
        if max_v < cum_sum:
            max_v = cum_sum

    return max_v


def array_manipulation(n, queries):
    max_v = 0;
    arr_list = [0] * n

    for qry in queries:
        for i in range(qry[0], qry[1]):
            arr_list[i] = arr_list[i] + qry[2]
            if max_v < arr_list[i]:
                max_v = arr_list[i]

    return max_v


if __name__ == '__main__':
    arr_len = 10
    query_list = [[1, 5, 3], [4, 8, 7], [6, 9, 1]]

    max_val = array_manipulation(arr_len, query_list)
    print('Method 1 (Traditional): ', max_val)

    max_val = array_manipulation1(arr_len, query_list)
    print('Method 2 (Efficient): ', max_val)
