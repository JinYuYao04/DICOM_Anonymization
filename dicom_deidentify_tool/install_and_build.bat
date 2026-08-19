@echo off
echo Step 1: Installing dependencies...
pip install pyinstaller pydicom PyQt6
echo.

echo Step 2: Cleaning old files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

echo Step 3: Building executable...
pyinstaller --onefile --windowed --name DICOM_Deidentify_Tool main.py
echo.

echo Done! Check dist folder for the executable.
pause
