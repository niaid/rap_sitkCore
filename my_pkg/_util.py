# The "_util" module is private to the "my_pkg" package, by convention since it begins with an '_'.


def helper(n: int) -> int:
    """
    Classic recursive implementation of computing a Fibonacci number.

    :param n: an non-negative integer
    :return: returns the n-th fibonacci number
    """

    assert n >= 0

    if n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return helper(n - 1) + helper(n - 2)
