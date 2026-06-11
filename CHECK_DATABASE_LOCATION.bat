@echo off
cd /d "%~dp0"
echo TrackPoint database location:
echo %~dp0data\trackpoint.db
echo.
if exist "%~dp0data\trackpoint.db" (
    echo STATUS: Database file found.
) else (
    echo STATUS: Database file has not been created yet.
    echo Run main.py or TrackPoint.exe once to create it.
)
echo.
pause
