# Delta for v1-core

## ADDED Requirements

### Requirement: Application configuration file

The system SHALL store its configuration in a JSON file at `{user_config_dir}/ACE_GUI/config.json`.

#### Scenario: First launch
- GIVEN no existing config file
- WHEN the app starts
- THEN config.json is created with default values
- AND path detection runs

#### Scenario: Config file corruption
- GIVEN a corrupted config.json
- WHEN the app tries to read it
- THEN the file is reset to defaults
- AND the previous file is backed up as config.json.bak

### Requirement: SPKG format probe

The system SHALL inspect the first 4 bytes of any `.spkg` file to determine if it is a ZIP archive (PK\x03\x04 magic number) before deciding to extract or copy.

#### Scenario: ZIP magic number found
- GIVEN an `.spkg` file starting with PK\x03\x04
- WHEN format detection runs
- THEN it is treated as a ZIP archive for extraction

#### Scenario: Non-ZIP magic number
- GIVEN an `.spkg` file that does not start with PK\x03\x04
- WHEN format detection runs
- THEN it is treated as a raw binary to be copied
- AND a warning is logged for diagnostic

### Requirement: Livery JSON GUID injection

The system SHALL parse the livery JSON configuration file after extraction and set the `carguide` field to the GUID of the car selected by the user.

#### Scenario: GUID field updated
- GIVEN an extracted livery with a JSON config file containing a `carguide` field
- WHEN the user selects a car from the garage modal
- THEN the `carguide` field is overwritten with the selected car GUID
- AND the JSON is saved with correct formatting

#### Scenario: JSON config missing carguide field
- GIVEN a livery JSON config without a `carguide` field
- WHEN the system attempts GUID injection
- THEN the field is added to the JSON structure
- AND set to the selected car GUID

### Requirement: Garage car detection

The system SHALL read the user's saved cars from `{ACE_PATH}/profile_data/*/saved_cars/*.json` to populate the car selection modal during livery installation.

#### Scenario: Cars found in profile
- GIVEN saved_cars directory with JSON files
- WHEN livery installation starts
- THEN the system reads each JSON to extract car name and GUID
- AND presents them in the selection modal

#### Scenario: Multiple profiles
- GIVEN multiple profile directories under profile_data
- WHEN the system scans for saved cars
- THEN it aggregates cars from all profiles
- AND deduplicates by GUID
