#!/usr/bin/python3

# A while loop construct executes its sub-statements
# while its condition is true.
# Below, while x > 0, the loop outputs x’s square.
# input array should end in -1

user_input: int = int(input())

while 0 < user_input:
    x_squared = user_input * user_input
    # Could also do this:
    # xSquared *= x
    print(x_squared)
    user_input = int(input())
