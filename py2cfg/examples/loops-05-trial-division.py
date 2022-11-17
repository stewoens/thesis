#!/usr/bin/python3

# smallest prime is 2, how odd...
value: int = 2

max_value: int = int(input("Display primes up to what value?"))

while value <= max_value:
    is_prime: int = 1
    trial_factor: int = 2

    while trial_factor < value:
        if value % trial_factor == 0:
            is_prime = 0
        trial_factor = trial_factor + 1

    if is_prime == 1:
        print(value, " is prime")
    else:
        print(value, " is not prime")

    value = value + 1
