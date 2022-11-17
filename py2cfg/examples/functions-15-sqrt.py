#!/usr/bin/python3

import math


def sqare_rt(my_val: float) -> float:
    diff: float = 1.0
    root: float = 1.0

    while (diff > 0.0001) or (diff < -0.0001):
        root = (root + (my_val / root)) / 2.0
        diff = (root * root) - my_val
    return root


twenty: float = 20.0
print(sqare_rt(20.0))
# Versus Python's:
print(math.sqrt(20.0))
