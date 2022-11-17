#!/usr/bin/python3

from typing import List

# smallest prime is 2, how odd...
value: int = 2

max_value: int = int(input("Display primes up to what value?"))
primes: List[int] = []

while value <= max_value:
    is_prime: int = 1
    trial_factor: int = 2

    while trial_factor < value:
        if value % trial_factor == 0:
            is_prime = 0
            break
        trial_factor = trial_factor + 1

    if is_prime == 1:
        primes.append(value)
        print(value, " is prime")
    else:
        print(value, " is not prime")

    value = value + 1

print("\nThe primes are", primes)
