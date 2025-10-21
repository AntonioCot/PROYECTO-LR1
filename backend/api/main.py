from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

import os
import sys

# Asegurar que el package backend esté en sys.path
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from analyzer import Grammar, LR1Parser


class ParseRequest(BaseModel):
    grammar: str
    tokens: Optional[List[str]] = None


app = FastAPI(title="LR1 Parser API", version="0.1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia a ["http://localhost:3000"] si quieres restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_grammar_from_string(text: str) -> Grammar:
    """Construye un objeto Grammar a partir de texto en el mismo formato que los archivos de gramática."""
    from utils.io_helpers import read_grammar_from_file
    g = Grammar()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '->' not in line:
            continue
        left, right = line.split('->', 1)
        left = left.strip()
        rhs = [tok.strip() for tok in right.strip().split()]
        g.add_production(left, rhs)
    g.calculate_first()
    return g


def serialize_first(grammar: Grammar) -> Dict[str, List[str]]:
    # grammar.first already contains terminals and non-terminals entries.
    non_terminals = {}
    terminals = {}
    for nt in grammar.non_terminals:
        non_terminals[nt] = list(grammar.first.get(nt, []))
    for t in grammar.terminals:
        terminals[t] = [t]
    return {"non_terminals": non_terminals, "terminals": terminals}


def build_parser_and_serialize(grammar: Grammar, tokens: Optional[List[str]]):
    parser = LR1Parser(grammar)

    # Build closures info by reusing run.collect_transitions logic inline
    transitions_from = {}
    for (st, sym), act in parser.action_table.items():
        if isinstance(act, tuple) and act[0] == 'shift':
            transitions_from.setdefault(st, []).append((sym, act[1]))
    for (st, sym), to in parser.goto_table.items():
        transitions_from.setdefault(st, []).append((sym, to))

    # Create a state mapping using the same algorithm as views.lr_closure_view.create_state_mapping
    # so numbering (shown states) matches the output of run.py
    from utils.format_helpers import format_items, get_transition_sort_key

    state_mapping = {}
    kernel_to_state = {}
    next_state = 0

    # register start state 0
    start_kernel = format_items(parser.states[0].items, grammar.productions)
    state_mapping[0] = 0
    kernel_to_state[start_kernel] = 0
    next_state = 1

    # collect and sort transitions
    state_transitions = []
    for from_state in range(len(parser.states)):
        for sym, to in transitions_from.get(from_state, []):
            state_transitions.append((from_state, sym, to))

    sorted_transitions = sorted(state_transitions, key=lambda t: get_transition_sort_key(t, grammar))

    for from_state, sym, to in sorted_transitions:
        kernel_str = format_items(parser.states[to].items, grammar.productions)
        if kernel_str in kernel_to_state:
            state_mapping[to] = kernel_to_state[kernel_str]
        elif to not in state_mapping:
            state_mapping[to] = next_state
            kernel_to_state[kernel_str] = next_state
            next_state += 1

    # closures serialization: include kernel, closure and goto transitions from that state
    closures = []
    def format_kernel(state_idx):
        items = parser.states[state_idx].items
        start_prod = grammar.productions[0]
        kernel_items = [it for it in items if it.dot_position > 0 or it.production == start_prod]
        return [str(it) for it in kernel_items]

    for real_state in range(len(parser.states)):
        items = [str(it) for it in parser.states[real_state].items]
        # collect gotos from this state (both shifts and goto table)
        gotos = []
        # transitions_from holds (sym, dest) for shifts and gotos
        for (st, sym), act in parser.action_table.items():
            if st == real_state and isinstance(act, tuple) and act[0] == 'shift':
                dest = act[1]
                gotos.append({"symbol": str(sym), "to": state_mapping.get(dest, dest)})
        for (st, A), dest in parser.goto_table.items():
            if st == real_state:
                gotos.append({"symbol": str(A), "to": state_mapping.get(dest, dest)})

        closures.append({
            "state": state_mapping.get(real_state, real_state),
            "kernel": format_kernel(real_state),
            "closure": items,
            "goto": gotos
        })

    # LR table serialization - follow views.lr_table_view.get_table_columns logic
    # Columnas ACTION: solo terminales que aparecen en action_table
    action_cols = [t for t in grammar.terminals
                  if any((st, t) in parser.action_table
                        for st in range(len(parser.states)))]
    if any(sym == '$' for (_, sym) in parser.action_table.keys()) and '$' not in action_cols:
        action_cols.append('$')

    # Columnas GOTO: incluir S' y luego no terminales que aparecen en goto_table
    goto_present = {sym for (_, sym) in parser.goto_table.keys()}
    goto_cols = ["S'"] + [A for A in grammar.non_terminals if A in goto_present and A != "S'"]

    # Build rows ordered by shown state (0..num_shown-1) using inv_map
    inv_map = {shown: real for real, shown in state_mapping.items()}
    num_shown = max(state_mapping.values()) + 1
    rows = []
    for s_shown in range(num_shown):
        real = inv_map.get(s_shown, s_shown)
        action_map = {}
        for t in action_cols:
            act = parser.action_table.get((real, t))
            if not act:
                action_map[t] = None
            else:
                kind, val = act
                if kind == 'shift':
                    action_map[t] = f's{state_mapping.get(val, val)}'
                elif kind == 'reduce':
                    action_map[t] = f'r{val}'
                elif kind == 'accept':
                    action_map[t] = 'acc'
                else:
                    action_map[t] = str(act)
        goto_map = {}
        for A in goto_cols:
            dest = parser.goto_table.get((real, A))
            goto_map[A] = None if dest is None else str(state_mapping.get(dest, dest))
        rows.append({"state": s_shown, "action": action_map, "goto": goto_map})

    # Además, construir `table` en el mismo formato que views.lr_table_view espera
    # Esto facilita que el frontend reconstruya la tabla tal como se imprime en backend/run.py
    inv_map = {shown: real for real, shown in state_mapping.items()}
    table_headers = ["State"] + action_cols + goto_cols
    table_rows = []
    def fmt_action_local(action):
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

    for s_shown in range(num_shown):
        s_real = inv_map.get(s_shown, s_shown)
        row = {"State": s_shown}
        # ACTION columns
        for t in action_cols:
            row[t] = fmt_action_local(parser.action_table.get((s_real, t)))
        # GOTO columns
        for A in goto_cols:
            dest = parser.goto_table.get((s_real, A))
            row[A] = '' if dest is None else str(state_mapping.get(dest, dest))
        table_rows.append(row)

    # derivation: reuse parser.parse but construct rows similar to views
    derivation = []
    if tokens is not None:
        try:
            steps = parser.parse(tokens)
            # steps: list of {'stack': [...], 'input': [...], 'action': 'shift 4'...} from analyzer.lr_parser.parse
            # normalize to our derivation schema
            for i, st in enumerate(steps, start=1):
                # normalize action strings to human readable
                raw_action = st.get('action')
                action_str = raw_action
                if isinstance(raw_action, str):
                    if raw_action.startswith('shift'):
                        action_str = raw_action.replace('shift', 'shift')
                    elif raw_action.startswith('reduce'):
                        action_str = raw_action.replace('reduce', 'reduce')
                    elif raw_action.startswith('accept') or raw_action == 'accept':
                        action_str = 'accept'
                derivation.append({
                    "step": i,
                    "stack": st.get('stack', []),
                    "input": st.get('input', []),
                    "action": action_str
                })
        except Exception as e:
            derivation = {"error": str(e)}

    return {
        "first": serialize_first(grammar),
        "closures": closures,
        "lr_table": {"action_columns": action_cols, "goto_columns": goto_cols, "rows": rows},
        "table": {"headers": table_headers, "rows": table_rows},
        "derivation": derivation
    }


@app.post('/api/v1/parse')
def api_parse(req: ParseRequest):
    try:
        grammar = parse_grammar_from_string(req.grammar)
        result = build_parser_and_serialize(grammar, req.tokens)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
