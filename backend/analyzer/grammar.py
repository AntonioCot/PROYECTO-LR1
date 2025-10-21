class Production:
    def __init__(self, left, right):
        self.left = left  # lado izquierdo de la producción
        self.right = right  # lado derecho de la producción
    def __eq__(self, other):
        return isinstance(other, Production) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self.left, tuple(self.right)))

    def __str__(self):
        if not self.right:  # producción vacía
            return f"{self.left} -> ''"
        return f"{self.left} -> {' '.join(self.right)}"

class Grammar:
    def __init__(self):
        self.productions = []
        self.terminals = []  # Cambiado a lista para mantener orden
        self.non_terminals = []  # Cambiado a lista para mantener orden
        self.first = {}
        self.start_symbol = None

    def add_production(self, left, right):
        """Añade una nueva producción a la gramática"""
        # Para producciones vacías, asegurar que right sea una lista vacía
        if not right or right == ['ε'] or right == [''] or right == ["''"]:
            right = []
        production = Production(left, right)
        self.productions.append(production)
        if left not in self.non_terminals:
            self.non_terminals.append(left)
        # Detectar términos y no terminales en el lado derecho
        for symbol in right:
            # heurística: si el primer caracter es mayúscula lo tomamos como no terminal
            if symbol[0].isupper():
                if symbol not in self.non_terminals:
                    self.non_terminals.append(symbol)
            else:
                if symbol not in self.terminals:
                    self.terminals.append(symbol)

    def calculate_first(self):
        """Calcula el conjunto FIRST para todos los símbolos de la gramática"""
        # Inicializar FIRST usando OrderedDict para mantener el orden
        self.first = {nt: [] for nt in self.non_terminals}
        # Los terminales tienen FIRST(t) = {t}, manteniendo el orden
        for t in self.terminals:
            self.first[t] = [t]

        changed = True
        while changed:
            changed = False
            for prod in self.productions:
                A = prod.left
                rhs = prod.right
                # Si la producción es epsilon
                if len(rhs) == 0 or (len(rhs) == 1 and (rhs[0] == 'ε' or rhs[0] == '' or rhs[0] == "''")):
                    if 'ε' not in self.first[A]:
                        self.first[A].append('ε')
                        changed = True
                    continue

                # Recorremos los símbolos del RHS
                add_eps = True
                for X in rhs:
                    if X in self.terminals:
                        if X not in self.first[A]:
                            self.first[A].append(X)
                            changed = True
                        add_eps = False
                        break
                    else:
                        # X es no terminal
                        before_len = len(self.first[A])
                        # Añadimos FIRST(X) sin epsilon manteniendo el orden
                        for s in self.first.get(X, []):
                            if s != 'ε' and s not in self.first[A]:
                                self.first[A].append(s)
                        if len(self.first[A]) != before_len:
                            changed = True
                        # si FIRST(X) contiene epsilon seguimos al siguiente simbolo
                        if 'ε' in self.first.get(X, []):
                            add_eps = True
                        else:
                            add_eps = False
                            break

                if add_eps:
                    if 'ε' not in self.first[A]:
                        self.first[A].append('ε')
                        changed = True

    def get_first(self, symbols):
        """Obtiene el conjunto FIRST para una secuencia de símbolos"""
        result = set()  # Usamos set aquí porque el LR parser espera un set
        if not symbols:
            return result

        for i, symbol in enumerate(symbols):
            # Si el símbolo es un terminal conocido (o no es un no terminal), lo tratamos como terminal
            if symbol in self.terminals or symbol not in self.non_terminals:
                result.add(symbol)
                return result
            # non-terminal
            first_list = self.first.get(symbol, [])
            result.update(s for s in first_list if s != 'ε')
            if 'ε' not in first_list:
                return result

        # Si todos los simbolos pueden producir epsilon, agregar epsilon
        result.add('ε')
        return result