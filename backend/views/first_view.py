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
        # Tomar directamente la lista ordenada del FIRST
        first_list = grammar.first.get(nt, [])
        writer.write_line(f"{nt}: {{{', '.join(repr(x) for x in first_list)}}}")
