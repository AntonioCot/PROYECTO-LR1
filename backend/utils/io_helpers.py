"""Utilidades de entrada/salida para el analizador LR(1)."""
import os

def read_grammar_from_file(filename):
    """Lee una gramática desde un archivo."""
    from analyzer import Grammar
    g = Grammar()
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '->' not in line:
                continue
            left, right = line.split('->', 1)
            left = left.strip()
            # split tokens, but treat explicit epsilon markers ('' or ε) as empty RHS
            parts = [tok.strip() for tok in right.strip().split()]
            if len(parts) == 0 or (len(parts) == 1 and parts[0] in ("''", "ε", "")):
                rhs = []
            else:
                rhs = parts
            g.add_production(left, rhs)
    return g

def read_tokens_from_file(tokens_file):
    """Lee tokens desde un archivo."""
    try:
        with open(tokens_file, 'r') as tf:
            data = tf.read().strip()
            for line in data.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                return line.split()
    except Exception:
        return []
    return []

class OutputWriter:
    """Clase para manejar la escritura de salida tanto a consola como a archivo."""
    def __init__(self):
        self.lines = []
    
    def write_line(self, s=''):
        """Escribe una línea tanto a la lista como a la consola."""
        self.lines.append(s)
        print(s)
    
    def save_to_file(self, filepath):
        """Guarda todas las líneas en un archivo."""
        try:
            with open(filepath, 'w') as f:
                f.write('\n'.join(self.lines) + '\n')
            print(f"\nSalida guardada en: {filepath}")
        except Exception as e:
            print('Error escribiendo archivo de salida:', e)