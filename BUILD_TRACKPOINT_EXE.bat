@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo       TrackPoint Windows EXE Builder
echo ========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found.
    echo Install Python for Windows and tick "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/3] Installing or updating PyInstaller...
py -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: PyInstaller could not be installed.
    pause
    exit /b 1
)

echo.
echo [2/3] Removing old build files...
if exist build rmdir /s /q build
if exist TrackPoint.spec del /q TrackPoint.spec
if exist TrackPoint.exe del /q TrackPoint.exe

rem IMPORTANT: The data folder is deliberately NOT deleted.
rem It contains data\trackpoint.db and must survive every rebuild.

echo.
echo [3/3] Building TrackPoint.exe into the project folder...
py -m PyInstaller --noconfirm --clean --onefile --windowed --name TrackPoint --distpath "%~dp0" main.py
if errorlevel 1 (
    echo.
    echo BUILD FAILED. Review the error shown above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETE
echo EXE:      %~dp0TrackPoint.exe
echo DATABASE: %~dp0data\trackpoint.db
echo BACKUP:   %~dp0data\backup.sql
echo ========================================
echo.
echo The EXE and SQLite database now stay inside this project folder.
start "" "%~dp0"
pause
