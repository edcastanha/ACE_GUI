# Caminhos Specification

## Purpose

Define how ACE_GUI discovers and validates the Assetto Corsa Evo save directory across Windows and Linux (Proton) environments. The system SHALL locate the ACE game save path automatically, validate that required subdirectories exist, and provide a fallback manual selector when auto-detection fails. This is the foundation capability — every other feature depends on knowing where the game stores its data.

## Requirements

### Requirement: Windows path auto-detection

The system SHALL locate the ACE save directory on Windows by reading the `%USERPROFILE%\Saved Games\ACE` environment variable path.

#### Scenario: Default Windows path exists
- GIVEN Windows with default Steam installation of ACE
- WHEN the app starts for the first time
- THEN it reads `%USERPROFILE%\Saved Games\ACE`
- AND confirms the directory exists
- AND stores the path in app configuration

#### Scenario: Windows path not found
- GIVEN Windows where the default path does not exist
- WHEN auto-detection runs
- THEN no path is resolved
- AND a manual directory picker is shown to the user

### Requirement: Linux Proton path auto-detection

The system SHALL locate the ACE save directory on Linux by scanning `~/.steam/steam/steamapps/compatdata/1548780/pfx/drive_c/users/steamuser/Saved Games/ACE`.

#### Scenario: Default Proton path exists
- GIVEN Linux with ACE installed via Steam under default library
- WHEN the app starts
- THEN it finds the path under compatdata/1548780
- AND confirms the directory exists

#### Scenario: Custom Steam library path
- GIVEN Linux with ACE installed in a non-default Steam library
- WHEN auto-detection fails on default path
- THEN the app offers a "Search Steam libraries" button
- AND scans all `steamapps` directories for compatdata/1548780

#### Scenario: Flatpak Steam path
- GIVEN Linux with Steam installed via Flatpak
- WHEN auto-detection fails under `~/.steam`
- THEN the app checks `~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/1548780`

### Requirement: Directory structure validation

The system SHALL verify that the ACE save directory contains `Mods/` and `External Liveries/` subdirectories, creating them if they do not exist.

#### Scenario: Subdirectories missing on first run
- GIVEN a valid ACE save path
- WHEN `/Mods` or `/External Liveries` is missing
- THEN the app creates both directories silently
- AND logs the creation for audit

### Requirement: Manual path override

The system SHALL allow the user to manually select the ACE save directory via a native folder picker when auto-detection fails or when the user wants to override.

#### Scenario: User triggers manual selection
- GIVEN no valid path found automatically
- WHEN the user clicks "Browse" on the setup screen
- THEN a native OS folder picker opens
- AND the selected path is validated for ACE structure
- AND saved to app configuration

### Requirement: Configuration persistence

The system SHALL persist the detected or manually selected ACE path so that subsequent launches skip path detection.

#### Scenario: Path already configured
- GIVEN a previously configured ACE path in app config
- WHEN the app starts
- THEN it reads config directly
- AND skips auto-detection
- AND validates that the stored path still exists

#### Scenario: Stored path is invalid
- GIVEN a stored path that no longer exists on disk
- WHEN the app validates it on startup
- THEN it falls back to auto-detection
- AND notifies the user that the previous path was unavailable
