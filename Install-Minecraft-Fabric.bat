@echo off
setlocal enabledelayedexpansion

:: Define URLs and paths
set "FABRIC_INSTALLER_URL=https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.exe"
set "FABRIC_API_URL=https://www.curseforge.com/minecraft/mc-mods/fabric-api"
set "VOICE_CHAT_URL=https://www.curseforge.com/minecraft/mc-mods/simple-voice-chat"
set "MODS_FOLDER=%APPDATA%\.minecraft\mods"
set "TEMP_DIR=%TEMP%\minecraft_fabric_setup"

:: Create timestamp for backup
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "BACKUP_DATE=%datetime:~0,8%_%datetime:~8,6%"

:: Create temporary directory
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Step 1: Download Fabric installer
echo Downloading Fabric installer...
powershell -Command "& {Invoke-WebRequest -Uri '%FABRIC_INSTALLER_URL%' -OutFile '%TEMP_DIR%\fabric-installer.exe'}"

:: Step 2: Backup existing mods folder if it exists
if exist "%MODS_FOLDER%" (
    echo Backing up existing mods folder...
    ren "%MODS_FOLDER%" "mods_backup_%BACKUP_DATE%"
)

:: Step 3: Run Fabric installer
echo Running Fabric installer...
echo Please complete the installer wizard when it opens.
echo Select the latest Minecraft version and proceed with the installation.
start /wait "" "%TEMP_DIR%\fabric-installer.exe"

:: Steps 4 & 5: Open browser for mod downloads
echo.
echo Opening download pages for required mods...
echo 1. Fabric API - Please download the latest version compatible with your Minecraft version
start "" "%FABRIC_API_URL%"
timeout /t 2 /nobreak >nul

echo 2. Simple Voice Chat - Please download the latest version compatible with your Minecraft version
start "" "%VOICE_CHAT_URL%"

:: Create new mods folder
if not exist "%MODS_FOLDER%" mkdir "%MODS_FOLDER%"

:: Step 6: Help user move mod files
echo.
echo Once you have downloaded the mod files:
echo Please move the downloaded mod files to: %MODS_FOLDER%
echo A File Explorer window will open to the mods folder.
echo You can drag and drop the files into this folder.
start explorer "%MODS_FOLDER%"

:: Wait for user confirmation
echo.
set /p "DUMMY=Press Enter once you have moved the mod files..."

:: Step 7: Final instructions
echo.
echo Setup is almost complete!
echo Please open the Minecraft launcher and select the new Fabric installation profile.
echo The profile should be named something like 'fabric-loader-[version]'

:: Cleanup
del /f /q "%TEMP_DIR%\fabric-installer.exe"
echo.
echo Setup complete! The temporary files have been cleaned up.

:: Wait before closing
echo.
pause
