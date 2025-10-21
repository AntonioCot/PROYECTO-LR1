"""Vista de la clausura LR(1)."""
from utils.format_helpers import pad_center, format_items, get_transition_sort_key

def write_lr_closure(writer, parser, transitions_from):
    """Escribe la tabla de clausura LR(1)."""
    # Recolectar filas (sin imprimir) para calcular anchos dinámicos
    rows = []  # cada fila: (goto_label, kernel_str, state_str, closure_str)

    writer.write_line('\nLR(1) closure table')

    # Crear mapeo de estados
    state_mapping = create_state_mapping(parser, transitions_from)

    # fila inicial
    kitems = format_kernel_items(parser, 0)
    citems = format_items(parser.states[0].items, parser.grammar.productions, True)
    rows.append(('','' , '0', ''))
    # We'll build a proper initial row explicitly later; store strings ready
    initial_row = ('', kitems, '0', citems)

    # Recolectar y ordenar transiciones
    state_transitions = []
    for from_state in range(len(parser.states)):
        trans = transitions_from.get(from_state, [])
        for sym, to in trans:
            state_transitions.append((from_state, sym, to))

    sorted_transitions = sorted(state_transitions, key=lambda t: get_transition_sort_key(t, parser.grammar))

    seen_transitions = set()
    seen_states = {0}

    transition_rows = []
    for from_state, sym, to in sorted_transitions:
        transition_key = (from_state, str(sym), to)
        if transition_key in seen_transitions:
            continue
        seen_transitions.add(transition_key)
        show_closure = not to in seen_states
        seen_states.add(to)

        goto_label = f"goto({state_mapping[from_state]}, {sym})"
        kernel_str = format_kernel_items(parser, to)
        closure_str = format_items(parser.states[to].items, parser.grammar.productions, True) if show_closure else ''
        state_str = str(state_mapping[to])
        transition_rows.append((goto_label, kernel_str, state_str, closure_str))

    # Usar anchos fijos que coincidan con la imagen objetivo
    col_goto = 18
    col_kernel = 43
    col_state = 7
    col_closure = 107

    # Table headers
    write_table_headers(writer, col_goto, col_kernel, col_state, col_closure)

    # imprimir fila inicial usando los strings ya preparados
    writer.write_line('|' + ' '.ljust(col_goto) + '|' + initial_row[1].ljust(col_kernel) + '|' + pad_center(initial_row[2], col_state) + '|' + initial_row[3].ljust(col_closure) + '|')

    # imprimir transiciones
    for goto_label, kernel_str, state_str, closure_str in transition_rows:
        writer.write_line('|' + goto_label.ljust(col_goto) + '|' + kernel_str.ljust(col_kernel) + '|' + pad_center(state_str, col_state) + '|' + closure_str.ljust(col_closure) + '|')

    # Table bottom border
    writer.write_line('+-' + '-' * col_goto + '+' + '-' * col_kernel + '+' + '-' * col_state + '+' + '-' * col_closure + '+')

    writer.write_line('')
    return state_mapping

def create_state_mapping(parser, transitions_from):
    """Crea un mapeo de estados para mantener consistencia en la numeración."""
    state_mapping = {}
    kernel_to_state = {}
    next_state = 0

    # Registrar estado inicial
    start_kernel = format_kernel_items(parser, 0)
    state_mapping[0] = 0
    kernel_to_state[start_kernel] = 0
    next_state = 1

    # Recolectar y ordenar todas las transiciones
    state_transitions = []
    for from_state in range(len(parser.states)):
        trans = transitions_from.get(from_state, [])
        for sym, to in trans:
            state_transitions.append((from_state, sym, to))
    
    sorted_transitions = sorted(state_transitions, 
                              key=lambda t: get_transition_sort_key(t, parser.grammar))

    # Pre-procesar todos los estados para crear el mapeo
    for from_state, sym, to in sorted_transitions:
        kernel_str = format_kernel_items(parser, to)
        
        if kernel_str in kernel_to_state:
            state_mapping[to] = kernel_to_state[kernel_str]
        elif to not in state_mapping:
            state_mapping[to] = next_state
            kernel_to_state[kernel_str] = next_state
            next_state += 1

    return state_mapping

def format_kernel_items(parser, state_idx):
    """Formatea los ítems del kernel de un estado."""
    start_prod = parser.grammar.productions[0]
    items = parser.states[state_idx].items
    kernel_items = [it for it in items 
                   if it.dot_position > 0 or it.production == start_prod]
    # devolver con llaves y corchetes para coincidir con la vista esperada
    return format_items(kernel_items, parser.grammar.productions, always_show_start=True)

def write_table_headers(writer, col_goto, col_kernel, col_state, col_closure):
    """Escribe los encabezados de la tabla de clausura."""
    writer.write_line('+-' + '-' * col_goto + '+' + '-' * col_kernel + '+' + 
                     '-' * col_state + '+' + '-' * col_closure + '+')
    writer.write_line('| ' + pad_center('Goto', col_goto-2) + 
                     ' | ' + pad_center('Kernel', col_kernel-2) + 
                     ' | ' + pad_center('State', col_state-2) + 
                     ' | ' + pad_center('Closure', col_closure-2) + ' |')
    writer.write_line('+-' + '-' * col_goto + '+' + '-' * col_kernel + '+' + 
                     '-' * col_state + '+' + '-' * col_closure + '+')

def write_initial_state(writer, parser, col_goto, col_kernel, col_state, col_closure):
    """Escribe el estado inicial en la tabla de clausura."""
    kitems = format_kernel_items(parser, 0)
    citems = format_items(parser.states[0].items, parser.grammar.productions, True)
    writer.write_line('|' + ' '.ljust(col_goto) + 
                     '|' + kitems.ljust(col_kernel) + 
                     '|' + pad_center('0', col_state) + 
                     '|' + citems.ljust(col_closure) + '|')

def write_transitions(writer, parser, transitions_from, state_mapping, 
                     col_goto, col_kernel, col_state, col_closure):
    """Escribe las transiciones en la tabla de clausura."""
    # Recolectar y ordenar transiciones
    state_transitions = []
    for from_state in range(len(parser.states)):
        trans = transitions_from.get(from_state, [])
        for sym, to in trans:
            state_transitions.append((from_state, sym, to))
            
    sorted_transitions = sorted(state_transitions, 
                              key=lambda t: get_transition_sort_key(t, parser.grammar))
    
    seen_transitions = set()
    seen_states = {0}
    
    for from_state, sym, to in sorted_transitions:
        transition_key = (from_state, str(sym), to)
        if transition_key not in seen_transitions:
            write_transition(writer, parser, from_state, sym, to, state_mapping,
                           col_goto, col_kernel, col_state, col_closure,
                           not to in seen_states)
            seen_transitions.add(transition_key)
            seen_states.add(to)
    
    # Table bottom border
    writer.write_line('+-' + '-' * col_goto + '+' + '-' * col_kernel + '+' + 
                     '-' * col_state + '+' + '-' * col_closure + '+')
    writer.write_line('')

def write_transition(writer, parser, from_state, sym, to, state_mapping,
                    col_goto, col_kernel, col_state, col_closure, show_closure=True):
    """Escribe una transición individual en la tabla de clausura."""
    kernel_str = format_kernel_items(parser, to)
    state_num = state_mapping[to]
    from_state_num = state_mapping[from_state]
    
    goto_label = f"goto({from_state_num}, {sym})"
    closure_str = format_items(parser.states[to].items, parser.grammar.productions, True) if show_closure else ''
    
    writer.write_line('|' + goto_label.ljust(col_goto) + 
                     '|' + kernel_str.ljust(col_kernel) + 
                     '|' + pad_center(str(state_num), col_state) + 
                     '|' + closure_str.ljust(col_closure) + '|')