#!/usr/bin/python3

print(
    "Enter your message lenth: 0-10 Caesar encoded (A-0, B-2, .. Z-25) characters long: "
)
length: int = int(input())

print("\nEnter your Caesar key in numeric form (1-25): ")
key: int = int(input())

print("\nEnter 1 for encryption, and 0 for decryption: ")
mode: int = int(input())

for counter in range(0, length):
    print("\nNow type in your next character to decrypt")
    character = int(input())
    print("\tYour letter translated to:")

    # Does using a loop help here? If yes, why? If no, why?
    if mode == 1:
        # 26 is the symbol set size (# letters in alphabet)
        print("\t", (character + key) % 26)
    else:
        print("\t", (character - key) % 26)

print("\nend of Caesar encoded message\n")
