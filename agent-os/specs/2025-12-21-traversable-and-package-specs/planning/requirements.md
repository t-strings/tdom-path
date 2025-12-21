# Spec Requirements: Traversable and Package Specs

## Initial Description
Support for package assets using Traversable and package-oriented path specifications.

## Requirements Discussion

### First Round Questions

**Q1:** For package asset string format - I assume you want `mypackage:static/styles.css` format (colon separator). Is that correct, or would you prefer a different separator like `@` or `::` ?

**Answer:** Colon separator confirmed.

**Q2:** For relative path syntax - I'm thinking we support `./` and `../` prefixes for relative paths. Should we also allow plain `static/styles.css` (without prefix) to work as a relative path, or require an explicit prefix?

**Answer:** Support `./`, `../`, and plain `static/styles.css` (without prefix) as local relative paths.

**Q3:** For the Traversable vs PurePosixPath decision - I assume we want to stick with PurePosixPath for its clean API and then convert to Traversable only when needed for package resources. Is that the right approach, or should we switch back to Traversable as the primary type?

**Answer:** Switch back to Traversable. User likes Traversable because it resolves into packages and is package-name oriented. If we can switch to `package:path` as the native, first-class format, it better represents the logical model.

**Q4:** For asset existence validation - should we fail immediately if an asset doesn't exist, collect all missing assets and report at the end, or add a strict/lenient mode flag?

**Answer:** Fail immediately for now, but leave a TODO suggesting options to consider: collect missing assets and report at end, add strict/lenient mode flag, log warnings instead of failing, or all as options to consider.

**Q5:** For test fixture strategy - should we create a fake package structure in the tests directory, or use an external test package dependency?

**Answer:** Create fake package structure in tests directory (like `tests/fixtures/fake_package/`) and use `importlib.resources.files()` to access it.

**Q6:** For documentation - should we update README, add docstrings, or create a separate guide on package asset usage?

**Answer:** Update README with package asset support.

**Q7:** Are there any features or edge cases you want to explicitly exclude from this spec (like network URLs, absolute filesystem paths, symlink handling)?

**Answer:** No exclusions mentioned.

### Existing Code to Reference

No similar existing features identified for reference.

### Follow-up Questions

**Follow-up 1:** For path type detection - should we detect package paths purely based on the presence of a colon, or should we also validate that the package name follows Python package naming conventions?

**Answer:** Purely based on presence of colon - if string contains `:` then it's a package asset, otherwise it's a local relative path.

**Follow-up 2:** For the TODO comment about validation options - should I suggest all the options (collect and report, strict/lenient mode, log warnings) or just one or two?

**Answer:** Suggest all options in the TODO comment: collect all missing assets and report at the end, add a strict/lenient mode flag, log warnings instead of failing, and all of the above as options to consider.

## Visual Assets

### Files Provided:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- Support package asset string format using `mypackage:static/styles.css` (colon separator)
- Support local relative paths with `./`, `../`, and plain `static/styles.css` (without prefix)
- Use Traversable as the primary type instead of PurePosixPath - it's package-name oriented and better represents the logical model where `package:path` is the native, first-class format
- Detect path type purely based on presence of colon: if string contains `:` then it's a package asset, otherwise it's a local relative path
- Validate asset existence and fail immediately if asset doesn't exist
- Leave TODO comment suggesting future validation options: collect missing assets and report at end, add strict/lenient mode flag, log warnings instead of failing, or all as options to consider
- Create fake package structure in tests directory (like `tests/fixtures/fake_package/`) using `importlib.resources.files()` for testing
- Update README with package asset support documentation

### Reusability Opportunities
No similar features identified for reuse.

### Scope Boundaries

**In Scope:**
- Package asset string format with colon separator
- Local relative path support (with and without prefixes)
- Traversable-based implementation as primary type
- Simple colon-based path type detection
- Immediate asset existence validation with future-proofing TODO
- Test fixtures using fake package structure
- README documentation updates

**Out of Scope:**
- Network URLs
- Absolute filesystem paths
- Symlink handling
- Python package naming convention validation (relying on colon presence only)
- Multiple validation modes (planned for future via TODO)

### Technical Considerations
- Switch from PurePosixPath to Traversable as the primary internal representation
- `package:path` format becomes the native, first-class format
- Path type detection based on string analysis (presence of `:` character)
- Use `importlib.resources.files()` for package resource access
- Backward compatibility maintained - no required explicit prefix for relative paths
- Validation strategy uses fail-fast approach with extensibility TODO for future enhancements
- Test strategy uses local fixtures rather than external dependencies

### Architectural Rationale
The decision to switch back to Traversable is based on:
- Traversable resolves into packages naturally
- Package-name oriented design philosophy
- `package:path` better represents the logical model
- First-class support for package assets as primary use case
- Cleaner semantic alignment with the domain model
