#!/usr/bin/python3

print("Enter base, hit enter, then exponent")
base: int = int(input())
exponent: int = int(input())
total: int = 1

for counter in range(0, exponent):
    total = total * base

print("Base ", base)
print(" to the power of ", exponent)
print(" is ", total)
