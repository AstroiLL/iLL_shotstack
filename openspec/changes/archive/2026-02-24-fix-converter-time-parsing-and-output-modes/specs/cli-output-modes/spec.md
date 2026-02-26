## ADDED Requirements

### Requirement: Support verbose output mode
The system SHALL support a verbose mode (`-v` or `--verbose` flag) that displays detailed, line-by-line information about the conversion or validation process.

#### Scenario: Verbose mode in converter
- **WHEN** user runs `convert_script.py script.md -v`
- **THEN** the system SHALL display each parsing step
- **AND** show each clip being processed with its details
- **AND** show merge fields being generated

#### Scenario: Verbose mode in checker
- **WHEN** user runs `check.py script.json -v`
- **THEN** the system SHALL display each validation step
- **AND** show detailed information about placeholders found
- **AND** display all OK checks (not just errors/warnings)

### Requirement: Support quiet output mode
The system SHALL support a quiet mode (`-q` or `--quiet` flag) that suppresses all output except for the exit code, suitable for automated/scripted execution.

#### Scenario: Quiet mode success
- **WHEN** user runs `convert_script.py script.md -q` and conversion succeeds
- **THEN** no output SHALL be displayed to stdout or stderr
- **AND** exit code SHALL be `0`

#### Scenario: Quiet mode failure
- **WHEN** user runs `check.py invalid.json -q` and validation fails
- **THEN** no output SHALL be displayed to stdout or stderr
- **AND** exit code SHALL be `1`

#### Scenario: Quiet mode in automated scripts
- **WHEN** the tool is invoked from a shell script with `-q` flag
- **THEN** the script SHALL be able to check `$?` to determine success/failure
- **AND** no terminal output SHALL interfere with script processing

### Requirement: Default normal output mode
The system SHALL use a default "normal" mode that displays only essential information: input/output file names, project name, resources directory, and summary statistics.

#### Scenario: Normal mode conversion output
- **WHEN** user runs `convert_script.py script.md` without flags
- **THEN** output SHALL display: `Converted: script.md -> script.json`
- **AND** display: `Name: <project_name>`
- **AND** display: `Resources: <resources_dir>`
- **AND** display: `Clips: <count>`
- **AND** no other verbose information SHALL be shown

#### Scenario: Normal mode check output
- **WHEN** user runs `check.py script.json` without flags
- **THEN** output SHALL display validation summary with errors/warnings count
- **AND** display final result status
- **AND** OK checks SHALL NOT be displayed (unlike verbose mode)
