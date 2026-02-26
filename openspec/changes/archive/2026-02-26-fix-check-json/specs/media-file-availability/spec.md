## ADDED Requirements

### Requirement: Media file availability check
The system SHALL verify that all referenced media files exist in local filesystem.

#### Scenario: All files available
- **WHEN** all media files referenced in merge array exist
- **THEN** system SHALL return validation success

#### Scenario: Missing media file
- **WHEN** referenced media file does not exist
- **THEN** system SHALL return error with missing file path

#### Scenario: Inaccessible media file
- **WHEN** referenced media file exists but lacks read permissions
- **THEN** system SHALL return error indicating permission issue

#### Scenario: Relative path resolution
- **WHEN** media files referenced with relative paths
- **THEN** system SHALL resolve paths relative to script location