TRACKPOINT - EBHS ATHLETICS MANAGEMENT SYSTEM
=============================================
Student: Ashaz Mohammed
Course: Year 12 Software Engineering
Language: Python 3 with Tkinter
Database: SQLite

WHAT IS INCLUDED
----------------
TrackPoint is a complete desktop application for managing an EBHS athletics carnival.
It includes secure login, role-based authorisation, competitor/event/result management,
automatic house scoring, a live leaderboard, a Student Portal, record editing, SQL backup,
an integrated Help page, realistic demonstration data and supporting documentation.

DEMONSTRATION ACCOUNTS
----------------------
Admin   Username: admin     Password: admin123
Staff   Username: staff     Password: staff123
Student Username: student   Password: student123

ROLE PERMISSIONS
----------------
Admin:
- Full access to users, competitors, events, results and leaderboard
- Add, update and delete competitors, events and results
- Create and delete user accounts
- Create SQL backups

Staff:
- Add competitors, events and results
- View dashboard and leaderboard
- Create SQL backups
- Cannot manage users, update records or delete records

Student:
- View-only access to linked profile and personal results
- View events and leaderboard
- Cannot add, update or delete data

RUN FROM PYTHON SOURCE
----------------------
1. Install Python 3.10 or newer.
2. Extract the complete TrackPoint folder.
3. Open Command Prompt in the extracted folder.
4. Run: python main.py

No third-party runtime libraries are required. Tkinter, sqlite3, hashlib, os and sys
are included with standard Python installations on Windows.

BUILD THE WINDOWS EXE
---------------------
1. On a Windows computer, double-click BUILD_TRACKPOINT_EXE.bat.
2. The script installs PyInstaller if necessary and builds TrackPoint.exe.
3. Keep TrackPoint.exe beside the data folder.
4. Test the EXE before submission.

IMPORTANT: A Windows EXE cannot be produced reliably from this Linux workspace. The
batch file is included and must be run once on Windows before final school submission.

DATA AND BACKUP
---------------
The supplied database contains:
- 3 demonstration user accounts
- 16 fictional competitors across all four houses and multiple year groups
- 8 Track and Field events
- 32 realistic results covering different placings, units and point values

The database is stored at data\trackpoint.db.
Admin and Staff users can create data\backup.sql from the Leaderboard page.

DOCUMENTATION
-------------
Open the documentation folder for:
- Component B and C supporting documentation
- Visual user tutorial
- Installation and troubleshooting guides
- Automated test evidence
- Algorithms and logbook evidence guide
- Peer feedback form questions
- Video presentation script
- Complete updated source-code copy
- Screenshots of the working program

FINAL STUDENT ACTIONS STILL REQUIRED
------------------------------------
1. Build TrackPoint.exe on Windows and add it to this folder.
2. Upload documentation\TrackPoint_Updated_Source_Code.txt to Google Docs and paste the
   share link into the school template.
3. Obtain genuine feedback from three peers and add screenshots/results.
4. Add genuine Git/GitHub screenshots to the logbook.
5. Record the final five-minute presentation.
6. Confirm all Google links are shared as "Anyone with the link can view".
