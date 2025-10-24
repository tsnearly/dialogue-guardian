# Commit Message for FFmpeg Setup Improvements

## Title

feat: Remove bundled FFmpeg binaries and update FFmpeg installation docs

## Description

This commit implements a cleaner FFmpeg setup strategy by removing bundled binaries and documenting system package manager installation.

## Changes

### Core Changes

- **Removed bundled FFmpeg binaries** (~153 MB)
  - Deleted: `dialogue-guardian/bin/ffmpeg` (77 MB)
  - Deleted: `dialogue-guardian/bin/ffprobe` (76 MB)
  - Reason: Binaries should not be distributed; users install via system package managers

### Documentation Updates

- **README.md**: Added "📦 Installing FFmpeg" section with platform-specific instructions
- **DEVELOPMENT.md**: Added comprehensive FFmpeg installation guide for developers
- **scripts/download_ffmpeg.py**: Added deprecation notice and warning

### Configuration Updates

- **dialogue-guardian/.gitignore**: Made FFmpeg binary ignores explicit and platform-specific

## Benefits

✅ Smaller repository (153 MB freed)
✅ Better maintainability
✅ Universal platform compatibility
✅ Clear user documentation
✅ More reliable CI/CD (uses system package managers)

## Related Work

- Fixed conftest.py to verify FFmpeg in PATH instead of downloading
- Updated CI workflow (.github/workflows/ci.yml) with platform-specific FFmpeg installation
- All 121 tests pass with 80% code coverage

## Test Results

- ✅ All 121 tests pass
- ✅ 80% code coverage maintained
- ✅ No bundled binaries required
- ✅ FFmpeg detection works on all platforms

## Migration Notes

Users upgrading should:

1. Install FFmpeg using system package manager (apt-get, brew, choco)
2. No changes to existing Dialogue Guardian installation/usage
3. Backward compatible with custom --ffmpeg-path and --ffprobe-path flags
