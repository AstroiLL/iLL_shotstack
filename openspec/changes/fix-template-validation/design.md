## Context

The Fast-Clip project uses a "template + merge" workflow for Shotstack video assembly. Script JSON files contain:
- A `template` object with placeholder syntax (`{{field}}`) in values
- A `merge` array containing replacement data for those placeholders

The current `check.py` validator (509 lines) handles basic validation of flat and template-wrapped structures but misses:
1. Invalid placeholder syntax (e.g., `{file}` instead of `{{file}}`)
2. Missing `merge` array when template has placeholders
3. Placeholders referencing fields not present in merge array
4. Malformed merge entries missing required `src` or `dest` fields

This causes assembly-time failures that should be caught during validation.

## Goals / Non-Goals

**Goals:**
- Validate placeholder syntax follows the `{{field}}` pattern using regex
- Validate `merge` array exists when template contains placeholders
- Validate all placeholders in template have corresponding entries in `merge`
- Validate each merge entry has required `src` and `dest` fields
- Provide clear error messages distinguishing template vs merge issues
- Maintain backward compatibility with existing validation logic

**Non-Goals:**
- Validating the actual file paths in `src` fields (assembly-time concern)
- Checking if `dest` paths are valid (assembly-time concern)
- Modifying the converter or assembler scripts
- Adding new validation for non-template fields (already covered)

## Decisions

**Decision 1: Regex-based placeholder detection**
- Use pattern `\{\{([^}]+)\}\}` to detect valid placeholders
- This captures content between `{{` and `}}` without nested braces
- Rationale: Simple, fast, and matches the project's current placeholder convention

**Decision 2: Recursive template scanning**
- Scan all string values recursively in the template object
- Use a helper function that walks nested dicts/lists
- Rationale: Placeholders can appear at any depth (e.g., `template.timeline.tracks[0].clips[0].asset.src`)

**Decision 3: Merge field mapping strategy**
- Build a set of `find` values from merge array
- Compare against set of placeholders found in template
- Report missing fields with specific paths where they're used
- Rationale: Provides actionable error messages showing exactly which placeholders lack merge data

**Decision 4: Validation method placement**
- Add `check_template_structure()` method to `ScriptChecker` class
- Add `check_merge_array()` method to `ScriptChecker` class
- Call these from existing `run()` method after basic validation
- Rationale: Keeps validation organized and maintains existing code structure

## Risks / Trade-offs

**[Risk] False positives on edge-case placeholder formats**
→ Users might use `{{nested{field}}}` or other unusual patterns
→ **Mitigation**: Document the supported pattern clearly in error messages

**[Risk] Performance impact on large templates**
→ Recursive scanning of deeply nested structures
→ **Mitigation**: Template depth is typically limited (Shotstack API has constraints), overhead is minimal

**[Risk] Breaking existing workflows that relied on lax validation**
→ Some scripts might pass validation but have placeholder typos
→ **Mitigation**: This is the intended behavior - catching real errors

**[Trade-off] Strict validation vs flexibility**
→ We validate merge array entries have `src` and `dest` fields
→ Shotstack might accept additional fields we don't know about
→ **Acceptance**: We validate core required fields; additional fields are allowed (not an error)
