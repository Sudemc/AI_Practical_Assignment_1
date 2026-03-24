from graphviz import Digraph
import AI


# ----------- Winner helpers (same logic as your game) -----------

def final_score(state):
    if state.points % 2 == 0:
        return state.points + state.bank
    else:
        return state.points - state.bank


def get_winner(state):
    score = final_score(state)
    return 1 if score % 2 == 1 else 2


# ----------- Graph building -----------

def add_to_graph(graph, node):
    s = node.state

    label = (
        f"N={s.number}\n"
        f"P={s.points}\n"
        f"B={s.bank}\n"
        f"Pl={s.player}\n"
        f"H={node.hef}"
    )

    # Terminal node styling
    if node.terminal:
        # Ensure winner is set
        if node.winner is None:
            node.winner = get_winner(s)

        if node.winner == 1:
            color = "lightgreen"
            winner_text = "Winner: P1"
        else:
            color = "lightblue"
            winner_text = "Winner: P2"

        graph.node(
            node.id,
            label=label + f"\n{winner_text}",
            style="filled",
            fillcolor=color,
            shape="box"
        )
    else:
        graph.node(node.id, label=label, shape="box")

    # Edges
    for child in node.children:
        add_to_graph(graph, child)
        graph.edge(node.id, child.id, label=f"/{child.move}")


# ----------- Visualization -----------

def visualize_tree(root, filename="game_tree"):
    dot = Digraph(comment="Game Tree", format="png")
    dot.attr(rankdir="TB", size="100000,10000")

    add_to_graph(dot, root)

    dot.render(filename, view=True)
    print(f"Tree saved to {filename}.png")


# ----------- Build tree using AI.py -----------

def build_tree_raw_hef(initial_number, depth=10):
    state = AI.GameState()
    state.number = initial_number
    state.points = 0
    state.bank = 0
    state.player = 1

    root = AI.generate_tree(state, depth)

    def assign_hef(node):
        node.hef = node.heuristic()
        for child in node.children:
            assign_hef(child)

    assign_hef(root)

    return root
def build_tree_alpha_beta(initial_number, depth=10):
    state = AI.GameState()
    state.number = initial_number
    state.points = 0
    state.bank = 0
    state.player = 1

    root = AI.generate_tree(state, depth)

    AI.alphabeta(root, float("-inf"), float("inf"), True)

    return root

def build_tree_minimax(initial_number, depth=10):
    state = AI.GameState()
    state.number = initial_number
    state.points = 0
    state.bank = 0
    state.player = 1

    root = AI.generate_tree(state, depth)

    AI.minimax(root, True)

    return root

# ----------- Main -----------

if __name__ == "__main__":
    start_number = 120

    tree = build_tree_minimax(start_number)

    visualize_tree(tree, "game_tree")

    input()