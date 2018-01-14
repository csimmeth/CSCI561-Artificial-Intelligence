# Caleb Simmeth
# CSCI 561 Homework 1
import copy

input_file = "input.txt"
output_file = "output.txt"
board_weights = [[99, -8, 8, 6, 6, 8, -8, 99],
                 [-8, -24, -4, -3, -3, -4, -24, -8],
                 [8, -4, 7, 4, 4, 7, -4, 8],
                 [6, -3, 4, 0, 0, 4, -3, 6],
                 [6, -3, 4, 0, 0, 4, -3, 6],
                 [8, -4, 7, 4, 4, 7, -4, 8],
                 [-8, -24, -4, -3, -3, -4, -24, -8],
                 [99, -8, 8, 6, 6, 8, -8, 99]]
directions = [(-1, 0), (0, 1), (1, 0), (0, -1),
              (-1, 1), (1, 1), (1, -1), (-1, -1)]

max_token = ""
min_token = ""
max_depth = 0
board = []
next_board = []
log = "Node,Depth,Value,Alpha,Beta"


def opposite(token):
    """Return the opposite of the given token"""
    if token == 'X':
        return 'O'
    return 'X'


def cell_name(i, j):
    """Return the Letter and number corresponding with row i and column j."""
    return str(unichr(97 + j)) + str(i + 1)


def to_str(num):
    """Convert the max and min values to Infinity"""
    if num == 1000:
        return "Infinity"
    elif num == -1000:
        return "-Infinity"
    else:
        return str(num)


def write_log(cell, depth, v, a, b):
    """Write this step to the log string."""
    global log
    log += "\n" + cell + "," + \
        str(depth) + "," + to_str(v) + "," + to_str(a) + "," + to_str(b)


def utility(current_board):
    """Calculate the utility of the current board."""
    util = 0
    for i in range(0, 8):
        for j in range(0, 8):
            if current_board[i][j] is max_token:
                util += board_weights[i][j]
            elif current_board[i][j] is min_token:
                util -= board_weights[i][j]
    return util


def valid_moves(current_board, token):
    """Return an array of all valid moves on the board."""
    moves = []
    for i in range(0, 8):
        for j in range(0, 8):
            if(is_valid_move(current_board, token, i, j)):
                moves.append((i, j))
    return moves


def is_valid_move(current_board, token, i, j):
    """Check if a move is valid on the given board"""

    # Check if the space is taken
    if current_board[i][j] is not "*":
        return False

    for x, y in directions:
        seen_opponent = False
        current_x = j + x
        current_y = i + y
        while current_x in range(0,8)  and current_y in range(0,8):
            # Remember seeing an opponent token 
            if current_board[current_y][current_x] is opposite(token):
                seen_opponent = True
            # On seeing my token, check I have also seen an opponent 
            elif current_board[current_y][current_x] is token:
                if seen_opponent:
                    return True
                else:
                    break
            # Otherwise this space is blank, so try another direction
            else:
                break
            current_x += x
            current_y += y
    return False


def create_new_board(current_board, token, i, j):
    """Add a new piece to the board and flip colors accordingly."""
    new_board = copy.deepcopy(current_board)
    new_board[i][j] = token

    for x, y in directions:
        to_flip = []
        current_x = j + x
        current_y = i + y
        while current_x in range(0, 8) and current_y in range(0, 8):
            # On seeing an  opponent's token, remember it
            if new_board[current_y][current_x] is opposite(token):
                to_flip.append((current_x, current_y))
            # If I see my own token flip all previous opponent's tokens then break
            elif new_board[current_y][current_x] is token:
                for x, y in to_flip:
                    new_board[y][x] = token
                break
            else:
                # The space is blank, break
                break
            current_x += x
            current_y += y

    return new_board


def max_value(cell, current_board, depth, a, b):
    """Find the max possible board value."""
    global next_board
    if(depth == max_depth):
        value = utility(current_board)
        if cell == "pass2":
            cell = "pass"
        write_log(cell, depth, value, a, b)
        return value

    # Find available moves
    moves = valid_moves(current_board, max_token)

    # Check if we are out of moves (2 passes in a row)
    if len(moves) == 0 and cell == "pass2":
        value = utility(current_board)
        write_log("pass", depth, value, a, b)
        return value

    v = -1000
    write_log(cell, depth, v, a, b)

    # Explore all potential moves
    for i, j in moves:
        new_board = create_new_board(current_board, max_token, i, j)
        v = max(v, min_value(cell_name(i, j), new_board, depth + 1, a, b))
        if(v > a and depth == 0):
            next_board = copy.deepcopy(new_board)
        if v >= b:
            write_log(cell, depth, v, a, b)
            return v
        a = max(a, v)
        write_log(cell, depth, v, a, b)

    # Handle passing
    if len(moves) == 0:
        next_cell = "pass"
        if cell == "pass":
            next_cell = "pass2" # Mark that we are already one pass deep
        v = max(v, min_value(next_cell, current_board, depth + 1, a, b))
        if v >= b:
            write_log(cell, depth, v, a, b)
            return v
        a = max(a, v)
        write_log(cell, depth, v, a, b)
    return v


def min_value(cell, current_board, depth, a, b):
    """Find the min possible board value."""
    if(depth == max_depth):
        value = utility(current_board)
        if cell is "pass2":
            cell = "pass"
        write_log(cell, depth, value, a, b)
        return value

    moves = valid_moves(current_board, min_token) 

    if len(moves) == 0 and cell == "pass2":
        value = utility(current_board)
        write_log("pass", depth, value, a, b)
        return value

    v = 1000
    write_log(cell, depth, v, a, b)

    for i, j in moves:
        new_board = create_new_board(current_board, min_token, i, j)
        v = min(v, max_value(cell_name(i, j), new_board, depth + 1, a, b))

        if v <= a:
            write_log(cell, depth, v, a, b)
            return v

        b = min(b, v)
        write_log(cell, depth, v, a, b)
        if v <= a:
            return v

    if len(moves) == 0:
        next_cell = "pass"
        if cell is "pass":
            next_cell = "pass2" # Mark that we are already one pass deep
        v = min(v, max_value(next_cell, current_board, depth + 1, a, b))
        if v <= a:
            write_log(cell, depth, v, a, b)
            return v
        b = min(b, v)
        write_log(cell, depth, v, a, b)
    return v


if __name__ == '__main__':
    """Read input, run the solver, and write the results to the output."""
    with open(input_file) as file:
        max_token = file.readline().strip()
        min_token = opposite(max_token)
        max_depth = int(file.readline().strip())
        board = [list(line.strip()) for line in file]

    next_board = copy.deepcopy(board)

    max_value("root", board, 0, -1000, 1000)

    with open(output_file, "w") as file:
        for row in next_board:
            file.write(''.join(row) + '\n')
        file.write(log)
