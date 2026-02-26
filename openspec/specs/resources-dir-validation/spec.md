# Resources Directory Validation

## Purpose

Ensures proper validation of media file resources relative to the JSON script location, with correct placeholder resolution for workspace-based projects.

## Requirements

### Requirement: Resources directory validation relative to JSON file location
The system SHALL validate existence of media files relative to the directory containing the JSON script file, not the current working directory.

#### Scenario: Validate resources in project directory
- **WHEN** validating a JSON script located at `/project/video.json`
- **AND** the script contains `resourcesDir: "Content"`
- **THEN** the system SHALL look for files in `/project/Content/`
- **AND** NOT in the current working directory

#### Scenario: Handle absolute paths in resourcesDir
- **WHEN** `resourcesDir` is an absolute path like `/home/user/Videos`
- **THEN** the system SHALL use that absolute path directly
- **AND** ignore the JSON file location

#### Scenario: Missing resourcesDir defaults to current directory
- **WHEN** `resourcesDir` is not specified in JSON
- **THEN** the system SHALL look for files in the same directory as the JSON file

### Requirement: Correct placeholder validation
The system SHALL validate that files referenced in merge placeholders exist in the resources directory.

#### Scenario: Validate placeholder files exist
- **WHEN** JSON contains `{{Content/video.mp4}}` placeholder
- **AND** validating with `check.py`
- **THEN** the system SHALL check if `Content/video.mp4` exists
- **AND** report warning only if file is actually missing

#### Scenario: Suppress false warnings for placeholder files
- **WHEN** placeholder references a file that exists in resources directory
- **THEN** no warning SHALL be displayed
- **AND** validation SHALL pass successfully