# Tokenizador y Resaltador de Código  

## Autoras  
- Zuleyca Guadalupe Balles Soto A01741687  
- Mariana Islas Mondragón A01253435  
- Maria Regina Orduño López A01252959  
- Mariana Carrillo Holguin A01253358  

## Fecha  
13-04-2025  

## Descripción  
Este script tokeniza bloques de código escritos en **C++**, **Racket** y **R** presentes en un mismo archivo. Genera un archivo HTML con resaltado sintáctico, preservando espacios y saltos de línea.  

### Características principales  
- Detecta automáticamente el lenguaje de cada bloque de código basado en ciertas palabras clave.  
- Resalta sintácticamente los bloques de código utilizando estilos CSS.  
- Preserva el formato original del código, incluyendo espacios y saltos de línea.  

### Instrucciones importantes  
- Asegúrese de que los bloques de código empiecen con las expresiones clave para detectar el lenguaje:  
    - Para **C++**, el código debe incluir `#include`.  
    - Para **Racket**, el código debe incluir `#lang`.  
    - Para **R**, el código debe incluir `# R`.  
- Si no se incluyen estas expresiones, el lenguaje podría no ser detectado correctamente.  

## Funciones principales  
- `tokenize_block(block: str, language: str) -> List[Token]`: Tokeniza un bloque de código según el lenguaje especificado.  
- `detect_language(line: str, current: str) -> str`: Detecta el lenguaje de un bloque de código basado en su primera línea.  
- `highlight_all(code: str) -> str`: Procesa el código completo, detecta lenguajes, tokeniza y genera el HTML con resaltado sintáctico.  
- `main()`: Punto de entrada del script. Lee un archivo de entrada, genera el HTML resaltado y lo guarda.  

## Estilos CSS  
Incluye estilos predefinidos para cada tipo de token (comentarios, cadenas, números, palabras clave, etc.).  

## Uso  
Ejecute el script desde la línea de comandos con el nombre del archivo como argumento:  
```bash  
python lexer_highlighter.py <archivo>  
```  
El archivo HTML generado se guardará en la misma ubicación que el archivo de entrada, con la extensión `.html`.  

## Complejidad del algoritmo  
- La función `highlight_all` procesa bloques de código separados por doble salto de línea.  
- Divide el código en bloques: **O(n)**, donde `n` es el tamaño del código.  
- Itera sobre cada bloque y tokeniza: **O(m * k)**, donde `m` es el número de bloques y `k` es el tamaño promedio de cada bloque.  
- La tokenización en `tokenize_block` itera sobre cada carácter del bloque: **O(k)**.  
- En total, la complejidad es aproximadamente **O(n + m * k)**, que se simplifica a **O(n)** si asumimos que `m * k ≈ n`.  
