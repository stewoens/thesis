#!/usr/bin/python3

# Enters and outputs the lowest positive primes

from typing import List

prime_array: List[int] = []

prime_array.append(2)
prime_array.append(3)
prime_array.append(5)
prime_array.append(7)
prime_array.append(11)

print("Low primes are: ")

for prime in reversed(prime_array):
    print(prime)

print()

for i in range(len(prime_array) - 1, -1, -1):
    print(prime_array[i])
