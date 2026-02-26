## ADDED Requirements

### Requirement: Shotstack SDK field validation
The system SHALL validate all fields against Shotstack API specifications.

#### Scenario: Valid transition field
- **WHEN** transition field contains valid Shotstack transition name
- **THEN** system SHALL accept field as valid

#### Scenario: Invalid transition field
- **WHEN** transition field contains unknown transition name
- **THEN** system SHALL return warning with list of valid transitions

#### Scenario: Valid effect field
- **WHEN** effect field contains valid Shotstack effect name
- **THEN** system SHALL accept field as valid

#### Scenario: Invalid effect field
- **WHEN** effect field contains unknown effect name
- **THEN** system SHALL return warning with list of valid effects

#### Scenario: Valid filter field
- **WHEN** filter field contains valid Shotstack filter name
- **THEN** system SHALL accept field as valid

#### Scenario: Invalid filter field
- **WHEN** filter field contains unknown filter name
- **THEN** system SHALL return warning with list of valid filters