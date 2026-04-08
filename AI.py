import uuid
import copy
import random
from enum import Enum


DIVISORS = [2, 3, 4, 5]
class Player(Enum):
    MAXIMIZER = 1
    MINIMIZER = 2

class GameNode:
    def __init__ (self, _state: GameState):
        self.state = _state
        self.move = None
        self.children = []
        self.terminal = False
        self.winner = None
        self.hef = None
        self.id = str(uuid.uuid4())
    
    def heuristic(self):
        self.hef = hef(self)
        return self.hef
    
class GameState:
    def __init__(self):
        self.number = 0
        self.points = 0
        self.bank = 0
        self.player = Player.MAXIMIZER
        self.starting_player = Player.MAXIMIZER

def apply_move(state: GameState, divisor):
    new_state = copy.deepcopy(state)
    new_state.number = state.number // divisor
    if new_state.number % 2 == 1:
        new_state.points += 1
    else:
        new_state.points -= 1

    if new_state.number % 10 == 0 or new_state.number % 10 == 5:
        new_state.bank += 1
    if state.player == Player.MAXIMIZER:
        new_state.player = Player.MINIMIZER
    else:
        new_state.player = Player.MAXIMIZER
    return new_state

def generate_tree(state: GameState, remaining_depth, node_number = 0):
    node = GameNode(state)
    node_number += 1

    valid_moves = [d for d in DIVISORS if state.number % d == 0]

    if not valid_moves:
        node.terminal = True
        return node, node_number
    
    if remaining_depth == 0:
        return node, node_number
    
    for d in valid_moves:
        new_state = apply_move(state, d)
        child, node_number = generate_tree(new_state, remaining_depth-1, node_number)
        child.move = d
        node.children.append(child)
    return node, node_number

def minimax(node: GameNode, maximizing: bool):
    if node.terminal or not node.children:
        return node.heuristic()
    if maximizing:
        value = float("-inf")
        for child in node.children:
            value = max(value, minimax(child, False))
        node.hef = value
        return value
    else:
        value = float("inf")
        for child in node.children:
            value = min(value, minimax(child, True))
        node.hef = value
        return value
    
def alphabeta(node: GameNode, alpha, beta, maximizing: bool, value_num = 0):
    value_num += 1
    if node.terminal or not node.children:
        return node.heuristic(), value_num

    if maximizing:
        value = float("-inf")
        for child in node.children:
            child_value, value_num = alphabeta(child, alpha, beta, False, value_num)
            value = max(value, child_value)
            alpha = max(alpha, value)
            if beta <= alpha:
                break  # prune
        node.hef = value
        return value, value_num
    else:
        value = float("inf")
        for child in node.children:
            child_value, value_num = alphabeta(child, alpha, beta, True, value_num)
            value = min(value, child_value)
            beta = min(beta, value)
            if beta <= alpha:
                break  # prune
        node.hef = value
        return value, value_num

def next_computer_move(state: GameState, depth: int, alg: str = "alphabeta"):
    root, node_number = generate_tree(state, depth)
    evaluated_nodes = 0

    if alg == "alphabeta":
        _, evaluated_nodes = alphabeta(root, float("-inf"), float("inf"), True)
    elif alg == "minimax":
        minimax(root, True)
        evaluated_nodes = node_number
    else:
        return
    print(f"Game tree generated with {node_number} nodes")
    print(f"Evaluated {evaluated_nodes} nodes from the tree")
    max_hef = float("-inf")
    best_moves = []
    
    for child in root.children:
        if child.hef > max_hef:
            max_hef = child.hef
            best_moves = [child.move]
        elif child.hef == max_hef:
            best_moves.append(child.move)    
    if(alg == "minimax"):
        move = random.choice(best_moves)
    else:
        move = best_moves[0]

    return move


def print_tree(node, indent=0):
    prefix = " " * indent
    
    print(f"{prefix}Node: number={node.number}, points={node.game_points}, bank={node.bank}, move={node.move}, heuristic={node.heuristic()}")

    for child in node.children:
        print_tree(child, indent + 8)

def hef(node: GameNode):
    divisors = divisors_number(node.state.number)
    divisors_low_to_high = divisors_number_low_to_high(node.state.number)
    divisor5 = divisor5_number(node.state.number)
    bank = node.state.bank
    points = node.state.points
    parity_shift = 0
    result = 0

    if node.state.starting_player == Player.MINIMIZER:
        parity_shift = 1

    min_influence5 = max(0, divisor5 - 1)

    result += ((min_influence5 + divisors + bank + points + parity_shift) % 2) * 2
    result += (min_influence5 + divisors_low_to_high + bank + points + parity_shift) % 2 * 0.5
    result += (divisors + bank + points + parity_shift) % 2 *0.25
    result += ((divisors_low_to_high + bank + points + parity_shift) % 2) * 0.25

    return result

def divisors_number(n):
    count = 0
    for d in [5, 4, 3, 2]:
        while n % d == 0:
            n //= d
            count += 1
    return count
def divisors_number_low_to_high(n):
    count = 0
    for d in [2, 3, 4, 5]:
        while n % d == 0:
            n //= d
            count += 1
    return count
def divisor5_number(n):
    count = 0
    while n%5 ==0:
        n //= 5
        count += 1
    return count

def divisor4_number(n):
    count = 0
    while n%4 ==0:
        n //= 4
        count += 1
    return count