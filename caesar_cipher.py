#!/usr/bin/env python3
"""
Caesar Cipher Implementation
Lab 1 - Cybersecurity
Activity 1: Encryption Algorithm

This program implements the Caesar cipher algorithm to encrypt text using a specified shift value.
"""

import sys


def caesar_encrypt(text, shift):
    """
    Encrypt text using Caesar cipher with the given shift value.
    Supports Unicode characters - only ASCII letters are encrypted, Unicode characters are preserved.
    
    Args:
        text (str): The text to encrypt (supports Unicode)
        shift (int): The number of positions to shift each character
        
    Returns:
        str: The encrypted text with Unicode characters preserved
    """
    encrypted_text = ""
    
    for char in text:
        # Only apply Caesar cipher to ASCII letters, preserve all other characters including Unicode
        if char.isalpha() and ord(char) < 128:  # ASCII letters only
            # Handle uppercase letters
            if char.isupper():
                encrypted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            # Handle lowercase letters
            else:
                encrypted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            encrypted_text += encrypted_char
        else:
            # Non-ASCII alphabetic characters and all other characters remain unchanged
            encrypted_text += char
    
    return encrypted_text


def main():
    """Main function to handle command line arguments and execute encryption."""
    if len(sys.argv) != 3:
        print("Usage: python3 caesar_cipher.py <text_to_encrypt> <shift_value>")
        print("Example: python3 caesar_cipher.py 'Hello World' 3")
        sys.exit(1)
    
    try:
        text_to_encrypt = sys.argv[1]
        shift_value = int(sys.argv[2])
        
        print(f"Original text: {text_to_encrypt}", file=sys.stderr)
        print(f"Shift value: {shift_value}", file=sys.stderr)
        
        encrypted_text = caesar_encrypt(text_to_encrypt, shift_value)
        print(encrypted_text)
        
        return encrypted_text
        
    except ValueError:
        print("Error: Shift value must be an integer")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()