import tkinter as tk
from tkinter import messagebox
from settings import *


class StudentPage:
    def __init__(self, app):
        self.app = app

    def show(self):
        if self.app.role != "Student":
            messagebox.showerror("Permission Denied", "Student access only.")
            return
        self.app.activate("Student Portal")
        self.app.clear_content()
        self.app.heading("Student Portal", "View your house, events, personal results and the live leaderboard.")

        competitor = self.app.db.get_competitor(self.app.student_competitor_id)
        if competitor is None:
            card = self.app.card(self.app.content, "No linked competitor", "Ask an admin to link this student login to a competitor record.")
            card.pack(fill="x")
            return

        top = tk.Frame(self.app.content, bg=BG)
        top.pack(fill="x", pady=(0, 16))
        self.info_card(top, "Student", competitor["name"], "Year " + competitor["year_group"]).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.info_card(top, "House", competitor["house"], "Carnival team", HOUSE_COLOUR.get(competitor["house"], PRIMARY)).pack(side="left", fill="x", expand=True, padx=10)
        self.info_card(top, "Events", len(self.app.db.get_events()), "Available events", SUCCESS).pack(side="left", fill="x", expand=True, padx=(10, 0))

        lower = tk.Frame(self.app.content, bg=BG)
        lower.pack(fill="both", expand=True)

        results_card = self.app.card(lower, "My Results", "Only results linked to your competitor record are shown.")
        results_card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        table = self.app.tree(results_card, ["Event", "Type", "Age", "Place", "Value", "Points"], [170, 80, 80, 80, 90, 80])
        for row in self.app.db.get_student_results(competitor["competitor_id"]):
            table.insert("", tk.END, values=(row["event_name"], row["event_type"], row["age_group"], row["placing"], row["result_value"], row["points_awarded"]))

        leaderboard_card = self.app.card(lower, "Leaderboard", "Current house points.")
        leaderboard_card.pack(side="left", fill="both", expand=True, padx=(12, 0))
        body = tk.Frame(leaderboard_card, bg=CARD)
        body.pack(fill="both", expand=True, padx=18, pady=18)
        rank = 1
        for item in self.app.db.leaderboard():
            colour = HOUSE_COLOUR.get(item["house"], PRIMARY)
            line = tk.Frame(body, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
            line.pack(fill="x", pady=6)
            tk.Label(line, text="#" + str(rank), bg=CARD_2, fg=colour, font=("Segoe UI", 16, "bold"), width=4).pack(side="left", padx=8, pady=10)
            tk.Label(line, text=item["house"], bg=CARD_2, fg=TEXT, font=("Segoe UI", 13, "bold"), width=12, anchor="w").pack(side="left")
            tk.Label(line, text=str(item["points"]) + " pts", bg=CARD_2, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(side="right", padx=12)
            rank += 1

        self.app.set_status("Student portal loaded")

    def info_card(self, parent, title, value, subtitle, colour=PRIMARY):
        frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(frame, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(frame, text=str(value), bg=CARD, fg=colour, font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=18)
        tk.Label(frame, text=subtitle, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(2, 16))
        return frame
