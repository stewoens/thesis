#!/usr/bin/python3

x: int = int(input())
y: int = int(input())
z: int = int(input())

if (y - z) < 10:
    print("Close")

if x < 10:
    print("Small")
    # Nested conditions
    if x > 8:
        print("nine")
elif x < 20:
    print("Med")
else:
    print("Large")

# elseif is optional, any number OK
# else is optional, must be last
# Conditional expression’s operators:
#    (), ==, !=, , =, and, or, not
# Precedence (high to low):
#    (), not, * / % + -, < >=, == !=, and, or
