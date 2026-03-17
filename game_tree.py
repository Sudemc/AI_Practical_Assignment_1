# required graphviz installed in python as well as in your system

from dataclasses import dataclass, field
from typing import List, Optional
from graphviz import Digraph
import uuid

DIVISORS = [2, 3, 4, 5]


@dataclass
class GameNode:
    number: int
    points: int
    bank: int
    player: int
    depth: int = 0
    move: Optional[int] = None
    children: List["GameNode"] = field(default_factory=list)
    terminal: bool = False
    winner: Optional[int] = None
    hef: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


def hef(node: "GameNode"):
    d = divisors_number(node.number)
    d5 = divisor5_number(node.number)
    d4 = divisor4_number(node.number)
    b = node.bank
    p = node.points

    if node.depth % 2 == 0:
        times_5_can_change = d5
    else:
        times_5_can_change = max(0, d5 - 1)

    times_4_can_change = d4
    
    return ((times_4_can_change + times_5_can_change + d + b + p) % 2 
           + (d + b + p) % 2
           + (times_5_can_change) % 2)


def apply_move(number, points, bank, divisor):
    new_number = number // divisor

    if new_number % 2 == 1:
        points += 1
    else:
        points -= 1

    if new_number % 10 == 0 or new_number % 10 == 5:
        bank += 1

    return new_number, points, bank


def finalize_score(points, bank):
    if points % 2 == 1:
        points -= bank
    else:
        points += bank
    return points


def determine_winner(points):
    return 1 if points % 2 == 1 else 2


def generate_tree(number, points=0, bank=0, player=1, depth=0):
    node = GameNode(number, points, bank, player, depth)

    node.hef = hef(node)

    valid_moves = [d for d in DIVISORS if number % d == 0]

    if not valid_moves:
        node.terminal = True
        final_points = finalize_score(points, bank)
        node.winner = determine_winner(final_points)
        return node

    next_player = 2 if player == 1 else 1

    for d in valid_moves:
        new_number, new_points, new_bank = apply_move(number, points, bank, d)
        child = generate_tree(new_number, new_points, new_bank, next_player, depth + 1)
        child.move = d
        node.children.append(child)

    return node


def add_to_graph(graph, node):
    label = (
        f"N={node.number}\n"
        f"P={node.points}\n"
        f"B={node.bank}\n"
        f"Pl={node.player}\n"
        f"H={node.hef}"
    )

    if node.terminal:
        color = "lightgreen" if node.winner == 1 else "lightblue"
        graph.node(node.id, label=label + f"\nWinner: P{node.winner}",
                   style="filled", fillcolor=color, shape="box")
    else:
        graph.node(node.id, label=label, shape="box")

    for child in node.children:
        add_to_graph(graph, child)
        graph.edge(node.id, child.id, label=f"/{child.move}")


def visualize_tree(root, filename="game_tree"):
    dot = Digraph(comment="Game Tree", format="png")
    dot.attr(rankdir="TB", size="100,100")

    add_to_graph(dot, root)

    dot.render(filename, view=True)
    print(f"Tree saved to {filename}.png")


def divisors_number(n):
    count = 0
    for d in [2, 3, 5]:
        while n % d == 0:
            n //= d
            count += 1
    return count


def divisor5_number(n):
    count = 0
    while n % 5 == 0:
        n //= 5
        count += 1
    return count


def divisor4_number(n):
    count = 0
    while n % 4 == 0:
        n //= 4
        count += 1
    return count


if __name__ == "__main__":
    start_number = 500

    tree = generate_tree(start_number)

    visualize_tree(tree, "game_tree")

    print("Divisors:", divisors_number(start_number))
    print("Divisor 5:", divisor5_number(start_number))
    print("Divisor 4:", divisor4_number(start_number))

    input()