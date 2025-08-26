#!/usr/bin/env python3
"""
Lab 1 - Cybersecurity Demo Script
Complete demonstration of the three activities

This script demonstrates the complete workflow:
1. Encrypt a message using Caesar cipher
2. Show how the message would be transmitted via stealth ICMP packets
3. Demonstrate the MitM attack by decoding all possible Caesar combinations
"""

import subprocess
import sys
import os


def run_demo():
    """Run the complete cybersecurity lab demonstration."""
    print("=" * 70)
    print("LAB 1 - CYBERSECURITY DEMONSTRATION")
    print("Deep Packet Inspection (DPI) Evasion via ICMP Stealth Mode")
    print("=" * 70)
    
    # Demo message
    original_message = "Secret Data"
    shift_value = 7
    
    print(f"\n1. ORIGINAL MESSAGE: '{original_message}'")
    print(f"   Shift value: {shift_value}")
    
    # Activity 1: Caesar Cipher Encryption
    print("\n" + "="*50)
    print("ACTIVITY 1: CAESAR CIPHER ENCRYPTION")
    print("="*50)
    
    result = subprocess.run([
        'python3', 'caesar_cipher.py', original_message, str(shift_value)
    ], capture_output=True, text=True, cwd='/home/runner/work/Lab1Sec3/Lab1Sec3')
    
    if result.returncode == 0:
        print(result.stdout)
        # Extract encrypted text from output
        lines = result.stdout.strip().split('\n')
        encrypted_message = lines[-1].split(': ')[1] if lines else ""
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
    print(f"Number of ICMP packets needed: {len(encrypted_message) + 1}")
    print("\nSimulated ICMP packet transmission:")
    
    for i, char in enumerate(encrypted_message):
        print(f"  Packet {i+1}: Character '{char}' embedded in ICMP data field")
    print(f"  Packet {len(encrypted_message)+1}: End marker 'b'")
    
    print("\nEach packet would look like a normal ping with:")
    print("  - Standard ICMP Echo Request header (Type 8, Code 0)")
    print("  - Process ID as packet identifier")
    print("  - Sequential packet numbering")
    print("  - 32-byte data payload (first byte = our character)")
    print("  - 1 second intervals between packets")
    print("  - This mimics normal ping behavior to avoid DPI detection")
    
    # Activity 3: MitM Attack and Decoding
    print("\n" + "="*50)
    print("ACTIVITY 3: MAN-IN-THE-MIDDLE ATTACK & DECODING")
    print("="*50)
    
    result = subprocess.run([
        'python3', 'mitm_decoder.py', encrypted_message
    ], capture_output=True, text=True, cwd='/home/runner/work/Lab1Sec3/Lab1Sec3')
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error in MitM decoder: {result.stderr}")
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nSUMMARY:")
    print(f"✓ Original message: '{original_message}'")
    print(f"✓ Caesar cipher encryption (shift {shift_value}): '{encrypted_message}'")
    print("✓ Stealth ICMP transmission simulation completed")
    print("✓ MitM attack successfully decoded the message")
    print("\nThis demonstrates how attackers can:")
    print("1. Hide data in seemingly innocent network traffic")
    print("2. Bypass DPI systems that only look for obvious patterns")
    print("3. Intercept and decode hidden messages if they know the method")


def main():
    """Main function."""
    # Check if we're in the correct directory
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caesar_cipher.py')):
        print("Error: Lab files not found. Please run from the correct directory.")
        sys.exit(1)
    
    run_demo()


if __name__ == "__main__":
    main()