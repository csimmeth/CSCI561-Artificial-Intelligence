# Caleb Simmeth
# CSCI 561 Homework 2
import copy

input_file = "input.txt"
output_file = "output.txt"


def main():
    with open(input_file) as file:
        n_guests, n_tables = file.readline().split()
        lines = file.read().splitlines()

    num_guests = int(n_guests)
    num_tables = int(n_tables)

    clauses = []
    # Every guest must be seated at a table
    for guest in range(1, num_guests + 1):
        clause = [(guest, table, True) for table in range(1, num_tables + 1)]
        clauses.append(clause)

    # Each guest can not be seated at multiple tables
    for guest in range(1, num_guests + 1):
        for t1 in range(1, num_tables + 1):
            for t2 in range(t1 + 1, num_tables + 1):
                clauses.append([(guest, t1, False), (guest, t2, False)])

    # Add friends and enemies
    for line in lines:
        (g1, g2, rel) = line.split()
        if rel is "F":
            add_friend(clauses, int(g1), int(g2), num_tables)
        else:
            add_enemy(clauses, int(g1), int(g2), num_tables)

    # Create a symbol for each combination of guest and table
    symbols = [(guest, table) for guest in range(1, num_guests + 1) for table in range(1, num_tables + 1)]
    
    # Create an empty model
    model = [[None for x in range(num_tables)] for y in range(num_guests)]

    # Solve
    (success, new_model) = DPLL(clauses, symbols, model)

    with open(output_file, "w") as file:
        if success:
            file.write("yes")
            for guest in range(0, num_guests):
                for table in range(0, num_tables):
                    if new_model[guest][table] is True:
                        file.write("\n" + str(guest + 1) + " " + str(table + 1))
        else:
            file.write("no")


def add_friend(clauses, g1, g2, num_tables):
    """Add the clauses to make sure g1 and g2 sit at the same table."""
    for table in range(1, num_tables + 1):
        clauses.append([(g1, table, False), (g2, table, True)])
        clauses.append([(g1, table, True), (g2, table, False)])



def add_enemy(clauses, g1, g2, num_tables):
    """Add the clauses to make sure g1 and g2 do not sit at the same table."""
    for table in range(1, num_tables + 1):
        clauses.append([(g1, table, False), (g2, table, False)])


def DPLL(clauses, symbols, model):
    """Implementation of the DPLL algorithm."""
    if(every_clause_true(clauses, model)):
        return (True, model)

    if(some_clause_false(clauses, model)):
        return (False, model)

    # Try to find a pure symbol
    (symbol, value) = find_pure_symbol(clauses, symbols, model)
    if symbol is not None:
        symbols.remove(symbol)
        update_model(model, symbol, value)
        return DPLL(clauses, symbols, model)

    # Try to find a unit clause
    (symbol, value) = find_unit_clause(clauses, model)
    if symbol is not None:
        symbols.remove(symbol)
        update_model(model, symbol, value)
        return DPLL(clauses, symbols, model)

    # Branch
    new_symbols = copy.deepcopy(symbols)
    symbol = new_symbols.pop(0)
    new_model = copy.deepcopy(model)

    # Try setting the next symbol to true
    update_model(new_model, symbol, True)
    (success, return_model) = DPLL(clauses, new_symbols, new_model)
    if(success):
        return (True, return_model)

    # Now try setting it to false
    update_model(new_model, symbol, False)
    (success, return_model) = DPLL(clauses, new_symbols, new_model)
    if(success):
        return (True, return_model)

    return (False, model)


def every_clause_true(clauses, model):
    """Check if every clause is true."""
    for clause in clauses:
        if not satisfied(clause, model):
            return False
    return True


def satisfied(clause, model):
    """Check if a clause is satisfied."""
    for literal in clause:
        if model_matches_literal(literal, model):
            return True
    return False


def some_clause_false(clauses, model):
    """Check if at least one clause is false."""
    for clause in clauses:
        if empty(clause, model):
            return True
    return False


def empty(clause, model):
    """Check if a clause is unsatisfyable."""
    for literal in clause:
        if not model_contradicts_literal(literal, model):
            return False
    return True


def find_pure_symbol(clauses, symbols, model):
    """Try to find a symbol which only appears as either positive or negative."""
    true_symbols = set()
    false_symbols = set()
    for clause in clauses:
        # Check that the clause is not already satisfied
        if not satisfied(clause, model):
            # Add each literal to it's corresponding set
            for literal in clause:
                if model_not_set(literal, model):
                    if literal[2] is True:
                        true_symbols.add((literal[0], literal[1]))
                    else:
                        false_symbols.add((literal[0], literal[1]))

    for symbol in true_symbols:
        if symbol not in false_symbols:
            return (symbol, True)
    for symbol in false_symbols:
        if symbol not in true_symbols:
            return (symbol, False)
    return (None, None)


def find_unit_clause(clauses, model):
    """Try to find a clause with just one symbol remaining."""
    for clause in clauses:
        # check that the clause is not already satisfied
        if not satisfied(clause, model):
            # Check if only one symbol is not false
            literals_left = 0
            found_literal = None
            for literal in clause:
                if not model_contradicts_literal(literal, model):
                    literals_left += 1
                    found_literal = literal
            if literals_left == 1:
                return ((found_literal[0], found_literal[1]), found_literal[2])
    return (None, None)


def model_contradicts_literal(literal, model):
    """Check if the literal must be false."""
    model_value = model[literal[0] - 1][literal[1] - 1]
    return model_value is (not literal[2]) and (not None)


def model_matches_literal(literal, model):
    """Check if the literal must be true."""
    return literal[2] is model[literal[0] - 1][literal[1] - 1]


def update_model(model, symbol, value):
    """Update the model."""
    model[symbol[0] - 1][symbol[1] - 1] = value


def model_not_set(literal, model):
    """Check if a literal does not have a value assigned."""
    return model[literal[0] - 1][literal[1] - 1] is None


if __name__ == '__main__':
    main()
