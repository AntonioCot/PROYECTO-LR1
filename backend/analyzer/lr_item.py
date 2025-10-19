class LR1Item:
    def __init__(self, production, dot_position, lookahead):
        self.production = production  # La producción
        self.dot_position = dot_position  # Posición del punto
        self.lookahead = lookahead  # Símbolo de lookahead

    def __eq__(self, other):
        if not isinstance(other, LR1Item):
            return False
        return (self.production == other.production and
                self.dot_position == other.dot_position and
                self.lookahead == other.lookahead)

    def __hash__(self):
        return hash((self.production, self.dot_position, self.lookahead))

    def get_next_symbol(self):
        """Obtiene el símbolo después del punto"""
        if self.dot_position < len(self.production.right):
            return self.production.right[self.dot_position]
        return None

    def advance_dot(self):
        """Crea un nuevo item con el punto avanzado una posición"""
        return LR1Item(self.production, self.dot_position + 1, self.lookahead)

    def __str__(self):
        """Representación en string del item LR(1)"""
        right = list(self.production.right)
        right.insert(self.dot_position, ".")
        return f"{self.production.left} -> {' '.join(right)}, {self.lookahead}"

    def __repr__(self):
        return self.__str__()