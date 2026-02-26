# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Comprehensive Validation System**
  - New modular validation framework in `fast_clip/check/validation/`
  - JSON structure validation for Shotstack Template format
  - Media file availability checking with path resolution
  - Shotstack SDK field validation (transitions, effects, filters, aspect ratios)
  - Validation report system with ERROR, WARNING, and INFO levels
  - Caching support for improved performance

- **New Modules**
  - `JsonValidator` - Validates JSON syntax and structure
  - `FileChecker` - Checks media file accessibility and permissions
  - `FieldValidator` - Validates field values against Shotstack SDK
  - `ValidationConfig` - Configuration management for validation

- **Performance Optimizations**
  - Parallel file checking for large projects (configurable worker count)
  - Result caching to avoid redundant checks
  - Configurable parallel threshold (default: 5 files)
  - Optimized path resolution with directory caching

- **Configuration Support**
  - `.validation.toml` configuration file support
  - Environment variable support (`VALIDATION_*`)
  - Example configuration file (`.validation.toml.example`)
  - Configurable validation modes (strict, skip file validation, etc.)

- **Enhanced CLI Features**
  - New `check.py` script with comprehensive validation
  - `--strict` flag for strict validation mode
  - `--skip-validate` flag for quick operations
  - `--verbose` and `--quiet` mode flags
  - Structured error/warning/suggestion output

- **Integration**
  - Automatic validation in `convert_script.py` after conversion
  - Automatic validation in `assemble.py` before assembly
  - Early error detection to save API credits
  - Integrated validation workflow across all tools

- **Testing & Documentation**
  - Comprehensive test suite in `tests/data/`
  - Test cases for various validation scenarios
  - Migration guide (`migrate_validation.py`)
  - Updated documentation in `README.md`

### Changed
- `check.py` - Enhanced with new validation framework
  - Maintains backward compatibility with existing API
  - Improved error messages with suggestions
  - Better structured output with color-coded results

- `check_json.py` - Marked as deprecated
  - Now wraps new validation system internally
  - Deprecation warning on execution
  - Scheduled for removal in future release

### Deprecated
- `check_json.py` - Legacy validation wrapper
  - Please migrate to `check.py` for new features
  - Run `python migrate_validation.py` for migration guide
  - Will be removed in a future release

### Fixed
- JSON syntax validation with detailed error messages
- File path resolution relative to script location
- Detection of missing required fields
- Placeholder syntax validation (`{{field}}` pattern)
- Merge array structure validation
- Template and timeline structure validation

### Security
- Improved file permission checking before accessing files
- Better handling of symbolic links and special paths

## [0.1.0] - 2026-02-24

### Added
- Initial release of Fast-Clip video assembly utility
- Shotstack Template + Merge workflow
- Bidirectional MD ↔ JSON converter
- Basic JSON validation
- Video assembly orchestrator with Shotstack API integration
- File upload via Ingest API
- Text overlay support
- Sound effects track support
