# Implementation Plan

- [x] 1. Fix version extraction logic in release workflow
  - Replace the unreliable `cut -d' ' -f3` command with a more robust parsing method
  - Use `awk` or `sed` to properly extract the version from .bumpversion.cfg
  - Add error checking to ensure version extraction succeeds
  - _Requirements: 1.1, 1.2, 3.2_

- [x] 1.1 Update the version extraction command
  - Replace `NEW_VERSION=$(grep "current_version" .bumpversion.cfg | cut -d' ' -f3)` with a more reliable method
  - Use `awk -F' = ' '/current_version/ {print $2}' .bumpversion.cfg` for robust parsing
  - _Requirements: 1.1, 1.2_

- [x] 1.2 Add version validation and error handling
  - Add a check to ensure NEW_VERSION is not empty after extraction
  - Add logging to show the extracted version for debugging
  - Exit with error if version extraction fails
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 1.3 Test the sed command with improved version extraction
  - Verify that the sed command works correctly with the properly extracted version
  - Ensure all __VERSION__ placeholders in README.md are replaced
  - _Requirements: 1.3, 2.2_

- [ ]* 1.4 Add fallback sed delimiter if needed
  - If issues persist with special characters, change sed delimiter from `/` to `|`
  - Update sed command to `sed -i.bak "s|__VERSION__|$NEW_VERSION|g" ../README.md`
  - _Requirements: 2.1, 2.2_