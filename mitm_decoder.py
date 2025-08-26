#!/usr/bin/env python3
"""
Man-in-the-Middle ICMP Decoder
Lab 1 - Cybersecurity
Activity 3: MitM

This program intercepts ICMP packets and attempts to decode Caesar cipher messages
by trying all possible shift combinations (0-25) and highlighting the most probable
plaintext in green.
"""

import socket
import struct
import sys
import re
from collections import Counter


def caesar_decrypt(text, shift):
    """
    Decrypt text using Caesar cipher with the given shift value.
    
    Args:
        text (str): The text to decrypt
        shift (int): The number of positions to shift back
        
    Returns:
        str: The decrypted text
    """
    decrypted_text = ""
    
    for char in text:
        if char.isalpha():
            # Handle uppercase letters
            if char.isupper():
                decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            # Handle lowercase letters
            else:
                decrypted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            decrypted_text += decrypted_char
        else:
            # Non-alphabetic characters remain unchanged
            decrypted_text += char
    
    return decrypted_text


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


def parse_icmp_packet(packet):
    """
    Parse an ICMP packet and extract the character from the data field.
    
    Args:
        packet (bytes): The raw packet data
        
    Returns:
        tuple: (icmp_type, character) or (None, None) if not a valid ICMP Echo Request
    """
    try:
        # Parse IP header (20 bytes minimum)
        ip_header = struct.unpack('!BBHHHBBH4s4s', packet[:20])
        ip_header_length = (ip_header[0] & 0xF) * 4
        
        # Parse ICMP header (8 bytes)
        icmp_header = struct.unpack('!BBHHH', packet[ip_header_length:ip_header_length + 8])
        icmp_type, icmp_code, checksum, packet_id, sequence = icmp_header
        
        # Only process ICMP Echo Request packets (type 8)
        if icmp_type == 8:
            # Extract the first byte of ICMP data (our hidden character)
            data_start = ip_header_length + 8
            if len(packet) > data_start:
                character = chr(packet[data_start])
                return icmp_type, character, sequence
        
        return None, None, None
        
    except (struct.error, IndexError, ValueError):
        return None, None, None


def capture_icmp_packets():
    """
    Capture ICMP packets and extract hidden characters.
    
    Returns:
        str: The reconstructed message from ICMP packets
    """
    try:
        # Create raw socket to capture ICMP packets
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        print("Listening for ICMP packets...")
        print("Press Ctrl+C to stop and analyze captured data")
        print("-" * 50)
        
        captured_chars = {}
        
        while True:
            packet, addr = sock.recvfrom(1024)
            icmp_type, character, sequence = parse_icmp_packet(packet)
            
            if icmp_type == 8 and character:  # ICMP Echo Request
                print(f"Captured packet {sequence}: Character '{character}' from {addr[0]}")
                captured_chars[sequence] = character
                
                # Check if we received the end marker 'b'
                if character == 'b':
                    print("End marker 'b' received. Stopping capture.")
                    break
        
        sock.close()
        
        # Reconstruct message in sequence order (excluding the end marker)
        message = ""
        for seq in sorted(captured_chars.keys()):
            if captured_chars[seq] != 'b':  # Exclude end marker
                message += captured_chars[seq]
        
        return message
        
    except PermissionError:
        print("Error: This program requires root privileges to capture packets.")
        print("Please run with sudo: sudo python3 mitm_decoder.py")
        return None
    except KeyboardInterrupt:
        print("\nCapture stopped by user.")
        sock.close()
        
        # Reconstruct message from captured data
        message = ""
        for seq in sorted(captured_chars.keys()):
            if captured_chars[seq] != 'b':  # Exclude end marker
                message += captured_chars[seq]
        return message
    except Exception as e:
        print(f"Error: {e}")
        return None


def analyze_captured_message(encrypted_message):
    """
    Analyze the captured message by trying all Caesar cipher shifts.
    
    Args:
        encrypted_message (str): The captured encrypted message
    """
    if not encrypted_message:
        print("No message captured.")
        return
    
    print(f"\nCaptured encrypted message: '{encrypted_message}'")
    print("\nTrying all possible Caesar cipher shifts:")
    print("=" * 70)
    
    # Colors for terminal output
    GREEN = '\033[92m'  # Green color
    RESET = '\033[0m'   # Reset color
    
    best_score = float('-inf')
    best_shift = 0
    best_message = ""
    
    # Try all possible shifts (0-25)
    for shift in range(26):
        decrypted = caesar_decrypt(encrypted_message, shift)
        score = calculate_english_score(decrypted)
        
        # Track the best (most likely English) result
        if score > best_score:
            best_score = score
            best_shift = shift
            best_message = decrypted
        
        print(f"Shift {shift:2d}: {decrypted} (Score: {score:.2f})")
    
    print("=" * 70)
    print(f"{GREEN}Most likely plaintext (Shift {best_shift}): {best_message}{RESET}")
    print(f"English likelihood score: {best_score:.2f}")


def simulate_with_test_data(test_message):
    """
    Simulate the MitM attack with test data instead of capturing live packets.
    
    Args:
        test_message (str): The encrypted message to analyze
    """
    print("SIMULATION MODE: Analyzing provided encrypted message")
    print("-" * 50)
    analyze_captured_message(test_message)


def main():
    """Main function to handle command line arguments and execute MitM decoder."""
    if len(sys.argv) == 1:
        # Live packet capture mode
        print("Starting MitM ICMP packet capture and decoder...")
        captured_message = capture_icmp_packets()
        if captured_message:
            analyze_captured_message(captured_message)
    elif len(sys.argv) == 2:
        # Simulation mode with provided encrypted message
        test_message = sys.argv[1]
        simulate_with_test_data(test_message)
    else:
        print("Usage:")
        print("  sudo python3 mitm_decoder.py                    # Live packet capture")
        print("  python3 mitm_decoder.py <encrypted_message>     # Simulation mode")
        print("\nExamples:")
        print("  sudo python3 mitm_decoder.py                    # Capture live ICMP packets")
        print("  python3 mitm_decoder.py 'Khoor Zruog'           # Analyze given encrypted text")
        sys.exit(1)


if __name__ == "__main__":
    main()