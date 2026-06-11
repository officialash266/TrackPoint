import tkinter as tk
from tkinter import ttk
from database import Database
from settings import *
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.competitors_page import CompetitorsPage
from pages.events_page import EventsPage
from pages.results_page import ResultsPage
from pages.leaderboard_page import LeaderboardPage
from pages.users_page import UsersPage
from pages.student_page import StudentPage
from pages.help_page import HelpPage


class TrackPointApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1280x760")
        self.root.minsize(1100, 680)
        self.root.configure(bg=BG)
        self.db = Database()
        self.user = None
        self.role = None
        self.student_competitor_id = None
        self.content = None
        self.status = None
        self.nav_buttons = {}
        self.setup_style()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.show_login()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=32, background=CARD, fieldbackground=CARD)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=NAV, foreground="white")
        style.map("Treeview", background=[("selected", PRIMARY)])

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def set_status(self, text, colour=SUCCESS):
        if self.status is not None:
            self.status.config(text=text, fg=colour)

    def button(self, parent, text, command, bg=PRIMARY, width=None):
        return tk.Button(parent, text=text, command=command, bg=bg, fg="white",
                         activebackground=PRIMARY_DARK, activeforeground="white",
                         relief="flat", bd=0, padx=14, pady=9, width=width,
                         cursor="hand2", font=("Segoe UI", 10, "bold"))

    def card(self, parent, title="", subtitle=""):
        frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        if title != "":
            tk.Label(frame, text=title, bg=CARD, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=18, pady=(16, 2))
        if subtitle != "":
            tk.Label(frame, text=subtitle, bg=CARD, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 10))
        return frame

    def heading(self, title, subtitle):
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0, 16))
        tk.Label(top, text=title, bg=BG, fg=TEXT, font=("Segoe UI", 27, "bold")).pack(anchor="w")
        tk.Label(top, text=subtitle, bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w")

    def entry_field(self, parent, label, show=None, max_length=None):
        """Create a labelled entry field and optionally limit its character count."""
        tk.Label(parent, text=label, bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=18, pady=(10, 4)
        )
        entry = tk.Entry(
            parent, show=show, bg=CARD_2, fg=TEXT, relief="solid", bd=1,
            font=("Segoe UI", 11)
        )
        entry.pack(fill="x", padx=18, pady=(0, 8), ipady=7)
        if max_length is not None:
            self.limit_entry(entry, max_length)
        return entry

    def limit_entry(self, entry, max_length):
        """Prevent a Tkinter Entry from exceeding the data-dictionary size."""
        command = self.root.register(lambda proposed: len(proposed) <= max_length)
        entry.configure(validate="key", validatecommand=(command, "%P"))

    def combo_field(self, parent, label, values):
        tk.Label(parent, text=label, bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(10, 4))
        variable = tk.StringVar(value=values[0])
        combo = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly")
        combo.pack(fill="x", padx=18, pady=(0, 8), ipady=4)
        return variable

    def tree(self, parent, columns, widths):
        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="both", expand=True, padx=18, pady=14)
        table = ttk.Treeview(frame, columns=columns, show="headings", height=13)
        table.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        scroll.pack(side="right", fill="y")
        table.configure(yscrollcommand=scroll.set)
        for index in range(len(columns)):
            table.heading(columns[index], text=columns[index])
            table.column(columns[index], width=widths[index], anchor="w")
        return table

    def selected_id(self, table):
        selected = table.selection()
        if len(selected) == 0:
            return None
        values = table.item(selected[0], "values")
        if len(values) == 0:
            return None
        return values[0]

    def show_login(self):
        LoginPage(self).show()

    def login_success(self, username, role, competitor_id=None):
        self.user = username
        self.role = role
        self.student_competitor_id = competitor_id
        self.show_shell()

    def show_shell(self):
        self.clear_window()
        sidebar = tk.Frame(self.root, bg=NAV, width=245)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="TrackPoint", bg=NAV, fg="white", font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=22, pady=(24, 0))
        tk.Label(sidebar, text=self.role + " Workspace", bg=NAV, fg="#94a3b8", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24, pady=(2, 24))

        self.nav_buttons = {}
        if self.role == "Student":
            self.add_nav(sidebar, "Student Portal", self.show_student_portal)
            self.add_nav(sidebar, "Events", self.show_events)
            self.add_nav(sidebar, "Leaderboard", self.show_leaderboard)
        else:
            self.add_nav(sidebar, "Dashboard", self.show_dashboard)
            self.add_nav(sidebar, "Competitors", self.show_competitors)
            self.add_nav(sidebar, "Events", self.show_events)
            self.add_nav(sidebar, "Results", self.show_results)
            self.add_nav(sidebar, "Leaderboard", self.show_leaderboard)
            if self.role == "Admin":
                self.add_nav(sidebar, "Users", self.show_users)
        self.add_nav(sidebar, "Help", self.show_help)
        tk.Frame(sidebar, bg=NAV).pack(fill="both", expand=True)
        self.add_nav(sidebar, "Logout", self.show_login)

        right = tk.Frame(self.root, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        topbar = tk.Frame(right, bg=CARD, height=62, highlightbackground=BORDER, highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="Logged in as " + self.user, bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left", padx=24)
        self.status = tk.Label(topbar, text="Ready", bg=CARD, fg=SUCCESS, font=("Segoe UI", 10, "bold"))
        self.status.pack(side="right", padx=24)
        self.content = tk.Frame(right, bg=BG)
        self.content.pack(fill="both", expand=True, padx=26, pady=22)
        if self.role == "Student":
            self.show_student_portal()
        else:
            self.show_dashboard()

    def add_nav(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command, bg=NAV, fg="#e5e7eb", activebackground=NAV_2,
                           activeforeground="white", relief="flat", anchor="w", bd=0, padx=24, pady=13,
                           font=("Segoe UI", 11, "bold"), cursor="hand2")
        button.pack(fill="x", padx=12, pady=3)
        self.nav_buttons[text] = button

    def activate(self, page):
        for key in self.nav_buttons:
            self.nav_buttons[key].config(bg=NAV, fg="#e5e7eb")
        if page in self.nav_buttons:
            self.nav_buttons[page].config(bg=NAV_2, fg="white")

    def show_dashboard(self):
        DashboardPage(self).show()

    def show_competitors(self):
        CompetitorsPage(self).show()

    def show_events(self):
        EventsPage(self).show()

    def show_results(self):
        ResultsPage(self).show()

    def show_leaderboard(self):
        LeaderboardPage(self).show()

    def show_users(self):
        UsersPage(self).show()

    def show_student_portal(self):
        StudentPage(self).show()

    def show_help(self):
        HelpPage(self).show()

    def close_app(self):
        self.db.close()
        self.root.destroy()
