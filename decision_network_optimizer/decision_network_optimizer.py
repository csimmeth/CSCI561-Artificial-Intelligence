# Caleb Simmeth
# CSCI 561 Homework 3
import copy

class Node:
    def __init__(self, name, parents):
        self.name = name
        self.parents = parents
        self.p_list = []
        self.p_list.append(name)
        for parent in self.parents:
            self.p_list.append(parent)
        self.p = {}


class Factor:
    def __init__(self, variables):
        self.variables = variables
        self.p = {}


input_file = "input.txt"
output_file = "output.txt"


def parse_input(input_file):
    """Parse the input file into the correct groups."""
    queries = []
    node_lines = [[]]
    section = 0
    node_number = 0
    with open(input_file) as file:
        for line in file:
            line = line.strip()
            if line == "******":
                section += 1
            elif section == 0:
                queries.append(line)
            elif section == 1:
                if line == "***":
                    node_number += 1
                    node_lines.append([])
                else:
                    node_lines[node_number].append(line)
            elif section == 2:
                # If there is a utility node, treat it as a normal node
                if line[:7] == "utility":
                    node_number += 1
                    node_lines.append([])
                node_lines[node_number].append(line)
    return queries, node_lines


def parse_node(node_input):
    """Parse the string input for a node into a Node object."""
    node_info = node_input.pop(0)
    if '|' in node_info:
        name, parents = node_info.split('|')
    else:
        name = node_info.strip()
        parents = ""

    name = name.strip()
    parent_list = parents.split()
    new_node = Node(name, parent_list)

    for line in node_input:
        if new_node.name == "utility":
            words = line.split()
            prob = float(words.pop(0))
            index = tuple(words)
            new_node.p[index] = prob
        else:
            if line == "decision":
                new_node.p = "decision"
            elif len(new_node.parents) is 0:
                new_node.p[tuple(['+'])] = float(line)
                new_node.p[tuple(['-'])] = 1 - float(line)
            else:
                words = line.split()
                prob = float(words.pop(0))
                words.insert(0, '+')
                pos_t = tuple(words)
                words[0] = '-'
                neg_t = tuple(words)

                new_node.p[pos_t] = prob
                new_node.p[neg_t] = 1 - prob
    return new_node


def main():
    """Parse the input then answer queries."""
    nodes = {}
    decision_nodes = {}
    utility_node = None
    queries, node_lines = parse_input(input_file)

    for node_input in node_lines:
        new_node = parse_node(node_input)
        if new_node.name == "utility":
            utility_node = new_node
        elif new_node.p == "decision":
            decision_nodes[new_node.name] = new_node
        else:
            nodes[new_node.name] = new_node

    output = ""
    for query_line in queries:
        evidence = []
        query_variables = []
        decisions = []
        maximizing_vars = []
        query_type, variables = query_line[:-1].split('(')
        if '|' in variables:
            to_find, given = variables.split('|')
        else:
            to_find = variables
            given = None

        # Categorize the observed variables
        for n in to_find.split(','):
            if query_type == "MEU": # In this case no value is given
                node_name = n.strip()
                maximizing_vars.append(node_name)
            else: 
                node_name, value = n.split('=')
                node_name = node_name.strip()
                value = value.strip()
                if query_type == "EU":  # Save this as a decision
                    decisions.append((node_name, value))
                else: # This is a variable in the probability query
                    query_variables.append((node_name, value))

        # Evidence variables, these will always be assigned values
        if given is not None:
            for n in given.split(','):
                node_name, value = n.split('=')
                node_name = node_name.strip()
                value = value.strip()
                evidence.append((node_name, value))

        if query_type == "P":
            norm = probability_distribution(query_variables, evidence, nodes)
            index = assignments_to_tuple(query_variables)
            p = norm[index]
            output += "%.2f" % p + '\n'
        elif query_type == "EU":
            utility = expected_utility(
                utility_node, decisions, evidence, nodes)
            output += "%.0f" % utility + '\n'
        else:
            assignment, utility = MEU(
                maximizing_vars, utility_node, decisions, evidence, nodes)
            output += "%s %.0f\n" % (assignment, utility)

    with open(output_file, "w") as file:
        file.write(output)


def probability_distribution(query_variables, evidence, nodes):
    """Calculate the probability disribution for every assignement of variables."""
    vars_to_assign = [var[0] for var in query_variables]
    final_probs = {}

    # Cycle through every assignment of vars to assign (for normalization)
    for i in range(0, pow(2, len(vars_to_assign))):
        assignments = int_to_assignment(vars_to_assign, i)
        index = assignments_to_tuple(assignments)
        assigned_set = list(set().union(assignments, evidence))
        factors = [make_factor(node, assigned_set) for name, node in nodes.items()]

        # Get all the remaining variables
        to_eliminate = {var for factor in factors for var in factor.variables}

        for variable in to_eliminate:
            factors = eliminate(variable, factors)

        # All the factors are now just values so multiply them together
        p = 1
        for factor in factors:
            p *= factor.p

        final_probs[index] = p

    total = sum(final_probs.values())
    norm = {key: value / total for key, value in final_probs.items()}
    return norm


def expected_utility(utility_node, decisions, evidence, nodes):
    """Calculate the expected utility of the utility node."""
    query_variables = []
    for parent in utility_node.parents:
        if parent not in [i[0] for i in decisions]:
            query_variables.append((parent, None))

    static_parents = []
    for node in decisions + evidence:
        if node[0] in utility_node.parents:
            static_parents.append((node[0], node[1]))

    norm = probability_distribution(
        query_variables, evidence + decisions, nodes)
    
    # Sum the utility for every variable assignment
    utility = 0
    for key, value in norm.items():
        variables = [parent for parent in static_parents]
        variables += [(query_variables[i][0], key[i]) for i in range(0, len(key))]
        utility += value * get_node_prob(utility_node, variables)

    return utility


def MEU(maximizing_vars, utility_node, decisions, evidence, nodes):
    """Calculate the parent values which maximize the utility node."""
    max_assignment = None
    max_utility = -9999999
    for i in range(0, pow(2, len(maximizing_vars))):
        assignment = int_to_assignment(maximizing_vars, i)
        utility = expected_utility(
            utility_node, decisions + assignment, evidence, nodes)
        if utility > max_utility:
            max_utility = utility
            max_assignment = assignment
    assignment_string = " ".join(assignments_to_tuple(max_assignment))
    return assignment_string, max_utility


def make_factor(node, evidence):
    """Create a factor for a node."""
    variables = [node.name] + [p_node for p_node in node.parents]
    evidence_names = [evi[0] for evi in evidence]
    hidden_variables = [var for var in variables if var not in evidence_names]
    factor = Factor(hidden_variables)

    if len(hidden_variables) > 0:
        for i in range(0, pow(2, len(hidden_variables))):
            assignments = int_to_assignment(hidden_variables, i)
            prob = get_node_prob(node, set().union(assignments, evidence))
            index = assignments_to_tuple(assignments)
            factor.p[index] = prob
    else:
        prob = get_node_prob(node, evidence)
        factor.p = prob
    return factor


def assignments_to_tuple(assignments):
    """Convert a list of variables with valuse to a tuple of just the values."""
    return tuple([a[1] for a in assignments])


def int_to_assignment(variables, i):
    """Convert an integer to a series of variable assignments."""
    assignments = []
    mask = 1
    for var in variables:
        if(i & mask):
            assignments.append((var, '+'))
        else:
            assignments.append((var, '-'))
        mask *= 2
    return assignments


def get_node_prob(node, assignments):
    """Get a node's probability based on assignments."""
    reorder = [assignment[1] for var in node.p_list for assignment in assignments \
               if var == assignment[0]]
    return node.p[tuple(reorder)]


def eliminate(var, factors):
    """Eliminate a variable from all factors."""
    to_combine = [factor for factor in factors if var in factor.variables]

    # Remove these factors from the factors list
    all_variables = {var}
    for factor in to_combine:
        factors.remove(factor)
        for v in factor.variables:
            all_variables.add(v)

    # Cross multiplication
    union_dict = {}
    for i in range(0, pow(2, len(all_variables))):
        assignment = int_to_assignment(all_variables, i)
        for factor in to_combine:
            prob = get_factor_prob(factor, assignment)
            index = assignments_to_tuple(assignment)
            if index in union_dict:
                union_dict[index] *= prob
            else:
                union_dict[index] = prob

    # Sum out the variable and create a new factor
    new_variables = [variable for variable in all_variables if variable != var]
    new_factor = Factor(new_variables)
    if len(new_variables) is 0:  # There are no variables left, so just do the probability
        new_factor.p = union_dict[tuple('+')] + union_dict[tuple('-')]
    else:
        for i in range(0, pow(2, len(new_variables))):
            new_a = int_to_assignment(new_variables, i)
            index = assignments_to_tuple(new_a)
            p_index = assignments_to_tuple([("old", '+')] + new_a)
            n_index = assignments_to_tuple([("old", '-')] + new_a)
            new_factor.p[index] = union_dict[p_index] + union_dict[n_index]

    factors.append(new_factor)
    return factors


def get_factor_prob(factor, assignments):
    """Get the probability of a factor given an assignment."""
    reorder = [assignment[1] for var in factor.variables for assignment in assignments\
              if var == assignment[0]]
    return factor.p[tuple(reorder)]


if __name__ == '__main__':
    main()
