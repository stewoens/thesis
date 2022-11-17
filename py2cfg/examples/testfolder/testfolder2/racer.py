#!/usr/bin/python3
"""
taylor@mst.edu
"""

# Do NOT edit the next two lines of code:
import sys


def skull():
    print(
        """
    hey
"""
    )


def fireworks():
    print(
        """
xC:w

"""
    )


def lightbulb():
    print(
        """
e
"""
    )


def car():
    print(
        """
i
"""
    )


def print_map():
    print(my_row)


def ascii_racer():
    my_lib = [
        "00   |*     *|",
        "01    |*     *|",
        "02     |*     *|",
        "03    |*      *|",
        "04   |*      *|",
        "05  |*      *|",
        "06  |*      *|",
        "07   |*     *|",
        "08    |*     *|",
        "09     |*     *|",
        "10      |*     *|",
        "11       |*     *|",
        "12        |*     *|",
        "13         |*     *|",
        "14        |*     *|",
        "15       |*     *|",
        "16      |*     *|",
        "17     |*     *|",
        "18    |*     *|",
        "19   |*     *|",
        "20  |*     *|",
        "21 |*     *|",
        "22  |*     *|",
    ]

    laps = 0
    row = 0
    lr_pos = 9

    car()
    print("Welcome to ASCII-racer.")
    print("Navigate through to the light at the end of the tunnel to win!")
    print("Press 'a' for left, 'd' for right', enter for nothing.")
    print("If you hit the walls, you lose.")
    print("To win, you have to complete 2 laps around the tunnel array.")
    input("Press any key to start!")

    while True:
        print(
            "ASCII Racer 2.0, level: ",
            row,
            " completed rows in lap number ",
            laps + 1,
        )
        lightbulb()

        my_row = my_lib[row]
        my_row = my_row[:lr_pos] + "^" + my_row[lr_pos + 1 :]

        if (my_row.count("|*") != 1) or (my_row.count("*|") != 1):
            skull()
            print("You hit the wall, and lose!")
            return

        print(my_lib[(row + 2) % len(my_lib)])
        print(my_lib[(row + 1) % len(my_lib)])
        print(my_row)

        user_input = input()
        if user_input == "d":
            lr_pos += 1
        if user_input == "a":
            lr_pos -= 1

        row += 1
        if row == len(my_lib):
            row = 0
            laps += 1
            if laps == 2:
                fireworks()
                print("You win!")
                return


if __name__ == "__main__":
    play_again = "y"

    while play_again == "y":
        ascii_racer()
        play_again = "?"

        while play_again != "y" and play_again != "n":
            print("\nDo you want to play again? (y/n): ")
            play_again = input()
