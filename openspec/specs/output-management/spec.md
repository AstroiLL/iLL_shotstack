# Output Management

## Purpose

Provides configurable output file management including default locations, naming conventions, automatic indexing to prevent overwrites, and custom output path options via CLI.

## Requirements

### Requirement: Default output directory
The system SHALL create output files in an `output/` subdirectory within the working directory by default.

#### Scenario: Default output location
- **GIVEN** JSON file is located at `/project/script.json`
- **WHEN** assembling video without explicit output flag
- **THEN** output SHALL be saved to `/project/output/script.mp4`
- **AND** directory `output/` SHALL be created if it doesn't exist

### Requirement: Output filename matching script name
The system SHALL name the output file based on the script name (without extension).

#### Scenario: Name from JSON filename
- **GIVEN** script file is named `my_video.json`
- **WHEN** assembling video
- **THEN** output filename SHALL be `my_video.mp4`
- **AND** format SHALL match `output.format` from JSON

#### Scenario: Name from project name
- **GIVEN** JSON contains `name: "SummerVacation"`
- **WHEN** assembling video
- **THEN** output filename SHALL be `SummerVacation.mp4`

### Requirement: Automatic file indexing
The system SHALL NOT overwrite existing output files. Instead, it SHALL automatically add an index to the filename.

#### Scenario: First output
- **GIVEN** no output file exists
- **WHEN** assembling video from `script.json`
- **THEN** output SHALL be `output/script.mp4`

#### Scenario: Second output
- **GIVEN** `output/script.mp4` already exists
- **WHEN** assembling video again
- **THEN** output SHALL be `output/script_1.mp4`

#### Scenario: Multiple outputs
- **GIVEN** `output/script.mp4` and `output/script_1.mp4` exist
- **WHEN** assembling video again
- **THEN** output SHALL be `output/script_2.mp4`

### Requirement: Custom output path via CLI
The system SHALL support specifying custom output directory and/or filename via command line.

#### Scenario: Custom output directory
- **WHEN** running `assemble.py script.json -o /custom/path/`
- **THEN** output SHALL be saved to `/custom/path/script.mp4`

#### Scenario: Custom output file
- **WHEN** running `assemble.py script.json -o /custom/path/result.mp4`
- **THEN** output SHALL be saved to `/custom/path/result.mp4`
- **AND** automatic indexing SHALL still apply if file exists

#### Scenario: Relative output path
- **GIVEN** working directory is `/project/`
- **WHEN** running `assemble.py script.json -o ../renders/`
- **THEN** output SHALL be saved to `/renders/script.mp4`