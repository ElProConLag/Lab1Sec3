#!/usr/bin/env python3
"""
Decodificador ICMP Man-in-the-Middle
Lab 1 - Ciberseguridad
Actividad 3: MitM

Este programa intercepta paquetes ICMP e intenta decodificar mensajes Caesar cipher
probando todas las combinaciones de desplazamiento posibles (0-25) y resaltando el
texto plano más probable en verde. Soporta caracteres Unicode transmitidos como secuencias de bytes UTF-8.
"""

import socket
import struct
import sys
import re
from collections import Counter


def caesar_decrypt(text, shift):
    """
    Descifrar texto usando Caesar cipher con el valor de desplazamiento dado.
    Soporta caracteres Unicode - solo las letras ASCII son descifradas, los caracteres Unicode se preservan.
    
    Args:
        text (str): El texto a descifrar (soporta Unicode)
        shift (int): El número de posiciones a desplazar hacia atrás
        
    Returns:
        str: El texto descifrado con caracteres Unicode preservados
    """
    decrypted_text = ""
    
    for char in text:
        # Solo aplicar Caesar cipher a letras ASCII, preservar todos los otros caracteres incluyendo Unicode
        if char.isalpha() and ord(char) < 128:  # Solo letras ASCII
            # Manejar letras mayúsculas
            if char.isupper():
                decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            # Manejar letras minúsculas
            else:
                decrypted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            decrypted_text += decrypted_char
        else:
            # Caracteres alfabéticos no ASCII y todos los otros caracteres permanecen sin cambio
            decrypted_text += char
    
    return decrypted_text


def calculate_english_score(text):
    """
    Calcular una puntuación indicando qué tan probable es que el texto sea inglés.
    Puntuaciones más altas indican texto inglés más probable.
    
    Args:
        text (str): El texto a analizar
        
    Returns:
        float: La puntuación de probabilidad de inglés
    """
    # Convertir a mayúsculas y remover caracteres no alfabéticos para análisis
    clean_text = ''.join(char.upper() for char in text if char.isalpha())
    
    if not clean_text:
        return 0
    
    score = 0
    
    # Verificar palabras comunes en inglés (insensible a mayúsculas/minúsculas)
    common_words = ['HELLO', 'WORLD', 'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 
                   'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'HAVE', 'SECRET', 'MESSAGE',
                   'THIS', 'THAT', 'WITH', 'WILL', 'FROM', 'THEY', 'KNOW', 'ATTACK',
                   'WANT', 'BEEN', 'GOOD', 'MUCH', 'SOME', 'TIME', 'VERY', 'DATA',
                   'WHEN', 'COME', 'HERE', 'HOW', 'JUST', 'LIKE', 'LONG', 'PING',
                   'MAKE', 'MANY', 'OVER', 'SUCH', 'TAKE', 'THAN', 'THEM', 'ICMP',
                   'WELL', 'WERE', 'PACKET', 'NETWORK', 'SECURITY', 'CIPHER', 'KEY']
    
    # Dividir por espacios y verificar cada palabra
    words = text.upper().split()
    for word in words:
        word_clean = ''.join(char for char in word if char.isalpha())
        if word_clean in common_words:
            score += 50  # Bonificación alta para palabras comunes en inglés
    
    # Verificar patrones de letras comunes en inglés
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
    
    # Bonificación por tener vocales (A, E, I, O, U)
    vowels = sum(1 for char in clean_text if char in 'AEIOU')
    consonants = len(clean_text) - vowels
    
    # El inglés típicamente tiene una proporción de vocales entre 35-45%
    if len(clean_text) > 0:
        vowel_ratio = vowels / len(clean_text)
        if 0.30 <= vowel_ratio <= 0.50:
            score += 20
    
    # Penalizar combinaciones de letras inusuales
    unusual_patterns = ['QQ', 'XX', 'ZZ', 'JJ', 'VV', 'WW']
    for pattern in unusual_patterns:
        if pattern in clean_text:
            score -= 20
    
    # Verificar distribución de longitud de palabras razonable
    if words:
        avg_word_length = sum(len(''.join(char for char in word if char.isalpha())) for word in words) / len(words)
        if 3 <= avg_word_length <= 7:  # Longitudes típicas de palabras en inglés
            score += 10
    
    return score


def parse_icmp_packet(packet):
    """
    Analizar un paquete ICMP y extraer el valor del byte del campo de datos.
    
    Args:
        packet (bytes): Los datos del paquete crudo
        
    Returns:
        tuple: (icmp_type, byte_value, sequence) o (None, None, None) si no es un ICMP Echo Request válido
    """
    try:
        # Analizar cabecera IP (mínimo 20 bytes)
        ip_header = struct.unpack('!BBHHHBBH4s4s', packet[:20])
        ip_header_length = (ip_header[0] & 0xF) * 4
        
        # Analizar cabecera ICMP (8 bytes)
        icmp_header = struct.unpack('!BBHHH', packet[ip_header_length:ip_header_length + 8])
        icmp_type, icmp_code, checksum, packet_id, sequence = icmp_header
        
        # Solo procesar paquetes ICMP Echo Request (type 8)
        if icmp_type == 8:
            # Extraer el primer byte de datos ICMP (nuestro byte oculto)
            data_start = ip_header_length + 8
            if len(packet) > data_start:
                byte_value = packet[data_start]
                return icmp_type, byte_value, sequence
        
        return None, None, None
        
    except (struct.error, IndexError, ValueError):
        return None, None, None


def capture_icmp_packets():
    """
    Capturar paquetes ICMP y extraer bytes ocultos, luego reconstruir mensaje UTF-8.
    
    Returns:
        str: El mensaje reconstruido de los paquetes ICMP
    """
    try:
        # Crear socket raw para capturar paquetes ICMP
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        print("Escuchando paquetes ICMP...")
        print("Presione Ctrl+C para parar y analizar los datos capturados")
        print("-" * 50)
        
        captured_bytes = {}
        
        while True:
            packet, addr = sock.recvfrom(1024)
            icmp_type, byte_value, sequence = parse_icmp_packet(packet)
            
            if icmp_type == 8 and byte_value is not None:  # ICMP Echo Request
                # Mostrar representación de carácter para legibilidad
                try:
                    char_repr = chr(byte_value) if 32 <= byte_value <= 126 else f"\\x{byte_value:02x}"
                except ValueError:
                    char_repr = f"\\x{byte_value:02x}"
                
                print(f"Paquete capturado {sequence}: Byte {byte_value} ({char_repr}) de {addr[0]}")
                captured_bytes[sequence] = byte_value
                
                # Verificar si recibimos el marcador de fin (carácter 'b')
                if byte_value == ord('b'):
                    print("Marcador de fin (carácter 'b') recibido. Deteniendo captura.")
                    break
        
        sock.close()
        
        # Reconstruir mensaje en orden de secuencia (excluyendo el marcador de fin)
        byte_list = []
        for seq in sorted(captured_bytes.keys()):
            if captured_bytes[seq] != ord('b'):  # Excluir marcador de fin
                byte_list.append(captured_bytes[seq])
        
        # Convertir bytes de vuelta a cadena UTF-8
        try:
            message = bytes(byte_list).decode('utf-8')
            return message
        except UnicodeDecodeError as e:
            print(f"Advertencia: No se pudo decodificar como UTF-8: {e}")
            # Devolver como latin-1 para preservar todos los valores de byte
            return bytes(byte_list).decode('latin-1')
        
    except PermissionError:
        print("Error: Este programa requiere privilegios de root para capturar paquetes.")
        print("Por favor ejecute con sudo: sudo python3 mitm_decoder.py")
        return None
    except KeyboardInterrupt:
        print("\nCaptura detenida por el usuario.")
        sock.close()
        
        # Reconstruir mensaje de los datos capturados
        byte_list = []
        for seq in sorted(captured_bytes.keys()):
            if captured_bytes[seq] != ord('b'):  # Excluir marcador de fin
                byte_list.append(captured_bytes[seq])
        
        # Convertir bytes de vuelta a cadena UTF-8
        try:
            message = bytes(byte_list).decode('utf-8')
            return message
        except UnicodeDecodeError as e:
            print(f"Advertencia: No se pudo decodificar como UTF-8: {e}")
            # Devolver como latin-1 para preservar todos los valores de byte
            return bytes(byte_list).decode('latin-1')
    except Exception as e:
        print(f"Error: {e}")
        return None


def analyze_captured_message(encrypted_message):
    """
    Analizar el mensaje capturado probando todos los desplazamientos Caesar cipher.
    
    Args:
        encrypted_message (str): El mensaje cifrado capturado
    """
    if not encrypted_message:
        print("No se capturó ningún mensaje.")
        return
    
    print(f"\nMensaje cifrado capturado: '{encrypted_message}'")
    print("\nProbando todos los desplazamientos Caesar cipher posibles:")
    print("=" * 70)
    
    # Colores para salida de terminal
    GREEN = '\033[92m'  # Color verde
    RESET = '\033[0m'   # Resetear color
    
    best_score = float('-inf')
    best_shift = 0
    best_message = ""
    
    # Probar todos los desplazamientos posibles (0-25)
    for shift in range(26):
        decrypted = caesar_decrypt(encrypted_message, shift)
        score = calculate_english_score(decrypted)
        
        # Rastrear el mejor resultado (más probable en inglés)
        if score > best_score:
            best_score = score
            best_shift = shift
            best_message = decrypted
        
        print(f"Desplazamiento {shift:2d}: {decrypted} (Puntuación: {score:.2f})")
    
    print("=" * 70)
    print(f"{GREEN}Texto plano más probable (Desplazamiento {best_shift}): {best_message}{RESET}")
    print(f"Puntuación de probabilidad de inglés: {best_score:.2f}")


def simulate_with_test_data(test_message):
    """
    Simular el ataque MitM con datos de prueba en lugar de capturar paquetes en vivo.
    
    Args:
        test_message (str): El mensaje cifrado a analizar
    """
    print("MODO SIMULACIÓN: Analizando mensaje cifrado proporcionado")
    print("-" * 50)
    analyze_captured_message(test_message)


def main():
    """Función principal para manejar argumentos de línea de comandos y ejecutar el decodificador MitM."""
    if len(sys.argv) == 1:
        # Modo de captura de paquetes en vivo
        print("Iniciando captura de paquetes ICMP y decodificador MitM...")
        captured_message = capture_icmp_packets()
        if captured_message:
            analyze_captured_message(captured_message)
    elif len(sys.argv) == 2:
        # Modo simulación con mensaje cifrado proporcionado
        test_message = sys.argv[1]
        simulate_with_test_data(test_message)
    else:
        print("Uso:")
        print("  sudo python3 mitm_decoder.py                    # Captura de paquetes en vivo")
        print("  python3 mitm_decoder.py <mensaje_cifrado>       # Modo simulación")
        print("\nEjemplos:")
        print("  sudo python3 mitm_decoder.py                    # Capturar paquetes ICMP en vivo")
        print("  python3 mitm_decoder.py 'Khoor Zruog'           # Analizar texto cifrado dado")
        sys.exit(1)


if __name__ == "__main__":
    main()