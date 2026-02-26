# Backward Compatibility Notice

## Overview

Fast-Clip has been updated with a comprehensive validation system. This notice describes how the changes affect existing workflows and provides guidance for migration.

## What Changed

### New Validation System

The validation system has been completely restructured with:
- Modular validation framework (`fast_clip/check/validation/`)
- Comprehensive JSON structure validation
- Media file availability checking
- Shotstack SDK field validation
- Performance optimizations for large projects
- Configuration file support

### Script Changes

**Old Command:**
```bash
python check_json.py script.json
```

**New Command:**
```bash
python check.py script.json
```

### API Changes

The `check_script()` function remains compatible, but now uses the new validation framework internally.

```python
# Old usage (still works)
from fast_clip.check import check_script
is_valid, results = check_script(Path("script.json"), verbose=True)

# New usage with additional options
is_valid, results = check_script(
    Path("script.json"),
    verbose=True,
    quiet=False,
    skip_validate=False,
    strict_mode=False
)
```

## Migration Guide

### 1. Update Command Line Scripts

Replace `check_json.py` with `check.py`:

```bash
# Old
python check_json.py script.json
python check_json.py -v script.json

# New
python check.py script.json
python check.py -v script.json
```

### 2. Update Import Statements

The import path remains the same, but new options are available:

```python
# Existing import (still works)
from fast_clip.check import check_script

# New validation modules available
from fast_clip.check.validation import (
    JsonValidator,
    FileChecker,
    FieldValidator,
    ValidationConfig
)
```

### 3. Review Validation Output

The new validation system provides more detailed output:

- **ERROR**: Critical issues that must be fixed
- **WARNING**: Recommended fixes (non-blocking)
- **INFO**: Informational messages
- **Suggestions**: Specific recommendations for fixing issues

### 4. Optional Configuration

Create `.validation.toml` for project-specific settings:

```toml
[validation]
strict_mode = false
max_workers = 8
parallel_threshold = 5
enable_cache = true
verbose = false
```

### 5. Update CI/CD Pipelines

If using validation in CI/CD, update commands:

```yaml
# Old
- name: Validate Script
  run: python check_json.py script.json

# New
- name: Validate Script
  run: python check.py script.json
```

## Breaking Changes

### Deprecation of `check_json.py`

The `check_json.py` script is deprecated and will be removed in a future release.

**Action Required:** Migrate to `check.py` before the next major version.

### Warning in Output

Running `check_json.py` now shows a deprecation warning:

```
⚠️  WARNING: check_json.py is deprecated
Please migrate to the new 'check.py' script
Run 'python migrate_validation.py' for information
```

## New Features

### 1. Additional Validation Checks

The new system validates:
- JSON structure and syntax
- Required fields (template, output, merge)
- Media file availability and permissions
- Shotstack SDK fields (transitions, effects, filters)
- Placeholder syntax (`{{field}}`)
- Merge array structure

### 2. Performance Improvements

- Parallel file checking for large projects
- Result caching to avoid redundant checks
- Configurable worker count and thresholds

### 3. Configuration Options

- Configuration file (`.validation.toml`)
- Environment variables (`VALIDATION_*`)
- Command-line flags
- Programmatic configuration

### 4. Enhanced CLI

```bash
python check.py [options] <script.json>

Options:
  -v, --verbose    Show detailed output
  -q, --quiet      Suppress all output (exit code only)
  --skip-validate  Skip comprehensive validation
  --strict         Enable strict validation mode
  -h, --help       Show help
```

## Testing Your Migration

### 1. Test with Existing Scripts

Run validation on your existing scripts:

```bash
python check.py your_script.json
```

### 2. Review Validation Output

Check for new warnings or suggestions:

```bash
python check.py -v your_script.json
```

### 3. Update Configuration

Create `.validation.toml` if needed:

```bash
cp .validation.toml.example .validation.toml
# Edit .validation.toml with your settings
```

### 4. Update Workflows

Update any scripts, makefiles, or CI/CD pipelines to use `check.py`.

## Rollback Plan

If you encounter issues, you can temporarily use the old validation by setting an environment variable:

```bash
export VALIDATION_SKIP_FILE_VALIDATION=true
python check.py script.json
```

Note: This is for temporary rollback only. Please migrate fully as soon as possible.

## Support and Resources

- **Migration Guide:** Run `python migrate_validation.py`
- **Documentation:** See `README.md`
- **Examples:** See `docs/validation_examples.md`
- **Issues:** Report bugs and request features on GitHub

## Timeline

- **Now:** `check_json.py` shows deprecation warning
- **Next Release:** `check_json.py` will be removed
- **Action Required:** Migrate to `check.py` before next release

## Questions?

If you have questions about the migration:

1. Check the migration guide: `python migrate_validation.py`
2. Review the documentation: `README.md`
3. Check the examples: `docs/validation_examples.md`
4. Open an issue on GitHub for support

---

**Last Updated:** 2026-02-26
**Version:** 0.2.0
