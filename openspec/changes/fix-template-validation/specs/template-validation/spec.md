## ADDED Requirements

### Requirement: Template field structure validation
The validation system SHALL check that when a `template` field is present in the script JSON, it contains valid nested objects.

#### Scenario: Valid template structure
- **WHEN** a script contains a template field with valid nested objects
- **THEN** validation SHALL pass without errors

#### Scenario: Invalid template type
- **WHEN** a script contains a template field that is not an object
- **THEN** validation SHALL report an ERROR indicating the template must be an object

### Requirement: Merge array structure validation
The validation system SHALL check that when placeholders exist in the template, a `merge` array is present and contains valid entries.

#### Scenario: Template with placeholders has merge array
- **WHEN** a template contains placeholders and a merge array is present
- **THEN** validation SHALL continue to merge entry validation

#### Scenario: Template with placeholders missing merge array
- **WHEN** a template contains placeholders but no merge array is present
- **THEN** validation SHALL report an ERROR indicating merge array is required

#### Scenario: Empty merge array
- **WHEN** a merge array exists but is empty and template has placeholders
- **THEN** validation SHALL report an ERROR indicating no merge data for placeholders

### Requirement: Placeholder syntax validation
The validation system SHALL verify that all placeholders in template values follow the `{{field}}` pattern using double braces.

#### Scenario: Valid placeholder syntax
- **WHEN** a template value contains `{{resources_dir/video.mp4}}`
- **THEN** validation SHALL recognize it as a valid placeholder

#### Scenario: Invalid placeholder - single braces
- **WHEN** a template value contains `{resources_dir/video.mp4}`
- **THEN** validation SHALL report a WARNING indicating invalid placeholder syntax

#### Scenario: Invalid placeholder - mismatched braces
- **WHEN** a template value contains `{{resources_dir/video.mp4}`
- **THEN** validation SHALL report a WARNING indicating invalid placeholder syntax

#### Scenario: Invalid placeholder - empty braces
- **WHEN** a template value contains `{{}}`
- **THEN** validation SHALL report a WARNING indicating empty placeholder

### Requirement: Merge field matching validation
The validation system SHALL verify that every placeholder in the template has a corresponding entry in the merge array.

#### Scenario: All placeholders have merge entries
- **WHEN** template contains `{{video1}}` and merge array has `{ "find": "video1", "replace": "..." }`
- **THEN** validation SHALL pass without errors

#### Scenario: Placeholder missing merge entry
- **WHEN** template contains `{{video1}}` but merge array has no entry with `find: "video1"`
- **THEN** validation SHALL report an ERROR indicating missing merge data for placeholder

#### Scenario: Multiple placeholders - one missing
- **WHEN** template contains `{{video1}}` and `{{video2}}` but merge only has entry for `video1`
- **THEN** validation SHALL report an ERROR for the missing `video2` merge entry

### Requirement: Merge entry required fields validation
The validation system SHALL verify that each merge array entry contains the required `find` and `replace` fields.

#### Scenario: Valid merge entry
- **WHEN** a merge entry contains both `find` and `replace` fields
- **THEN** validation SHALL pass for that entry

#### Scenario: Missing find field
- **WHEN** a merge entry lacks the `find` field
- **THEN** validation SHALL report an ERROR indicating missing required field

#### Scenario: Missing replace field
- **WHEN** a merge entry lacks the `replace` field
- **THEN** validation SHALL report an ERROR indicating missing required field

#### Scenario: Empty find value
- **WHEN** a merge entry has an empty string for the `find` field
- **THEN** validation SHALL report a WARNING indicating empty find value

### Requirement: Placeholder location tracking
The validation system SHALL report the specific location (JSON path) where each placeholder is used when reporting errors.

#### Scenario: Report placeholder location
- **WHEN** a placeholder at `template.timeline.tracks[0].clips[0].asset.src` lacks merge data
- **THEN** the error message SHALL include the path `template.timeline.tracks[0].clips[0].asset.src`
