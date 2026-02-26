## ADDED Requirements

### Requirement: Validation integration in converter
The system SHALL automatically validate JSON before MD to JSON conversion.

#### Scenario: Conversion with valid script
- **WHEN** user runs convert_script.py with valid MD script
- **THEN** system SHALL validate generated JSON before saving
- **AND** conversion SHALL complete successfully

#### Scenario: Conversion with invalid script
- **WHEN** conversion generates invalid JSON
- **THEN** system SHALL report validation errors
- **AND** conversion SHALL stop with informative error message

### Requirement: Validation integration in assembler
The system SHALL automatically validate JSON before video assembly.

#### Scenario: Assembly with valid JSON
- **WHEN** user runs assemble.py with valid JSON script
- **THEN** system SHALL validate JSON before starting assembly
- **AND** assembly SHALL proceed normally

#### Scenario: Assembly with invalid JSON
- **WHEN** user runs assemble.py with invalid JSON script
- **THEN** system SHALL report validation errors
- **AND** assembly SHALL stop without consuming API credits

### Requirement: Standalone validation execution
The system SHALL support standalone validation execution.

#### Scenario: Direct validation
- **WHEN** user runs check.py with JSON file argument
- **THEN** system SHALL perform complete validation
- **AND** display structured results with errors, warnings, and suggestions