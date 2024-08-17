"""
Multiple Rotations


"""


def multiple_rotations(arr, rot_cnt):
    ret_val = []
    n = len(arr)

    for i in range(n):
        ret_val.append(arr[(i + rot_cnt) % n])

    return ret_val;


if __name__ == '__main__':
    ar = [1, 3, 5, 7, 9]
    rt = 8

    rt_val = multiple_rotations(ar, rt % len(ar))
    print(rt_val)
