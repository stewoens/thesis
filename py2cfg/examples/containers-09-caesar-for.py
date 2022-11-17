#!/usr/bin/python3

from typing import List

caesar_encoding: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

print("\nEnter your Caesar key in numeric form (1-25): ")
key: int = int(input())

print("\nEnter 1 for encryption, and 0 for decryption: ")
mode: int = int(input())

message: str = input("\nEnter your message, in English:\n")
translated: List[int] = []

for character in message:
    if mode == 1:
        # 26 is the symbol set size (# letters in alphabet)
        encoded_char = caesar_encoding.find(character.upper())
        translated.append((encoded_char + key) % 26)
    else:
        encoded_char = caesar_encoding.find(character.upper())
        translated.append((encoded_char - key) % 26)

print("\nYour encrypted text is:")
# To print the string:
for encoded_char in translated:
    print(caesar_encoding[encoded_char], end="")

# To recover the string:
plaintext: List[int] = []
for counter, encoded_char in enumerate(translated):
    plaintext.append(caesar_encoding[encoded_char])

plaintext_string = "".join(plaintext)
