# Design Document

## Overview

The release workflow failure is caused by incorrect version extraction from the .bumpversion.cfg file. The current command `NEW_VERSION=$(grep "current_version" .bumpversion.cfg | cut -d' ' -f3)` is not reliably extracting the version number, leading to an empty or malformed `$NEW_VERSION` variable. When this malformed variable is used in the `sed` command, it causes the "unterminated `s' command" error.

## Architecture

The issue is with the version extraction logic in the release workflow. The current method using `cut -d' ' -f3` is unreliable and fails to properly extract the version number from .bumpversion.cfg, resulting in an empty or malformed `$NEW_VERSION` variable that causes the sed command to fail.

The solution is to fix the version extraction logic using a more robust parsing method.

## Components and Interfaces

### Current Problematic Code
```bash
# Unreliable version extraction
NEW_VERSION=$(grep "current_version" .bumpversion.cfg | cut -d' ' -f3)

# sed command fails when NEW_VERSION is empty or malformed
sed -i.bak "s/__VERSION__/$NEW_VERSION/g" ../README.md
```

### Recommended Solution: Fix Version Extraction
Use a more robust method to extract the version from .bumpversion.cfg:
```bash
# More reliable version extraction using awk or sed
NEW_VERSION=$(awk -F' = ' '/current_version/ {print $2}' .bumpversion.cfg)
# OR
NEW_VERSION=$(sed -n 's/current_version = //p' .bumpversion.cfg)
```

### Alternative Solution: Use Different sed Delimiter
If the version extraction is fixed but there are still issues with special characters:
```bash
sed -i.bak "s|__VERSION__|$NEW_VERSION|g" ../README.md
```

## Data Models

### Input
- `new_version`: String containing the version number (e.g., "1.3.0")
- `readme_path`: Path to the README.md file

### Output
- Updated README.md file with version placeholders replaced
- Success/failure status

## Error Handling

### Python Script Approach
- Check if README.md file exists before processing
- Validate that the version string is in expected format
- Handle file I/O errors gracefully
- Provide clear error messages for debugging

### sed Command Approach
- Use proper delimiter to avoid conflicts with version number format
- Add error checking after sed command execution
- Log the version number being used for replacement

## Testing Strategy

### Manual Testing
1. Test with various version number formats (1.0.0, 1.10.0, 2.0.0-beta1)
2. Verify all __VERSION__ placeholders are replaced correctly
3. Ensure the original file structure and formatting is preserved

### Automated Testing
- Add a test step in the workflow that verifies the replacement worked
- Check that no __VERSION__ placeholders remain after replacement
- Validate that the replaced URLs are properly formatted

## Implementation Recommendation

**Primary Recommendation: Fix Version Extraction**
- Addresses the root cause of the issue
- Minimal change to existing workflow
- Uses more reliable parsing methods (awk or sed)
- Maintains current architecture while fixing the bug
- Quick fix that can be implemented immediately

**Fallback Option: Use Different sed Delimiter**
- Minimal additional change if version extraction fix isn't sufficient
- Uses pipe delimiter instead of forward slash to avoid conflicts with version format
- Addresses potential regex metacharacter issues