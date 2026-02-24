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
    move: Optional[int] = None
    children: List["GameNode"] = field(default_factory=list)
    terminal: bool = False
    winner: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())) #generates unique ids, needed for visualization lib


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


def generate_tree(number, points=0, bank=0, player=1):
    node = GameNode(number, points, bank, player)

    valid_moves = [d for d in DIVISORS if number % d == 0]

    if not valid_moves:
        node.terminal = True
        final_points = finalize_score(points, bank)
        node.winner = determine_winner(final_points)
        return node

    next_player = 2 if player == 1 else 1

    for d in valid_moves:
        new_number, new_points, new_bank = apply_move(number, points, bank, d)
        child = generate_tree(new_number, new_points, new_bank, next_player)
        child.move = d
        node.children.append(child)

    return node



def add_to_graph(graph, node):
    label = f"N={node.number}\nP={node.points}\nB={node.bank}\nPl={node.player}"

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



if __name__ == "__main__":
    start_number = 120
    tree = generate_tree(start_number)

    visualize_tree(tree, "game_tree")