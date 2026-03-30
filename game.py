import tkinter as tk
from tkinter import messagebox
import ctypes
import time

import AI

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class GameState:
    def __init__(self):
        self.number = 0
        self.points = 0
        self.bank = 0
        self.player = 1
    
class DivideGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Division Game")

        self.state = GameState()
        self.depth = 10

        # GUI fields
        self.start_label = None
        self.start_entry = None
        self.start_button = None
        self.info_label = None
        self.info_turn_label = None
        self.buttons_frame = None
        self.buttons = []

        # Interface startup
        self.start_label = tk.Label(root, text="Enter starting number:")
        self.start_label.pack()

        self.start_entry = tk.Entry(root)
        self.start_entry.pack()

        self.start_button = tk.Button(root, text="Start Game", command=self.start_game)
        self.start_button.pack()

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
            text="Alphabeta",
            command=lambda: self.make_computer_move("alphabeta")
        )

        self.minimax_move_btn.pack(side=tk.LEFT, padx=10)
        self.alphabeta_move_btn.pack(side=tk.LEFT, padx=10)
        self.minimax_move_btn.config(state = "disabled")
        self.alphabeta_move_btn.config(state= "disabled")
        
        for btn in self.buttons:
            btn.config(state="disabled")

    def start_game(self):
        try:
            self.state.number = int(self.start_entry.get())
        except:
            messagebox.showerror("Error", "Enter a valid number")
            return

        self.state.points = 0
        self.state.bank = 0
        self.state.player = 1
        self.update_info()

    def update_info(self):
        if self.state.player == 1:
            player_str = "Player 1"
            color = "green"
        else:
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

        # Disable impossible moves
        if self.state.player == 1:
            for i, d in enumerate([2,3,4,5]):
                if self.state.number % d == 0:
                    self.buttons[i].config(state="normal")
                else:
                    self.buttons[i].config(state="disabled")

            self.minimax_move_btn.config(state = "disabled")
            self.alphabeta_move_btn.config(state= "disabled")
        else:
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
        self.state.player = 2 if self.state.player == 1 else 1
        self.update_info()

    def make_computer_move(self, alg: str):
        start = time.perf_counter()
        div = AI.next_computer_move(self.state, self.depth, alg)
        end = time.perf_counter()
        print(f"Computer move took {end - start:.6f} seconds. {alg} algorithm was used.")
        self.make_move(div)
        
    def end_game(self):
        # Bank adjustment
        if self.state.points % 2 == 0:
            self.state.points += self.state.bank
        else:
            self.state.points -= self.state.bank

        # Determine winner
        if self.state.points % 2 == 1:
            winner = "Player 1"
        else:
            winner = "Computer"

        messagebox.showinfo("Game Over", f"Final points: {self.state.points}\nWinner: {winner}")

        for b in self.buttons:
            b.config(state="disabled")


root = tk.Tk()
game = DivideGame(root)
root.mainloop()