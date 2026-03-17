from dataclasses import dataclass, field
from typing import List, Optional
import uuid

DIVISORS = [2, 3, 4, 5]


@dataclass
class GameNode:
    number: int
    game_points: int
    bank: int
    depth: int
    move: Optional[int] = None
    children: List["GameNode"] = field(default_factory=list)
    terminal: bool = False
    winner: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())) #generates unique ids, needed for visualization lib
    
    def heuristic(self):
        return hef(self)

def apply_move(number, game_points, bank, divisor):
    new_number = number // divisor

    if new_number % 2 == 1:
        game_points += 1
    else:
        game_points -= 1

    if new_number % 10 == 0 or new_number % 10 == 5:
        bank += 1

    return new_number, game_points, bank


def generate_tree(number, game_points=0, bank=0, remaining_depth = 3, node_depth = 0):
    node = GameNode(number, game_points, bank, node_depth)

    valid_moves = [d for d in DIVISORS if number % d == 0]

    if not valid_moves:
        node.terminal = True
        return node
    
    if remaining_depth == 0:
        return node
    
    for d in valid_moves:
        new_number, new_points, new_bank = apply_move(number, game_points, bank, d)
        child = generate_tree(new_number, new_points, new_bank, remaining_depth-1, node_depth+1)
        child.move = d
        node.children.append(child)

    return node

def print_tree(node, indent=0):
    prefix = " " * indent
    
    print(f"{prefix}Node: number={node.number}, points={node.game_points}, bank={node.bank}, move={node.move}, heuristic={node.heuristic()}")

    for child in node.children:
        print_tree(child, indent + 8)

def hef(node: GameNode):
    d = divisors_number(node.number)
    d5 = divisor5_number(node.number)
    d4 = divisor4_number(node.number)
    b = node.bank
    p = node.game_points
    if node.depth % 2 == 0:
        times_5_can_change = d5
    else:
        times_5_can_change = max(0, d5 - 1)
    times_4_can_change = d4
    return ((times_4_can_change + times_5_can_change + d + b + p) % 2 
           + (d + b + p) % 2
           + (times_5_can_change) % 2)

def divisors_number(n):
    count = 0
    for d in [2, 3, 5]:
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

if __name__ == "__main__":
    start_number = 3000
    tree = generate_tree(start_number)
    print_tree(tree)
    input()