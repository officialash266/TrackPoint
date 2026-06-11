import tkinter as tk
from tkinter import messagebox
from settings import *


class DashboardPage:
    def __init__(self, app):
        self.app = app

    def show(self):
        if self.app.role not in ("Admin", "Staff"):
            messagebox.showerror("Permission Denied", "Admin or Staff access only.")
            return
        self.app.activate("Dashboard")
        self.app.clear_content()
        self.app.heading("Dashboard", "Overview of TrackPoint carnival data.")

        competitors = self.app.db.get_competitors()
        events = self.app.db.get_events()
        results = self.app.db.get_results()
        board = self.app.db.leaderboard()
        leading = "None"
        if len(board) > 0 and board[0]["points"] > 0:
            leading = board[0]["house"]

        row = tk.Frame(self.app.content, bg=BG)
        row.pack(fill="x", pady=(0, 18))
        self.stat(row, "Competitors", len(competitors), "registered students", PRIMARY).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.stat(row, "Events", len(events), "available events", SUCCESS).pack(side="left", fill="x", expand=True, padx=10)
        self.stat(row, "Results", len(results), "saved results", WARNING).pack(side="left", fill="x", expand=True, padx=10)
        self.stat(row, "Leading House", leading, "current rank 1", DANGER).pack(side="left", fill="x", expand=True, padx=(10, 0))

        quick = self.app.card(
            self.app.content,
            "Quick Start",
            "Recommended workflow for a new carnival.",
        )
        quick.pack(fill="x", pady=(0, 14))
        tk.Label(
            quick,
            text=(
                "Use the left sidebar in this order: Competitors -> Events -> Results -> Leaderboard. "
                "Select Help at any time for step-by-step instructions. TrackPoint does not require a separate Settings menu."
            ),
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=850,
        ).pack(anchor="w", padx=18, pady=(0, 10))
        quick_actions = tk.Frame(quick, bg=CARD)
        quick_actions.pack(fill="x", padx=18, pady=(0, 14))
        self.app.button(quick_actions, "Open Help", self.app.show_help, width=12).pack(side="left")

        card = self.app.card(self.app.content, "Leaderboard Preview", "Scores are calculated from the SQL results table.")
        card.pack(fill="both", expand=True)
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=True, padx=18, pady=18)

        rank = 1
        for item in board:
            colour = HOUSE_COLOUR.get(item["house"], PRIMARY)
            line = tk.Frame(body, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
            line.pack(fill="x", pady=7)
            tk.Label(line, text="#" + str(rank), bg=CARD_2, fg=colour, font=("Segoe UI", 18, "bold"), width=5).pack(side="left", padx=10, pady=13)
            tk.Label(line, text=item["house"], bg=CARD_2, fg=TEXT, font=("Segoe UI", 15, "bold"), width=16, anchor="w").pack(side="left")
            tk.Label(line, text=str(item["points"]) + " pts", bg=CARD_2, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(side="right", padx=18)
            rank += 1

        self.app.set_status("Dashboard loaded")

    def stat(self, parent, title, value, subtitle, colour):
        frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(frame, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(frame, text=str(value), bg=CARD, fg=colour, font=("Segoe UI", 25, "bold")).pack(anchor="w", padx=18)
        tk.Label(frame, text=subtitle, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(2, 16))
        return frame
