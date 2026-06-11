TRACKPOINT WINDOWS EXE BUILD
============================

The SQLite database and SQL backup are stored in the writable "data" folder inside the TrackPoint project folder.

BUILD THE FINAL EXE
1. Use a Windows computer with Python installed.
2. Extract this ZIP completely.
3. Double-click BUILD_TRACKPOINT_EXE.bat.
4. Wait for the build to finish.
5. The executable will be created in the project root at:
   TrackPoint.exe

FIRST RUN
Opening TrackPoint.exe uses or creates:
   data\trackpoint.db

Using the Backup SQL button creates:
   data\backup.sql

DEMO LOGINS
Admin:   admin / admin123
Staff:   staff / staff123
Student: student / student123

DEBUGGING
If TrackPoint.exe does not open, double-click BUILD_DEBUG_EXE.bat and run TrackPoint_Debug.exe. The console window will display the error.

IMPORTANT
- Keep TrackPoint.exe inside this project folder so it uses the same data\trackpoint.db file as the source-code version.
- Do not delete the data folder when rebuilding.
- A genuine Windows .exe must be built on Windows. PyInstaller builds for the operating system it runs on.
