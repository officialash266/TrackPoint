"""Shared TrackPoint settings and data-dictionary limits."""

import os
import sys

APP_TITLE = "TrackPoint"

# Source mode: store data beside the source files.
# EXE mode: store data beside TrackPoint.exe.
if getattr(sys, "frozen", False):
    PROJECT_FOLDER = os.path.dirname(sys.executable)
else:
    PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

DB_FILE = os.path.join(DATA_FOLDER, "trackpoint.db")
BACKUP_FILE = os.path.join(DATA_FOLDER, "backup.sql")
DATA_FOLDER_DISPLAY = DATA_FOLDER

# Fixed values used by drop-down fields and validation.
HOUSES = ["Midson", "Darvall", "Harris", "Terry"]
HOUSE_COLOUR = {
    "Midson": "#2563eb",    # blue
    "Darvall": "#dc2626",   # red
    "Harris": "#ca8a04",    # yellow
    "Terry": "#16a34a"      # green
}
YEAR_GROUPS = ["7", "8", "9", "10", "11", "12"]
EVENT_TYPES = ["Track", "Field"]
ROLES = ["Admin", "Staff", "Student"]
POINTS_TABLE = {1: 8, 2: 6, 3: 4, 4: 2, 5: 1}
RESULT_UNITS = {"Track": "s", "Field": "m"}

# Maximum sizes from the TrackPoint data dictionary.
MAX_ID_DIGITS = 6
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 20
PASSWORD_HASH_LENGTH = 64
MAX_COMPETITOR_NAME_LENGTH = 50
MAX_EVENT_NAME_LENGTH = 40
MAX_AGE_GROUP_LENGTH = 10
MAX_RESULT_VALUE_LENGTH = 15
MAX_SEARCH_LENGTH = 50

# User interface colours.
BG = "#eef2f7"
CARD = "#ffffff"
CARD_2 = "#f8fafc"
NAV = "#0f172a"
NAV_2 = "#1e293b"
TEXT = "#111827"
MUTED = "#64748b"
BORDER = "#d1d5db"
PRIMARY = "#2563eb"
PRIMARY_DARK = "#1d4ed8"
SUCCESS = "#16a34a"
DANGER = "#dc2626"
WARNING = "#f59e0b"
