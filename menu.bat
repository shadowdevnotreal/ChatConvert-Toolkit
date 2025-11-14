@echo off
REM ChatConvert Toolkit - Windows Launcher
REM Automatically detects Python and runs the menu

setlocal enabledelayedexpansion

echo ============================================================
echo    ChatConvert Toolkit - Windows Launcher
echo ============================================================
echo.

REM Check for Python 3
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo Python 3 found: python3
    python3 --version
    echo.
    echo Starting ChatConvert Toolkit...
    echo.
    python3 menu.py
    goto :end
)

REM Check for Python (might be Python 3)
where python >nul 2>&1
if %errorlevel% equ 0 (
    REM Check if it's Python 3
    python --version 2>&1 | findstr /C:"Python 3" >nul
    if %errorlevel% equ 0 (
        echo Python 3 found: python
        python --version
        echo.
        echo Starting ChatConvert Toolkit...
        echo.
        python menu.py
        goto :end
    ) else (
        echo Error: Python 2 detected, but Python 3 is required!
        echo Please install Python 3.6 or higher.
        goto :error
    )
)

REM Python not found
echo Error: Python not found!
echo.
echo Please install Python 3.6 or higher from:
echo https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation.
goto :error

:error
echo.
pause
exit /b 1

:end
echo.
pause
exit /b 0
