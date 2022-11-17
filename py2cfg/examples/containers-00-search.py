#!/usr/bin/python3

# input: 2 3 4 5 6 7 -1

from typing import List

key: int = 5
tempvalue: int = int(input())
numbers: List[int] = []
i: int = 0

while tempvalue != -1:
    numbers.append(tempvalue)
    tempvalue = int(input())
    i = i + 1

for i in range(len(numbers)):
    if numbers[i] == key:
        print("Your key of", key, "is at the following index: ", i)
