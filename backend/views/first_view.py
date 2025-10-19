"""Vista de los conjuntos FIRST de la gramática."""

def write_first_sets(writer, grammar):
    """Escribe los conjuntos FIRST de la gramática."""
    writer.write_line('/------------------FIRST----------------------')
    # Preservar el orden de aparición de no terminales basado en producciones
    seen_nt = []
    for prod in grammar.productions:
        if prod.left not in seen_nt:
            seen_nt.append(prod.left)
    
    for nt in seen_nt:
        # Convertir la lista ordenada a set para mostrar
        first_set = set(grammar.first.get(nt, []))
        # Ordenar los elementos según el orden de aparición en la gramática
        sorted_first = sorted(first_set, key=lambda x: (
            grammar.terminals.index(x) if x in grammar.terminals else float('inf')
        ))
        writer.write_line(f"{nt}: {{{', '.join(repr(x) for x in sorted_first)}}}")