@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller
if exist build rmdir /s /q build
if exist TrackPoint_Debug.spec del /q TrackPoint_Debug.spec
if exist TrackPoint_Debug.exe del /q TrackPoint_Debug.exe
py -m PyInstaller --noconfirm --clean --onefile --console --name TrackPoint_Debug --distpath "%~dp0" main.py
pause
