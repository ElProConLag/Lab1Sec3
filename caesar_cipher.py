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


def caesar_decrypt(text, shift):
    """
    Decrypt text using Caesar cipher with the given shift value.
    Supports Unicode characters - only ASCII letters are decrypted, Unicode characters are preserved.
    
    Args:
        text (str): The text to decrypt (supports Unicode)
        shift (int): The number of positions to shift back
        
    Returns:
        str: The decrypted text with Unicode characters preserved
    """
    decrypted_text = ""
    
    for char in text:
        # Only apply Caesar cipher to ASCII letters, preserve all other characters including Unicode
        if char.isalpha() and ord(char) < 128:  # ASCII letters only
            # Handle uppercase letters
            if char.isupper():
                decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            # Handle lowercase letters
            else:
                decrypted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            decrypted_text += decrypted_char
        else:
            # Non-ASCII alphabetic characters and all other characters remain unchanged
            decrypted_text += char
    
    return decrypted_text


def calculate_spanish_score(text):
    """
    Calculate a score indicating how likely the text is to be Spanish.
    Higher scores indicate more likely Spanish text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        float: The Spanish likelihood score
    """
    # Convert to uppercase and remove non-alphabetic characters for analysis
    clean_text = ''.join(char.upper() for char in text if char.isalpha())
    
    if not clean_text:
        return 0
    
    score = 0
    
    # Check for common Spanish words (case-insensitive)
    common_words = ['HOLA', 'MUNDO', 'EL', 'LA', 'DE', 'QUE', 'Y', 'A', 'EN', 'UN', 'ES', 'SE', 'NO', 'TE', 'LO',
                   'LE', 'DA', 'SU', 'POR', 'SON', 'CON', 'PARA', 'COMO', 'ESTA', 'ESTÁ', 'TU', 'PERO', 'MAS', 'MÁS',
                   'UNA', 'TIENE', 'ME', 'AHORA', 'PRIMER', 'TRES', 'AÑOS', 'MUCHO', 'PORQUE', 'CADA',
                   'CASA', 'VIDA', 'OTROS', 'NUEVO', 'MISMO', 'DESPUÉS', 'HASTA', 'DONDE', 'OTRA', 'CUANDO',
                   'AQUÍ', 'SOLO', 'SIN', 'ENTRE', 'FORMA', 'PAÍS', 'GOBIERNO', 'POLÍTICA', 'PERSONA', 'GRUPO',
                   'TRABAJO', 'LUGAR', 'MOMENTO', 'AGUA', 'MANO', 'PARTE', 'DÍA', 'NOCHE', 'MENSAJE', 'SECRETO',
                   'ATAQUE', 'CIFRADO', 'CLAVE', 'SEGURIDAD', 'RED', 'PAQUETE', 'DATOS', 'INFORMACIÓN']
    
    # Split by spaces and check each word
    words = text.upper().split()
    for word in words:
        word_clean = ''.join(char for char in word if char.isalpha())
        if word_clean in common_words:
            score += 50  # High bonus for common Spanish words
    
    # Check for common Spanish letter patterns
    if 'QU' in clean_text:
        score += 15  # QU is very common in Spanish
    if 'LL' in clean_text:
        score += 10  # LL is common in Spanish
    if 'RR' in clean_text:
        score += 10  # RR is distinctive in Spanish
    if 'Ñ' in clean_text:
        score += 5   # Ñ is a strong indicator
    if 'CH' in clean_text:
        score += 8   # CH is common in Spanish
    
    # Bonus for having vowels (A, E, I, O, U) - Spanish has high vowel frequency
    vowels = sum(1 for char in clean_text if char in 'AEIOU')
    consonants = len(clean_text) - vowels
    
    # Spanish typically has a higher vowel ratio than English (40-50%)
    if len(clean_text) > 0:
        vowel_ratio = vowels / len(clean_text)
        if 0.40 <= vowel_ratio <= 0.55:
            score += 25
        elif 0.35 <= vowel_ratio <= 0.60:
            score += 15
    
    # Check for Spanish-specific letter frequency patterns
    # Spanish has high frequency of A, E, O
    a_count = clean_text.count('A')
    e_count = clean_text.count('E')
    o_count = clean_text.count('O')
    
    if len(clean_text) > 0:
        a_freq = a_count / len(clean_text)
        e_freq = e_count / len(clean_text)
        o_freq = o_count / len(clean_text)
        
        if a_freq > 0.11:  # Spanish has high A frequency
            score += 10
        if e_freq > 0.12:  # Spanish has high E frequency
            score += 10
        if o_freq > 0.08:  # Spanish has moderate O frequency
            score += 8
    
    # Penalize letter combinations that are unusual in Spanish
    unusual_patterns = ['KK', 'WW', 'ZZ', 'XX', 'QQ']
    for pattern in unusual_patterns:
        if pattern in clean_text:
            score -= 15
    
    # Check for reasonable word length distribution
    if words:
        avg_word_length = sum(len(''.join(char for char in word if char.isalpha())) for word in words) / len(words)
        if 4 <= avg_word_length <= 8:  # Typical Spanish word lengths
            score += 10
    
    return score


def calculate_english_score(text):
    """
    Calculate a score indicating how likely the text is to be English.
    Higher scores indicate more likely English text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        float: The English likelihood score
    """
    # Convert to uppercase and remove non-alphabetic characters for analysis
    clean_text = ''.join(char.upper() for char in text if char.isalpha())
    
    if not clean_text:
        return 0
    
    score = 0
    
    # Check for common English words (case-insensitive)
    common_words = ['HELLO', 'WORLD', 'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 
                   'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'HAVE', 'SECRET', 'MESSAGE',
                   'THIS', 'THAT', 'WITH', 'WILL', 'FROM', 'THEY', 'KNOW', 'ATTACK',
                   'WANT', 'BEEN', 'GOOD', 'MUCH', 'SOME', 'TIME', 'VERY', 'DATA',
                   'WHEN', 'COME', 'HERE', 'HOW', 'JUST', 'LIKE', 'LONG', 'PING',
                   'MAKE', 'MANY', 'OVER', 'SUCH', 'TAKE', 'THAN', 'THEM', 'ICMP',
                   'WELL', 'WERE', 'PACKET', 'NETWORK', 'SECURITY', 'CIPHER', 'KEY']
    
    # Split by spaces and check each word
    words = text.upper().split()
    for word in words:
        word_clean = ''.join(char for char in word if char.isalpha())
        if word_clean in common_words:
            score += 50  # High bonus for common English words
    
    # Check for common English letter patterns
    if 'TH' in clean_text:
        score += 10
    if 'HE' in clean_text:
        score += 10
    if 'IN' in clean_text:
        score += 10
    if 'ER' in clean_text:
        score += 10
    if 'AN' in clean_text:
        score += 10
    
    # Bonus for having vowels (A, E, I, O, U)
    vowels = sum(1 for char in clean_text if char in 'AEIOU')
    consonants = len(clean_text) - vowels
    
    # English typically has a vowel ratio between 35-45%
    if len(clean_text) > 0:
        vowel_ratio = vowels / len(clean_text)
        if 0.30 <= vowel_ratio <= 0.50:
            score += 20
    
    # Penalize unusual letter combinations
    unusual_patterns = ['QQ', 'XX', 'ZZ', 'JJ', 'VV', 'WW']
    for pattern in unusual_patterns:
        if pattern in clean_text:
            score -= 20
    
    # Check for reasonable word length distribution
    if words:
        avg_word_length = sum(len(''.join(char for char in word if char.isalpha())) for word in words) / len(words)
        if 3 <= avg_word_length <= 7:  # Typical English word lengths
            score += 10
    
    return score


def analyze_with_language_detection(encrypted_message):
    """
    Analyze encrypted message by trying all Caesar cipher shifts and detecting language.
    Prioritizes Spanish detection over English but keeps both.
    
    Args:
        encrypted_message (str): The encrypted message to analyze
        
    Returns:
        dict: Results with best Spanish and English candidates
    """
    if not encrypted_message:
        return None
    
    print(f"\nAnalyzing encrypted message: '{encrypted_message}'")
    print("\nTrying all possible Caesar cipher shifts:")
    print("=" * 80)
    
    # Colors for terminal output
    GREEN = '\033[92m'  # Green color
    YELLOW = '\033[93m' # Yellow color
    RESET = '\033[0m'   # Reset color
    
    best_spanish_score = float('-inf')
    best_spanish_shift = 0
    best_spanish_message = ""
    
    best_english_score = float('-inf')
    best_english_shift = 0
    best_english_message = ""
    
    # Try all possible shifts (0-25)
    for shift in range(26):
        decrypted = caesar_decrypt(encrypted_message, shift)
        spanish_score = calculate_spanish_score(decrypted)
        english_score = calculate_english_score(decrypted)
        
        # Track the best Spanish result
        if spanish_score > best_spanish_score:
            best_spanish_score = spanish_score
            best_spanish_shift = shift
            best_spanish_message = decrypted
        
        # Track the best English result
        if english_score > best_english_score:
            best_english_score = english_score
            best_english_shift = shift
            best_english_message = decrypted
        
        print(f"Shift {shift:2d}: {decrypted} (ES: {spanish_score:.1f}, EN: {english_score:.1f})")
    
    print("=" * 80)
    
    # Prioritize Spanish but show both results
    if best_spanish_score > 0 and best_spanish_score >= best_english_score * 0.8:
        # Spanish has good score and is competitive with English
        print(f"{GREEN}Most likely Spanish text (Shift {best_spanish_shift}): {best_spanish_message}{RESET}")
        print(f"Spanish likelihood score: {best_spanish_score:.2f}")
        if best_english_score > 0:
            print(f"{YELLOW}Alternative English text (Shift {best_english_shift}): {best_english_message}{RESET}")
            print(f"English likelihood score: {best_english_score:.2f}")
    elif best_english_score > 0:
        # Fall back to English
        print(f"{YELLOW}Most likely English text (Shift {best_english_shift}): {best_english_message}{RESET}")
        print(f"English likelihood score: {best_english_score:.2f}")
        if best_spanish_score > 0:
            print(f"Spanish alternative (Shift {best_spanish_shift}): {best_spanish_message}")
            print(f"Spanish likelihood score: {best_spanish_score:.2f}")
    else:
        # No clear language detected
        print("No clear language pattern detected. Showing both best candidates:")
        print(f"Best Spanish candidate (Shift {best_spanish_shift}): {best_spanish_message} (Score: {best_spanish_score:.2f})")
        print(f"Best English candidate (Shift {best_english_shift}): {best_english_message} (Score: {best_english_score:.2f})")
    
    return {
        'spanish': {
            'text': best_spanish_message,
            'shift': best_spanish_shift,
            'score': best_spanish_score
        },
        'english': {
            'text': best_english_message,
            'shift': best_english_shift,
            'score': best_english_score
        }
    }


def main():
    """Main function to handle command line arguments and execute encryption or decryption."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Encrypt: python3 caesar_cipher.py <text_to_encrypt> <shift_value>")
        print("  Decrypt: python3 caesar_cipher.py --decrypt <encrypted_text>")
        print("  Analyze: python3 caesar_cipher.py --analyze <encrypted_text>")
        print("\nExamples:")
        print("  python3 caesar_cipher.py 'Hello World' 3")
        print("  python3 caesar_cipher.py --decrypt 'Khoor Zruog'")
        print("  python3 caesar_cipher.py --analyze 'Krod pxqgr'")
        sys.exit(1)
    
    try:
        # Check for decrypt mode
        if sys.argv[1] == "--decrypt":
            if len(sys.argv) != 3:
                print("Usage for decrypt: python3 caesar_cipher.py --decrypt <encrypted_text>")
                sys.exit(1)
            
            encrypted_text = sys.argv[2]
            print(f"Encrypted text: {encrypted_text}", file=sys.stderr)
            
            # Try all shifts and show all possibilities
            print("All possible decryptions:")
            for shift in range(26):
                decrypted = caesar_decrypt(encrypted_text, shift)
                print(f"Shift {shift:2d}: {decrypted}")
            
            return
        
        # Check for analyze mode (with language detection)
        elif sys.argv[1] == "--analyze":
            if len(sys.argv) != 3:
                print("Usage for analyze: python3 caesar_cipher.py --analyze <encrypted_text>")
                sys.exit(1)
            
            encrypted_text = sys.argv[2]
            analyze_with_language_detection(encrypted_text)
            return
        
        # Default encryption mode
        else:
            if len(sys.argv) != 3:
                print("Usage for encrypt: python3 caesar_cipher.py <text_to_encrypt> <shift_value>")
                sys.exit(1)
            
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