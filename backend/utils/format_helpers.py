"""Utilidades de formato para las vistas del analizador LR(1)."""

def pad_center(text, width):
    """Centra el texto en un ancho específico."""
    text = str(text)
    padding = width - len(text)
    left = padding // 2
    right = padding - left
    return ' ' * left + text + ' ' * right

def format_items(items, grammar_productions, always_show_start=False):
    """Formatea un conjunto de items LR(1)."""
    if not items:
        return ''

    # Crear un mapa de producciones según aparecen en la gramática
    prod_order = {}
    for idx, prod in enumerate(grammar_productions):
        prod_key = (prod.left, tuple(prod.right))
        prod_order[prod_key] = idx

    def get_item_sort_key(item):
        """Determina el orden de los items en la clausura."""
        prod_key = (item.production.left, tuple(item.production.right))
        prod_idx = prod_order.get(prod_key, float('inf'))

        left_part = item.production.right[:item.dot_position]
        right_part = item.production.right[item.dot_position:]

        # Obtener el siguiente símbolo después del punto
        next_symbol = right_part[0] if right_part else None
        
        # Verificar si este item comienza con el símbolo al que apunta otro item
        # Por ejemplo, si V -> id , . V, $ apunta a V, entonces V -> . id , V debe seguirlo
        is_pointed_to = False
        for other_item in items:
            other_right = other_item.production.right[other_item.dot_position:]
            if (other_right and 
                other_item != item and 
                other_right[0] == item.production.left):
                is_pointed_to = True
                break

        # Dar prioridad a items con el punto antes de un no terminal
        # que aparece como lado izquierdo de alguna producción
        points_to_nonterm = next_symbol in {p.left for p in grammar_productions}

        return (
            0 if item.production.left == "S'" else 1,    # S' primero
            0 if points_to_nonterm else 1,               # Items que apuntan a no terminales
            0 if is_pointed_to else 1,                   # Items que son apuntados por otros
            prod_idx,                                    # Orden en la gramática
            -item.dot_position,                          # Posición del punto
            str(item.lookahead)                          # Ordenar por lookahead
        )

    # Ordenar los items usando la función de ordenamiento personalizada
    sorted_items = sorted(items, key=get_item_sort_key)
    # Unir los items con punto y coma y envolver en llaves y corchetes
    return '{[' + '; '.join(str(it) for it in sorted_items) + ']}'

def get_transition_sort_key(t, grammar):
    """Obtiene la clave de ordenamiento para las transiciones."""
    from_state, sym, to = t
    sym_str = str(sym)
    is_non_terminal = sym_str in grammar.non_terminals
    
    # Primero por estado de origen
    # Luego por no terminales antes que terminales
    # Luego por orden de aparición en la gramática
    # Finalmente por estado destino (para mantener orden consistente)
    try:
        if is_non_terminal:
            sym_order = grammar.non_terminals.index(sym_str)
            type_order = 0
        else:
            sym_order = grammar.terminals.index(sym_str)
            type_order = 1
    except ValueError:
        sym_order = float('inf')
        type_order = 2
        
    return (from_state, type_order, sym_order, to)
