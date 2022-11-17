#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 05:34:58 2019
Sudoku solver
@author: taylor@mst.edu
"""


# Takes a partially filled-in grid and attempts to assign values to
# all unassigned locations in such a way as to meet the requirements
# for Sudoku: non-duplication across rows, columns, and zones
def SolveSudoku(grid, indent=""):
    row_col = []

    # If there is no unassigned location, we are done
    # Otherwise, row and col are modified
    # (since they are passed by ref)
    if not FindUnassignedLocation(grid, row_col):
        # Total sucess
        return True

    row, col = row_col

    # consider digits 1 to 9
    for num in range(1, 10):
        # Does this digit produce any immediate conflicts?
        if isSafe(grid, row, col, num):
            # make tentative assignment
            grid[row][col] = num
            print(indent, "grid[", row, "]", "[", col, "] = ", num, sep="")

            # return, if success, yay!
            if SolveSudoku(grid, indent + " "):
                # like it occurs after recursive call
                return True

            # failure, un-do (backtrack) and try again
            grid[row][col] = UNASSIGNED

    print(indent, "grid[", row, "]", "[", col, "] = 1-9 all conflict!", sep="")
    # this triggers backtracking
    return False


# Searches the grid to find an entry that is still unassigned. If
# found, the reference parameters row, col will be end up set
# (by the for loop) to the location that is unassigned,
# and true is returned. If no unassigned entries remain,
# false is returned.
def FindUnassignedLocation(grid, row_col):
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == UNASSIGNED:
                row_col[:] = row, col
                return True
    return False


# Returns a boolean which indicates whether any assigned entry
# in the specified row matches the given number.
def UsedInRow(grid, row, num):
    for col in range(len(grid[0])):
        if grid[row][col] == num:
            return True
    return False


# Returns a boolean which indicates whether any assigned entry
# in the specified column matches the given number.
def UsedInCol(grid, col, num):
    for row in range(len(grid)):
        if grid[row][col] == num:
            return True
    return False


# Returns a boolean which indicates whether any assigned entry
# within the specified 3x3 box matches the given number.
def UsedInBox(grid, boxStartRow, boxStartCol, num):
    for row in range(3):
        for col in range(3):
            if grid[row + boxStartRow][col + boxStartCol] == num:
                return True
    return False


# Returns a boolean which indicates whether it will be legal to assign
# num to the given row,col location.
def isSafe(grid, row, col, num):
    # Check if 'num' is not already placed in current row,
    # current column and current 3x3 box
    return (
        not UsedInRow(grid, row, num)
        and not UsedInCol(grid, col, num)
        and not UsedInBox(grid, row - row % 3, col - col % 3, num)
    )


# Print grid
def printGrid(grid):
    for row in grid:
        for element in row:
            print(element, " ", end="")
        print()


if __name__ == "__main__":
    # UNASSIGNED is used for empty cells in grid
    UNASSIGNED = 0

    # N is used for size of Sudoku grid. Size is NxN
    N = 9

    # 0 for unassigned cells
    grid = [
        [3, 0, 6, 5, 0, 8, 4, 0, 0],
        [5, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 8, 7, 0, 0, 0, 0, 3, 1],
        [0, 0, 3, 0, 1, 0, 0, 8, 0],
        [9, 0, 0, 8, 6, 3, 0, 0, 5],
        [0, 5, 0, 0, 9, 0, 6, 0, 0],
        [1, 3, 0, 0, 0, 0, 2, 5, 0],
        [0, 0, 0, 0, 0, 0, 0, 7, 4],
        [0, 0, 5, 2, 0, 6, 3, 0, 0],
    ]

    print("Problem is:")

    printGrid(grid)

    print("Solution is:")

    if SolveSudoku(grid):
        printGrid(grid)
    else:
        print("No solution exists")
