"""SQLite back end for the TrackPoint athletics management system.

The database layer keeps SQL and validation separate from the Tkinter pages.
All values supplied by users are validated before parameterised SQL statements
are executed. Transactions are committed only after a successful operation and
rolled back when SQLite reports an error.
"""

import hashlib
import os
import sqlite3

from settings import (
    BACKUP_FILE,
    DB_FILE,
    HOUSES,
    PASSWORD_HASH_LENGTH,
    POINTS_TABLE,
)
from validation import ValidationError, validate_value


def make_hash(password):
    """Return a 64-character SHA-256 password hash."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class Database:
    """Create the database and provide parameterised SQL routines."""

    def __init__(self):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        self.connection = sqlite3.connect(DB_FILE, timeout=10)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = DELETE")
        self.connection.row_factory = sqlite3.Row
        self.create_tables()
        self.create_validation_triggers()
        self.insert_sample_data()

    def run(self, sql, values=()):
        """Execute a parameterised SQL statement and save the change."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            return cursor
        except sqlite3.Error:
            self.connection.rollback()
            raise

    def all(self, sql, values=()):
        """Return all selected rows as dictionaries."""
        cursor = self.connection.cursor()
        cursor.execute(sql, values)
        return [dict(row) for row in cursor.fetchall()]

    def one(self, sql, values=()):
        """Return one selected row as a dictionary, or None."""
        cursor = self.connection.cursor()
        cursor.execute(sql, values)
        row = cursor.fetchone()
        return None if row is None else dict(row)

    def create_tables(self):
        """Create the four linked SQL tables used by TrackPoint."""
        self.run("""
            CREATE TABLE IF NOT EXISTS competitors (
                competitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 50),
                year_group TEXT NOT NULL CHECK(year_group IN ('7', '8', '9', '10', '11', '12')),
                house TEXT NOT NULL CHECK(house IN ('Midson', 'Darvall', 'Harris', 'Terry'))
            )
        """)
        self.run("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE CHECK(length(username) BETWEEN 3 AND 20),
                password_hash TEXT NOT NULL CHECK(length(password_hash) = 64),
                role TEXT NOT NULL CHECK(role IN ('Admin', 'Staff', 'Student')),
                competitor_id INTEGER,
                FOREIGN KEY(competitor_id) REFERENCES competitors(competitor_id)
            )
        """)
        self.run("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL CHECK(length(event_name) BETWEEN 1 AND 40),
                event_type TEXT NOT NULL CHECK(event_type IN ('Track', 'Field')),
                age_group TEXT NOT NULL CHECK(length(age_group) BETWEEN 1 AND 10)
            )
        """)
        self.run("""
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                competitor_id INTEGER NOT NULL,
                placing INTEGER NOT NULL CHECK(placing BETWEEN 1 AND 8),
                result_value TEXT NOT NULL CHECK(length(result_value) BETWEEN 1 AND 15),
                points_awarded INTEGER NOT NULL CHECK(points_awarded IN (0, 1, 2, 4, 6, 8)),
                FOREIGN KEY(event_id) REFERENCES events(event_id),
                FOREIGN KEY(competitor_id) REFERENCES competitors(competitor_id),
                UNIQUE(event_id, competitor_id)
            )
        """)
        # A competitor can be connected to only one Student login.
        self.run("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_student_competitor
            ON users(competitor_id)
            WHERE role = 'Student' AND competitor_id IS NOT NULL
        """)

    def create_validation_triggers(self):
        """Enforce important rules for INSERT and UPDATE operations."""
        triggers = [
            """
            CREATE TRIGGER IF NOT EXISTS validate_competitor_insert
            BEFORE INSERT ON competitors
            WHEN length(trim(NEW.name)) NOT BETWEEN 1 AND 50
              OR NEW.year_group NOT IN ('7', '8', '9', '10', '11', '12')
              OR NEW.house NOT IN ('Midson', 'Darvall', 'Harris', 'Terry')
            BEGIN SELECT RAISE(ABORT, 'Invalid competitor data'); END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS validate_competitor_update
            BEFORE UPDATE ON competitors
            WHEN length(trim(NEW.name)) NOT BETWEEN 1 AND 50
              OR NEW.year_group NOT IN ('7', '8', '9', '10', '11', '12')
              OR NEW.house NOT IN ('Midson', 'Darvall', 'Harris', 'Terry')
            BEGIN SELECT RAISE(ABORT, 'Invalid competitor data'); END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS validate_user_insert
            BEFORE INSERT ON users
            WHEN length(NEW.username) NOT BETWEEN 3 AND 20
              OR NEW.username GLOB '*[^A-Za-z0-9_]*'
              OR length(NEW.password_hash) != 64
              OR NEW.role NOT IN ('Admin', 'Staff', 'Student')
              OR (NEW.role = 'Student' AND NEW.competitor_id IS NULL)
              OR (NEW.role != 'Student' AND NEW.competitor_id IS NOT NULL)
            BEGIN SELECT RAISE(ABORT, 'Invalid user data'); END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS validate_event_insert
            BEFORE INSERT ON events
            WHEN length(trim(NEW.event_name)) NOT BETWEEN 1 AND 40
              OR NEW.event_type NOT IN ('Track', 'Field')
              OR length(trim(NEW.age_group)) NOT BETWEEN 1 AND 10
            BEGIN SELECT RAISE(ABORT, 'Invalid event data'); END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS validate_event_update
            BEFORE UPDATE ON events
            WHEN length(trim(NEW.event_name)) NOT BETWEEN 1 AND 40
              OR NEW.event_type NOT IN ('Track', 'Field')
              OR length(trim(NEW.age_group)) NOT BETWEEN 1 AND 10
            BEGIN SELECT RAISE(ABORT, 'Invalid event data'); END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS validate_result_insert
            BEFORE INSERT ON results
            WHEN NEW.placing NOT BETWEEN 1 AND 8
              OR length(trim(NEW.result_value)) NOT BETWEEN 1 AND 15
              OR NEW.points_awarded != CASE NEW.placing
                    WHEN 1 THEN 8 WHEN 2 THEN 6 WHEN 3 THEN 4
                    WHEN 4 THEN 2 WHEN 5 THEN 1 ELSE 0 END
            BEGIN SELECT RAISE(ABORT, 'Invalid result data'); END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS validate_result_update
            BEFORE UPDATE ON results
            WHEN NEW.placing NOT BETWEEN 1 AND 8
              OR length(trim(NEW.result_value)) NOT BETWEEN 1 AND 15
              OR NEW.points_awarded != CASE NEW.placing
                    WHEN 1 THEN 8 WHEN 2 THEN 6 WHEN 3 THEN 4
                    WHEN 4 THEN 2 WHEN 5 THEN 1 ELSE 0 END
            BEGIN SELECT RAISE(ABORT, 'Invalid result data'); END
            """,
        ]
        for trigger in triggers:
            self.run(trigger)

    def insert_sample_data(self):
        """Insert a varied fictional demonstration dataset when tables are empty."""
        if self.one("SELECT competitor_id FROM competitors LIMIT 1") is None:
            students = [
                ("Ali Khan", "12", "Midson"),
                ("Noah Smith", "10", "Darvall"),
                ("Lucas Chen", "11", "Harris"),
                ("Ryan Patel", "9", "Terry"),
                ("Ethan Brown", "8", "Midson"),
                ("Liam Wilson", "7", "Darvall"),
                ("Oliver Nguyen", "10", "Harris"),
                ("Jack Thompson", "12", "Terry"),
                ("Henry Davis", "11", "Midson"),
                ("William Lee", "9", "Darvall"),
                ("James Martin", "8", "Harris"),
                ("Thomas Walker", "7", "Terry"),
                ("Benjamin Young", "12", "Midson"),
                ("Samuel Moore", "10", "Darvall"),
                ("Daniel White", "11", "Harris"),
                ("Max Harris", "9", "Terry"),
            ]
            for name, year_group, house in students:
                self.add_competitor(name, year_group, house)

        if self.one("SELECT user_id FROM users LIMIT 1") is None:
            self.add_user("admin", "admin123", "Admin")
            self.add_user("staff", "staff123", "Staff")
            self.add_user("student", "student123", "Student", 1)

        if self.one("SELECT event_id FROM events LIMIT 1") is None:
            events = [
                ("100m Sprint", "Track", "Open"),
                ("Long Jump", "Field", "Open"),
                ("400m Run", "Track", "U16"),
                ("Shot Put", "Field", "Open"),
                ("200m Sprint", "Track", "U14"),
                ("High Jump", "Field", "U16"),
                ("800m Run", "Track", "Open"),
                ("Discus", "Field", "U14"),
            ]
            for event_name, event_type, age_group in events:
                self.add_event(event_name, event_type, age_group)

        # A new database should immediately demonstrate scoring and rankings.
        if self.one("SELECT result_id FROM results LIMIT 1") is None:
            demo_results = [
                (1, 1, 1, "12.42 s"), (1, 2, 2, "12.66 s"),
                (1, 3, 3, "12.91 s"), (1, 4, 4, "13.10 s"),
                (2, 5, 2, "5.21 m"), (2, 6, 1, "5.48 m"),
                (2, 7, 4, "4.95 m"), (2, 8, 3, "5.10 m"),
                (3, 9, 1, "56.22 s"), (3, 10, 3, "57.43 s"),
                (3, 11, 2, "56.89 s"), (3, 12, 5, "59.11 s"),
                (4, 13, 3, "9.32 m"), (4, 14, 2, "9.55 m"),
                (4, 15, 1, "9.87 m"), (4, 16, 4, "8.96 m"),
                (5, 1, 2, "25.18 s"), (5, 6, 4, "26.02 s"),
                (5, 11, 1, "24.88 s"), (5, 16, 3, "25.57 s"),
                (6, 5, 1, "1.62 m"), (6, 10, 3, "1.55 m"),
                (6, 15, 2, "1.59 m"), (6, 8, 5, "1.48 m"),
                (7, 9, 2, "133.20 s"), (7, 14, 1, "131.76 s"),
                (7, 3, 4, "136.45 s"), (7, 12, 3, "134.82 s"),
                (8, 13, 1, "28.40 m"), (8, 2, 3, "26.85 m"),
                (8, 7, 2, "27.66 m"), (8, 4, 4, "25.90 m"),
            ]
            for event_id, competitor_id, placing, result_value in demo_results:
                self.add_result(event_id, competitor_id, placing, result_value)

    def check_login(self, username, password):
        """Authenticate a user using the stored password hash."""
        try:
            username = validate_value("username", username)
            password = validate_value("password", password)
        except ValidationError:
            return None
        return self.one(
            "SELECT username, role, competitor_id FROM users WHERE username = ? AND password_hash = ?",
            (username, make_hash(password)),
        )

    def get_users(self):
        return self.all("""
            SELECT users.user_id, users.username, users.role,
                   users.competitor_id, competitors.name
            FROM users
            LEFT JOIN competitors ON users.competitor_id = competitors.competitor_id
            ORDER BY users.user_id
        """)

    def add_user(self, username, password, role, competitor_id=None):
        """Validate and add an Admin, Staff or Student account."""
        username = validate_value("username", username)
        password = validate_value("password", password)
        role = validate_value("role", role)
        if role == "Student":
            competitor_id = validate_value("competitor_id", competitor_id)
            if self.get_competitor(competitor_id) is None:
                raise ValidationError("No competitor exists with that ID.")
            if self.one(
                "SELECT user_id FROM users WHERE role = 'Student' AND competitor_id = ?",
                (competitor_id,),
            ) is not None:
                raise ValidationError("That competitor is already linked to a Student account.")
        elif competitor_id not in (None, ""):
            raise ValidationError("Competitor ID must be blank for Admin and Staff accounts.")
        else:
            competitor_id = None
        password_hash = make_hash(password)
        if len(password_hash) != PASSWORD_HASH_LENGTH:
            raise ValidationError("Password hash could not be generated correctly.")
        self.run(
            "INSERT INTO users (username, password_hash, role, competitor_id) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, competitor_id),
        )

    def delete_user(self, user_id):
        user_id = validate_value("user_id", user_id)
        self.run("DELETE FROM users WHERE user_id = ? AND username != 'admin'", (user_id,))

    def get_competitors(self, search=""):
        search = validate_value("search_text", search)
        search_value = "%" + search + "%"
        return self.all("""
            SELECT competitor_id, name, year_group, house
            FROM competitors
            WHERE CAST(competitor_id AS TEXT) LIKE ?
               OR name LIKE ? OR house LIKE ? OR year_group LIKE ?
            ORDER BY competitor_id
        """, (search_value, search_value, search_value, search_value))

    def get_competitor(self, competitor_id):
        if competitor_id in (None, ""):
            return None
        competitor_id = validate_value("competitor_id", competitor_id)
        return self.one(
            "SELECT competitor_id, name, year_group, house FROM competitors WHERE competitor_id = ?",
            (competitor_id,),
        )

    def add_competitor(self, name, year_group, house):
        name = validate_value("competitor_name", name)
        year_group = validate_value("year_group", year_group)
        house = validate_value("house", house)
        self.run(
            "INSERT INTO competitors (name, year_group, house) VALUES (?, ?, ?)",
            (name, year_group, house),
        )

    def update_competitor(self, competitor_id, name, year_group, house):
        """Validate and edit an existing competitor record."""
        competitor_id = validate_value("competitor_id", competitor_id)
        name = validate_value("competitor_name", name)
        year_group = validate_value("year_group", year_group)
        house = validate_value("house", house)
        if self.get_competitor(competitor_id) is None:
            raise ValidationError("The selected competitor no longer exists.")
        self.run(
            "UPDATE competitors SET name = ?, year_group = ?, house = ? WHERE competitor_id = ?",
            (name, year_group, house, competitor_id),
        )

    def delete_competitor(self, competitor_id):
        competitor_id = validate_value("competitor_id", competitor_id)
        linked_user = self.one(
            "SELECT username FROM users WHERE role = 'Student' AND competitor_id = ?",
            (competitor_id,),
        )
        if linked_user is not None:
            raise ValidationError("Delete the linked Student account before deleting this competitor.")
        self.run("DELETE FROM results WHERE competitor_id = ?", (competitor_id,))
        self.run("DELETE FROM competitors WHERE competitor_id = ?", (competitor_id,))

    def get_events(self):
        return self.all(
            "SELECT event_id, event_name, event_type, age_group FROM events ORDER BY event_id"
        )

    def get_event(self, event_id):
        event_id = validate_value("event_id", event_id)
        return self.one(
            "SELECT event_id, event_name, event_type, age_group FROM events WHERE event_id = ?",
            (event_id,),
        )

    def add_event(self, event_name, event_type, age_group):
        event_name = validate_value("event_name", event_name)
        event_type = validate_value("event_type", event_type)
        age_group = validate_value("age_group", age_group)
        self.run(
            "INSERT INTO events (event_name, event_type, age_group) VALUES (?, ?, ?)",
            (event_name, event_type, age_group),
        )

    def update_event(self, event_id, event_name, event_type, age_group):
        """Validate and edit an existing event record."""
        event_id = validate_value("event_id", event_id)
        event_name = validate_value("event_name", event_name)
        event_type = validate_value("event_type", event_type)
        age_group = validate_value("age_group", age_group)
        if self.get_event(event_id) is None:
            raise ValidationError("The selected event no longer exists.")
        # Changing Track/Field could invalidate stored units, so block that unsafe change.
        current = self.get_event(event_id)
        if current["event_type"] != event_type and self.one(
            "SELECT result_id FROM results WHERE event_id = ? LIMIT 1", (event_id,)
        ) is not None:
            raise ValidationError(
                "Delete this event's saved results before changing its Track/Field type."
            )
        self.run(
            "UPDATE events SET event_name = ?, event_type = ?, age_group = ? WHERE event_id = ?",
            (event_name, event_type, age_group, event_id),
        )

    def delete_event(self, event_id):
        event_id = validate_value("event_id", event_id)
        self.run("DELETE FROM results WHERE event_id = ?", (event_id,))
        self.run("DELETE FROM events WHERE event_id = ?", (event_id,))

    def get_results(self):
        return self.all("""
            SELECT results.result_id, results.event_id, results.competitor_id,
                   events.event_name, competitors.name, competitors.house,
                   results.placing, results.result_value, results.points_awarded
            FROM results
            JOIN events ON results.event_id = events.event_id
            JOIN competitors ON results.competitor_id = competitors.competitor_id
            ORDER BY results.result_id
        """)

    def get_result(self, result_id):
        result_id = validate_value("result_id", result_id)
        return self.one("""
            SELECT result_id, event_id, competitor_id, placing, result_value, points_awarded
            FROM results WHERE result_id = ?
        """, (result_id,))

    def get_student_results(self, competitor_id):
        competitor_id = validate_value("competitor_id", competitor_id)
        return self.all("""
            SELECT events.event_name, events.event_type, events.age_group,
                   results.placing, results.result_value, results.points_awarded
            FROM results
            JOIN events ON results.event_id = events.event_id
            WHERE results.competitor_id = ?
            ORDER BY events.event_name
        """, (competitor_id,))

    def _normalise_result(self, event_id, competitor_id, placing, result_value):
        """Validate result fields and return normalised values and calculated points."""
        event_id = validate_value("event_id", event_id)
        competitor_id = validate_value("competitor_id", competitor_id)
        placing = validate_value("placing", placing)
        event = self.get_event(event_id)
        if event is None:
            raise ValidationError("The selected event does not exist.")
        if self.get_competitor(competitor_id) is None:
            raise ValidationError("The selected competitor does not exist.")
        result_value = validate_value("result_value", result_value, event["event_type"])
        return event_id, competitor_id, placing, result_value, POINTS_TABLE.get(placing, 0)

    def add_result(self, event_id, competitor_id, placing, result_value):
        event_id, competitor_id, placing, result_value, points = self._normalise_result(
            event_id, competitor_id, placing, result_value
        )
        self.run("""
            INSERT INTO results (event_id, competitor_id, placing, result_value, points_awarded)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, competitor_id, placing, result_value, points))

    def update_result(self, result_id, event_id, competitor_id, placing, result_value):
        """Validate and edit a result, recalculating points from the placing."""
        result_id = validate_value("result_id", result_id)
        if self.get_result(result_id) is None:
            raise ValidationError("The selected result no longer exists.")
        event_id, competitor_id, placing, result_value, points = self._normalise_result(
            event_id, competitor_id, placing, result_value
        )
        self.run("""
            UPDATE results
            SET event_id = ?, competitor_id = ?, placing = ?,
                result_value = ?, points_awarded = ?
            WHERE result_id = ?
        """, (event_id, competitor_id, placing, result_value, points, result_id))

    def delete_result(self, result_id):
        result_id = validate_value("result_id", result_id)
        self.run("DELETE FROM results WHERE result_id = ?", (result_id,))

    def leaderboard(self):
        """Calculate and rank totals for every EBHS house."""
        board = []
        for house in HOUSES:
            row = self.one("""
                SELECT SUM(results.points_awarded) AS total
                FROM results
                JOIN competitors ON results.competitor_id = competitors.competitor_id
                WHERE competitors.house = ?
            """, (house,))
            points = row["total"] if row["total"] is not None else 0
            board.append({"house": house, "points": points})
        board.sort(key=lambda item: item["points"], reverse=True)
        return board

    def backup(self):
        """Write SQL statements that recreate the current database."""
        with open(BACKUP_FILE, "w", encoding="utf-8") as file:
            for line in self.connection.iterdump():
                file.write(line + "\n")
        return BACKUP_FILE

    def close(self):
        self.connection.close()
