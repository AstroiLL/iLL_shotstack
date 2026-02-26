## ADDED Requirements

### Requirement: Workspace project structure support
The system SHALL support workspace structure where each project resides in its own directory containing scripts, media, and output files.

#### Scenario: Project directory structure
- **WHEN** project is located at `/workspace/MyProject/`
- **THEN** the system SHALL treat this as the working directory
- **AND** all relative paths SHALL be resolved from this directory

#### Scenario: Multiple projects in workspace
- **WHEN** workspace contains multiple projects:
  ```
  /workspace/
  ├── ProjectA/
  │   ├── script.json
  │   └── Content/
  └── ProjectB/
      ├── script.json
      └── Media/
  ```
- **THEN** each project SHALL be isolated
- **AND** validation/build of ProjectA SHALL NOT affect ProjectB

### Requirement: Consistent path resolution
The system SHALL consistently resolve all relative paths from the directory containing the JSON script file.

#### Scenario: Convert from project directory
- **GIVEN** user runs command from `/workspace/MyProject/`
- **WHEN** executing `convert_script.py script.md`
- **THEN** output SHALL be created in `/workspace/MyProject/`
- **AND** paths SHALL be relative to this directory

#### Scenario: Convert from different directory
- **GIVEN** user runs command from `/workspace/`
- **WHEN** executing `convert_script.py ProjectA/script.md`
- **THEN** output SHALL be created in `/workspace/ProjectA/`
- **AND** paths SHALL be relative to `/workspace/ProjectA/`
