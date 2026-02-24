## Why

The current validation script (`check.py`) only partially supports the template + merge workflow structure. While it handles both flat and template-wrapped structures for basic fields, it doesn't validate:
1. Placeholder syntax in template values (`{{placeholders}}`)
2. The presence and structure of the `merge` array
3. Whether merge fields match the placeholders used in the template

This leads to validation passing on scripts that will fail during assembly, causing confusing errors late in the workflow. Proper validation at the check stage will catch these issues early.

## What Changes

- Add validation for `template` field structure in script JSON
- Add validation for `merge` array presence and structure
- Add validation to ensure placeholder syntax follows the `{{field}}` pattern
- Add validation to ensure merge fields referenced in placeholders exist in the merge array
- Add validation to ensure all merge array entries have required fields (src, dest)
- Update error messages to be clearer about template vs merge issues

## Capabilities

### New Capabilities
- `template-validation`: Enhanced validation of template + merge workflow structure including placeholder syntax checking and merge array validation

### Modified Capabilities
- *(none)*

## Impact

- **check.py**: Core validation logic will be extended
- **AGENTS.md**: Documentation may need updates to reflect new validation rules
- All existing scripts will be re-validated with stricter rules (may reveal previously missed issues)
