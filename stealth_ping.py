#!/usr/bin/env python3
"""
Stealth ICMP Data Transmission
Lab 1 - Cybersecurity
Activity 2: Stealth Mode

This program sends encrypted text through ICMP request packets to avoid detection 
by Deep Packet Inspection (DPI) systems. Each UTF-8 byte is sent as a separate packet
to support Unicode characters. The transmission ends with a special marker (byte 255).
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


def create_icmp_packet_from_byte(byte_val, packet_id, sequence):
    """
    Create an ICMP Echo Request packet with a single byte value in the data field.
    Mimics standard ping packet structure more closely.
    
    Args:
        byte_val (int): The byte value (0-255) to embed in the packet
        packet_id (int): The packet ID
        sequence (int): The sequence number
        
    Returns:
        bytes: The complete ICMP packet
    """
    # ICMP type (8 = Echo Request), code (0), checksum (0 for now), id, sequence
    icmp_type = 8
    icmp_code = 0
    icmp_checksum = 0
    
    # Create data that looks more like real ping data
    # Standard ping usually includes timestamp followed by pattern data
    # We'll embed our byte as the first byte, then add a timestamp-like structure
    
    # Get current time in microseconds (like ping does)
    import time
    timestamp = int(time.time() * 1000000) & 0xFFFFFFFFFFFFFFFF
    
    # Create 56 bytes of data (standard ping data size)
    # First byte: our hidden data
    # Next 8 bytes: timestamp (to mimic real ping)
    # Remaining bytes: pattern data similar to ping
    data_bytes = bytearray(56)
    data_bytes[0] = byte_val  # Our hidden byte
    
    # Add timestamp bytes (8 bytes in big-endian format)
    timestamp_bytes = struct.pack('!Q', timestamp)
    data_bytes[1:9] = timestamp_bytes
    
    # Fill remaining with pattern similar to ping (incrementing pattern)
    for i in range(9, 56):
        data_bytes[i] = (i - 9 + 0x08) & 0xFF
    
    full_data = bytes(data_bytes)
    
    # Create ICMP header without checksum
    icmp_header = struct.pack('!BBHH', icmp_type, icmp_code, icmp_checksum, packet_id)
    icmp_header += struct.pack('!H', sequence)
    
    # Calculate checksum with header and data
    icmp_checksum = checksum(icmp_header + full_data)
    
    # Recreate header with correct checksum
    icmp_header = struct.pack('!BBHH', icmp_type, icmp_code, icmp_checksum, packet_id)
    icmp_header += struct.pack('!H', sequence)
    
    return icmp_header + full_data


def create_icmp_packet(data_char, packet_id, sequence):
    """
    Create an ICMP Echo Request packet with a single character in the data field.
    This function is kept for backward compatibility.
    
    Args:
        data_char (str): The character to embed in the packet
        packet_id (int): The packet ID
        sequence (int): The sequence number
        
    Returns:
        bytes: The complete ICMP packet
    """
    # Convert character to its first UTF-8 byte value
    byte_val = data_char.encode('utf-8')[0]
    return create_icmp_packet_from_byte(byte_val, packet_id, sequence)


def send_stealth_ping(target_host, encrypted_message):
    """
    Send the encrypted message via stealth ICMP packets.
    Supports Unicode by sending each UTF-8 byte as a separate packet.
    
    Args:
        target_host (str): Target hostname or IP address
        encrypted_message (str): The encrypted message to transmit (supports Unicode)
    """
    try:
        # Create raw socket (requires root privileges)
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        # Get target IP
        target_ip = socket.gethostbyname(target_host)
        print(f"Sending stealth data to {target_host} ({target_ip})")
        print(f"Message to transmit: '{encrypted_message}'")
        
        # Convert message to UTF-8 bytes to support Unicode characters
        message_bytes = encrypted_message.encode('utf-8')
        print(f"UTF-8 encoded bytes: {len(message_bytes)} bytes")
        print(f"Total packets to send: {len(message_bytes) + 1}")  # +1 for end marker
        print(f"Packet size: 64 bytes total (8 byte ICMP header + 56 byte data)")
        print(f"Data structure: [hidden_byte][8-byte timestamp][47 pattern bytes]")
        print("-" * 50)
        
        packet_id = os.getpid() & 0xFFFF  # Use process ID as packet ID (like real ping)
        
        # Send each UTF-8 byte as a separate ICMP packet
        for i, byte_val in enumerate(message_bytes):
            sequence = i + 1
            packet = create_icmp_packet_from_byte(byte_val, packet_id, sequence)
            
            # Show character representation for readability
            try:
                char_repr = chr(byte_val) if 32 <= byte_val <= 126 else f"\\x{byte_val:02x}"
            except ValueError:
                char_repr = f"\\x{byte_val:02x}"
            
            print(f"Packet {sequence}: Sending byte {byte_val} ({char_repr}) in ICMP data field")
            sock.sendto(packet, (target_ip, 0))
            time.sleep(1)  # 1 second delay between packets (like normal ping)
        
        # Send end marker (special byte value 255)
        final_sequence = len(message_bytes) + 1
        end_packet = create_icmp_packet_from_byte(255, packet_id, final_sequence)
        print(f"Packet {final_sequence}: Sending end marker (byte 255)")
        sock.sendto(end_packet, (target_ip, 0))
        
        sock.close()
        print("-" * 50)
        print("Stealth transmission completed successfully!")
        print("All packets sent with standard ping structure:")
        print("- 64 bytes total (8 ICMP header + 56 data)")
        print("- Real timestamps included for authenticity") 
        print("- Standard ping timing (1s intervals)")
        print("- Process ID as packet identifier")
        print("- Sequential packet numbering")
        print("Unicode characters transmitted as UTF-8 byte sequences.")
        
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
    print("\nICMP Data (56 bytes - standard Linux ping size):")
    print("  Byte 0: Timestamp (8 bytes) - microseconds since epoch")
    print("  Bytes 8-55: Pattern data (0x08, 0x09, 0x0a, ... )")
    print("\nOur stealth packets use the SAME structure but replace")
    print("the first byte of data with our UTF-8 byte, then include")
    print("real timestamp and pattern data to perfectly mimic ping.")
    print("Timing matches standard ping (1s intervals).")
    print("Unicode characters are sent as multiple packets (one per UTF-8 byte).")
    print("Transmission ends with byte value 255.")
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