from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

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
    return {nt: list(vals) for nt, vals in grammar.first.items()}


def build_parser_and_serialize(grammar: Grammar, tokens: Optional[List[str]]):
    parser = LR1Parser(grammar)

    # Build closures info by reusing run.collect_transitions logic inline
    transitions_from = {}
    for (st, sym), act in parser.action_table.items():
        if isinstance(act, tuple) and act[0] == 'shift':
            transitions_from.setdefault(st, []).append((sym, act[1]))
    for (st, sym), to in parser.goto_table.items():
        transitions_from.setdefault(st, []).append((sym, to))

    # Create a simple state mapping consistent with views.lr_closure_view
    # Map displayed states to real states (0..n)
    kernel_to_state = {}
    state_mapping = {}
    next_state = 0
    def format_kernel(state_idx):
        items = parser.states[state_idx].items
        # kernel: items with dot_position>0 or start prod
        start_prod = grammar.productions[0]
        kernel_items = [it for it in items if it.dot_position > 0 or it.production == start_prod]
        return [str(it) for it in kernel_items]

    # initial
    state_mapping[0] = 0
    kernel_to_state[tuple(format_kernel(0))] = 0
    next_state = 1

    # collect transitions sorted by from
    state_transitions = []
    for from_state in range(len(parser.states)):
        for sym, to in transitions_from.get(from_state, []):
            state_transitions.append((from_state, str(sym), to))

    state_transitions.sort()
    for from_state, sym, to in state_transitions:
        k = tuple(format_kernel(to))
        if k in kernel_to_state:
            state_mapping[to] = kernel_to_state[k]
        elif to not in state_mapping:
            state_mapping[to] = next_state
            kernel_to_state[k] = next_state
            next_state += 1

    # closures serialization
    closures = []
    seen_states = set()
    # include state 0
    for real_state, shown_state in sorted(state_mapping.items(), key=lambda x: x[1]):
        items = [str(it) for it in parser.states[real_state].items]
        closures.append({
            "state": shown_state,
            "kernel": format_kernel(real_state),
            "closure": items
        })
        seen_states.add(real_state)

    # LR table serialization
    # action columns: terminals present + '$' if accept exists
    action_cols = [t for t in grammar.terminals if any((st, t) in parser.action_table for st in range(len(parser.states)))]
    if any(k[1] == '$' for k in parser.action_table.keys()) and '$' not in action_cols:
        action_cols.append('$')

    goto_cols = [A for A in grammar.non_terminals]

    num_states = max(state_mapping.values()) + 1
    rows = []
    inv_map = {shown: real for real, shown in state_mapping.items()}
    for shown in range(num_states):
        real = inv_map.get(shown, shown)
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
        rows.append({"state": shown, "action": action_map, "goto": goto_map})

    # derivation: reuse parser.parse but construct rows similar to views
    derivation = []
    if tokens is not None:
        try:
            steps = parser.parse(tokens)
            # steps: list of {'stack': [...], 'input': [...], 'action': 'shift 4'...} from analyzer.lr_parser.parse
            # normalize to our derivation schema
            for i, st in enumerate(steps, start=1):
                derivation.append({
                    "step": i,
                    "stack": st.get('stack', []),
                    "input": st.get('input', []),
                    "action": st.get('action')
                })
        except Exception as e:
            derivation = {"error": str(e)}

    return {
        "first": serialize_first(grammar),
        "closures": closures,
        "lr_table": {"action_columns": action_cols, "goto_columns": goto_cols, "rows": rows},
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
