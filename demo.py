#!/usr/bin/env python3
"""
Lab 1 - Cybersecurity Demo Script
Complete demonstration of the three activities with Unicode support

This script demonstrates the complete workflow:
1. Encrypt a message using Caesar cipher (supports Unicode)
2. Show how the message would be transmitted via stealth ICMP packets (UTF-8 byte-level)
3. Demonstrate the MitM attack by decoding all possible Caesar combinations
"""

import subprocess
import sys
import os

# Module-level constant for script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_demo():
    """Run the complete cybersecurity lab demonstration."""
    print("=" * 70)
    print("LAB 1 - CYBERSECURITY DEMONSTRATION")
    print("Deep Packet Inspection (DPI) Evasion via ICMP Stealth Mode")
    print("Unicode Support Enabled")
    print("=" * 70)
    
    # Demo message with Unicode
    original_message = "Secret 世界"  # "Secret World" in Chinese
    shift_value = 7
    
    print(f"\n1. ORIGINAL MESSAGE: '{original_message}' (includes Unicode)")
    print(f"   Shift value: {shift_value}")
    print(f"   UTF-8 byte length: {len(original_message.encode('utf-8'))} bytes")
    
    # Activity 1: Caesar Cipher Encryption
    print("\n" + "="*50)
    print("ACTIVITY 1: CAESAR CIPHER ENCRYPTION")
    print("="*50)
    
    result = subprocess.run([
        'python3', 'caesar_cipher.py', original_message, str(shift_value)
    ], capture_output=True, text=True, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        print(result.stdout)
        # Extract encrypted text from output (last line)
        encrypted_message = result.stdout.strip().split('\n')[-1]
    else:
        print(f"Error in Caesar cipher: {result.stderr}")
        return
    
    # Activity 2: Stealth Mode (Simulation)
    print("\n" + "="*50)
    print("ACTIVITY 2: STEALTH ICMP TRANSMISSION")
    print("="*50)
    print("NOTE: This would normally require root privileges for raw sockets.")
    print("Simulating the stealth transmission process...\n")
    
    print(f"Encrypted message to transmit: '{encrypted_message}'")
    
    # Show UTF-8 byte breakdown
    message_bytes = encrypted_message.encode('utf-8')
    print(f"UTF-8 encoded bytes: {list(message_bytes)}")
    print(f"Number of ICMP packets needed: {len(message_bytes) + 1}")
    print("\nSimulated ICMP packet transmission:")
    
    for i, byte_val in enumerate(message_bytes):
        try:
            char_repr = chr(byte_val) if 32 <= byte_val <= 126 else f"\\x{byte_val:02x}"
        except ValueError:
            char_repr = f"\\x{byte_val:02x}"
        print(f"  Packet {i+1}: Byte {byte_val} ({char_repr}) embedded in ICMP data field")
    print(f"  Packet {len(message_bytes)+1}: End marker (character 'b')")
    
    print("\nEach packet would look like a normal ping with:")
    print("  - Standard ICMP Echo Request header (Type 8, Code 0)")
    print("  - Process ID as packet identifier")
    print("  - Sequential packet numbering")
    print("  - 32-byte data payload (first byte = our UTF-8 byte)")
    print("  - 1 second intervals between packets")
    print("  - This mimics normal ping behavior to avoid DPI detection")
    print("  - Unicode characters sent as multiple packets (one per UTF-8 byte)")
    
    # Activity 3: MitM Attack and Decoding
    print("\n" + "="*50)
    print("ACTIVITY 3: MAN-IN-THE-MIDDLE ATTACK & DECODING")
    print("="*50)
    
    result = subprocess.run([
        'python3', 'mitm_decoder.py', encrypted_message
    ], capture_output=True, text=True, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error in MitM decoder: {result.stderr}")
    
    # Demonstrate with a second example (ASCII only)
    print("\n" + "="*50)
    print("BONUS: ASCII-ONLY EXAMPLE")
    print("="*50)
    
    ascii_message = "Hello World"
    print(f"ASCII message: '{ascii_message}'")
    
    result = subprocess.run([
        'python3', 'caesar_cipher.py', ascii_message, "3"
    ], capture_output=True, text=True, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        ascii_encrypted = result.stdout.strip().split('\n')[-1]
        print(f"Encrypted: '{ascii_encrypted}'")
        
        result = subprocess.run([
            'python3', 'mitm_decoder.py', ascii_encrypted
        ], capture_output=True, text=True, cwd=SCRIPT_DIR)
        
        if result.returncode == 0:
            # Extract just the result line
            lines = result.stdout.split('\n')
            for line in lines:
                if "Most likely plaintext" in line:
                    print(line)
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nSUMMARY:")
    print(f"✓ Original message: '{original_message}' (Unicode supported)")
    print(f"✓ Caesar cipher encryption (shift {shift_value}): '{encrypted_message}'")
    print("✓ Stealth ICMP transmission simulation completed")
    print("✓ UTF-8 byte-level transmission ensures Unicode compatibility")
    print("✓ MitM attack successfully decoded the message")
    print("\nThis demonstrates how attackers can:")
    print("1. Hide data in seemingly innocent network traffic")
    print("2. Bypass DPI systems that only look for obvious patterns")
    print("3. Support international characters via UTF-8 encoding")
    print("4. Intercept and decode hidden messages if they know the method")


def main():
    """Main function."""
    # Check if we're in the correct directory
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'caesar_cipher.py')):
        print("Error: Lab files not found. Please run from the correct directory.")
        sys.exit(1)
    
    run_demo()


if __name__ == "__main__":
    main()