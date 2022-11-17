#!/usr/bin/python3

# Averaging some floats

from typing import List

my_array: List[float] = []

my_array.append(2.1)
my_array.append(3.4)
my_array.append(5.3)

print("The average of these numbers is: ")
print((my_array[0] + my_array[1] + my_array[0 + 2]) / 3)
# Weird indexing just to show example

# or
print(sum(my_array) / len(my_array))
