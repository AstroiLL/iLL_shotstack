# Deprecation and Removal Plan

## Overview

This document outlines the plan for removing deprecated code from the Fast-Clip project, specifically focusing on the `check_json.py` script.

## Deprecated Items

### 1. `check_json.py` Script

**Status:** Deprecated (current version)
**Planned Removal:** Version 1.0.0
**Alternative:** `check.py`

**Reason for Deprecation:**
- The new modular validation system (`check.py`) provides comprehensive validation
- `check_json.py` is now a thin wrapper around the new system
- Maintaining two scripts creates unnecessary complexity
- The new script provides better features and performance

## Timeline

### Current Release (0.2.0) - February 2026

- ✅ `check_json.py` marked as deprecated
- ✅ Deprecation warning added to script output
- ✅ Migration guide created
- ✅ Backward compatibility notice published
- ✅ Comprehensive documentation updated

### Next Release (0.3.0) - March 2026

- ⏳ Enhanced deprecation warning in `check_json.py`
- ⏳ Add version number to removal warning
- ⏳ Update all documentation to reference `check.py`
- ⏳ Update examples and tutorials
- ⏳ Send deprecation notice to users

### Future Release (1.0.0) - Q2 2026

- ⏳ Remove `check_json.py` from repository
- ⏳ Remove any internal references to `check_json.py`
- ⏳ Update CHANGELOG.md with removal
- ⏳ Add migration notice to release notes

## Migration Steps for Users

### Phase 1: Awareness (Current - Version 0.2.0)

**Goal:** Inform users about the upcoming deprecation

**Actions:**
- ✅ Deprecation warning in script output
- ✅ Migration guide published
- ✅ Documentation updated
- ⏳ Blog post/announcement

**User Action:**
- Review deprecation warning
- Read migration guide
- Test `check.py` with existing scripts

### Phase 2: Transition (Version 0.3.0)

**Goal:** Encourage users to migrate

**Actions:**
- ⏳ Enhanced deprecation warning with version number
- ⏳ Update all tutorials and examples
- ⏳ Add migration checklist to documentation

**User Action:**
- Update command references
- Test all scripts with `check.py`
- Update CI/CD pipelines
- Report any issues

### Phase 3: Removal (Version 1.0.0)

**Goal:** Remove deprecated code

**Actions:**
- ⏳ Delete `check_json.py`
- ⏳ Update release notes
- ⏳ Final migration reminder

**User Action:**
- Ensure all scripts use `check.py`
- Remove any references to `check_json.py`

## Impact Assessment

### Breaking Changes

**Yes:** Removal of `check_json.py` is a breaking change

**Impact:**
- Users still using `check_json.py` will need to update their workflows
- Old command-line scripts will fail
- CI/CD pipelines may break

**Mitigation:**
- Provide migration guide
- Give 2+ months notice
- Document the change clearly
- Test migration with users

### Non-Breaking Changes

**Yes:** The `check.py` API maintains backward compatibility with `check_script()` function

**Impact:**
- Programmatic usage remains compatible
- No code changes required for Python scripts

## Rollout Plan

### 1. Documentation Updates

- [x] Update `README.md` to reference `check.py`
- [x] Create migration guide
- [x] Create backward compatibility notice
- [x] Update AGENTS.md
- [ ] Update all tutorials and examples
- [ ] Update inline code comments
- [ ] Update API documentation

### 2. Deprecation Warnings

- [x] Add deprecation warning to `check_json.py`
- [ ] Enhance warning with version number (v0.3.0)
- [ ] Add warning to import statements if applicable
- [ ] Log deprecation warnings in verbose mode

### 3. Testing and Validation

- [x] Test `check.py` with existing scripts
- [x] Validate all features work correctly
- [ ] Performance testing
- [ ] User acceptance testing
- [ ] Collect user feedback

### 4. Communication

- [x] Document the change in CHANGELOG.md
- [x] Create migration guide
- [ ] Blog post announcement
- [ ] GitHub release notes
- [ ] Email/announcement to users

### 5. Removal

- [ ] Create checklist for removal
- [ ] Verify all users have migrated
- [ ] Delete `check_json.py` from repository
- [ ] Remove from documentation
- [ ] Update CHANGELOG.md
- [ ] Publish release notes

## Verification Checklist

Before removing `check_json.py`, verify:

- [ ] Migration guide is comprehensive and tested
- [ ] All documentation references `check.py`
- [ ] No internal code uses `check_json.py`
- [ ] All examples and tutorials use `check.py`
- [ ] User feedback is positive
- [ ] At least 2 months have passed since deprecation announcement
- [ ] Migration guide has been tested by users
- [ ] No critical bugs in `check.py`
- [ ] Performance is acceptable
- [ ] All features from `check_json.py` are available in `check.py`

## Post-Removal Tasks

After removing `check_json.py`:

- [ ] Monitor GitHub issues for migration problems
- [ ] Update migration guide based on user feedback
- [ ] Archive old documentation
- [ ] Update project description
- [ ] Update README.md to remove legacy references

## Contingency Plan

If users report significant issues after removal:

1. **Immediate Action:**
   - Temporarily restore `check_json.py` with critical bug fixes
   - Issue emergency release

2. **Short-term:**
   - Investigate and fix issues
   - Update migration guide
   - Provide support to affected users

3. **Long-term:**
   - Extend deprecation period if necessary
   - Delay removal to next release
   - Re-evaluate removal plan

## Success Metrics

We will consider the migration successful when:

- ✅ Less than 5% of users still use `check_json.py` (based on GitHub issues/queries)
- ⏳ No critical bugs reported in `check.py`
- ⏳ Positive user feedback on migration process
- ⏳ All documentation updated
- ⏳ Performance is equal to or better than `check_json.py`

## Questions and Feedback

If you have questions about this deprecation plan:

1. Review the migration guide: `MIGRATION_GUIDE.md`
2. Check the backward compatibility notice: `BACKWARD_COMPATIBILITY.md`
3. Open an issue on GitHub
4. Contact the project maintainers

---

**Document Version:** 1.0
**Created:** 2026-02-26
**Last Updated:** 2026-02-26
**Next Review:** 2026-03-26
