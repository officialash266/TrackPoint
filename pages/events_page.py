"""Athletics event management and student event-viewing page."""

import tkinter as tk
from tkinter import messagebox

from settings import (
    BG,
    CARD,
    DANGER,
    EVENT_TYPES,
    MAX_AGE_GROUP_LENGTH,
    MAX_EVENT_NAME_LENGTH,
    WARNING,
)
from validation import ValidationError, validate_value


class EventsPage:
    """Create, edit, delete or view athletics events according to role."""

    def __init__(self, app):
        self.app = app

    def show(self):
        if self.app.role not in ("Admin", "Staff", "Student"):
            messagebox.showerror("Permission Denied", "You must be logged in to view events.")
            return

        self.app.activate("Events")
        self.app.clear_content()
        self.app.heading("Events", "Create or view Track and Field events.")

        layout = tk.Frame(self.app.content, bg=BG)
        layout.pack(fill="both", expand=True)

        if self.app.role != "Student":
            form = self.app.card(
                layout,
                "Event Details",
                "Select a table row to load it. Editing and deletion are Admin-only.",
            )
            form.pack(side="left", fill="y", padx=(0, 14))
            self.event_entry = self.app.entry_field(
                form, "Event Name", max_length=MAX_EVENT_NAME_LENGTH
            )
            self.type_var = self.app.combo_field(form, "Event Type", EVENT_TYPES)
            self.age_entry = self.app.entry_field(
                form, "Age Group", max_length=MAX_AGE_GROUP_LENGTH
            )
            self.age_entry.insert(0, "Open")
            buttons = tk.Frame(form, bg=CARD)
            buttons.pack(fill="x", padx=18, pady=(12, 18))
            self.app.button(buttons, "Add", self.add_event, width=8).pack(
                side="left", padx=(0, 6)
            )
            if self.app.role == "Admin":
                self.app.button(
                    buttons, "Update", self.update_event, bg=WARNING, width=8
                ).pack(side="left", padx=(0, 6))
                self.app.button(
                    buttons, "Delete", self.delete_event, bg=DANGER, width=8
                ).pack(side="left")
            self.app.button(form, "Clear Form", self.clear_form, width=12).pack(
                anchor="w", padx=18, pady=(0, 18)
            )

        card = self.app.card(
            layout,
            "Event Records",
            "Students can view events but cannot create, update or delete them.",
        )
        card.pack(side="left", fill="both", expand=True)
        self.table = self.app.tree(
            card, ["ID", "Event Name", "Type", "Age Group"], [90, 300, 130, 150]
        )
        if self.app.role != "Student":
            self.table.bind("<<TreeviewSelect>>", self.load_selected)
        self.refresh()
        self.app.set_status("Event page loaded")

    def refresh(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for row in self.app.db.get_events():
            self.table.insert(
                "",
                tk.END,
                values=(row["event_id"], row["event_name"], row["event_type"], row["age_group"]),
            )

    def clear_form(self):
        self.event_entry.delete(0, tk.END)
        self.type_var.set(EVENT_TYPES[0])
        self.age_entry.delete(0, tk.END)
        self.age_entry.insert(0, "Open")
        for item in self.table.selection():
            self.table.selection_remove(item)
        self.event_entry.focus()

    def load_selected(self, event=None):
        selected = self.table.selection()
        if not selected:
            return
        values = self.table.item(selected[0], "values")
        if len(values) < 4:
            return
        self.event_entry.delete(0, tk.END)
        self.event_entry.insert(0, values[1])
        self.type_var.set(values[2])
        self.age_entry.delete(0, tk.END)
        self.age_entry.insert(0, values[3])

    def _form_values(self):
        name = validate_value("event_name", self.event_entry.get())
        event_type = validate_value("event_type", self.type_var.get())
        age = validate_value("age_group", self.age_entry.get())
        return name, event_type, age

    def add_event(self):
        if self.app.role not in ("Admin", "Staff"):
            messagebox.showerror("Permission Denied", "Admin or Staff access only.")
            return
        try:
            self.app.db.add_event(*self._form_values())
        except ValidationError as error:
            messagebox.showwarning("Invalid Event", str(error))
            return
        self.refresh()
        self.clear_form()
        self.app.set_status("Event added")

    def update_event(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return
        item_id = self.app.selected_id(self.table)
        if item_id is None:
            messagebox.showwarning("No Selection", "Select an event to update.")
            return
        try:
            self.app.db.update_event(item_id, *self._form_values())
        except ValidationError as error:
            messagebox.showwarning("Update Failed", str(error))
            return
        self.refresh()
        self.clear_form()
        self.app.set_status("Event updated", WARNING)

    def delete_event(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return
        item_id = self.app.selected_id(self.table)
        if item_id is None:
            messagebox.showwarning("No Selection", "Select an event to delete.")
            return
        warning = (
            "Delete event " + str(item_id) + "?\n\n"
            "All results linked to this event will also be deleted."
        )
        if not messagebox.askyesno("Confirm Delete", warning):
            return
        self.app.db.delete_event(item_id)
        self.refresh()
        self.clear_form()
        self.app.set_status("Event deleted", DANGER)
