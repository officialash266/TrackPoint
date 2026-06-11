"""Integrated help and tutorial page available to every authenticated user."""

import tkinter as tk
from tkinter import messagebox

from settings import BG, CARD, MUTED, PRIMARY, TEXT


class HelpPage:
    """Display role-aware instructions for the completed TrackPoint program."""

    def __init__(self, app):
        self.app = app

    def show(self):
        if self.app.role not in ("Admin", "Staff", "Student"):
            messagebox.showerror("Permission Denied", "You must be logged in to view Help.")
            return

        self.app.activate("Help")
        self.app.clear_content()
        self.app.heading("Help and Tutorial", "Instructions for using TrackPoint safely and correctly.")

        outer = tk.Frame(self.app.content, bg=BG)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=BG)
        body.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.section(
            body,
            "Quick start - where to go next",
            "TrackPoint uses the left sidebar rather than a separate Settings menu. For a new carnival, follow this order: "
            "1) add or check Competitors, 2) create Events, 3) enter Results, 4) open Leaderboard and select Refresh, "
            "and 5) create a Backup SQL file. Admin users can also manage accounts from Users.",
            accent=True,
        )
        self.section(
            body,
            "1. Login and roles",
            "Use an authorised username and password. Admin users have full management access. "
            "Staff users can add competitors, events and results but cannot manage users, edit or delete records. "
            "Student users have view-only access to their linked profile, events and leaderboard.",
        )
        self.section(
            body,
            "2. Competitors",
            "Open Competitors to register a student. Enter a name using letters and spaces, select Year 7-12, "
            "and select Midson, Darvall, Harris or Terry. Use Search to filter records. Admin users may select a row, "
            "change the form values and choose Update, or choose Delete after confirmation.",
        )
        self.section(
            body,
            "3. Events",
            "Open Events to create Track or Field events. Event names may be up to 40 characters. Age groups can be "
            "values such as Open, U14, U16 or Year 12. Admin users can update or delete selected events. Changing an "
            "event between Track and Field is blocked while results are linked because the measurement unit would become invalid.",
        )
        self.section(
            body,
            "4. Results and points",
            "Choose an event and competitor, enter a placing from 1 to 8, then enter a measured result. Track events "
            "must use seconds, for example 12.42 s. Field events must use metres, for example 5.80 m. Points are "
            "calculated automatically: 1st=8, 2nd=6, 3rd=4, 4th=2, 5th=1, and 6th-8th=0. A competitor can only "
            "have one result for each event. Admin users can update or delete a selected result.",
        )
        self.section(
            body,
            "5. Leaderboard and backup",
            "The Leaderboard totals points by joining result and competitor records, then ranks all four houses from "
            "highest to lowest. Select Refresh after changes. Admin and Staff users can select Backup SQL to create "
            "data\\backup.sql, which contains the SQL commands needed to recreate the database.",
        )
        self.section(
            body,
            "6. User Management (Admin)",
            "Create Admin, Staff or Student accounts from Users. Student accounts must link to an existing competitor ID. "
            "Admin and Staff accounts must leave Competitor ID blank. Passwords are stored as SHA-256 hashes, not plaintext. "
            "The default admin account cannot be deleted.",
        )
        self.section(
            body,
            "7. Student Portal",
            "A Student login displays only the competitor profile linked to that account, personal results, the number of "
            "available events and the live house standings. Students are not shown add, update or delete controls.",
        )
        self.section(
            body,
            "8. Common warnings",
            "Incorrect login: re-enter the supplied credentials. Invalid unit: use s for Track or m for Field. Duplicate result: "
            "the selected competitor already has a result for that event. Delete blocked: remove a linked Student account before "
            "deleting its competitor. No selection: click a table row before Update or Delete.",
        )
        self.section(
            body,
            "Demonstration accounts",
            "Admin: admin / admin123\nStaff: staff / staff123\nStudent: student / student123",
            accent=True,
        )
        self.app.set_status("Help page loaded")

    def section(self, parent, title, text, accent=False):
        card = tk.Frame(parent, bg=CARD, highlightbackground="#d1d5db", highlightthickness=1)
        card.pack(fill="x", padx=(0, 12), pady=(0, 12))
        tk.Label(
            card,
            text=title,
            bg=CARD,
            fg=PRIMARY if accent else TEXT,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=18, pady=(14, 5))
        tk.Label(
            card,
            text=text,
            bg=CARD,
            fg=TEXT if accent else MUTED,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=850,
        ).pack(anchor="w", padx=18, pady=(0, 16))
