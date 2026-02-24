"""
Game Tree - Minimax & Alpha-Beta Pruning
=========================================
Implements game tree generation, heuristic evaluation,
minimax and alpha-beta pruning algorithms for a number
division game.

Structures used: dataclasses (standard Python)
Visualization:   graphviz (optional)
"""

from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import math

# ============================================================
# CONSTANTS
# ============================================================

DIVISORS = [2, 3, 4, 5]           # Valid divisors
DEFAULT_MAX_DEPTH = 6             # Default depth limit


# ============================================================
# DATA STRUCTURE - GameNode
# ============================================================

@dataclass
class GameNode:
    """Represents a single node in the game tree.

    Attributes:
        number:   Current number value.
        points:   Total accumulated points so far.
        bank:     Bank points (increases on numbers ending with 5 or 0).
        player:   Current player (1 = Computer, 2 = Human).
        depth:    Depth of this node in the tree (root = 0).
        move:     The divisor used to reach this node.
        children: List of child nodes.
        terminal: Whether the game ended at this node (no valid moves left).
        winner:   Winning player (only meaningful for terminal nodes).
        id:       Unique identifier for visualization.
    """
    number: int
    points: int
    bank: int
    player: int
    depth: int = 0
    move: Optional[int] = None
    children: List["GameNode"] = field(default_factory=list)
    terminal: bool = False
    winner: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def apply_move(number: int, points: int, bank: int, divisor: int):
    """Applies a division move and returns the new state.

    Rules:
        - The number is divided by the divisor (integer division).
        - If the result is odd, points +1; if even, points -1.
        - If the result's last digit is 0 or 5, bank +1.

    Returns:
        (new_number, new_points, new_bank) tuple.
    """
    new_number = number // divisor

    # Odd result -> gain a point, even result -> lose a point
    if new_number % 2 == 1:
        points += 1
    else:
        points -= 1

    # Last digit is 0 or 5 -> bank increases
    if new_number % 10 == 0 or new_number % 10 == 5:
        bank += 1

    return new_number, points, bank


def finalize_score(points: int, bank: int) -> int:
    """Applies the bank to the total points at the end of the game.

    Rule:
        - If points is odd, subtract bank.
        - If points is even, add bank.
    """
    if points % 2 == 1:
        points -= bank
    else:
        points += bank
    return points


def determine_winner(final_points: int) -> int:
    """Determines the winner based on the final points.

    Returns:
        1 -> Computer wins (points is odd).
        2 -> Human wins (points is even).
    """
    return 1 if final_points % 2 == 1 else 2


# ============================================================
# TREE GENERATION - N-ply Look Ahead
# ============================================================

def generate_tree(number: int, points: int = 0, bank: int = 0,
                  player: int = 1, depth: int = 0,
                  max_depth: int = None) -> GameNode:
    """Recursively generates the game tree.

    Args:
        number:    Current number.
        points:    Current points.
        bank:      Current bank.
        player:    Current player (1 or 2).
        depth:     Current depth (root = 0).
        max_depth: Maximum depth limit. None means unlimited.

    Returns:
        Root GameNode with the entire subtree attached.
    """
    node = GameNode(number, points, bank, player, depth=depth)

    # Find valid moves
    valid_moves = [d for d in DIVISORS if number % d == 0]

    # --- Case 1: No valid moves -> game over (terminal) ---
    if not valid_moves:
        node.terminal = True
        final_points = finalize_score(points, bank)
        node.winner = determine_winner(final_points)
        return node

    # --- Case 2: Depth limit reached -> leaf node ---
    if max_depth is not None and depth >= max_depth:
        # terminal=False stays, children remains empty.
        # This node will be evaluated by the heuristic in minimax/alpha-beta.
        return node

    # --- Case 3: Normal expansion ---
    next_player = 2 if player == 1 else 1

    for d in valid_moves:
        new_number, new_points, new_bank = apply_move(number, points, bank, d)
        child = generate_tree(
            new_number, new_points, new_bank,
            next_player, depth + 1, max_depth
        )
        child.move = d
        node.children.append(child)

    return node


# ============================================================
# HEURISTIC EVALUATION
# ============================================================

def evaluate_node(node: GameNode) -> float:
    """Calculates a heuristic score for a non-terminal leaf node.

    Evaluates from the Computer's (Player 1) perspective:
        - Positive score -> favorable for Computer.
        - Negative score -> favorable for Human.

    Components:
        1. Point effect: Estimated final score and winning tendency.
        2. Bank effect:  Potential contribution of bank to points.
        3. Number parity: Odd/even nature of the current number.

    Returns:
        float: Heuristic evaluation score.
    """
    # Estimate the final points
    estimated_final = finalize_score(node.points, node.bank)

    # Component 1: Point status
    # Odd points -> Computer wins (+), even points -> Human wins (-)
    if estimated_final % 2 == 1:
        score = float(estimated_final)        # Favorable for Computer
    else:
        score = -float(estimated_final)       # Favorable for Human

    # Component 2: Bank effect
    # Higher bank -> greater impact on the outcome
    score += 0.5 * node.bank

    # Component 3: Number parity
    # Odd number -> higher chance of odd result in next division
    if node.number % 2 == 1:
        score += 0.5       # Odd number is advantageous
    else:
        score -= 0.5       # Even number is disadvantageous

    return score


# ============================================================
# MINIMAX ALGORITHM
# ============================================================

def minimax(node: GameNode, depth: int, max_depth: int,
            is_maximizing: bool, counter: dict) -> float:
    """Computes the best score using the Minimax algorithm.

    Args:
        node:           The node to evaluate.
        depth:          Current search depth.
        max_depth:      Maximum search depth.
        is_maximizing:  True for Computer (max), False for Human (min).
        counter:        {"count": 0} -> tracks the number of visited nodes.

    Returns:
        float: Minimax value of the node.
    """
    # Increment node counter
    counter["count"] += 1

    # --- Base case: terminal node ---
    if node.terminal:
        final_points = finalize_score(node.points, node.bank)
        winner = determine_winner(final_points)
        # Computer wins -> +100, loses -> -100
        return 100.0 if winner == 1 else -100.0

    # --- Base case: leaf node (depth limit reached) ---
    if not node.children:
        return evaluate_node(node)

    # --- Recursive case ---
    if is_maximizing:
        best_value = -math.inf
        for child in node.children:
            value = minimax(child, depth + 1, max_depth, False, counter)
            best_value = max(best_value, value)
        return best_value
    else:
        best_value = math.inf
        for child in node.children:
            value = minimax(child, depth + 1, max_depth, True, counter)
            best_value = min(best_value, value)
        return best_value


# ============================================================
# ALPHA-BETA PRUNING ALGORITHM
# ============================================================

def alpha_beta(node: GameNode, depth: int, max_depth: int,
               alpha: float, beta: float,
               is_maximizing: bool, counter: dict) -> float:
    """Computes the best score using Alpha-Beta pruning.

    Produces the same result as Minimax but prunes unnecessary
    branches to reduce the number of visited nodes.

    Args:
        node:           The node to evaluate.
        depth:          Current search depth.
        max_depth:      Maximum search depth.
        alpha:          Best MAX score so far (initial: -inf).
        beta:           Best MIN score so far (initial: +inf).
        is_maximizing:  True for Computer (max), False for Human (min).
        counter:        {"count": 0} -> tracks the number of visited nodes.

    Returns:
        float: Alpha-beta value of the node.
    """
    # Increment node counter
    counter["count"] += 1

    # --- Base case: terminal node ---
    if node.terminal:
        final_points = finalize_score(node.points, node.bank)
        winner = determine_winner(final_points)
        return 100.0 if winner == 1 else -100.0

    # --- Base case: leaf node (depth limit reached) ---
    if not node.children:
        return evaluate_node(node)

    # --- Recursive case ---
    if is_maximizing:
        best_value = -math.inf
        for child in node.children:
            value = alpha_beta(child, depth + 1, max_depth,
                               alpha, beta, False, counter)
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
            # Pruning: if beta <= alpha, no need to explore this branch
            if beta <= alpha:
                break
        return best_value
    else:
        best_value = math.inf
        for child in node.children:
            value = alpha_beta(child, depth + 1, max_depth,
                               alpha, beta, True, counter)
            best_value = min(best_value, value)
            beta = min(beta, best_value)
            # Pruning: if beta <= alpha, no need to explore this branch
            if beta <= alpha:
                break
        return best_value


# ============================================================
# GAME CONTROLLER - GUI Compatible
# ============================================================

class GameController:
    """Controller class for connecting game logic to a GUI.

    Usage:
        controller = GameController(start_number=120, max_depth=6)
        controller.start_game()
        best_move = controller.get_best_move()
        controller.make_move(best_move)
    """

    def __init__(self, start_number: int, max_depth: int = DEFAULT_MAX_DEPTH,
                 algorithm: str = "alpha_beta"):
        """
        Args:
            start_number: Starting number for the game.
            max_depth:    Search depth limit.
            algorithm:    "minimax" or "alpha_beta".
        """
        self.start_number = start_number
        self.max_depth = max_depth
        self.algorithm = algorithm          # "minimax" or "alpha_beta"

        # Game state
        self.current_number = start_number
        self.current_points = 0
        self.current_bank = 0
        self.current_player = 1             # 1 = Computer, 2 = Human
        self.game_over = False
        self.winner = None

        # Statistics
        self.last_node_count = 0
        self.last_best_score = 0.0

    def start_game(self):
        """Starts the game. Resets the state."""
        self.current_number = self.start_number
        self.current_points = 0
        self.current_bank = 0
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_node_count = 0
        self.last_best_score = 0.0

    def get_valid_moves(self) -> List[int]:
        """Returns valid moves for the current number."""
        return [d for d in DIVISORS if self.current_number % d == 0]

    def get_best_move(self) -> Optional[int]:
        """Runs the selected algorithm and finds the best move.

        Returns:
            Best divisor (int) or None (if no valid moves).
        """
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None

        # Build the tree
        tree = generate_tree(
            self.current_number, self.current_points, self.current_bank,
            self.current_player, depth=0, max_depth=self.max_depth
        )

        # Run the algorithm
        counter = {"count": 0}
        best_move = None
        best_value = -math.inf

        for child in tree.children:
            if self.algorithm == "minimax":
                value = minimax(child, 1, self.max_depth, False, counter)
            else:  # alpha_beta
                value = alpha_beta(child, 1, self.max_depth,
                                   -math.inf, math.inf, False, counter)

            if value > best_value:
                best_value = value
                best_move = child.move

        # Save statistics
        self.last_node_count = counter["count"]
        self.last_best_score = best_value

        return best_move

    def make_move(self, divisor: int) -> bool:
        """Applies a move (for either computer or human).

        Args:
            divisor: The divisor to apply.

        Returns:
            True -> move successful, False -> invalid move.
        """
        if self.game_over:
            return False

        if self.current_number % divisor != 0:
            return False

        # Apply the move
        self.current_number, self.current_points, self.current_bank = \
            apply_move(self.current_number, self.current_points,
                       self.current_bank, divisor)

        # Switch player
        self.current_player = 2 if self.current_player == 1 else 1

        # Check if game is over
        if not self.get_valid_moves():
            self.game_over = True
            final = finalize_score(self.current_points, self.current_bank)
            self.winner = determine_winner(final)

        return True

    def get_stats(self) -> dict:
        """Returns statistics from the last algorithm run.

        Returns:
            dict: {
                "algorithm": str,
                "node_count": int,
                "best_score": float,
                "max_depth": int
            }
        """
        return {
            "algorithm": self.algorithm,
            "node_count": self.last_node_count,
            "best_score": self.last_best_score,
            "max_depth": self.max_depth,
        }

    def is_game_over(self) -> bool:
        """Returns whether the game is over."""
        return self.game_over

    def get_state(self) -> dict:
        """Returns the current game state (useful for GUI).

        Returns:
            dict: Number, points, bank, player, game status.
        """
        return {
            "number": self.current_number,
            "points": self.current_points,
            "bank": self.current_bank,
            "player": self.current_player,
            "game_over": self.game_over,
            "winner": self.winner,
        }


# ============================================================
# VISUALIZATION (Optional - requires graphviz)
# ============================================================

def add_to_graph(graph, node):
    """Adds a node to the graphviz graph (recursive)."""
    label = (f"N={node.number}\nP={node.points}"
             f"\nB={node.bank}\nPl={node.player}")

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
    """Saves the tree as a PNG and opens it."""
    try:
        from graphviz import Digraph
    except ImportError:
        print("graphviz library is not installed. Skipping visualization.")
        return

    dot = Digraph(comment="Game Tree", format="png")
    dot.attr(rankdir="TB", size="100,100")
    add_to_graph(dot, root)
    dot.render(filename, view=True)
    print(f"Tree saved to {filename}.png")


# ============================================================
# COMPARISON FUNCTION
# ============================================================

def compare_algorithms(start_number: int, max_depth: int = DEFAULT_MAX_DEPTH):
    """Compares Minimax and Alpha-Beta algorithms.

    Runs both algorithms on the same tree and compares:
        - Whether they produce the same result.
        - The number of nodes visited by each.
    """
    print(f"\n{'='*50}")
    print(f"ALGORITHM COMPARISON")
    print(f"Start number: {start_number}, Depth: {max_depth}")
    print(f"{'='*50}")

    # Build the tree
    tree = generate_tree(start_number, max_depth=max_depth)

    # --- Minimax ---
    mm_counter = {"count": 0}
    mm_best_move = None
    mm_best_value = -math.inf

    for child in tree.children:
        value = minimax(child, 1, max_depth, False, mm_counter)
        if value > mm_best_value:
            mm_best_value = value
            mm_best_move = child.move

    # --- Alpha-Beta ---
    ab_counter = {"count": 0}
    ab_best_move = None
    ab_best_value = -math.inf

    for child in tree.children:
        value = alpha_beta(child, 1, max_depth,
                           -math.inf, math.inf, False, ab_counter)
        if value > ab_best_value:
            ab_best_value = value
            ab_best_move = child.move

    # --- Print results ---
    print(f"\n--- Minimax ---")
    print(f"  Best move      : /{mm_best_move}")
    print(f"  Best score     : {mm_best_value}")
    print(f"  Nodes visited  : {mm_counter['count']}")

    print(f"\n--- Alpha-Beta ---")
    print(f"  Best move      : /{ab_best_move}")
    print(f"  Best score     : {ab_best_value}")
    print(f"  Nodes visited  : {ab_counter['count']}")

    # Pruning ratio
    if mm_counter["count"] > 0:
        pruned = mm_counter["count"] - ab_counter["count"]
        ratio = (pruned / mm_counter["count"]) * 100
        print(f"\n--- Pruning Gain ---")
        print(f"  Pruned nodes   : {pruned}")
        print(f"  Gain ratio     : {ratio:.1f}%")

    print(f"{'='*50}\n")


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":
    start_number = 120

    # --- Demo 1: GameController usage ---
    print("=== GameController Demo ===\n")

    controller = GameController(
        start_number=start_number,
        max_depth=6,
        algorithm="alpha_beta"
    )
    controller.start_game()

    state = controller.get_state()
    print(f"Initial state: Number={state['number']}, "
          f"Points={state['points']}, Bank={state['bank']}")

    best = controller.get_best_move()
    stats = controller.get_stats()
    print(f"Best move: /{best}")
    print(f"Algorithm: {stats['algorithm']}")
    print(f"Nodes visited: {stats['node_count']}")
    print(f"Depth: {stats['max_depth']}")

    # --- Demo 2: Comparison at different depths ---
    for depth in [3, 6, 10]:
        compare_algorithms(start_number, max_depth=depth)
