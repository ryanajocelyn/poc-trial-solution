"""
Fibonacci Series

"""


def fibonacci(n):
    if n == 1:
        return 0

    if n == 2:
        return 1

    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == '__main__':
    fib = fibonacci(10)
    print(fib)
