from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import copy
import random


DIVISORS = [2, 3, 4, 5]


class GameNode:
    def __init__ (self, _state: GameState):
        self.state = _state
        self.move = None
        self.children = []
        self.terminal = False
        self.winner = None
        self.hef = hef(self)
        self.id = str(uuid.uuid4())
    
    def heuristic(self):
        return hef(self)
    
class GameState:
    def __init__(self):
        self.number = 0
        self.points = 0
        self.bank = 0
        self.player = 1

def apply_move(state: GameState, divisor):
    new_state = copy.deepcopy(state)
    new_state.number = state.number // divisor
    if new_state.number % 2 == 1:
        new_state.points += 1
    else:
        new_state.points -= 1

    if new_state.number % 10 == 0 or new_state.number % 10 == 5:
        new_state.bank += 1
    if state.player == 1:
        new_state.player = 2
    else:
        new_state.player = 1
    return new_state


def generate_tree(state: GameState, remaining_depth):
    node = GameNode(state)

    valid_moves = [d for d in DIVISORS if state.number % d == 0]

    if not valid_moves:
        node.terminal = True
        return node
    
    if remaining_depth == 0:
        return node
    
    for d in valid_moves:
        new_state = apply_move(state, d)
        child = generate_tree(new_state, remaining_depth-1)
        child.move = d
        node.children.append(child)
    return node

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
    
def alphabeta(node: GameNode, alpha, beta, maximizing: bool):
    if node.terminal or not node.children:
        return node.heuristic()

    if maximizing:
        value = float("-inf")
        for child in node.children:
            value = max(value, alphabeta(child, alpha, beta, False))
            alpha = max(alpha, value)
            if beta <= alpha:
                break  # prune
        node.hef = value
        return value
    else:
        value = float("inf")
        for child in node.children:
            value = min(value, alphabeta(child, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                break  # prune
        node.hef = value
        return value
    
def next_computer_move(state: GameState, depth: int, alg: str = "alphabeta"):
    root = generate_tree(state, depth)
    if state.player == 1:
        maximizing = True
    else:
        maximizing = False

    if alg == "alphabeta":
        alphabeta(root, float("-inf"), float("inf"), maximizing)
    elif alg == "minimax":
        minimax(root, maximizing)
    else:
        return
    min_hef = float("+inf")
    best_moves = []

    for child in root.children:
        if child.hef < min_hef:
            min_hef = child.hef
            best_moves = [child.move]
        elif child.hef == min_hef:
            best_moves.append(child.move)
    
    move = random.choice(best_moves)

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
    if node.state.player == 1:
        influence_5 = divisor5
    else:
        influence_5 = max(0, divisor5 - 1)
    result = 0
    if divisor5 == divisors:
        influence_5 = max(0, divisor5 - 1)
    result += ((influence_5 + divisors + bank + points) % 2) * 2
    result += ((divisors + bank + points) % 2)
    result += ((influence_5 + divisors_low_to_high + bank + points) % 2)
    result += ((divisors_low_to_high + bank + points) % 2) * 0.5

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