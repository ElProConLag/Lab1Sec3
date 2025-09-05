#!/usr/bin/env python3
"""
Implementación de Caesar Cipher
Lab 1 - Ciberseguridad
Actividad 1: Algoritmo de Cifrado

Este programa implementa el algoritmo Caesar cipher para cifrar texto usando un valor de desplazamiento especificado.
"""

import sys
import os
import argparse


def load_dictionary_from_file(filename):
    """
    Cargar palabras del diccionario desde un archivo de texto.
    
    Args:
        filename (str): Ruta al archivo del diccionario
        
    Returns:
        list: Lista de palabras en mayúsculas del archivo
    """
    words = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                # Omitir comentarios y líneas vacías
                if line and not line.startswith('#'):
                    words.append(line.upper())
    except FileNotFoundError:
        print(f"Advertencia: Archivo de diccionario '{filename}' no encontrado. Usando palabras de respaldo.", file=sys.stderr)
        # Recurrir a diccionario mínimo si no se encuentra el archivo
        if 'spanish' in filename.lower():
            words = ['HOLA', 'MUNDO', 'MENSAJE', 'SECRETO', 'CIFRADO', 'SEGURIDAD']
        else:
            words = ['HELLO', 'WORLD', 'MESSAGE', 'SECRET', 'CIPHER', 'SECURITY']
    except Exception as e:
        print(f"Error cargando diccionario '{filename}': {e}", file=sys.stderr)
        words = []
    
    return words


# Cargar diccionarios desde archivos externos
SPANISH_DICTIONARY = load_dictionary_from_file('spanish_dictionary.txt')
ENGLISH_DICTIONARY = load_dictionary_from_file('english_dictionary.txt')

# Códigos de color ANSI para salida de terminal
GREEN = '\033[92m'  # Color verde
YELLOW = '\033[93m' # Color amarillo
RESET = '\033[0m'   # Resetear color


def caesar_encrypt(text, shift):
    """
    Cifrar texto usando Caesar cipher con el valor de desplazamiento dado.
    Soporta caracteres Unicode - solo las letras ASCII son cifradas, los caracteres Unicode se preservan.
    
    Args:
        text (str): El texto a cifrar (soporta Unicode)
        shift (int): El número de posiciones a desplazar cada carácter
        
    Returns:
        str: El texto cifrado con caracteres Unicode preservados
    """
    encrypted_text = ""
    
    for char in text:
        # Solo aplicar Caesar cipher a letras ASCII, preservar todos los otros caracteres incluyendo Unicode
        if char.isalpha() and ord(char) < 128:  # Solo letras ASCII
            # Manejar letras mayúsculas
            if char.isupper():
                encrypted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            # Manejar letras minúsculas
            else:
                encrypted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            encrypted_text += encrypted_char
        else:
            # Caracteres alfabéticos no ASCII y todos los otros caracteres permanecen sin cambio
            encrypted_text += char
    
    return encrypted_text


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
    decrypted_chars = []
    
    for char in text:
        # Solo aplicar Caesar cipher a letras ASCII, preservar todos los otros caracteres incluyendo Unicode
        if char.isalpha() and ord(char) < 128:  # Solo letras ASCII
            # Manejar letras mayúsculas
            if char.isupper():
                decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            # Manejar letras minúsculas
            else:
                decrypted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            decrypted_chars.append(decrypted_char)
        else:
            # Caracteres alfabéticos no ASCII y todos los otros caracteres permanecen sin cambio
            decrypted_chars.append(char)
    
    return "".join(decrypted_chars)


def calculate_spanish_score(text):
    """
    Calcular una puntuación indicando qué tan probable es que el texto sea español.
    Puntuaciones más altas indican texto español más probable.
    
    Args:
        text (str): El texto a analizar
        
    Returns:
        float: La puntuación de probabilidad de español
    """
    # Convertir a mayúsculas y remover caracteres no alfabéticos para análisis
    clean_text = ''.join(char.upper() for char in text if char.isalpha())
    
    if not clean_text:
        return 0
    
    score = 0
    
    # Verificar palabras comunes en español (insensible a mayúsculas/minúsculas)
    common_words = SPANISH_DICTIONARY
    
    # Dividir por espacios y verificar cada palabra
    words = text.upper().split()
    cleaned_words = []
    for word in words:
        word_clean = ''.join(char for char in word if char.isalpha())
        if not word_clean:
            continue
        cleaned_words.append(word_clean)
        if word_clean in common_words:
            score += 50  # Bonificación alta para palabras comunes en español
    
    # Verificar patrones de letras comunes en español
    if 'QU' in clean_text:
        score += 15  # QU es muy común en español
    if 'LL' in clean_text:
        score += 10  # LL es común en español
    if 'RR' in clean_text:
        score += 10  # RR es distintivo en español
    if 'Ñ' in clean_text:
        score += 5   # Ñ es un indicador fuerte
    if 'CH' in clean_text:
        score += 8   # CH es común en español
    
    # Bonificación por tener vocales (A, E, I, O, U) - El español tiene alta frecuencia de vocales
    vowels = sum(1 for char in clean_text if char in 'AEIOU')
    consonants = len(clean_text) - vowels
    
    # El español típicamente tiene una proporción de vocales más alta que el inglés (40-50%)
    vowel_ratio = vowels / len(clean_text)
    if 0.40 <= vowel_ratio <= 0.55:
        score += 25
    elif 0.35 <= vowel_ratio <= 0.60:
        score += 15
    
    # Verificar patrones de frecuencia de letras específicos del español
    # El español tiene alta frecuencia de A, E, O
    a_count = clean_text.count('A')
    e_count = clean_text.count('E')
    o_count = clean_text.count('O')
    
    a_freq = a_count / len(clean_text)
    e_freq = e_count / len(clean_text)
    o_freq = o_count / len(clean_text)
    
    if a_freq > 0.11:  # El español tiene alta frecuencia de A
        score += 10
    if e_freq > 0.12:  # El español tiene alta frecuencia de E
        score += 10
    if o_freq > 0.08:  # El español tiene frecuencia moderada de O
        score += 8
    
    # Penalizar combinaciones de letras que son inusuales en español
    unusual_patterns = ['KK', 'WW', 'ZZ', 'XX', 'QQ']
    for pattern in unusual_patterns:
        if pattern in clean_text:
            score -= 15
    
    # Verificar distribución de longitud de palabras razonable
    if cleaned_words:
        avg_word_length = sum(len(w) for w in cleaned_words) / len(cleaned_words)
        if 4 <= avg_word_length <= 8:  # Longitudes típicas de palabras en español
            score += 10
    
    return score


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
    common_words = ENGLISH_DICTIONARY
    
    # Dividir por espacios y verificar cada palabra
    words = text.upper().split()
    cleaned_words = []
    for word in words:
        word_clean = ''.join(char for char in word if char.isalpha())
        if not word_clean:
            continue
        cleaned_words.append(word_clean)
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
    if cleaned_words:
        avg_word_length = sum(len(w) for w in cleaned_words) / len(cleaned_words)
        if 3 <= avg_word_length <= 7:  # Longitudes típicas de palabras en inglés
            score += 10
    
    return score


def analyze_with_language_detection(encrypted_message):
    """
    Analizar mensaje cifrado probando todos los desplazamientos Caesar cipher y detectando idioma.
    Prioriza la detección de español sobre inglés pero mantiene ambos.
    
    Args:
        encrypted_message (str): El mensaje cifrado a analizar
        
    Returns:
        dict: Resultados con mejores candidatos en español e inglés
    """
    if not encrypted_message:
        return None
    
    print(f"\nAnalizando mensaje cifrado: '{encrypted_message}'")
    print("\nProbando todos los desplazamientos Caesar cipher posibles:")
    print("=" * 80)
    
    best_spanish_score = float('-inf')
    best_spanish_shift = 0
    best_spanish_message = ""
    
    best_english_score = float('-inf')
    best_english_shift = 0
    best_english_message = ""
    
    # Probar todos los desplazamientos posibles (0-25)
    for shift in range(26):
        decrypted = caesar_decrypt(encrypted_message, shift)
        spanish_score = calculate_spanish_score(decrypted)
        english_score = calculate_english_score(decrypted)
        
        # Rastrear el mejor resultado en español
        if spanish_score > best_spanish_score:
            best_spanish_score = spanish_score
            best_spanish_shift = shift
            best_spanish_message = decrypted
        
        # Rastrear el mejor resultado en inglés
        if english_score > best_english_score:
            best_english_score = english_score
            best_english_shift = shift
            best_english_message = decrypted
        
        print(f"Desplazamiento {shift:2d}: {decrypted} (ES: {spanish_score:.1f}, EN: {english_score:.1f})")
    
    print("=" * 80)
    
    # Priorizar español pero mostrar ambos resultados
    if best_spanish_score > 0 and best_spanish_score >= best_english_score * 0.8:
        # El español tiene buena puntuación y es competitivo con el inglés
        print(f"{GREEN}Texto español más probable (Desplazamiento {best_spanish_shift}): {best_spanish_message}{RESET}")
        print(f"Puntuación de probabilidad de español: {best_spanish_score:.2f}")
        if best_english_score > 0:
            print(f"{YELLOW}Texto inglés alternativo (Desplazamiento {best_english_shift}): {best_english_message}{RESET}")
            print(f"Puntuación de probabilidad de inglés: {best_english_score:.2f}")
    elif best_english_score > 0:
        # Recurrir al inglés
        print(f"{YELLOW}Texto inglés más probable (Desplazamiento {best_english_shift}): {best_english_message}{RESET}")
        print(f"Puntuación de probabilidad de inglés: {best_english_score:.2f}")
        if best_spanish_score > 0:
            print(f"Alternativa en español (Desplazamiento {best_spanish_shift}): {best_spanish_message}")
            print(f"Puntuación de probabilidad de español: {best_spanish_score:.2f}")
    else:
        # No se detectó patrón de idioma claro
        print("No se detectó patrón de idioma claro. Mostrando ambos mejores candidatos:")
        print(f"Mejor candidato español (Desplazamiento {best_spanish_shift}): {best_spanish_message} (Puntuación: {best_spanish_score:.2f})")
        print(f"Mejor candidato inglés (Desplazamiento {best_english_shift}): {best_english_message} (Puntuación: {best_english_score:.2f})")
    
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
    """Función principal para manejar argumentos de línea de comandos y ejecutar cifrado o descifrado."""
    parser = argparse.ArgumentParser(
        description="Implementación de Caesar Cipher - cifra, descifra o analiza texto cifrado con Caesar.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s "Hello World" 3              # Cifrar texto con desplazamiento 3
  %(prog)s --decrypt "Khoor Zruog"      # Descifrar y mostrar todas las posibilidades
  %(prog)s --analyze "Krod pxqgr"       # Analizar con detección de idioma
        """
    )
    
    # Crear grupo mutuamente exclusivo para los tres modos principales
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('text', nargs='?', help='Texto a cifrar (requiere argumento de desplazamiento)')
    group.add_argument('--decrypt', dest='decrypt_text', metavar='TEXT', 
                      help='Texto a descifrar (muestra todos los desplazamientos posibles)')
    group.add_argument('--analyze', dest='analyze_text', metavar='TEXT',
                      help='Texto a analizar para detección de idioma')
    
    # Argumento de desplazamiento para modo de cifrado
    parser.add_argument('shift', nargs='?', type=int, 
                       help='Valor de desplazamiento para cifrado (requerido al cifrar)')
    
    try:
        args = parser.parse_args()
        
        # Modo descifrado
        if args.decrypt_text:
            encrypted_text = args.decrypt_text
            print(f"Texto cifrado: {encrypted_text}", file=sys.stderr)
            
            # Probar todos los desplazamientos y mostrar todas las posibilidades
            print("Todos los descifrados posibles:")
            for shift in range(26):
                decrypted = caesar_decrypt(encrypted_text, shift)
                print(f"Desplazamiento {shift:2d}: {decrypted}")
            
            return
        
        # Modo análisis (con detección de idioma)
        elif args.analyze_text:
            encrypted_text = args.analyze_text
            analyze_with_language_detection(encrypted_text)
            return
        
        # Modo cifrado (por defecto)
        elif args.text:
            if args.shift is None:
                parser.error("El valor de desplazamiento es requerido al cifrar texto")
            
            text_to_encrypt = args.text
            shift_value = args.shift
            
            print(f"Texto original: {text_to_encrypt}", file=sys.stderr)
            print(f"Valor de desplazamiento: {shift_value}", file=sys.stderr)
            
            encrypted_text = caesar_encrypt(text_to_encrypt, shift_value)
            print(encrypted_text)
            
            return encrypted_text
        
        else:
            parser.print_help()
            sys.exit(1)
            
    except ValueError as e:
        parser.error(f"El valor de desplazamiento debe ser un entero: {e}")
    except Exception as e:
        parser.error(f"Error: {e}")


if __name__ == "__main__":
    main()