# Migration Guide: Upgrading to the New Validation System

## Introduction

This guide helps you upgrade from the legacy `check_json.py` to the new modular validation system in Fast-Clip. The new system provides comprehensive validation, better performance, and more flexibility.

## Table of Contents

1. [Quick Start](#quick-start)
2. [What's New](#whats-new)
3. [Migration Steps](#migration-steps)
4. [Configuration](#configuration)
5. [Common Use Cases](#common-use-cases)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

## Quick Start

### Minimal Migration

The simplest migration is just changing the command:

```bash
# Old
python check_json.py script.json

# New
python check.py script.json
```

That's it! The new command will work with your existing scripts.

### With Verbose Output

```bash
# Old
python check_json.py -v script.json

# New
python check.py -v script.json
```

## What's New

### Enhanced Validation

The new system validates:
- ✅ JSON syntax and structure
- ✅ Required fields (template, output, merge)
- ✅ Media file availability
- ✅ Shotstack SDK fields (transitions, effects, filters)
- ✅ Placeholder syntax
- ✅ Merge array structure

### Performance Improvements

- ⚡ Parallel file checking for large projects
- ⚡ Result caching to avoid redundant checks
- ⚡ Configurable worker count and thresholds

### New Features

- 📝 Configuration file support
- 📝 Environment variable support
- 📝 Strict validation mode
- 📝 Skip validation option for quick operations

## Migration Steps

### Step 1: Test with Existing Scripts

Validate your current scripts with the new system:

```bash
python check.py your_script.json
```

Review the output for any new warnings or errors.

### Step 2: Review Validation Results

Check for new validation warnings:

```bash
python check.py -v your_script.json
```

Look for:
- File accessibility warnings
- Field validation warnings (transitions, effects, filters)
- Missing required fields
- Placeholder syntax issues

### Step 3: Update Command References

Replace all occurrences of `check_json.py` with `check.py` in:

- Shell scripts
- Makefiles
- CI/CD pipelines
- Documentation
- Build scripts

Example Makefile:

```makefile
# Old
validate:
	python check_json.py script.json

# New
validate:
	python check.py script.json
```

Example GitHub Actions:

```yaml
# Old
- name: Validate
  run: python check_json.py script.json

# New
- name: Validate
  run: python check.py script.json
```

### Step 4: Configure (Optional)

Create a `.validation.toml` file for project-specific settings:

```bash
cp .validation.toml.example .validation.toml
```

Edit `.validation.toml`:

```toml
[validation]
strict_mode = false
max_workers = 8
parallel_threshold = 5
skip_file_validation = false
enable_cache = true
verbose = false
```

### Step 5: Update CI/CD Pipelines

Update your CI/CD configuration to use the new command:

```yaml
# Example: .github/workflows/validate.yml
name: Validate Scripts

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Validate scripts
        run: |
          python check.py script.json
```

## Configuration

### Configuration File

Create `.validation.toml` in your project root:

```toml
[validation]
# Enable strict mode (warnings become errors)
strict_mode = false

# Maximum number of parallel workers
max_workers = 8

# Minimum files to trigger parallel validation
parallel_threshold = 5

# Skip file accessibility checks
skip_file_validation = false

# Enable result caching
enable_cache = true

# Enable verbose output
verbose = false
```

### Environment Variables

You can also configure via environment variables:

```bash
export VALIDATION_STRICT_MODE=false
export VALIDATION_MAX_WORKERS=8
export VALIDATION_PARALLEL_THRESHOLD=5
export VALIDATION_SKIP_FILE_VALIDATION=false
export VALIDATION_ENABLE_CACHE=true
export VALIDATION_VERBOSE=false
```

### Command-Line Flags

Command-line flags override configuration file and environment variables:

```bash
python check.py --strict script.json
python check.py --skip-validate script.json
python check.py -v script.json
python check.py -q script.json
```

Priority: Command-line > Environment variables > Configuration file

## Common Use Cases

### Basic Validation

```bash
python check.py script.json
```

### Verbose Output

```bash
python check.py -v script.json
```

### Strict Mode

```bash
python check.py --strict script.json
```

In strict mode, warnings become errors.

### Skip Validation (Quick Operation)

```bash
python check.py --skip-validate script.json
```

Only checks JSON syntax, skips comprehensive validation.

### Quiet Mode (CI/CD)

```bash
python check.py -q script.json
```

Suppresses all output, only returns exit code (0 = success, 1 = failure).

### Configuration with Environment Variables

```bash
export VALIDATION_STRICT_MODE=true
python check.py script.json
```

## Troubleshooting

### Issue: New Warnings Appear

**Problem:** Your script now shows warnings that didn't appear before.

**Solution:** Review the warnings and decide if they need fixing. Common warnings:
- File not found: Check file paths
- Invalid transition: Use a valid Shotstack transition
- Invalid effect: Use a valid Shotstack effect
- Invalid filter: Use a valid Shotstack filter

### Issue: Validation Takes Longer

**Problem:** Validation is slower than before.

**Solution:**
1. Enable caching: Set `enable_cache = true` in `.validation.toml`
2. Adjust parallel threshold: Set `parallel_threshold = 10` for more parallel processing
3. Adjust worker count: Set `max_workers = 4` for fewer workers if CPU is limited

### Issue: File Path Errors

**Problem:** Files are reported as not found even though they exist.

**Solution:**
1. Check that file paths are relative to the script directory
2. Verify file permissions
3. Use absolute paths if relative paths don't work

### Issue: Transition/Effect Warnings

**Problem:** Warnings about invalid transitions or effects.

**Solution:** Check the list of valid values:

**Valid Transitions:**
- fade, fadefast, fadeslow
- slideleft, slideright, slideup, slidedown
- wipeleft, wiperight
- carouselleft, carouselright, carouselupfast
- shuffleleftbottom, shuffletopright
- reveal, revealfast, revealslow
- zoom, zoomfast, zoomslow

**Valid Effects:**
- zoomIn, zoomOut, kenBurns

**Valid Filters:**
- boost, greyscale, contrast, muted

## FAQ

### Q: Do I need to change my scripts?

**A:** No. Your existing scripts will work without modification. The new validation system checks the same format.

### Q: Can I keep using `check_json.py`?

**A:** Yes, for now. However, it's deprecated and will be removed in a future release. Please migrate to `check.py`.

### Q: Will this affect my build time?

**A:** The new system is faster for large projects due to parallel processing and caching. Small projects may see negligible difference.

### Q: What if I don't want all the validation checks?

**A:** Use `--skip-validate` to skip comprehensive validation, or configure specific options in `.validation.toml`.

### Q: Can I use the validation modules programmatically?

**A:** Yes. Import the validation modules:

```python
from fast_clip.check.validation import (
    JsonValidator,
    FileChecker,
    FieldValidator,
    ValidationConfig
)
```

### Q: How do I report bugs or request features?

**A:** Open an issue on the GitHub repository with details about the problem or feature request.

## Additional Resources

- **Main Documentation:** `README.md`
- **Backward Compatibility Notice:** `BACKWARD_COMPATIBILITY.md`
- **Migration Script:** `python migrate_validation.py`
- **Examples:** `docs/validation_examples.md`
- **Configuration Example:** `.validation.toml.example`

## Support

If you need help with migration:

1. Run the migration script: `python migrate_validation.py`
2. Check the backward compatibility notice: `BACKWARD_COMPATIBILITY.md`
3. Review the examples: `docs/validation_examples.md`
4. Open an issue on GitHub for support

---

**Version:** 0.2.0
**Last Updated:** 2026-02-26
