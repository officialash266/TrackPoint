"""TrackPoint backend test driver.

This script uses a temporary SQLite database so the demonstration database is not
changed. It records expected and actual outcomes for authentication, validation,
authorisation-related data rules, CRUD operations, scoring, persistence and backup.
"""

import csv
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

import database
from validation import ValidationError


RESULTS = []


def record(test_id, feature, input_data, expected, actual, passed):
    RESULTS.append({
        "Test ID": test_id,
        "Feature": feature,
        "Input Data": input_data,
        "Expected Output": expected,
        "Actual Output": actual,
        "Result": "PASS" if passed else "FAIL",
    })


def run_tests():
    temp_dir = tempfile.mkdtemp(prefix="trackpoint_test_")
    original_db = database.DB_FILE
    original_backup = database.BACKUP_FILE
    database.DB_FILE = os.path.join(temp_dir, "test_trackpoint.db")
    database.BACKUP_FILE = os.path.join(temp_dir, "test_backup.sql")
    db = None
    try:
        db = database.Database()

        actual = db.check_login("admin", "admin123")
        record("T01", "Valid Admin authentication", "admin / admin123", "Admin account returned", str(actual), actual is not None and actual["role"] == "Admin")

        actual = db.check_login("admin", "incorrect")
        record("T02", "Invalid password", "admin / incorrect", "No account returned", str(actual), actual is None)

        try:
            db.add_competitor("", "7", "Midson")
            actual = "Accepted"
            passed = False
        except ValidationError as exc:
            actual = str(exc)
            passed = True
        record("T03", "Blank competitor validation", "name=''", "Rejected with validation message", actual, passed)

        before = len(db.get_competitors())
        db.add_competitor("Test Student", "8", "Terry")
        after = len(db.get_competitors())
        new_id = db.one("SELECT MAX(competitor_id) AS id FROM competitors")["id"]
        record("T04", "Add competitor", "Test Student, Year 8, Terry", str(before + 1) + " competitors", str(after) + " competitors", after == before + 1)

        db.update_competitor(new_id, "Test Student Updated", "9", "Harris")
        updated = db.get_competitor(new_id)
        record("T05", "Update competitor", "Name, year and house changed", "Updated values stored", str(updated), updated["name"] == "Test Student Updated" and updated["year_group"] == "9" and updated["house"] == "Harris")

        try:
            db.add_result(1, 1, 1, "12.42 m")
            actual = "Accepted"
            passed = False
        except ValidationError as exc:
            actual = str(exc)
            passed = "unit 's'" in actual or "seconds" in actual
        except sqlite3.IntegrityError:
            actual = "Existing demonstration result caused duplicate conflict"
            passed = False
        record("T06", "Track result unit validation", "12.42 m for Track", "Rejected; Track requires s", actual, passed)

        # Use a new competitor so no demonstration result conflicts occur.
        db.add_competitor("Result Tester", "10", "Midson")
        tester_id = db.one("SELECT MAX(competitor_id) AS id FROM competitors")["id"]
        db.add_result(1, tester_id, 1, "11.90 s")
        result = db.one("SELECT placing, points_awarded FROM results WHERE event_id = 1 AND competitor_id = ?", (tester_id,))
        record("T07", "Automatic points calculation", "1st place", "8 points", str(result["points_awarded"]) + " points", result["points_awarded"] == 8)

        try:
            db.add_result(1, tester_id, 2, "12.10 s")
            actual = "Duplicate accepted"
            passed = False
        except sqlite3.IntegrityError as exc:
            actual = "Duplicate blocked by UNIQUE constraint"
            passed = True
        record("T08", "Duplicate result prevention", "Same event and competitor twice", "Rejected", actual, passed)

        result_id = db.one("SELECT result_id FROM results WHERE event_id = 1 AND competitor_id = ?", (tester_id,))["result_id"]
        db.update_result(result_id, 1, tester_id, 2, "12.01 s")
        result = db.get_result(result_id)
        record("T09", "Update result and recalculate points", "Change 1st to 2nd", "6 points", str(result["points_awarded"]) + " points", result["points_awarded"] == 6)

        board = db.leaderboard()
        passed = len(board) == 4 and all(board[i]["points"] >= board[i + 1]["points"] for i in range(3))
        record("T10", "Leaderboard sorting", "Current results", "Four houses in descending order", str(board), passed)

        backup_path = db.backup()
        exists = os.path.exists(backup_path) and os.path.getsize(backup_path) > 0
        record("T11", "SQL backup", "Run backup()", "Non-empty SQL file created", backup_path if exists else "Missing", exists)

        db.close()
        db = database.Database()
        persisted = db.get_competitor(new_id)
        record("T12", "Database persistence", "Close and reopen database", "Updated competitor remains", str(persisted), persisted is not None and persisted["name"] == "Test Student Updated")

        db.delete_result(result_id)
        deleted = db.get_result(result_id)
        record("T13", "Delete result", "Delete selected result", "Result no longer exists", str(deleted), deleted is None)

        db.delete_competitor(new_id)
        deleted = db.get_competitor(new_id)
        record("T14", "Delete competitor", "Delete unlinked competitor", "Competitor no longer exists", str(deleted), deleted is None)

    finally:
        if db is not None:
            try:
                db.close()
            except sqlite3.Error:
                pass
        database.DB_FILE = original_db
        database.BACKUP_FILE = original_backup
        shutil.rmtree(temp_dir, ignore_errors=True)


def write_reports():
    output_dir = Path(__file__).resolve().parents[1] / "documentation"
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "AUTOMATED_TEST_RESULTS.csv"
    txt_path = output_dir / "AUTOMATED_TEST_RESULTS.txt"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RESULTS[0].keys())
        writer.writeheader()
        writer.writerows(RESULTS)
    passed = sum(row["Result"] == "PASS" for row in RESULTS)
    with txt_path.open("w", encoding="utf-8") as file:
        file.write("TRACKPOINT AUTOMATED BACKEND TEST REPORT\n")
        file.write("=" * 46 + "\n\n")
        for row in RESULTS:
            file.write(f"{row['Test ID']} - {row['Feature']} - {row['Result']}\n")
            file.write(f"Input: {row['Input Data']}\n")
            file.write(f"Expected: {row['Expected Output']}\n")
            file.write(f"Actual: {row['Actual Output']}\n\n")
        file.write(f"SUMMARY: {passed}/{len(RESULTS)} tests passed.\n")
    print(f"{passed}/{len(RESULTS)} tests passed")
    print(csv_path)
    print(txt_path)
    if passed != len(RESULTS):
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()
    write_reports()
