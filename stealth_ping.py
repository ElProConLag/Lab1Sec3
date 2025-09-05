#!/usr/bin/env python3
"""
Transmisión de Datos ICMP Stealth
Lab 1 - Ciberseguridad
Actividad 2: Modo Stealth

Este programa envía texto cifrado a través de paquetes ICMP request para evitar detección
por sistemas de Deep Packet Inspection (DPI). Cada byte UTF-8 se envía como un paquete separado
para soportar caracteres Unicode. La transmisión termina con el carácter 'b'.
"""

import socket
import struct
import time
import sys
import os


def checksum(source_string):
    """
    Calcular el checksum ICMP para los datos dados.
    
    Args:
        source_string (bytes): Los datos para calcular el checksum
        
    Returns:
        int: El checksum calculado
    """
    # Asegurarse de que tenemos un número par de bytes
    if len(source_string) % 2:
        source_string += b'\x00'
    
    # Sumar todas las palabras de 16 bits
    total = 0
    for i in range(0, len(source_string), 2):
        word = (source_string[i] << 8) + source_string[i + 1]
        total += word
        total = (total & 0xffff) + (total >> 16)
    
    # Complemento a uno
    return ~total & 0xffff


def create_icmp_packet_from_byte(byte_val, packet_id, sequence):
    """
    Crear un paquete ICMP Echo Request con un solo valor de byte en el campo de datos.
    
    Args:
        byte_val (int): El valor del byte (0-255) a incrustar en el paquete
        packet_id (int): El ID del paquete
        sequence (int): El número de secuencia
        
    Returns:
        bytes: El paquete ICMP completo
    """
    # ICMP type (8 = Echo Request), code (0), checksum (0 por ahora), id, sequence
    icmp_type = 8
    icmp_code = 0
    icmp_checksum = 0
    
    # Crear datos con el valor del byte y rellenar para parecer datos de ping normales
    # Un ping normal envía 32 bytes de datos por defecto
    data = bytes([byte_val])
    # Rellenar con patrón estándar de ping (bytes incrementales comenzando desde 0x08)
    padding = bytes([(i + 8) % 256 for i in range(31)])
    full_data = data + padding
    
    # Crear cabecera ICMP sin checksum
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, packet_id, sequence)
    
    # Calcular checksum con cabecera y datos
    icmp_checksum = checksum(icmp_header + full_data)
    
    # Recrear cabecera con checksum correcto
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, packet_id, sequence)
    
    return icmp_header + full_data


def create_icmp_packet(data_char, packet_id, sequence):
    """
    Crear un paquete ICMP Echo Request con un solo carácter en el campo de datos.
    Esta función se mantiene para compatibilidad hacia atrás.
    
    Args:
        data_char (str): El carácter a incrustar en el paquete
        packet_id (int): El ID del paquete
        sequence (int): El número de secuencia
        
    Returns:
        bytes: El paquete ICMP completo
    """
    # Convertir carácter a su primer valor de byte UTF-8
    byte_val = data_char.encode('utf-8')[0]
    return create_icmp_packet_from_byte(byte_val, packet_id, sequence)


def send_stealth_ping(target_host, encrypted_message):
    """
    Enviar el mensaje cifrado vía paquetes ICMP stealth.
    Soporta Unicode enviando cada byte UTF-8 como un paquete separado.
    
    Args:
        target_host (str): Hostname o dirección IP de destino
        encrypted_message (str): El mensaje cifrado a transmitir (soporta Unicode)
    """
    try:
        # Crear socket raw (requiere privilegios de root)
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        # Obtener IP de destino
        target_ip = socket.gethostbyname(target_host)
        print(f"Enviando datos stealth a {target_host} ({target_ip})")
        print(f"Mensaje a transmitir: '{encrypted_message}'")
        
        # Convertir mensaje a bytes UTF-8 para soportar caracteres Unicode
        message_bytes = encrypted_message.encode('utf-8')
        print(f"Bytes codificados UTF-8: {len(message_bytes)} bytes")
        print(f"Total de paquetes a enviar: {len(message_bytes) + 1}")  # +1 para marcador de fin
        print("-" * 50)
        
        packet_id = os.getpid() & 0xFFFF  # Usar ID de proceso como ID de paquete (como ping real)
        
        # Enviar cada byte UTF-8 como un paquete ICMP separado
        for i, byte_val in enumerate(message_bytes):
            sequence = i + 1
            packet = create_icmp_packet_from_byte(byte_val, packet_id, sequence)
            
            # Mostrar representación de carácter para legibilidad
            try:
                char_repr = chr(byte_val) if 32 <= byte_val <= 126 else f"\\x{byte_val:02x}"
            except ValueError:
                char_repr = f"\\x{byte_val:02x}"
            
            print(f"Paquete {sequence}: Enviando byte {byte_val} ({char_repr}) en el campo de datos ICMP")
            sock.sendto(packet, (target_ip, 0))
            time.sleep(1)  # Retraso de 1 segundo entre paquetes (como ping normal)
        
        # Enviar marcador de fin (carácter 'b')
        final_sequence = len(message_bytes) + 1
        end_packet = create_icmp_packet_from_byte(ord('b'), packet_id, final_sequence)
        print(f"Paquete {final_sequence}: Enviando marcador de fin (carácter 'b')")
        sock.sendto(end_packet, (target_ip, 0))
        
        sock.close()
        print("-" * 50)
        print("¡Transmisión stealth completada exitosamente!")
        print("Todos los paquetes enviados con timing y formato estándar de ping para evitar detección DPI.")
        print("Caracteres Unicode transmitidos como secuencias de bytes UTF-8.")
        
    except PermissionError:
        print("Error: Este programa requiere privilegios de root para crear sockets raw.")
        print("Por favor ejecute con sudo: sudo python3 stealth_ping.py")
        sys.exit(1)
    except socket.gaierror:
        print(f"Error: No se pudo resolver el hostname '{target_host}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def demonstrate_normal_ping():
    """
    Mostrar cómo se ve un paquete ping normal para comparación.
    """
    print("=" * 60)
    print("ESTRUCTURA DE PAQUETE PING NORMAL (para comparación):")
    print("=" * 60)
    print("Cabecera ICMP (8 bytes):")
    print("  Type: 8 (Echo Request)")
    print("  Code: 0")
    print("  Checksum: Calculado")
    print("  Identifier: ID de proceso")
    print("  Sequence Number: Incremental")
    print("\nDatos ICMP (32 bytes por defecto):")
    print("  Patrón estándar: 0x08, 0x09, 0x0a, 0x0b, ... 0x27")
    print("\nNuestros paquetes stealth usan la MISMA estructura pero reemplazan")
    print("el primer byte de datos con nuestro byte UTF-8, manteniendo el")
    print("mismo timing (intervalos de 1s) y tamaño de paquete para evitar detección.")
    print("Caracteres Unicode se envían como múltiples paquetes (uno por byte UTF-8).")
    print("La transmisión termina con el carácter «b».")
    print("=" * 60)


def main():
    """Función principal para manejar argumentos de línea de comandos y ejecutar transmisión stealth."""
    if len(sys.argv) != 3:
        print("Uso: sudo python3 stealth_ping.py <host_destino> <mensaje_cifrado>")
        print("Ejemplo: sudo python3 stealth_ping.py localhost 'Khoor Zruog'")
        print("\nNota: Este programa requiere privilegios de root para crear sockets raw.")
        sys.exit(1)
    
    target_host = sys.argv[1]
    encrypted_message = sys.argv[2]
    
    demonstrate_normal_ping()
    send_stealth_ping(target_host, encrypted_message)


if __name__ == "__main__":
    main()