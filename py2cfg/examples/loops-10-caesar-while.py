#!/usr/bin/python3

print("\nEnter your Caesar key in numeric form (1-25): ")
key: int = int(input())

print("\nEnter 1 for encryption, and 0 for decryption: ")
mode: int = int(input())

print("\nType in the first letter of your message, and hit enter:")
character: int = int(input())

print("\nNow type in your next character to decrypt, -1 for done")
character = int(input())

while character != -1:
    print("\tYour letter translated to:")

    # Does using a loop help here? If yes, why? If no, why?
    if mode == 1:
        # 26 is the symbol set size (# letters in alphabet)
        print("\t", (character + key) % 26)
    else:
        print("\t", (character - key) % 26)

    print("\nNow type in your next character to decrypt, -1 for done")
    character = int(input())

print("\nend of Caesar encoded message\n")
