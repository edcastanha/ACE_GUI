# Instalação Specification

## Purpose

Define how ACE_GUI handles installation of car mods (.spkg files) and custom liveries (.zip files) into the ACE game directory. The system SHALL process each content type according to ACE's expected directory structure, handle the mapping between livery ZIPs and in-game car IDs, and provide clear feedback on success or failure. This is the primary user-facing feature of the application.

## Requirements

### Requirement: SPKG mod installation

The system SHALL install `.spkg` car mod files by extracting or copying them into the `{ACE_PATH}/Mods/` directory.

#### Scenario: Successful SPKG install
- GIVEN a valid `.spkg` file selected by the user
- WHEN the user clicks "Install"
- THEN the file is copied to `{ACE_PATH}/Mods/`
- AND a success notification is displayed
- AND the mod appears in the installed mods list

#### Scenario: SPKG is a standard ZIP archive
- GIVEN an `.spkg` file that is a renamed ZIP archive
- WHEN the system inspects the file header
- THEN it extracts contents to `{ACE_PATH}/Mods/`
- AND preserves directory structure

#### Scenario: SPKG is a proprietary binary format
- GIVEN an `.spkg` file that is NOT a ZIP archive
- WHEN the system inspects the file header
- THEN it falls back to file copy (not extraction)
- AND logs the raw copy for diagnostic

#### Scenario: SPKG already exists
- GIVEN an `.spkg` file with the same name already installed
- WHEN the user attempts installation
- THEN a confirmation dialog asks whether to overwrite
- AND the existing mod is backed up before replacement

### Requirement: Livery ZIP installation

The system SHALL install livery `.zip` files by extracting them into `{ACE_PATH}/External Liveries/` and injecting the correct car GUID into the livery JSON configuration.

#### Scenario: Successful livery install with car selection
- GIVEN a valid livery `.zip` selected by the user
- WHEN the system detects the ZIP contains livery files
- THEN a modal displays the user's garage cars for selection
- AND the user selects the matching car
- AND the `.zip` is extracted to `{ACE_PATH}/External Liveries/<car_guid>/`
- AND the car GUID is injected into the `carguide` field of the livery JSON
- AND a success notification is displayed

#### Scenario: Livery ZIP extraction fails
- GIVEN a corrupted `.zip` file
- WHEN extraction is attempted
- THEN an error message is shown
- AND no partial files remain in External Liveries
- AND the user is asked to re-download the file

#### Scenario: Garage is empty
- GIVEN no cars found in the user's `profile_data/saved_cars`
- WHEN the user tries to install a livery
- THEN the modal shows "No cars found"
- AND the user can still proceed with a manual car GUID entry

### Requirement: Content type detection

The system SHALL automatically detect whether a selected file is an `.spkg` mod (car) or `.zip` livery (paint) and route it to the correct installation flow.

#### Scenario: File selected via drag-and-drop
- GIVEN a file dragged onto the app window
- WHEN the file has `.spkg` extension
- THEN the SPKG install flow starts
- WHEN the file has `.zip` extension
- THEN the livery install flow starts
- WHEN the file has any other extension
- THEN an error message says "Unsupported file type"

#### Scenario: Batch import
- The system MAY support batch installation of multiple files in a single operation for future phases.
