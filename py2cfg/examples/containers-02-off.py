#!/usr/bin/python3

# An array variable holds many values rather than just one value.
# The size can be read as lin(nameofarray)
# useful in loops iterating through the array.
# [type] array([size]) [identifier]
# myarray: List[type] = []
# myarray: List[type] = [item, item, ...]
# user_array[expression] can be any valid expression

from typing import List

user_nums: List[int] = list([0] * 5)

for i in range(len(user_nums) + 1):
    user_nums[i] = i * 2

x: int = user_nums[3]

for inum in user_nums:
    print(inum)
