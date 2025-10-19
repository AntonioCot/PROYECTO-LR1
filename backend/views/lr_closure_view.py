"""Vista de la clausura LR(1)."""
from utils.format_helpers import pad_center, format_items, get_transition_sort_key

def write_lr_closure(writer, parser, transitions_from):
    """Escribe la tabla de clausura LR(1)."""
    # Columnas para ASCII art table
    col_goto = 17      # ancho para goto y bordes
    col_kernel = 43    # ancho para kernel y bordes
    col_state = 7      # ancho para state y bordes
    col_closure = 107  # ancho para closure y bordes

    writer.write_line('\n/------------------TABLA LR(1) clausura-------------')

    # Crear mapeo de estados
    state_mapping = create_state_mapping(parser, transitions_from)

    # Table headers
    write_table_headers(writer, col_goto, col_kernel, col_state, col_closure)
    
    # First, state 0's kernel and closure
    write_initial_state(writer, parser, col_goto, col_kernel, col_state, col_closure)

    # Procesar las transiciones ordenadas
    write_transitions(writer, parser, transitions_from, state_mapping, 
                     col_goto, col_kernel, col_state, col_closure)

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
    return format_items(kernel_items, parser.grammar.productions)

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
    writer.write_line('| ' + ' ' * (col_goto-2) + 
                     ' | ' + f"{kitems}".ljust(col_kernel-2) + 
                     ' | ' + pad_center('0', col_state-2) + 
                     ' | ' + f"{citems}".ljust(col_closure-2) + ' |')

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
    closure_str = format_items(parser.states[to].items, parser.grammar.productions) if show_closure else ''
    
    writer.write_line('| ' + goto_label.ljust(col_goto-2) + 
                     ' | ' + f"{kernel_str}".ljust(col_kernel-2) + 
                     ' | ' + pad_center(str(state_num), col_state-2) + 
                     ' | ' + f"{closure_str}".ljust(col_closure-2) + ' |')