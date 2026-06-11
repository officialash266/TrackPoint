"""Admin-only account creation and deletion page."""

import sqlite3
import tkinter as tk
from tkinter import messagebox

from settings import (
    BG,
    CARD,
    DANGER,
    MAX_ID_DIGITS,
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MUTED,
    ROLES,
)
from validation import ValidationError, validate_value


class UsersPage:
    def __init__(self, app):
        self.app = app

    def show(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return

        self.app.activate("Users")
        self.app.clear_content()
        self.app.heading("User Management", "Create Admin, Staff and Student accounts.")

        layout = tk.Frame(self.app.content, bg=BG)
        layout.pack(fill="both", expand=True)
        form = self.app.card(
            layout,
            "Add User",
            "Student accounts must link to one competitor ID.",
        )
        form.pack(side="left", fill="y", padx=(0, 14))
        self.username_entry = self.app.entry_field(
            form, "Username", max_length=MAX_USERNAME_LENGTH
        )
        self.password_entry = self.app.entry_field(
            form, "Password", show="*", max_length=MAX_PASSWORD_LENGTH
        )
        self.role_var = self.app.combo_field(form, "Role", ROLES)
        self.link_entry = self.app.entry_field(
            form, "Competitor ID for Student", max_length=MAX_ID_DIGITS
        )
        tk.Label(
            form,
            text=(
                f"Username: 3–{MAX_USERNAME_LENGTH} characters\n"
                f"Password: {MIN_PASSWORD_LENGTH}–{MAX_PASSWORD_LENGTH} characters\n"
                "Leave Competitor ID blank for Admin or Staff."
            ),
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 8))
        buttons = tk.Frame(form, bg=CARD)
        buttons.pack(fill="x", padx=18, pady=(12, 18))
        self.app.button(buttons, "Add", self.add_user, width=10).pack(
            side="left", padx=(0, 8)
        )
        self.app.button(
            buttons, "Delete", self.delete_user, bg=DANGER, width=10
        ).pack(side="left")

        card = self.app.card(layout, "System Users", "Stored in the users SQL table.")
        card.pack(side="left", fill="both", expand=True)
        self.table = self.app.tree(
            card, ["ID", "Username", "Role", "Linked Student"], [80, 200, 120, 230]
        )
        self.refresh()
        self.app.set_status("User page loaded")

    def refresh(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for row in self.app.db.get_users():
            linked = ""
            if row["competitor_id"] is not None:
                linked = str(row["competitor_id"]) + " - " + str(row["name"])
            self.table.insert(
                "",
                tk.END,
                values=(row["user_id"], row["username"], row["role"], linked),
            )

    def add_user(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_var.get()
        link_text = self.link_entry.get().strip()
        competitor_id = None

        try:
            validate_value("username", username)
            validate_value("password", password)
            if role == "Student":
                competitor_id = validate_value("competitor_id", link_text)
            elif link_text != "":
                raise ValidationError(
                    "Competitor ID must be blank for Admin and Staff accounts."
                )
            self.app.db.add_user(username, password, role, competitor_id)
        except ValidationError as error:
            messagebox.showwarning("Invalid User", str(error))
            return
        except sqlite3.IntegrityError:
            messagebox.showwarning(
                "Duplicate Data",
                "That username or Student competitor link already exists.",
            )
            return

        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.link_entry.delete(0, tk.END)
        self.refresh()
        self.app.set_status("User account created")

    def delete_user(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return

        item_id = self.app.selected_id(self.table)
        if item_id is None:
            messagebox.showwarning("No Selection", "Select a user to delete.")
            return
        selected = self.table.item(self.table.selection()[0], "values")
        if selected[1] == "admin":
            messagebox.showwarning("Blocked", "The default admin account cannot be deleted.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete user " + str(item_id) + "?"):
            return
        self.app.db.delete_user(item_id)
        self.refresh()
        self.app.set_status("User deleted", DANGER)
