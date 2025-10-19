"""Vista de la tabla de derivación LR(1)."""

def write_derivation_table(writer, parser, tokens, state_mapping):
    """Escribe la tabla de derivación LR(1)."""
    writer.write_line('\n/------------------TABLA LR(1) de derivacion--------------')
    
    # Obtener filas de la simulación
    rows = simulate_parsing(parser, tokens, state_mapping)
    
    # Imprimir la tabla
    print_derivation_table(writer, rows)

def simulate_parsing(parser, tokens, state_mapping):
    """Simula el proceso de parsing y genera las filas de la tabla."""
    stack_states = [0]  # Pila "lógica" de estados
    stack_disp = [0]    # Pila "display" alternada (estado, símbolo, estado, ...)
    rem_input = list(tokens) + ['$']
    
    rows = []  # (step, stack_txt, input_txt, action_txt)
    
    while True:
        s_real = stack_states[-1]
        a = rem_input[0]
        
        # Acción LR(1)
        action, val = parser.action_table.get((s_real, a), (None, None))
        if action is None:
            # Error: no hay acción disponible
            add_row(rows, len(rows)+1, stack_disp, rem_input, '')
            raise SyntaxError(f"Token inesperado {a} en el estado {s_real}")
        
        if action == 'shift':
            handle_shift(rows, stack_states, stack_disp, rem_input, val, state_mapping)
        elif action == 'reduce':
            handle_reduce(rows, parser, stack_states, stack_disp, rem_input, val, state_mapping)
        elif action == 'accept':
            add_row(rows, len(rows)+1, stack_disp, rem_input, 'acc')
            break
        else:
            add_row(rows, len(rows)+1, stack_disp, rem_input, str(action))
            break
    return rows

def handle_shift(rows, stack_states, stack_disp, rem_input, val, state_mapping):
    """Maneja una acción de shift."""
    # Mostrar la acción shift
    mapped_state = state_mapping.get(val, val)
    add_row(rows, len(rows)+1, stack_disp, rem_input, f's{mapped_state}')
    
    # Actualizar pilas y entrada
    stack_disp.append(rem_input[0])   # terminal
    stack_states.append(val)          # estado real
    stack_disp.append(mapped_state)   # estado en display (usando el estado mapeado)
    rem_input.pop(0)

def handle_reduce(rows, parser, stack_states, stack_disp, rem_input, val, state_mapping):
    """Maneja una acción de reduce."""
    add_row(rows, len(rows)+1, stack_disp, rem_input, f'r{val}')
    prod = parser.grammar.productions[val]
    beta_len = len(prod.right)
    
    # Hacer pop de los símbolos y estados según la longitud de la parte derecha
    for _ in range(beta_len):
        if stack_disp and isinstance(stack_disp[-1], int):
            stack_disp.pop()
        if stack_disp and not isinstance(stack_disp[-1], int):
            stack_disp.pop()
        if stack_states:
            stack_states.pop()
    
    # Empujar el no terminal (LHS)
    stack_disp.append(prod.left)
    
    # Calcular y mostrar GOTO
    t_real = stack_states[-1]
    goto_state = parser.goto_table.get((t_real, prod.left))
    if goto_state is None:
        raise SyntaxError(f"No hay goto para {(t_real, prod.left)}")
    
    mapped_goto = state_mapping.get(goto_state, goto_state)
    add_row(rows, len(rows)+1, stack_disp, rem_input, str(mapped_goto))
    
    # Empujar el estado destino
    stack_states.append(goto_state)
    stack_disp.append(mapped_goto)

def add_row(rows, step, stack_disp, rem_input, action_txt):
    """Agrega una fila a la tabla de derivación."""
    rows.append((
        str(step),
        fmt_stack_display(stack_disp),
        fmt_input_display(rem_input),
        action_txt
    ))

def fmt_stack_display(stack_disp):
    """Formatea la pila para mostrar."""
    return ' '.join(str(x) for x in stack_disp) if stack_disp else 'ε'

def fmt_input_display(rem_input):
    """Formatea la entrada restante para mostrar."""
    return ' '.join(rem_input) if rem_input else ''

def print_derivation_table(writer, rows):
    """Imprime la tabla de derivación con formato ASCII."""
    headers = ('Step', 'Stack', 'Input', 'Action')
    
    # Cálculo de anchos de columna
    w_step = max(4, len(headers[0]), max(len(r[0]) for r in rows))
    w_stack = max(10, len(headers[1]), max(len(r[1]) for r in rows))
    w_input = max(10, len(headers[2]), max(len(r[2]) for r in rows))
    w_act = max(6, len(headers[3]), max(len(r[3]) for r in rows))
    
    # Imprimir tabla
    writer.write_line(make_hline(w_step, w_stack, w_input, w_act))
    writer.write_line(make_row(headers, w_step, w_stack, w_input, w_act))
    writer.write_line(make_hline(w_step, w_stack, w_input, w_act))
    
    for row in rows:
        writer.write_line(make_row(row, w_step, w_stack, w_input, w_act))
    
    writer.write_line(make_hline(w_step, w_stack, w_input, w_act))

def make_hline(w_step, w_stack, w_input, w_act):
    """Crea una línea horizontal de la tabla."""
    return '+' + '-'*(w_step+2) + '+' + '-'*(w_stack+2) + '+' + \
           '-'*(w_input+2) + '+' + '-'*(w_act+2) + '+'

def make_row(cells, w_step, w_stack, w_input, w_act):
    """Crea una fila de la tabla."""
    return '| ' + cells[0].ljust(w_step) + ' | ' + \
           cells[1].ljust(w_stack) + ' | ' + \
           cells[2].ljust(w_input) + ' | ' + \
           cells[3].ljust(w_act) + ' |'
