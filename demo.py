#!/usr/bin/env python3
"""
Lab 1 - Script de Demostración de Ciberseguridad
Demostración completa de las tres actividades con soporte Unicode

Este script demuestra el flujo de trabajo completo:
1. Cifrar un mensaje usando Caesar cipher (soporta Unicode)
2. Mostrar cómo se transmitiría el mensaje vía paquetes ICMP stealth (nivel de bytes UTF-8)
3. Demostrar el ataque MitM decodificando todas las combinaciones Caesar posibles
"""

import subprocess
import sys
import os

# Constante a nivel de módulo para el directorio de scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_demo():
    """Ejecutar la demostración completa del laboratorio de ciberseguridad."""
    print("=" * 70)
    print("LAB 1 - DEMOSTRACIÓN DE CIBERSEGURIDAD")
    print("Evasión de Deep Packet Inspection (DPI) vía Modo ICMP Stealth")
    print("Soporte Unicode Habilitado")
    print("=" * 70)
    
    # Mensaje demo con Unicode
    original_message = "Secret 世界"  # "Secret World" en chino
    shift_value = 7
    
    print(f"\n1. MENSAJE ORIGINAL: '{original_message}' (incluye Unicode)")
    print(f"   Valor de desplazamiento: {shift_value}")
    print(f"   Longitud en bytes UTF-8: {len(original_message.encode('utf-8'))} bytes")
    
    # Actividad 1: Cifrado Caesar
    print("\n" + "="*50)
    print("ACTIVIDAD 1: CIFRADO CAESAR")
    print("="*50)
    
    result = subprocess.run([
        'python3', 'caesar_cipher.py', original_message, str(shift_value)
    ], capture_output=True, text=True, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        print(result.stdout)
        # Extraer texto cifrado de la salida (última línea)
        encrypted_message = result.stdout.strip().split('\n')[-1]
    else:
        print(f"Error en Caesar cipher: {result.stderr}")
        return
    
    # Actividad 2: Modo Stealth (Simulación)
    print("\n" + "="*50)
    print("ACTIVIDAD 2: TRANSMISIÓN ICMP STEALTH")
    print("="*50)
    print("NOTA: Esto normalmente requiere privilegios de root para sockets raw.")
    print("Simulando el proceso de transmisión stealth...\n")
    
    print(f"Mensaje cifrado a transmitir: '{encrypted_message}'")
    
    # Mostrar descomposición de bytes UTF-8
    message_bytes = encrypted_message.encode('utf-8')
    print(f"Bytes codificados UTF-8: {list(message_bytes)}")
    print(f"Número de paquetes ICMP necesarios: {len(message_bytes) + 1}")
    print("\nTransmisión simulada de paquetes ICMP:")
    
    for i, byte_val in enumerate(message_bytes):
        try:
            char_repr = chr(byte_val) if 32 <= byte_val <= 126 else f"\\x{byte_val:02x}"
        except ValueError:
            char_repr = f"\\x{byte_val:02x}"
        print(f"  Paquete {i+1}: Byte {byte_val} ({char_repr}) incrustado en el campo de datos ICMP")
    print(f"  Paquete {len(message_bytes)+1}: Marcador de fin (carácter 'b')")
    
    print("\nCada paquete se vería como un ping normal con:")
    print("  - Cabecera ICMP Echo Request estándar (Type 8, Code 0)")
    print("  - ID de proceso como identificador de paquete")
    print("  - Numeración secuencial de paquetes")
    print("  - Payload de datos de 32 bytes (primer byte = nuestro byte UTF-8)")
    print("  - Intervalos de 1 segundo entre paquetes")
    print("  - Esto imita el comportamiento normal de ping para evitar detección DPI")
    print("  - Caracteres Unicode enviados como múltiples paquetes (uno por byte UTF-8)")
    
    # Actividad 3: Ataque MitM y Decodificación
    print("\n" + "="*50)
    print("ACTIVIDAD 3: ATAQUE MAN-IN-THE-MIDDLE & DECODIFICACIÓN")
    print("="*50)
    
    result = subprocess.run([
        'python3', 'mitm_decoder.py', encrypted_message
    ], capture_output=True, text=True, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error en el decodificador MitM: {result.stderr}")
    
    # Demostrar con un segundo ejemplo (solo ASCII)
    print("\n" + "="*50)
    print("BONUS: EJEMPLO SOLO ASCII")
    print("="*50)
    
    ascii_message = "Hello World"
    print(f"Mensaje ASCII: '{ascii_message}'")
    
    result = subprocess.run([
        'python3', 'caesar_cipher.py', ascii_message, "3"
    ], capture_output=True, text=True, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        ascii_encrypted = result.stdout.strip().split('\n')[-1]
        print(f"Cifrado: '{ascii_encrypted}'")
        
        result = subprocess.run([
            'python3', 'mitm_decoder.py', ascii_encrypted
        ], capture_output=True, text=True, cwd=SCRIPT_DIR)
        
        if result.returncode == 0:
            # Extraer solo la línea de resultado
            lines = result.stdout.split('\n')
            for line in lines:
                if "Most likely plaintext" in line:
                    print(line)
    
    print("\n" + "="*70)
    print("DEMOSTRACIÓN COMPLETA")
    print("="*70)
    print("\nRESUMEN:")
    print(f"✓ Mensaje original: '{original_message}' (Unicode soportado)")
    print(f"✓ Cifrado Caesar (desplazamiento {shift_value}): '{encrypted_message}'")
    print("✓ Simulación de transmisión ICMP stealth completada")
    print("✓ Transmisión a nivel de bytes UTF-8 asegura compatibilidad Unicode")
    print("✓ Ataque MitM decodificó exitosamente el mensaje")
    print("\nEsto demuestra cómo los atacantes pueden:")
    print("1. Ocultar datos en tráfico de red aparentemente inocente")
    print("2. Evadir sistemas DPI que solo buscan patrones obvios")
    print("3. Soportar caracteres internacionales vía codificación UTF-8")
    print("4. Interceptar y decodificar mensajes ocultos si conocen el método")


def main():
    """Función principal."""
    # Verificar si estamos en el directorio correcto
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'caesar_cipher.py')):
        print("Error: Archivos del laboratorio no encontrados. Por favor ejecute desde el directorio correcto.")
        sys.exit(1)
    
    run_demo()


if __name__ == "__main__":
    main()