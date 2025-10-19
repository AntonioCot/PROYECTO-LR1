"""Ejecutor principal del analizador LR(1)."""
import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import Grammar, LR1Parser
from utils.io_helpers import read_grammar_from_file, read_tokens_from_file, OutputWriter
from views.first_view import write_first_sets
from views.lr_closure_view import write_lr_closure
from views.lr_table_view import write_lr_table
from views.derivation_view import write_derivation_table


def collect_transitions(parser):
    """Recolecta todas las transiciones del parser."""
    transitions_from = {}
    
    # Recolectar shifts desde action_table
    for (st, sym), act in parser.action_table.items():
        if isinstance(act, tuple) and act[0] == 'shift':
            transitions_from.setdefault(st, []).append((sym, act[1]))
    
    # Recolectar gotos desde goto_table
    for (st, sym), to_st in parser.goto_table.items():
        transitions_from.setdefault(st, []).append((sym, to_st))
    
    return transitions_from


def main():
    # Configuración de argumentos de línea de comandos
    parser_args = argparse.ArgumentParser(description='Analizador LR(1)')
    parser_args.add_argument('--output', '-o', 
                           default='grammar_out1.txt',
                           help='Archivo de salida (relativo a backend/). Default: grammar_out1.txt')
    parser_args.add_argument('--tokens', '-t', 
                           default=None,
                           help='Cadena de tokens a parsear (espacio-separada). Si no se pasa, se leerá backend/input1.txt')
    args = parser_args.parse_args()

    # Configuración de rutas
    base = os.path.dirname(os.path.abspath(__file__))
    grammar_file = os.path.join(base, 'grammar1.txt')
    out_path = os.path.join(base, args.output)
    
    # Leer gramática y calcular FIRST
    grammar = read_grammar_from_file(grammar_file)
    grammar.calculate_first()
    
    # Crear el parser LR(1)
    parser = LR1Parser(grammar)
    
    # Recolectar transiciones para la vista de clausura
    transitions = collect_transitions(parser)
    
    # Configurar writer para salida
    writer = OutputWriter()
    
    # Escribir FIRST sets
    write_first_sets(writer, grammar)
    
    # Escribir clausura LR(1)
    state_mapping = write_lr_closure(writer, parser, transitions)
    
    # Escribir tabla LR(1)
    write_lr_table(writer, parser, state_mapping)
    
    # Determinar tokens de entrada
    if args.tokens is not None:
        tokens = args.tokens.split()
    else:
        tokens_file = os.path.join(base, 'input1.txt')
        tokens = read_tokens_from_file(tokens_file)
    
    # Ejecutar el parsing y escribir la tabla de derivación
    steps = parser.parse(tokens)
    write_derivation_table(writer, parser, tokens, state_mapping)
    
    # Guardar la salida en archivo
    writer.save_to_file(out_path)


if __name__ == '__main__':
    main()
