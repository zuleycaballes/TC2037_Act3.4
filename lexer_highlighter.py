#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importamos las bibliotecas necesarias
import re, sys
from pathlib import Path
from typing import List, Tuple

# Definimos un tipo de dato para los tokens
Token = Tuple[str, str]

# Patrones regex para identificar diferentes tipos de tokens
TOKEN_SPECS: List[Tuple[str, str]] = [
    ('COMMENT_C_BLOCK', r'/\*[\s\S]*?\*/'),  # Comentarios en bloque estilo C
    ('COMMENT_C_LINE',  r'//[^\n]*'),        # Comentarios de línea estilo C
    ('STRING',          r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''),  # Literales de cadena
    ('NUMBER',          r'\b[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?\b'),  # Números
    ('BOOLEAN',         r'\b(?:true|false|TRUE|FALSE|#t|#f)\b'),  # Booleanos
    ('KEYWORD',         r'\b(?:define|lambda|if|cond|case|let|let\*|namespace|letrec|begin|quote|display|displayln|quasiquote|unquote|unquote-splicing|define-syntax|syntax-rules|match|module|provide|require|set!|delay|force|and|or|unless|when)\b'),  # Palabras clave
    ('OP_COMPOUND',     r'==|!=|<=|>=|\+\+|--|&&|\|\|'),  # Operadores compuestos
    ('OP_SIMPLE',       r'[+\-*/%^=<>!&|]'),  # Operadores simples
    ('IDENT',           r'\b[A-Za-z_][A-Za-z0-9_]*\b'),  # Identificadores
    ('SEMICOLON',       r';'),  # Punto y coma
    ('DELIM',           r'[()\[\]{}\.,]'),  # Delimitadores
    ('NEWLINE',         r'\n'),  # Saltos de línea
    ('WS',              r'[ \t]+'),  # Espacios en blanco
    ('MISMATCH',        r'.'),  # Cualquier otro carácter no reconocido
]

# Compilamos todos los patrones en una sola expresión regular
master_re = re.compile('|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPECS), re.MULTILINE)

# Función para tokenizar un bloque de código
def tokenize_block(block: str, language: str) -> List[Token]:
    tokens, i, n = [], 0, len(block)
    while i < n:
        # En Racket, tratamos ';' como comentario
        if language == 'Racket' and block[i] == ';':
            j = block.find('\n', i)
            if j < 0: j = n
            tokens.append((block[i:j], 'COMMENT_RKT'))
            i = j
            continue
        
        # En R, tratamos '#' como comentario
        if language == 'R' and block[i] == '#':
            j = block.find('\n', i)
            if j < 0: j = n
            tokens.append((block[i:j], 'COMMENT_R'))
            i = j
            continue
        
        # Intentamos hacer coincidir el bloque con los patrones regex
        m = master_re.match(block, i)
        if not m:
            tokens.append((block[i], 'INVALID'))  # Si no coincide, lo marcamos como inválido
            i += 1
            continue

        # Obtenemos el tipo de token y su valor
        kind, lex = m.lastgroup, m.group()
        i = m.end()

        # Procesamos los tokens según su tipo
        if kind == 'WS':
            tokens.append((lex, 'WS'))
        elif kind == 'MISMATCH':
            tokens.append((lex, 'INVALID'))
        else:
            if kind in ('OP_COMPOUND', 'OP_SIMPLE'):
                kind = 'OPERATOR'  # Unificamos operadores en un solo tipo
            elif kind == 'SEMICOLON':
                kind = 'DELIM'  # Tratamos ';' como delimitador
            tokens.append((lex, kind))
    return tokens

# Función para detectar el lenguaje del código
def detect_language(line: str, current: str) -> str:
    fl = line.strip()
    if fl.startswith('#lang') or fl.startswith(';'):
        return 'Racket'  # Si empieza con '#lang' o ';', es Racket
    if fl.startswith('# R') and not fl.startswith('#lang'):
        return 'R'  # Si empieza con '# R', es R
    if '#include' in fl or 'cout' in fl or 'int ' in fl:
        return 'C++'  # Si contiene elementos de C++, lo identificamos como tal
    return current  # Si no coincide con nada, devolvemos el lenguaje actual

# Estilo CSS para el resaltado de sintaxis
CSS = """<style>
body{background:#1e1e1e;color:#d4d4d4;font-family:monospace;}
pre{white-space:pre-wrap;}
.COMMENT_C_BLOCK,.COMMENT_C_LINE{color:#6a9955;}
.COMMENT_R{color:#6a9955;}
.COMMENT_RKT{color:#6a9955;}
.STRING{color:#ce9178;}
.NUMBER{color:#b5cea8;}
.BOOLEAN{color:#569cd6;}
.KEYWORD{color:#c586c0;}
.OPERATOR{color:#d4d4d4;}
.IDENT{color:#9cdcfe;}
.DELIM{color:#d4d4d4;}
.INVALID{color:#9cdcfe;}
.WS{/* preserva espacios */}</style>"""

# Plantilla HTML para el resaltado de sintaxis
HTML_TMPL = "<!DOCTYPE html><html><head><meta charset=utf-8><title>Resaltado</title>{css}</head><body>{body}</body></html>"

# Función para resaltar todo el código
def highlight_all(code: str) -> str:
    blocks = [b for b in code.split('\n\n') if b.strip()]  # Dividimos el código en bloques
    parts = []
    current_lang = 'Desconocido'  # Lenguaje inicial desconocido
    for blk in blocks:
        first = next((l for l in blk.splitlines() if l.strip()), '')  # Primera línea no vacía
        current_lang = detect_language(first, current_lang)  # Detectamos el lenguaje
        toks = tokenize_block(blk, current_lang)  # Tokenizamos el bloque
        out = []
        for tok, kind in toks:
            esc = tok.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')  # Escapamos caracteres HTML
            if kind == 'WS':
                out.append(esc.replace(' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;'))  # Preservamos espacios
            elif kind == 'NEWLINE':
                out.append('\n')  # Mantenemos los saltos de línea
            else:
                out.append(f'<span class="{kind}">{esc}</span>')  # Envolvemos el token en un span con clase
        parts.append(f'<pre>{"" .join(out)}</pre>')  # Agregamos el bloque procesado
    return HTML_TMPL.format(css=CSS, body='\n'.join(parts))  # Generamos el HTML final

# Función principal
def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <archivo>")  # Mostramos el uso correcto si no hay argumentos
        sys.exit(1)
    code = Path(sys.argv[1]).read_text(encoding='utf-8')  # Leemos el archivo de entrada
    out = Path(sys.argv[1]).with_suffix('.html')  # Generamos el nombre del archivo de salida
    out.write_text(highlight_all(code), encoding='utf-8')  # Escribimos el HTML generado
    print('Generado:', out)  # Informamos al usuario

# Punto de entrada del script
if __name__ == '__main__':
    main()
