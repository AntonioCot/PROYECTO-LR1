from .grammar import Grammar
from .lr_item import LR1Item


class LR1State:
    def __init__(self, items):
        # items: set of LR1Item (closure)
        self.items = set(items)

    def __repr__(self):
        return f"LR1State({len(self.items)} items)"


class LR1Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = []  # list of sets (closures)
        self.action_table = {}  # (state_idx, terminal) -> ('shift', s) | ('reduce', prod_idx) | ('accept', None)
        self.goto_table = {}
        self.build_parsing_table()

    def closure(self, items):
        items = set(items)
        while True:
            added = set()
            for it in list(items):
                B = it.get_next_symbol()
                if B and B in self.grammar.non_terminals:
                    beta = it.production.right[it.dot_position + 1:]
                    beta = list(beta) + [it.lookahead]
                    first_set = self.grammar.get_first(beta)
                    for p in self.grammar.productions:
                        if p.left == B:
                            for a in first_set:
                                new = LR1Item(p, 0, a)
                                if new not in items:
                                    added.add(new)
            if not added:
                break
            items.update(added)
        return items

    def goto(self, items, symbol):
        moved = set()
        for it in items:
            if it.get_next_symbol() == symbol:
                moved.add(it.advance_dot())
        return self.closure(moved) if moved else set()

    def build_parsing_table(self):
        # augmented production assumed to be first
        start_prod = self.grammar.productions[0]
        start_item = LR1Item(start_prod, 0, '$')
        start_closure = self.closure({start_item})

        states = [start_closure]
        state_map = {frozenset(start_closure): 0}
        queue = [start_closure]

        symbols = list(self.grammar.terminals) + list(self.grammar.non_terminals)

        while queue:
            I = queue.pop(0)
            i_idx = state_map[frozenset(I)]
            for X in symbols:
                J = self.goto(I, X)
                if not J:
                    continue
                J_key = frozenset(J)
                if J_key not in state_map:
                    state_map[J_key] = len(states)
                    states.append(J)
                    queue.append(J)
                j_idx = state_map[J_key]
                if X in self.grammar.terminals:
                    # shift
                    self.action_table[(i_idx, X)] = ('shift', j_idx)
                else:
                    # goto
                    self.goto_table[(i_idx, X)] = j_idx

            # reductions and accept
            for it in I:
                if it.get_next_symbol() is None:
                    if it.production == start_prod and it.lookahead == '$':
                        self.action_table[(i_idx, '$')] = ('accept', None)
                    else:
                        prod_idx = self.grammar.productions.index(it.production)
                        self.action_table[(i_idx, it.lookahead)] = ('reduce', prod_idx)

        # store states as LR1State objects for nicer printing
        self.states = [LR1State(s) for s in states]

    def parse(self, tokens):
        stack = [0]
        tokens = list(tokens) + ['$']
        steps = []
        while True:
            state = stack[-1]
            a = tokens[0]
            if (state, a) not in self.action_table:
                raise SyntaxError(f"Unexpected token {a} at state {state}")
            action, val = self.action_table[(state, a)]
            steps.append({'stack': stack.copy(), 'input': tokens.copy(), 'action': f"{action}{'' if val is None else ' '+str(val)}"})
            if action == 'shift':
                stack.append(val)
                tokens.pop(0)
            elif action == 'reduce':
                prod = self.grammar.productions[val]
                for _ in prod.right:
                    stack.pop()
                t = stack[-1]
                goto_state = self.goto_table.get((t, prod.left))
                if goto_state is None:
                    raise SyntaxError(f"No goto for {(t, prod.left)}")
                stack.append(goto_state)
            elif action == 'accept':
                break
        return steps