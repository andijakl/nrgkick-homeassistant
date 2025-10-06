@echo off
REM Create Release Package Script for NRGkick Home Assistant Integration
REM Usage: create-release.bat [version]
REM Example: create-release.bat 0.1.0

powershell.exe -ExecutionPolicy Bypass -File "%~dp0create-release.ps1" %*
