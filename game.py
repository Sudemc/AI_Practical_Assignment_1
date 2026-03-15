import tkinter as tk
from tkinter import messagebox
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class DivideGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Division Game")

        # Game state fields
        self.number = 0
        self.points = 0
        self.bank = 0
        self.player = 1

        # GUI fields
        self.start_label = None
        self.start_entry = None
        self.start_button = None
        self.info_label = None
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

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()

        for d in [2,3,4,5]:
            btn = tk.Button(self.buttons_frame,
                            text=f"Divide by {d}",
                            command=lambda x=d: self.make_move(x))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.buttons.append(btn)

    def start_game(self):
        try:
            self.number = int(self.start_entry.get())
        except:
            messagebox.showerror("Error", "Enter a valid number")
            return

        self.points = 0
        self.bank = 0
        self.player = 1
        self.update_info()

    def update_info(self):
        self.info_label.config(
            text=f"Current number: {self.number}\n"
                 f"Points: {self.points}\n"
                 f"Bank: {self.bank}\n"
                 f"Player {self.player}'s turn"
        )

        # Disable impossible moves
        for i, d in enumerate([2,3,4,5]):
            if self.number % d == 0:
                self.buttons[i].config(state="normal")
            else:
                self.buttons[i].config(state="disabled")

        if all(self.number % d != 0 for d in [2,3,4,5]):
            self.end_game()

    def make_move(self, divisor):
        self.number = self.number // divisor

        # Points rule
        if self.number % 2 == 1:
            self.points += 1
        else:
            self.points -= 1

        # Bank rule
        if str(self.number).endswith(("0", "5")):
            self.bank += 1

        # Switch player
        self.player = 2 if self.player == 1 else 1
        self.update_info()

    def end_game(self):
        # Bank adjustment
        if self.points % 2 == 0:
            self.points += self.bank
        else:
            self.points -= self.bank

        # Determine winner
        if self.points % 2 == 1:
            winner = "Player 1 (Starter)"
        else:
            winner = "Player 2"

        messagebox.showinfo("Game Over", f"Final points: {self.points}\nWinner: {winner}")

        for b in self.buttons:
            b.config(state="disabled")


root = tk.Tk()
game = DivideGame(root)
root.mainloop()