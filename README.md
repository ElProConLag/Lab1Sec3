# Lab 1 - Cybersecurity: DPI Evasion via ICMP Stealth Mode

## Overview

This laboratory demonstrates how attackers can evade Deep Packet Inspection (DPI) systems by hiding encrypted data within seemingly innocent ICMP ping traffic. The implementation consists of three Python programs that showcase the complete attack chain from encryption to data exfiltration to interception and decoding.

## Lab Objectives

The goal is to audit whether DPI systems can effectively detect data exfiltration through network traffic by:

1. Creating a Caesar cipher encryption algorithm
2. Implementing stealth data transmission via ICMP packets
3. Demonstrating a Man-in-the-Middle (MitM) attack to intercept and decode hidden messages

## Programs Implemented

### 1. Caesar Cipher Encryption (`caesar_cipher.py`)

**Purpose**: Encrypt plaintext messages using the Caesar cipher algorithm with a configurable shift value.

**Usage**:
```bash
python3 caesar_cipher.py <text_to_encrypt> <shift_value>
```

**Example**:
```bash
python3 caesar_cipher.py "Hello World" 3
# Output: Khoor Zruog
```

**Features**:
- Handles both uppercase and lowercase letters
- Preserves non-alphabetic characters (spaces, punctuation)
- Supports any shift value (automatically wraps around the alphabet)

### 2. Stealth ICMP Transmission (`stealth_ping.py`)

**Purpose**: Transmit encrypted messages through ICMP Echo Request packets, embedding one character per packet in the data field to avoid DPI detection.

**Usage**:
```bash
sudo python3 stealth_ping.py <target_host> <encrypted_message>
```

**Example**:
```bash
sudo python3 stealth_ping.py localhost "Khoor Zruog"
```

**Key Features**:
- Mimics standard ping behavior (timing, packet structure, size)
- Uses process ID as packet identifier (like real ping)
- Sends packets with 1-second intervals
- 32-byte data payload with standard ping pattern
- Marks end of transmission with character 'b'
- Requires root privileges for raw socket access

**DPI Evasion Techniques**:
- Identical ICMP header structure to legitimate ping
- Standard packet timing and size
- Maintains normal ping data patterns (except first byte)
- Uses sequential packet numbering

### 3. MitM Decoder (`mitm_decoder.py`)

**Purpose**: Intercept ICMP packets and decode hidden Caesar cipher messages by trying all possible shift combinations.

**Usage**:
```bash
# Live packet capture (requires root)
sudo python3 mitm_decoder.py

# Simulation mode with provided encrypted text
python3 mitm_decoder.py <encrypted_message>
```

**Examples**:
```bash
# Analyze encrypted text directly
python3 mitm_decoder.py "Khoor Zruog"

# Capture live ICMP packets (requires root)
sudo python3 mitm_decoder.py
```

**Features**:
- Tries all 26 possible Caesar cipher shifts (0-25)
- Intelligent English text detection algorithm
- Highlights most probable plaintext in green
- Can capture live ICMP packets or analyze provided text
- Scores decryptions based on English language patterns

**English Detection Algorithm**:
- Recognizes common English words
- Analyzes vowel-to-consonant ratios
- Detects common letter patterns (TH, HE, IN, etc.)
- Penalizes unusual letter combinations
- Considers typical English word length distributions

## Complete Demonstration

### Running the Full Demo

```bash
python3 demo.py
```

This runs a complete demonstration showing:
1. Original message encryption
2. Simulated stealth transmission
3. MitM attack and decoding

### Example Workflow

1. **Encrypt a message**:
   ```bash
   python3 caesar_cipher.py "Secret Data" 7
   # Output: Zljyla Khah
   ```

2. **Transmit via stealth ICMP** (simulation):
   - Each character sent in separate ICMP packet
   - Packets look identical to normal ping traffic
   - End marker 'b' signals transmission complete

3. **Intercept and decode**:
   ```bash
   python3 mitm_decoder.py "Zljyla Khah"
   # Tries all shifts, identifies "Secret Data" as most likely plaintext
   ```

## Security Implications

### Attack Scenario

An attacker within a corporate network wants to exfiltrate sensitive data without triggering DPI systems that monitor for suspicious patterns. By using this technique:

1. **Data is encrypted** using Caesar cipher (simple but effective for demonstration)
2. **Data is hidden** in legitimate-looking ping traffic
3. **Exfiltration is slow** but undetectable by standard DPI signatures
4. **External accomplice** can decode the data using the MitM tool

### DPI Evasion Techniques Demonstrated

1. **Protocol Mimicry**: ICMP packets are identical to legitimate ping traffic
2. **Timing Normalization**: 1-second intervals match normal ping behavior
3. **Size Consistency**: 32-byte data payload matches default ping size
4. **Header Compliance**: All ICMP headers follow RFC standards
5. **Pattern Obfuscation**: Only one byte per packet is modified

### Defensive Countermeasures

1. **Deep Content Inspection**: Analyze ICMP data patterns for anomalies
2. **Behavioral Analysis**: Monitor for unusual ping patterns or destinations
3. **Statistical Analysis**: Look for non-random data in ICMP payloads
4. **Network Segmentation**: Restrict ICMP traffic between network segments
5. **Encryption Detection**: Use entropy analysis to detect encrypted content

## Technical Requirements

### Dependencies
- Python 3.x
- Root privileges (for raw socket operations in stealth_ping.py and live capture in mitm_decoder.py)

### Supported Platforms
- Linux (tested)
- macOS (should work with root privileges)
- Windows (requires modifications for raw socket handling)

## Files Structure

```
Lab1Sec3/
├── Informe_Laboratorio_1__2025___Sem_2_.pdf  # Original lab requirements
├── caesar_cipher.py                          # Activity 1: Encryption
├── stealth_ping.py                          # Activity 2: Stealth transmission
├── mitm_decoder.py                          # Activity 3: MitM attack
├── demo.py                                  # Complete demonstration
└── README.md                                # This documentation
```

## Lab Report Requirements

As specified in the PDF, this implementation addresses:

1. **Activity 1**: ✅ Caesar cipher encryption with configurable shift
2. **Activity 2**: ✅ Stealth ICMP transmission (one character per packet)
3. **Activity 3**: ✅ MitM attack with brute-force Caesar decoding

The implementation demonstrates that while DPI systems can detect obvious data exfiltration attempts, carefully crafted traffic that mimics legitimate protocols can potentially bypass detection mechanisms.

## Ethical Considerations

This code is provided for educational purposes only. The techniques demonstrated should only be used in authorized penetration testing or educational environments. Unauthorized use of these techniques for data exfiltration is illegal and unethical.

## Future Enhancements

1. **Advanced Encryption**: Implement stronger encryption algorithms
2. **Multiple Protocols**: Extend to other protocols (DNS, HTTP, etc.)
3. **Error Correction**: Add checksums and redundancy for reliable transmission
4. **Adaptive Timing**: Vary transmission intervals to avoid pattern detection
5. **Steganography**: Hide data in packet headers rather than payload