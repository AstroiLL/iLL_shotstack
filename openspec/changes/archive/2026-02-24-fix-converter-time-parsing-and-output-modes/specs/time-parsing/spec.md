## ADDED Requirements

### Requirement: Parse MM:SS:mmm time format
The system SHALL correctly parse time strings in the format `MM:SS:mmm` where MM is minutes, SS is seconds, and mmm is milliseconds, converting them to total seconds as a float.

#### Scenario: Parse time with milliseconds
- **WHEN** the input time string is `00:01:800`
- **THEN** the parsed result SHALL be `1.8` seconds

#### Scenario: Parse time with leading zeros
- **WHEN** the input time string is `00:18:800`
- **THEN** the parsed result SHALL be `18.8` seconds

#### Scenario: Parse time range
- **WHEN** the input timing string is `00:00:000-00:01:800`
- **THEN** the start time SHALL be `0.0` seconds
- **AND** the end time SHALL be `1.8` seconds

#### Scenario: Calculate trim from time range
- **WHEN** the timing string is `00:01:800-00:18:800`
- **THEN** the trim value SHALL be `1.8` seconds (start of range)
