#!/usr/bin/python3

from typing import List
import random


def key_gen() -> int:
    """
    Generates one Caesar key
    """
    key = random.randint(1, 25)
    print("\nYour Caesar key is: ")
    print(key)
    print("\n Share this with your partner. Don't tell anyone else\n")
    return key


def str_to_num_arr(message: str) -> List[int]:
    """
    Translates a string into a Caesar-encoded List
    """
    caesar_encoding: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    arr: List[int] = []
    for character in message:
        arr.append(caesar_encoding.find(character.upper()))
    return arr


def num_arr_to_str(encoded_arr: List[int]) -> str:
    """
    Translates a Caesar encoded list back into a string
    """
    caesar_encoding: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    plaintext: List[str] = []
    for counter, encoded_char in enumerate(encoded_arr):
        plaintext.append(caesar_encoding[encoded_char])
    plaintext_string = "".join(plaintext)
    return plaintext_string


def translate(encoded_arr: List[int], mode: int, key: int) -> List[int]:
    """
    Encrypts or decryps a Caesar-encoded List of ints
    """
    translated: List[int] = []
    for encoded_char in encoded_arr:
        if mode == 1:
            # 26 is the symbol set size (# letters in alphabet)
            translated.append((encoded_char + key) % 26)
        else:
            translated.append((encoded_char - key) % 26)
    return translated


message: str = input("\nEnter your message, in English:\n")

gen_key: str = input("Want to generate a key? (y/n)")

if gen_key == "y":
    ok: int = 0
    while ok == 0:
        key = key_gen()
        print("Is the key it ok with you (1-yes, 0-no, make another): ")
        ok = int(input())
else:
    key = int(input("What is your key (0-25)?"))

print("\nEnter 1 for encryption, and 0 for decryption: ")
mode: int = int(input())

message_arr = str_to_num_arr(message)
# message is changed after execution
message_arr = translate(message_arr, mode, key)
message = num_arr_to_str(message_arr)
print(message)
