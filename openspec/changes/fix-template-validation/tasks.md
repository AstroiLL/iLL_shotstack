## 1. Add Placeholder Detection Utilities

- [x] 1.1 Add regex pattern constant for placeholder detection (`\{\{([^}]+)\}\}`)
- [x] 1.2 Add helper function to recursively scan template for placeholders with path tracking
- [x] 1.3 Add helper function to extract all unique placeholders from a template

## 2. Implement Template Structure Validation

- [x] 2.1 Add `check_template_structure()` method to ScriptChecker class
- [x] 2.2 Validate template field is an object when present
- [x] 2.3 Call `check_template_structure()` from `run()` method

## 3. Implement Merge Array Validation

- [x] 3.1 Add `check_merge_array()` method to ScriptChecker class
- [x] 3.2 Validate merge array exists when template has placeholders
- [x] 3.3 Validate merge array is not empty when placeholders exist
- [x] 3.4 Validate each merge entry has required `find` field
- [x] 3.5 Validate each merge entry has required `replace` field
- [x] 3.6 Warn if merge entry has empty `find` value
- [x] 3.7 Call `check_merge_array()` from `run()` method

## 4. Implement Placeholder-Merge Matching

- [x] 4.1 Extract all placeholders from template using recursive scan
- [x] 4.2 Build set of `find` values from merge array
- [x] 4.3 Compare placeholder set against merge set
- [x] 4.4 Report ERROR for each placeholder missing from merge array
- [x] 4.5 Include JSON path in error messages showing where placeholder is used

## 5. Implement Placeholder Syntax Validation

- [x] 5.1 Validate placeholder syntax follows `{{field}}` pattern
- [x] 5.2 Warn on single brace usage (`{field}`)
- [x] 5.3 Warn on mismatched braces (`{{field}`)
- [x] 5.4 Warn on empty placeholders (`{{}}`)

## 6. Testing and Documentation

- [x] 6.1 Test with valid template + merge structure (should pass)
- [x] 6.2 Test with missing merge array (should fail with clear error)
- [x] 6.3 Test with invalid placeholder syntax (should warn)
- [x] 6.4 Test with placeholder missing from merge (should fail)
- [x] 6.5 Test with missing required merge fields (should fail)
- [x] 6.6 Run existing test suite to ensure no regressions
- [x] 6.7 Update AGENTS.md if validation behavior changes significantly
