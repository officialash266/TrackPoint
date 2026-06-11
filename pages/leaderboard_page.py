import tkinter as tk
from tkinter import messagebox
from settings import *


class LeaderboardPage:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.activate("Leaderboard")
        self.app.clear_content()
        self.app.heading("Leaderboard", "Live house rankings from SQL result records.")

        card = self.app.card(self.app.content, "House Rankings", "Midson=blue, Darvall=red, Harris=yellow, Terry=green.")
        card.pack(fill="both", expand=True)
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=True, padx=18, pady=18)

        board = self.app.db.leaderboard()
        highest = 1
        for item in board:
            if item["points"] > highest:
                highest = item["points"]

        rank = 1
        for item in board:
            colour = HOUSE_COLOUR.get(item["house"], PRIMARY)
            row = tk.Frame(body, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
            row.pack(fill="x", pady=7)
            tk.Label(row, text="#" + str(rank), bg=CARD_2, fg=colour, font=("Segoe UI", 18, "bold"), width=5).pack(side="left", padx=(10, 4), pady=13)
            tk.Label(row, text=item["house"], bg=CARD_2, fg=TEXT, font=("Segoe UI", 15, "bold"), width=16, anchor="w").pack(side="left")
            canvas = tk.Canvas(row, height=12, bg=CARD_2, highlightthickness=0)
            canvas.pack(side="left", fill="x", expand=True, padx=16)
            full_width = 360
            percent = item["points"] / highest
            canvas.create_rectangle(0, 0, full_width, 12, fill="#e5e7eb", outline="")
            canvas.create_rectangle(0, 0, int(full_width * percent), 12, fill=colour, outline="")
            tk.Label(row, text=str(item["points"]) + " pts", bg=CARD_2, fg=TEXT, font=("Segoe UI", 14, "bold"), width=10).pack(side="right", padx=14)
            rank += 1

        buttons = tk.Frame(card, bg=CARD)
        buttons.pack(fill="x", padx=18, pady=(0, 18))
        self.app.button(buttons, "Refresh", self.show, width=12).pack(side="left", padx=(0, 8))
        if self.app.role != "Student":
            self.app.button(buttons, "Backup SQL", self.backup, width=13).pack(side="left")
        self.app.set_status("Leaderboard refreshed")

    def backup(self):
        if self.app.role not in ("Admin", "Staff"):
            messagebox.showerror("Permission Denied", "Admin or Staff access only.")
            return
        backup_path = self.app.db.backup()
        self.app.set_status("SQL backup created")
        messagebox.showinfo("Backup Complete", "Backup saved to:\n" + backup_path)
