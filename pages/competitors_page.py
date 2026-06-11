"""Competitor registration, searching, editing and deletion page."""

import tkinter as tk
from tkinter import messagebox

from settings import (
    BG,
    CARD,
    CARD_2,
    DANGER,
    HOUSES,
    MAX_COMPETITOR_NAME_LENGTH,
    MAX_SEARCH_LENGTH,
    TEXT,
    WARNING,
    YEAR_GROUPS,
)
from validation import ValidationError, validate_value


class CompetitorsPage:
    """Manage competitor records for Admin and Staff users."""

    def __init__(self, app):
        self.app = app

    def show(self):
        if self.app.role not in ("Admin", "Staff"):
            messagebox.showerror("Permission Denied", "Admin or Staff access only.")
            return

        self.app.activate("Competitors")
        self.app.clear_content()
        self.app.heading("Competitors", "Register, search and maintain student records.")

        layout = tk.Frame(self.app.content, bg=BG)
        layout.pack(fill="both", expand=True)

        form = self.app.card(
            layout,
            "Competitor Details",
            "Select a table row to load it. Editing and deletion are Admin-only.",
        )
        form.pack(side="left", fill="y", padx=(0, 14))
        self.name_entry = self.app.entry_field(
            form, "Student Name", max_length=MAX_COMPETITOR_NAME_LENGTH
        )
        self.year_var = self.app.combo_field(form, "Year Group", YEAR_GROUPS)
        self.house_var = self.app.combo_field(form, "House", HOUSES)

        buttons = tk.Frame(form, bg=CARD)
        buttons.pack(fill="x", padx=18, pady=(12, 18))
        self.app.button(buttons, "Add", self.add_competitor, width=8).pack(
            side="left", padx=(0, 6)
        )
        if self.app.role == "Admin":
            self.app.button(
                buttons, "Update", self.update_competitor, bg=WARNING, width=8
            ).pack(side="left", padx=(0, 6))
            self.app.button(
                buttons, "Delete", self.delete_competitor, bg=DANGER, width=8
            ).pack(side="left")
        self.app.button(form, "Clear Form", self.clear_form, width=12).pack(
            anchor="w", padx=18, pady=(0, 18)
        )

        card = self.app.card(layout, "Competitor Records", "Search by ID, name, year or house.")
        card.pack(side="left", fill="both", expand=True)
        search_row = tk.Frame(card, bg=CARD)
        search_row.pack(fill="x", padx=18, pady=(8, 0))
        tk.Label(
            search_row, text="Search", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        self.search_entry = tk.Entry(
            search_row, bg=CARD_2, relief="solid", bd=1, font=("Segoe UI", 10)
        )
        self.app.limit_entry(self.search_entry, MAX_SEARCH_LENGTH)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=6)
        self.table = self.app.tree(
            card, ["ID", "Name", "Year", "House"], [90, 270, 110, 150]
        )
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh())
        self.table.bind("<<TreeviewSelect>>", self.load_selected)
        self.refresh()
        self.app.set_status("Competitor page loaded")

    def refresh(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            rows = self.app.db.get_competitors(self.search_entry.get().strip())
        except ValidationError as error:
            messagebox.showwarning("Invalid Search", str(error))
            return
        for row in rows:
            self.table.insert(
                "",
                tk.END,
                values=(row["competitor_id"], row["name"], row["year_group"], row["house"]),
            )

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.year_var.set(YEAR_GROUPS[0])
        self.house_var.set(HOUSES[0])
        for item in self.table.selection():
            self.table.selection_remove(item)
        self.name_entry.focus()

    def load_selected(self, event=None):
        selected = self.table.selection()
        if not selected:
            return
        values = self.table.item(selected[0], "values")
        if len(values) < 4:
            return
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.year_var.set(values[2])
        self.house_var.set(values[3])

    def _form_values(self):
        name = validate_value("competitor_name", self.name_entry.get())
        year_group = validate_value("year_group", self.year_var.get())
        house = validate_value("house", self.house_var.get())
        return name, year_group, house

    def add_competitor(self):
        if self.app.role not in ("Admin", "Staff"):
            messagebox.showerror("Permission Denied", "Admin or Staff access only.")
            return
        try:
            self.app.db.add_competitor(*self._form_values())
        except ValidationError as error:
            messagebox.showwarning("Invalid Competitor", str(error))
            return
        self.clear_form()
        self.refresh()
        self.app.set_status("Competitor added")

    def update_competitor(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return
        item_id = self.app.selected_id(self.table)
        if item_id is None:
            messagebox.showwarning("No Selection", "Select a competitor to update.")
            return
        try:
            self.app.db.update_competitor(item_id, *self._form_values())
        except ValidationError as error:
            messagebox.showwarning("Update Failed", str(error))
            return
        self.refresh()
        self.clear_form()
        self.app.set_status("Competitor updated", WARNING)

    def delete_competitor(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return
        item_id = self.app.selected_id(self.table)
        if item_id is None:
            messagebox.showwarning("No Selection", "Select a competitor to delete.")
            return
        warning = (
            "Delete competitor " + str(item_id) + "?\n\n"
            "Any results linked to this competitor will also be deleted. "
            "A competitor linked to a Student account cannot be deleted."
        )
        if not messagebox.askyesno("Confirm Delete", warning):
            return
        try:
            self.app.db.delete_competitor(item_id)
        except ValidationError as error:
            messagebox.showwarning("Delete Blocked", str(error))
            return
        self.refresh()
        self.clear_form()
        self.app.set_status("Competitor deleted", DANGER)
