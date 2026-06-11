"""Login and authentication page."""

import tkinter as tk
from tkinter import messagebox

from settings import (
    BG,
    CARD,
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MUTED,
    NAV,
    NAV_2,
    TEXT,
)
from validation import ValidationError, validate_value


class LoginPage:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_window()
        self.app.user = None
        self.app.role = None
        self.app.student_competitor_id = None

        main = tk.Frame(self.app.root, bg=BG)
        main.pack(fill="both", expand=True)

        hero = tk.Frame(main, bg=NAV, width=500)
        hero.pack(side="left", fill="y")
        hero.pack_propagate(False)

        tk.Label(hero, text="TrackPoint", bg=NAV, fg="white", font=("Segoe UI", 40, "bold")).pack(
            anchor="w", padx=54, pady=(92, 8)
        )
        tk.Label(
            hero,
            text="EBHS Athletics Management System",
            bg=NAV,
            fg="#cbd5e1",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", padx=58)
        tk.Label(
            hero,
            text="Manage competitors, events, results and live house rankings using an SQL database.",
            bg=NAV,
            fg="#cbd5e1",
            font=("Segoe UI", 12),
            wraplength=360,
            justify="left",
        ).pack(anchor="w", padx=58, pady=(8, 0))

        box = tk.Frame(hero, bg=NAV_2, highlightbackground="#334155", highlightthickness=1)
        box.pack(anchor="w", padx=54, pady=42, fill="x")
        features = [
            "Secure login",
            "Admin, staff and student roles",
            "Student result viewing",
            "SQLite database",
            "SQL backup",
        ]
        for feature in features:
            tk.Label(box, text="✓  " + feature, bg=NAV_2, fg="white", font=("Segoe UI", 12)).pack(
                anchor="w", padx=22, pady=9
            )

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        panel = tk.Frame(right, bg=CARD, highlightbackground="#d1d5db", highlightthickness=1)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=460, height=430)

        tk.Label(panel, text="Welcome back", bg=CARD, fg=TEXT, font=("Segoe UI", 28, "bold")).pack(
            anchor="w", padx=36, pady=(36, 2)
        )
        tk.Label(
            panel,
            text="Sign in with an authorised TrackPoint account.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(anchor="w", padx=38, pady=(0, 18))

        self.username_entry = self.app.entry_field(
            panel, "Username", max_length=MAX_USERNAME_LENGTH
        )
        self.password_entry = self.app.entry_field(
            panel, "Password", show="*", max_length=MAX_PASSWORD_LENGTH
        )
        self.app.button(panel, "Login", self.login).pack(fill="x", padx=38, pady=(14, 10))

        tk.Label(
            panel,
            text="Usernames are 3–20 characters. Passwords are 6–20 characters.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=38)
        self.username_entry.focus()
        self.app.root.bind("<Return>", self.login_enter)

    def login_enter(self, event):
        self.login()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        try:
            validate_value("username", username)
            validate_value("password", password)
        except ValidationError as error:
            messagebox.showwarning("Invalid Login Details", str(error))
            return

        user = self.app.db.check_login(username, password)
        if user is None:
            messagebox.showerror("Login Failed", "Incorrect username or password.")
            return

        self.app.root.unbind("<Return>")
        self.app.login_success(user["username"], user["role"], user["competitor_id"])
