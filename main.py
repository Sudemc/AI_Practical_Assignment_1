import tkinter as tk
from tkinter import messagebox
import ctypes
import time
import random
from AI import Player, GameState, next_computer_move


DEPTH = 8

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass
class DivideGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Division Game")

        self.state = GameState()
        self.depth = DEPTH
        self.chosen_number = 0

        # GUI fields
        self.start_numbers_frame = None
        self.starting_numbers = [random.randint(30000, 50000) for n in range(5)]
        self.start_entry = None
        self.info_label = None
        self.info_turn_label = None
        self.buttons_frame = None
        self.ai_buttons_frame= None
        self.start_buttons_frame = None
        self.buttons = []

        # Interface startup
        self.start_numbers_frame = tk.Frame(root)
        self.start_numbers_frame.pack()
        for i in range(5):
            btn = tk.Button(self.start_numbers_frame, 
                            text=f"{self.starting_numbers[i]}",
                            command=lambda n=self.starting_numbers[i]: self.choose_starting_number(n))
            btn.pack(side=tk.LEFT, padx=5)

        self.start_buttons_frame = tk.Frame(root)
        self.start_buttons_frame.pack(pady=20)
        self.player_start_button = tk.Button(self.start_buttons_frame,
                                            text="Player start", 
                                            command=lambda: self.start_game(Player.MINIMIZER))
        self.player_start_button.pack(side=tk.LEFT, padx=10)
        self.computer_start_button = tk.Button(self.start_buttons_frame, 
                                               text="Computer start", 
                                               command=lambda: self.start_game(Player.MAXIMIZER))
        self.computer_start_button.pack(side=tk.LEFT, padx=10)
        self.player_start_button.config(state = "disabled")
        self.computer_start_button.config(state = "disabled")

        self.info_label = tk.Label(root, text="")
        self.info_label.pack()
        self.info_turn_label = tk.Label(root, text="")
        self.info_turn_label.pack()

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()

        for d in [2,3,4,5]:
            btn = tk.Button(self.buttons_frame,
                            text=f"Divide by {d}",
                            command=lambda x=d: self.make_move(x))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.buttons.append(btn)

        self.ai_buttons_frame = tk.Frame(root)
        self.ai_buttons_frame.pack(pady=20)  # space below top row, centered

        self.minimax_move_btn = tk.Button(
            self.ai_buttons_frame,
            text="Minimax",
            command=lambda: self.make_computer_move("minimax")
        )
        self.alphabeta_move_btn = tk.Button(
            self.ai_buttons_frame,
            text="Alpha-beta",
            command=lambda: self.make_computer_move("alphabeta")
        )

        self.minimax_move_btn.pack(side=tk.LEFT, padx=10)
        self.alphabeta_move_btn.pack(side=tk.LEFT, padx=10)
        self.minimax_move_btn.config(state = "disabled")
        self.alphabeta_move_btn.config(state= "disabled")
        
        for btn in self.buttons:
            btn.config(state="disabled")

    def choose_starting_number(self, starting_number: int):
        for btn in self.start_numbers_frame.winfo_children():
                btn.config(state = "disabled")
        for btn in self.start_buttons_frame.winfo_children():
            btn.config(state = "normal")
        self.state.number = starting_number
        
    def start_game(self, starting_player: Player):
        self.state.points = 0
        self.state.bank = 0
        self.state.starting_player = starting_player
        self.state.player = starting_player

        for btn in self.start_buttons_frame.winfo_children():
            btn.config(state = "disabled")

        divisors = [d for d in [2,3,4,5] if self.state.number % d == 0]
        if not divisors:
            self.end_game()
            return
        
        self.update_info()

    def update_info(self):
        if self.state.player == Player.MINIMIZER:
            player_str = "Player"
            color = "green"
        elif self.state.player == Player.MAXIMIZER:
            player_str = "Computer"
            color = "red"

        self.info_label.config(
            text=f"Current number: {self.state.number}\n"
                 f"Points: {self.state.points}\n"
                 f"Bank: {self.state.bank}\n"
        )
        
        self.info_turn_label.config(
            text=f"{player_str}'s turn",
            fg=color
        )
        if all(self.state.number % d != 0 for d in [2,3,4,5]):
            self.end_game()
            return

        # Disable impossible moves
        if self.state.player == Player.MINIMIZER:
            for i, d in enumerate([2,3,4,5]):
                if self.state.number % d == 0:
                    self.buttons[i].config(state="normal")
                else:
                    self.buttons[i].config(state="disabled")

            self.minimax_move_btn.config(state = "disabled")
            self.alphabeta_move_btn.config(state= "disabled")
        elif self.state.player == Player.MAXIMIZER:
            for btn in self.buttons:
                btn.config(state = "disabled")
            self.minimax_move_btn.config(state = "normal")
            self.alphabeta_move_btn.config(state= "normal")

    def make_move(self, divisor):
        self.state.number = self.state.number // divisor

        # Points rule
        if self.state.number % 2 == 1:
            self.state.points += 1
        else:
            self.state.points -= 1

        # Bank rule
        if str(self.state.number).endswith(("0", "5")):
            self.state.bank += 1

        # Switch player
        self.state.player = Player.MINIMIZER if self.state.player == Player.MAXIMIZER else Player.MAXIMIZER
        self.update_info()

    def make_computer_move(self, alg: str):
        start = time.perf_counter()
        div = next_computer_move(self.state, self.depth, alg)
        end = time.perf_counter()
        print(f"Computer move took {end - start:.6f} seconds. {alg} algorithm was used.\n")
        self.make_move(div)
        
    def end_game(self):
        # Bank adjustment
        if self.state.points % 2 == 0:
            self.state.points += self.state.bank
        else:
            self.state.points -= self.state.bank

        # Determine winner
        if self.state.points % 2 == 1:
            winner = "Player" if self.state.starting_player == Player.MINIMIZER else "Computer"
        else:
            winner = "Computer" if self.state.starting_player == Player.MINIMIZER else "Player"
        self.info_turn_label.config(text="")
        messagebox.showinfo("Game Over", f"Final points: {self.state.points}\nWinner: {winner}")
        self.info_label.config(text="")

        for b in self.buttons:
            b.config(state="disabled")
        for b in self.ai_buttons_frame.winfo_children():
            b.configure(state = "disabled")

        self.starting_numbers = [random.randint(30000, 50000) for n in range(5)]
        for i, btn in enumerate(self.start_numbers_frame.winfo_children()):
            btn.configure(text=str(self.starting_numbers[i]),
                          state = "normal",
                          command=lambda n=self.starting_numbers[i]: self.choose_starting_number(n))


root = tk.Tk()
game = DivideGame(root)
root.mainloop()