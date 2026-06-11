"""Result entry, editing, validation and automatic points calculation page."""

import sqlite3
import tkinter as tk
from tkinter import messagebox

from settings import BG, CARD, DANGER, MAX_RESULT_VALUE_LENGTH, MUTED, WARNING
from validation import ValidationError, validate_value


class ResultsPage:
    """Manage event results for Admin and Staff users."""

    def __init__(self, app):
        self.app = app
        self.result_rows = {}

    def show(self):
        if self.app.role not in ("Admin", "Staff"):
            messagebox.showerror("Permission Denied", "Admin or Staff access only.")
            return

        self.app.activate("Results")
        self.app.clear_content()
        self.app.heading("Results", "Enter valid results and calculate house points.")

        self.competitors = self.app.db.get_competitors()
        self.events = self.app.db.get_events()
        if len(self.competitors) == 0 or len(self.events) == 0:
            card = self.app.card(
                self.app.content,
                "Setup Required",
                "Add at least one competitor and one event first.",
            )
            card.pack(fill="x")
            return

        layout = tk.Frame(self.app.content, bg=BG)
        layout.pack(fill="both", expand=True)
        form = self.app.card(
            layout,
            "Result Details",
            "Track uses seconds (s); Field uses metres (m). Select a row to edit.",
        )
        form.pack(side="left", fill="y", padx=(0, 14))

        self.event_values = [
            str(row["event_id"]) + " - " + row["event_name"] for row in self.events
        ]
        self.competitor_values = [
            str(row["competitor_id"]) + " - " + row["name"] for row in self.competitors
        ]
        self.event_var = self.app.combo_field(form, "Event", self.event_values)
        self.competitor_var = self.app.combo_field(form, "Competitor", self.competitor_values)
        self.placing_entry = self.app.entry_field(form, "Placing", max_length=1)
        self.result_entry = self.app.entry_field(
            form, "Result Value", max_length=MAX_RESULT_VALUE_LENGTH
        )
        tk.Label(
            form,
            text=(
                "Examples: 12.42 s or 5.80 m\n"
                "Points: 1st=8, 2nd=6, 3rd=4, 4th=2, 5th=1; 6th-8th=0"
            ),
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="left",
        ).pack(anchor="w", padx=18, pady=(2, 8))
        buttons = tk.Frame(form, bg=CARD)
        buttons.pack(fill="x", padx=18, pady=(12, 18))
        self.app.button(buttons, "Save", self.save_result, width=8).pack(
            side="left", padx=(0, 6)
        )
        if self.app.role == "Admin":
            self.app.button(
                buttons, "Update", self.update_result, bg=WARNING, width=8
            ).pack(side="left", padx=(0, 6))
            self.app.button(
                buttons, "Delete", self.delete_result, bg=DANGER, width=8
            ).pack(side="left")
        self.app.button(form, "Clear Form", self.clear_form, width=12).pack(
            anchor="w", padx=18, pady=(0, 18)
        )

        card = self.app.card(
            layout,
            "Saved Results",
            "Joined from the results, competitors and events SQL tables.",
        )
        card.pack(side="left", fill="both", expand=True)
        self.table = self.app.tree(
            card,
            ["ID", "Event", "Competitor", "House", "Place", "Value", "Points"],
            [70, 175, 175, 90, 65, 85, 70],
        )
        if self.app.role == "Admin":
            self.table.bind("<<TreeviewSelect>>", self.load_selected)
        self.refresh()
        self.app.set_status("Results page loaded")

    def refresh(self):
        for item in self.table.get_children():
            self.table.delete(item)
        rows = self.app.db.get_results()
        self.result_rows = {str(row["result_id"]): row for row in rows}
        for row in rows:
            self.table.insert(
                "",
                tk.END,
                values=(
                    row["result_id"], row["event_name"], row["name"], row["house"],
                    row["placing"], row["result_value"], row["points_awarded"],
                ),
            )

    def clear_form(self):
        self.event_var.set(self.event_values[0])
        self.competitor_var.set(self.competitor_values[0])
        self.placing_entry.delete(0, tk.END)
        self.result_entry.delete(0, tk.END)
        for item in self.table.selection():
            self.table.selection_remove(item)
        self.placing_entry.focus()

    def load_selected(self, event=None):
        result_id = self.app.selected_id(self.table)
        if result_id is None:
            return
        row = self.result_rows.get(str(result_id))
        if row is None:
            return
        event_text = next(
            (value for value in self.event_values if value.startswith(str(row["event_id"]) + " - ")),
            self.event_values[0],
        )
        competitor_text = next(
            (value for value in self.competitor_values if value.startswith(str(row["competitor_id"]) + " - ")),
            self.competitor_values[0],
        )
        self.event_var.set(event_text)
        self.competitor_var.set(competitor_text)
        self.placing_entry.delete(0, tk.END)
        self.placing_entry.insert(0, row["placing"])
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, row["result_value"])

    def _form_values(self):
        placing = validate_value("placing", self.placing_entry.get().strip())
        event_id = int(self.event_var.get().split(" - ")[0])
        competitor_id = int(self.competitor_var.get().split(" - ")[0])
        return event_id, competitor_id, placing, self.result_entry.get()

    def save_result(self):
        if self.app.role not in ("Admin", "Staff"):
            messagebox.showerror("Permission Denied", "Admin or Staff access only.")
            return
        try:
            self.app.db.add_result(*self._form_values())
        except ValidationError as error:
            messagebox.showwarning("Invalid Result", str(error))
            return
        except sqlite3.IntegrityError:
            messagebox.showwarning(
                "Duplicate Result", "This competitor already has a result for this event."
            )
            return
        self.clear_form()
        self.refresh()
        self.app.set_status("Result saved and points calculated")

    def update_result(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return
        result_id = self.app.selected_id(self.table)
        if result_id is None:
            messagebox.showwarning("No Selection", "Select a result to update.")
            return
        try:
            self.app.db.update_result(result_id, *self._form_values())
        except ValidationError as error:
            messagebox.showwarning("Update Failed", str(error))
            return
        except sqlite3.IntegrityError:
            messagebox.showwarning(
                "Duplicate Result", "That competitor already has another result for this event."
            )
            return
        self.refresh()
        self.clear_form()
        self.app.set_status("Result updated and points recalculated", WARNING)

    def delete_result(self):
        if self.app.role != "Admin":
            messagebox.showerror("Permission Denied", "Admin access only.")
            return
        item_id = self.app.selected_id(self.table)
        if item_id is None:
            messagebox.showwarning("No Selection", "Select a result to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete result " + str(item_id) + "?"):
            return
        self.app.db.delete_result(item_id)
        self.refresh()
        self.clear_form()
        self.app.set_status("Result deleted", DANGER)
