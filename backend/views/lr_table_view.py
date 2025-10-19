"""Vista de la tabla LR(1)."""

def write_lr_table(writer, parser, state_mapping):
    """Escribe la tabla LR(1)."""
    writer.write_line('\n/------------------TABLA LR(1)-------------------')

    # Obtener columnas de acción y goto
    action_cols, goto_cols = get_table_columns(parser)
    
    # Construir filas de la tabla
    action_rows, goto_rows = build_table_rows(parser, state_mapping, action_cols, goto_cols)
    
    # Imprimir la tabla
    print_lr_table(writer, action_cols, goto_cols, action_rows, goto_rows, len(parser.states))

def get_table_columns(parser):
    """Obtiene las columnas para las secciones ACTION y GOTO de la tabla."""
    grammar = parser.grammar
    
    # Columnas ACTION: solo terminales que aparecen en action_table
    action_cols = [t for t in grammar.terminals
                  if any((st, t) in parser.action_table 
                        for st in range(len(parser.states)))]
    if any(sym == '$' for (_, sym) in parser.action_table.keys()) and '$' not in action_cols:
        action_cols.append('$')

    # Columnas GOTO: incluir todos los no terminales, incluyendo S'
    # Primero S', luego el resto de no terminales que aparecen en goto_table
    goto_present = {sym for (_, sym) in parser.goto_table.keys()}
    goto_cols = ["S'"] + [A for A in grammar.non_terminals if A in goto_present and A != "S'"]
    
    return action_cols, goto_cols

def build_table_rows(parser, state_mapping, action_cols, goto_cols):
    """Construye las filas de la tabla LR(1)."""
    inv_map = {shown: real for real, shown in state_mapping.items()}
    action_rows, goto_rows = [], []
    
    for s_shown in range(len(parser.states)):
        s_real = inv_map.get(s_shown, s_shown)
        
        # Fila ACTION
        a_row = [fmt_action(parser.action_table.get((s_real, t)), state_mapping) 
                for t in action_cols]
        action_rows.append(a_row)
        
        # Fila GOTO
        g_row = []
        for A in goto_cols:
            dest = parser.goto_table.get((s_real, A))
            g_row.append('' if dest is None else str(state_mapping.get(dest, dest)))
        goto_rows.append(g_row)
        
    return action_rows, goto_rows

def fmt_action(action, state_mapping):
    """Formatea una acción de la tabla LR(1)."""
    if not action:
        return ''
    kind, val = action
    if kind == 'shift':
        return f's{state_mapping.get(val, val)}'
    if kind == 'reduce':
        return f'r{val}'
    if kind == 'accept':
        return 'acc'
    return str(action)

def print_lr_table(writer, action_cols, goto_cols, action_rows, goto_rows, num_states):
    """Imprime la tabla LR(1) con formato ASCII."""
    # Cálculo de anchos
    state_w = max(5, len(str(num_states - 1)))
    act_ws = [max(len(h), max((len(r[j]) for r in action_rows), default=0))
              for j, h in enumerate(action_cols)]
    goto_ws = [max(len(h), max((len(r[j]) for r in goto_rows), default=0))
               for j, h in enumerate(goto_cols)]
    
    act_group_w = sum(act_ws) + max(0, len(act_ws) - 1) * 3
    goto_group_w = sum(goto_ws) + max(0, len(goto_ws) - 1) * 3
    
    # Imprimir encabezados
    write_table_headers(writer, state_w, act_group_w, goto_group_w, 
                       action_cols, goto_cols, act_ws, goto_ws)
    
    # Imprimir filas
    for s_shown in range(num_states):
        write_table_row(writer, s_shown, state_w, action_rows[s_shown], goto_rows[s_shown],
                       act_ws, goto_ws)
    
    write_table_footer(writer, state_w, act_ws, goto_ws)

def write_table_headers(writer, state_w, act_group_w, goto_group_w, 
                       action_cols, goto_cols, act_ws, goto_ws):
    """Escribe los encabezados de la tabla LR(1)."""
    writer.write_line(make_top_border(state_w, act_group_w, goto_group_w))
    writer.write_line(make_group_header_row(state_w, act_group_w, goto_group_w))
    writer.write_line(make_column_border(state_w, act_ws, goto_ws))
    writer.write_line(make_column_header_row(state_w, action_cols, goto_cols, act_ws, goto_ws))
    writer.write_line(make_column_border(state_w, act_ws, goto_ws))

def write_table_row(writer, state_num, state_w, action_row, goto_row, act_ws, goto_ws):
    """Escribe una fila de la tabla LR(1)."""
    row = '|' + ' ' + center(str(state_num), state_w) + ' ' + '|'
    for val, w in zip(action_row, act_ws):
        row += ' ' + pad(val, w) + ' ' + '|'
    for val, w in zip(goto_row, goto_ws):
        row += ' ' + pad(val, w) + ' ' + '|'
    writer.write_line(row)

def write_table_footer(writer, state_w, act_ws, goto_ws):
    """Escribe el pie de la tabla LR(1)."""
    writer.write_line(make_column_border(state_w, act_ws, goto_ws))

def make_top_border(state_w, act_group_w, goto_group_w):
    """Crea el borde superior de la tabla."""
    return '+' + '-' * (state_w + 2) + '+' + '-' * (act_group_w + 2) + '+' + '-' * (goto_group_w + 2) + '+'

def make_group_header_row(state_w, act_group_w, goto_group_w):
    """Crea la fila de encabezados de grupo."""
    return ('|' + ' ' + center('State', state_w) + ' ' +
            '|' + ' ' + center('ACTION', act_group_w) + ' ' +
            '|' + ' ' + center('GOTO', goto_group_w) + ' ' + '|')

def make_column_border(state_w, act_ws, goto_ws):
    """Crea un borde entre columnas."""
    parts = ['+' + '-' * (state_w + 2)]
    for w in act_ws:
        parts.append('+' + '-' * (w + 2))
    for w in goto_ws:
        parts.append('+' + '-' * (w + 2))
    return ''.join(parts) + '+'

def make_column_header_row(state_w, action_cols, goto_cols, act_ws, goto_ws):
    """Crea la fila de encabezados de columnas."""
    row = '|' + ' ' + center('State', state_w) + ' ' + '|'
    for h, w in zip(action_cols, act_ws):
        row += ' ' + center(h, w) + ' ' + '|'
    for h, w in zip(goto_cols, goto_ws):
        row += ' ' + center(h, w) + ' ' + '|'
    return row

def center(s, w):
    """Centra un texto en un ancho dado."""
    s = str(s)
    if len(s) >= w:
        return s
    l = (w - len(s)) // 2
    return ' ' * l + s + ' ' * (w - len(s) - l)

def pad(s, w):
    """Rellena un texto a un ancho dado, alineado a la izquierda."""
    s = str(s)
    return s + ' ' * (w - len(s))