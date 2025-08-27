# Laboratorio 1 - Ciberseguridad: Evasión de DPI mediante Modo Stealth ICMP

## Resumen

Este laboratorio demuestra cómo los atacantes pueden evadir los sistemas de Inspección Profunda de Paquetes (DPI) ocultando datos cifrados dentro de tráfico ICMP ping aparentemente inocente. La implementación consiste en tres programas Python que muestran la cadena completa de ataque desde el cifrado hasta la exfiltración de datos y la interceptación y decodificación.

## Objetivos del Laboratorio

El objetivo es auditar si los sistemas DPI pueden detectar efectivamente la exfiltración de datos a través del tráfico de red mediante:

1. Creación de un algoritmo de cifrado César
2. Implementación de transmisión stealth de datos via paquetes ICMP
3. Demostración de un ataque Man-in-the-Middle (MitM) para interceptar y decodificar mensajes ocultos

## Programas Implementados

### 1. Cifrado César (`caesar_cipher.py`)

**Propósito**: Cifrar mensajes de texto plano usando el algoritmo de cifrado César con un valor de desplazamiento configurable.

**Uso**:
```bash
python3 caesar_cipher.py <text_to_encrypt> <shift_value>
```

**Ejemplo**:
```bash
python3 caesar_cipher.py "Hello World" 3
# Salida: Khoor Zruog
```

**Características**:
- Maneja letras mayúsculas y minúsculas
- Preserva caracteres no alfabéticos (espacios, puntuación)
- Soporta cualquier valor de desplazamiento (se ajusta automáticamente alrededor del alfabeto)

### 2. Transmisión ICMP Stealth (`stealth_ping.py`)

**Propósito**: Transmitir mensajes cifrados a través de paquetes ICMP Echo Request, incrustando un carácter por paquete en el campo de datos para evitar la detección DPI.

**Uso**:
```bash
sudo python3 stealth_ping.py <host_objetivo> <mensaje_cifrado>
```

**Ejemplo**:
```bash
sudo python3 stealth_ping.py localhost "Khoor Zruog"
```

**Características Clave**:
- Imita el comportamiento estándar de ping (temporización, estructura de paquetes, tamaño)
- Usa ID de proceso como identificador de paquete (como el ping real)
- Envía paquetes con intervalos de 1 segundo
- Payload de datos de 32 bytes con patrón estándar de ping
- Marca el final de transmisión con el carácter 'b'
- Requiere privilegios de root para acceso a socket raw

**Técnicas de Evasión DPI**:
- Estructura de encabezado ICMP idéntica al ping legítimo
- Temporización y tamaño de paquete estándar
- Mantiene patrones normales de datos ping (excepto primer byte)
- Usa numeración secuencial de paquetes

### 3. Decodificador MitM (`mitm_decoder.py`)

**Propósito**: Interceptar paquetes ICMP y decodificar mensajes César ocultos probando todas las combinaciones de desplazamiento posibles.

**Uso**:
```bash
# Captura de paquetes en vivo (requiere root)
sudo python3 mitm_decoder.py

# Modo simulación con texto cifrado proporcionado
python3 mitm_decoder.py <mensaje_cifrado>
```

**Ejemplos**:
```bash
# Analizar texto cifrado directamente
python3 mitm_decoder.py "Khoor Zruog"

# Capturar paquetes ICMP en vivo (requiere root)
sudo python3 mitm_decoder.py
```

**Características**:
- Prueba los 26 posibles desplazamientos de cifrado César (0-25)
- Algoritmo inteligente de detección de texto en inglés
- Resalta el texto plano más probable en verde
- Puede capturar paquetes ICMP en vivo o analizar texto proporcionado
- Puntúa las decodificaciones basándose en patrones del idioma inglés

**Algoritmo de Detección de Inglés**:
- Reconoce palabras comunes en inglés
- Analiza proporciones de vocales a consonantes
- Detecta patrones comunes de letras (TH, HE, IN, etc.)
- Penaliza combinaciones de letras inusuales
- Considera distribuciones típicas de longitud de palabras en inglés

## Demostración Completa

### Ejecutando la Demo Completa

```bash
python3 demo.py
```

Esto ejecuta una demostración completa mostrando:
1. Cifrado del mensaje original
2. Transmisión stealth simulada
3. Ataque MitM y decodificación

### Flujo de Trabajo de Ejemplo

1. **Cifrar un mensaje**:
   ```bash
   python3 caesar_cipher.py "Secret Data" 7
   # Salida: Zljyla Khah
   ```

2. **Transmitir via ICMP stealth** (simulación):
   - Cada carácter enviado en paquete ICMP separado
   - Los paquetes se ven idénticos al tráfico ping normal
   - El marcador de fin 'b' señala transmisión completa

3. **Interceptar y decodificar**:
   ```bash
   python3 mitm_decoder.py "Zljyla Khah"
   # Prueba todos los desplazamientos, identifica "Secret Data" como texto plano más probable
   ```

## Implicaciones de Seguridad

### Escenario de Ataque

Un atacante dentro de una red corporativa quiere exfiltrar datos sensibles sin activar sistemas DPI que monitorean patrones sospechosos. Usando esta técnica:

1. **Los datos son cifrados** usando cifrado César (simple pero efectivo para demostración)
2. **Los datos se ocultan** en tráfico ping de apariencia legítima
3. **La exfiltración es lenta** pero indetectable por firmas DPI estándar
4. **Un cómplice externo** puede decodificar los datos usando la herramienta MitM

### Técnicas de Evasión DPI Demostradas

1. **Imitación de Protocolo**: Los paquetes ICMP son idénticos al tráfico ping legítimo
2. **Normalización de Temporización**: Intervalos de 1 segundo coinciden con comportamiento normal de ping
3. **Consistencia de Tamaño**: Payload de datos de 32 bytes coincide con tamaño predeterminado de ping
4. **Cumplimiento de Encabezados**: Todos los encabezados ICMP siguen estándares RFC
5. **Ofuscación de Patrones**: Solo un byte por paquete es modificado

### Contramedidas Defensivas

1. **Inspección Profunda de Contenido**: Analizar patrones de datos ICMP para anomalías
2. **Análisis Comportamental**: Monitorear patrones de ping inusuales o destinos
3. **Análisis Estadístico**: Buscar datos no aleatorios en payloads ICMP
4. **Segmentación de Red**: Restringir tráfico ICMP entre segmentos de red
5. **Detección de Cifrado**: Usar análisis de entropía para detectar contenido cifrado

## Requisitos Técnicos

### Dependencias
- Python 3.x
- Privilegios de root (para operaciones de socket raw en stealth_ping.py y captura en vivo en mitm_decoder.py)

### Plataformas Soportadas
- Linux (probado)
- macOS (debería funcionar con privilegios de root)
- Windows (requiere modificaciones para manejo de socket raw)

## Estructura de Archivos

```
Lab1Sec3/
├── Informe_Laboratorio_1__2025___Sem_2_.pdf  # Requisitos originales del laboratorio
├── caesar_cipher.py                          # Actividad 1: Cifrado
├── stealth_ping.py                          # Actividad 2: Transmisión stealth
├── mitm_decoder.py                          # Actividad 3: Ataque MitM
├── demo.py                                  # Demostración completa
└── README.md                                # Esta documentación
```

## Requisitos del Informe de Laboratorio

Como se especifica en el PDF, esta implementación aborda:

1. **Actividad 1**: ✅ Cifrado César con desplazamiento configurable
2. **Actividad 2**: ✅ Transmisión ICMP stealth (un carácter por paquete)
3. **Actividad 3**: ✅ Ataque MitM con decodificación César por fuerza bruta

La implementación demuestra que mientras los sistemas DPI pueden detectar intentos obvios de exfiltración de datos, el tráfico cuidadosamente elaborado que imita protocolos legítimos puede potencialmente evadir mecanismos de detección.

## Consideraciones Éticas

Este código se proporciona únicamente con fines educativos. Las técnicas demostradas solo deben utilizarse en pruebas de penetración autorizadas o entornos educativos. El uso no autorizado de estas técnicas para exfiltración de datos es ilegal y poco ético.

## Mejoras Futuras

1. **Cifrado Avanzado**: Implementar algoritmos de cifrado más fuertes
2. **Múltiples Protocolos**: Extender a otros protocolos (DNS, HTTP, etc.)
3. **Corrección de Errores**: Agregar checksums y redundancia para transmisión confiable
4. **Temporización Adaptativa**: Variar intervalos de transmisión para evitar detección de patrones
5. **Esteganografía**: Ocultar datos en encabezados de paquetes en lugar del payload