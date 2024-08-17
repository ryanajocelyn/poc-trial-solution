"""
Staircase Problem

"""


cache = [0] * 10


def staircase_problem_s2(n):
    if n < 0:
        return 0
    if n == 0:
        return 1

    if cache[n] != 0:
        # print ("Fetching from cache {0}".format(n))
        return cache[n]

    cache[n] = staircase_problem_s2(n - 1) + staircase_problem_s2(n - 2)
    # print("Computing for {0}".format(n))
    return cache[n]


def staircase_problem(n, m=2):
    if n < 0:
        return 0
    if n == 0:
        return 1

    sc_cnt = 0
    for ind in range(m):
        sc_cnt += staircase_problem(n - ind - 1, m)

    # print(n, "=", sc_cnt)
    return sc_cnt


def staircase_problem_arr(n, m=[1, 2]):
    if n < 0:
        return 0
    if n == 0:
        return 1

    sc_cnt = 0
    for ind in m:
        sc_cnt += staircase_problem_arr(n - ind, m)

    # print(n, "=", sc_cnt)
    return sc_cnt


if __name__ == '__main__':
    cnt = staircase_problem(5, 3)
    print(cnt)

    cnt = staircase_problem_s2(6)
    print(cnt)

    cnt = staircase_problem_arr(6)
    print(cnt)
