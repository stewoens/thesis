#!/usr/bin/python3

from typing import List

base: int = 2
exponent: int = 16
total: int = 1
binary_array: List[int] = []

for counter in range(0, exponent):
    total = total * base
    binary_array.append(total)

for exp in binary_array:
    print(exp)
