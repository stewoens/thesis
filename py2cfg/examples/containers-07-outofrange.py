#!/usr/bin/python3

from typing import List

user_nums: List[int] = list([0] * 5)
limit = int(input("How high do you want to count by 2s (1-5 only!)"))

for i in range(limit):
    user_nums[i] = i * 2

for item in user_nums:
    print(item)
