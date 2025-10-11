# Requirements Document

## Introduction

The release workflow is failing due to a `sed` command error when trying to replace version placeholders in the README.md file. The error "unterminated `s' command" occurs because the version number contains dots that are interpreted as regex metacharacters by `sed`. This needs to be fixed to ensure reliable releases.

## Requirements

### Requirement 1

**User Story:** As a developer, I want the release workflow to successfully update version placeholders in README.md, so that releases can be created without manual intervention.

#### Acceptance Criteria

1. WHEN the release workflow runs THEN the sed command SHALL successfully replace __VERSION__ placeholders without errors
2. WHEN a version number contains dots (e.g., "1.3.0") THEN the sed command SHALL treat them as literal characters, not regex metacharacters
3. WHEN the version replacement occurs THEN all instances of __VERSION__ in README.md SHALL be replaced with the actual version number

### Requirement 2

**User Story:** As a developer, I want the release workflow to be robust against special characters in version numbers, so that future releases don't fail due to similar issues.

#### Acceptance Criteria

1. WHEN the version number contains special regex characters THEN the replacement SHALL still work correctly
2. WHEN using sed for text replacement THEN special characters SHALL be properly escaped or an alternative approach SHALL be used
3. WHEN the workflow completes THEN the README.md file SHALL contain the correct version numbers in all download links

### Requirement 3

**User Story:** As a developer, I want clear error handling in the release workflow, so that I can quickly identify and fix issues when they occur.

#### Acceptance Criteria

1. WHEN a sed command fails THEN the workflow SHALL provide clear error messages
2. WHEN version replacement fails THEN the workflow SHALL stop and not proceed with the release
3. WHEN debugging is needed THEN the workflow SHALL log the version number being used for replacement