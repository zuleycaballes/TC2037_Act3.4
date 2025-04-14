#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys
from pathlib import Path
from typing import List, Tuple

Token = Tuple[str, str]

# Patrones regex (sin COMMENT_RKT)
TOKEN_SPECS: List[Tuple[str, str]] = [
        ('COMMENT_C_BLOCK', r'/\*[\s\S]*?\*/'),
        ('COMMENT_C_LINE',  r'//[^\n]*'),
        ('STRING',          r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''), 
        ('NUMBER',          r'\b[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?\b'),
        ('BOOLEAN',         r'\b(?:true|false|TRUE|FALSE|#t|#f)\b'),
        ('KEYWORD',         r'\b(?:define|lambda|if|cond|case|let|let\*|namespace|letrec|begin|quote|display|displayln|quasiquote|unquote|unquote-splicing|define-syntax|syntax-rules|match|module|provide|require|set!|delay|force|and|or|unless|when)\b'),
        ('OP_COMPOUND',     r'==|!=|<=|>=|\+\+|--|&&|\|\|'),
        ('OP_SIMPLE',       r'[+\-*/%^=<>!&|]'),
        ('IDENT',           r'\b[A-Za-z_][A-Za-z0-9_]*\b'),
        ('SEMICOLON',       r';'),
        ('DELIM',           r'[()\[\]{}\.,]'),
        ('NEWLINE',         r'\n'),
        ('WS',              r'[ \t]+'),
        ('MISMATCH',        r'.'),
]
master_re = re.compile('|'.join(f'(?P<{n}>{p})' for n,p in TOKEN_SPECS), re.MULTILINE)

def tokenize_block(block: str, language: str) -> List[Token]:
        tokens, i, n = [], 0, len(block)
        while i < n:
                # Solo en Racket tratamos ';' como comentario
                if language == 'Racket' and block[i] == ';':
                        j = block.find('\n', i)
                        if j < 0: j = n
                        tokens.append((block[i:j], 'COMMENT_RKT'))
                        i = j
                        continue
                
                # Solo en R tratamos '#' como comentario
                if language == 'R' and block[i] == '#':
                        j = block.find('\n', i)
                        if j < 0: j = n
                        tokens.append((block[i:j], 'COMMENT_R'))
                        i = j
                        continue
                
                m = master_re.match(block, i)
                if not m:
                        tokens.append((block[i], 'INVALID'))
                        i += 1
                        continue

                kind, lex = m.lastgroup, m.group()
                i = m.end()

                if kind == 'WS':
                        tokens.append((lex, 'WS'))
                elif kind == 'MISMATCH':
                        tokens.append((lex, 'INVALID'))
                else:
                        if kind in ('OP_COMPOUND','OP_SIMPLE'):
                                kind = 'OPERATOR'
                        elif kind == 'SEMICOLON':
                                kind = 'DELIM'
                        tokens.append((lex, kind))
        return tokens

def detect_language(line: str, current: str) -> str:
        fl = line.strip()
        if fl.startswith('#lang') or fl.startswith(';'):
                return 'Racket'
        if fl.startswith('# R') and not fl.startswith('#lang'):
                return 'R'
        if '#include' in fl or 'cout' in fl or 'int ' in fl:
                return 'C++'
        return current

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

HTML_TMPL = "<!DOCTYPE html><html><head><meta charset=utf-8><title>Resaltado</title>{css}</head><body>{body}</body></html>"

def highlight_all(code: str) -> str:
        blocks = [b for b in code.split('\n\n') if b.strip()]
        parts = []
        current_lang = 'Desconocido'
        for blk in blocks:
                first = next((l for l in blk.splitlines() if l.strip()), '')
                current_lang = detect_language(first, current_lang)
                toks = tokenize_block(blk, current_lang)
                out = []
                for tok, kind in toks:
                        esc = tok.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                        if kind == 'WS':
                                out.append(esc.replace(' ', '&nbsp;').replace('\t','&nbsp;&nbsp;&nbsp;&nbsp;'))
                        elif kind == 'NEWLINE':
                                out.append('\n')
                        else:
                                out.append(f'<span class="{kind}">{esc}</span>')
                parts.append(f'<pre>{"" .join(out)}</pre>')
        return HTML_TMPL.format(css=CSS, body='\n'.join(parts))

def main():
        if len(sys.argv)!=2:
                print(f"Uso: {sys.argv[0]} <archivo>"); sys.exit(1)
        code = Path(sys.argv[1]).read_text(encoding='utf-8')
        out = Path(sys.argv[1]).with_suffix('.html')
        out.write_text(highlight_all(code), encoding='utf-8')
        print('Generado:', out)

if __name__=='__main__':
        main()
