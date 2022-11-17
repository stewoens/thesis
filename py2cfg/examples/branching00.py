#!/usr/bin/python3

# An if-else construct implements branching.
# Below, if  x < 0 is true, the first branch executes,
# outputting "Negative". Else, the second branch executes,
# outputting "Non-negative".
# General form:
# if [condexpr]:
#    [substatements]
# elif [condexpr]Q
#    [substatements]
# elseQ
#    [substatements]

x: int = int(input())

if x < 0:
    print("Negative")
else:
    print("Non-negative")
