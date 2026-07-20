# Remoção Specification

## Purpose

Define how ACE_GUI performs clean uninstallation of previously installed mods and liveries. The system SHALL remove all physical files associated with installed content, revert any configuration changes, and provide a rollback mechanism in case of accidental deletion. This ensures the user can safely manage their ACE content without manual filesystem navigation or risk of data loss.

## Requirements

### Requirement: Mod uninstallation

The system SHALL remove an installed car mod by deleting its files from `{ACE_PATH}/Mods/` and cleaning up any associated metadata.

#### Scenario: Mod successfully removed
- GIVEN an installed mod listed in the mods panel
- WHEN the user clicks the delete button on that mod
- THEN a confirmation dialog is shown
- AND upon confirmation, the mod's file or directory is deleted from `Mods/`
- AND the mod is removed from the installed mods list
- AND a success notification is displayed

#### Scenario: Mod file locked by another process
- GIVEN the mod file is in use by another process
- WHEN deletion fails
- THEN an error message tells the user which file could not be deleted
- AND suggests closing ACE before retrying

### Requirement: Livery uninstallation

The system SHALL remove an installed livery by deleting its directory from `{ACE_PATH}/External Liveries/<car_guid>/` and cleaning up any references.

#### Scenario: Livery successfully removed
- GIVEN an installed livery listed in the liveries panel
- WHEN the user clicks the delete button
- THEN the livery's subdirectory under `External Liveries/` is deleted
- AND the livery is removed from the active liveries list

#### Scenario: Deleting last livery of a car
- GIVEN the last livery for a specific car is being removed
- WHEN deletion completes
- THEN the car's directory under `External Liveries/` is also removed if empty
- AND no empty orphan directories remain

### Requirement: Rollback on failed uninstall

The system SHALL create a temporary backup of content before deletion, so that if the deletion fails mid-operation, the system can restore the original state.

#### Scenario: Partial deletion failure with rollback
- GIVEN a mod with multiple files
- WHEN some files are deleted and then an error occurs
- THEN the backup is restored from the temporary location
- AND the user is notified of the failure and rollback
- AND no data loss occurs

### Requirement: Uninstall logging

The system SHALL log every uninstall operation with timestamp, content name, and outcome for audit trail purposes.

#### Scenario: Audit log after uninstall
- GIVEN a successful uninstall
- WHEN the operation completes
- THEN an entry is written to the audit log
- AND the entry includes: timestamp, content name, content type, and "success" status

#### Scenario: Audit log on failed uninstall
- GIVEN a failed uninstall
- WHEN the error occurs
- THEN an entry is written with the error details and "failed" status
- AND the rollback is also logged
