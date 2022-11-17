# include <iostream>

print("Help! My computer doesn't work!\n")
print(
    "Does the computer make any sounds (fans, etc.) or show any lights? (y/n):"
)
choice: str = input()

if choice == "n":
    print("Is it plugged in? (y/n):")
    choice = input()
    if choice == "n":
        print(
            "Plug it in. \
             If the problem persists, \
             please run this program again.\n"
        )
    else:
        print('Is the switch in the "on" position? (y/n):')
        choice = input()
        if choice == "n":
            print(
                "Turn it on. \
                 If the problem persists, \
                 please run this program again.\n"
            )
        else:
            print("Does the computer have a fuse?  (y/n):")
            choice = input()
            if choice == "n":
                print("Is the outlet OK? (y/n):")
                choice = input()
                if choice == "n":
                    print(
                        "Check the outlet's circuit breaker or fuse. \
                         Move to a new outlet, if necessary. \
                         If the problem persists, \
                         please run this program again.\n"
                    )
                else:
                    print("Please consult a service technician.\n")
            else:
                print(
                    "Check the fuse. Replace if necessary. \
                     If the problem persists, \
                     then please run this program again.\n"
                )
else:
    print("Please consult a service technician.\n")
