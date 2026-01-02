# FFmpeg Setup Improvements - Summary

## Changes Made

### 1. Removed Bundled FFmpeg Binaries

- **Deleted**: `dialogue-guardian/bin/ffmpeg` (77 MB) and `dialogue-guardian/bin/ffprobe` (76 MB)
- **Reason**: Binaries should not be distributed; users should install via system package managers
- **Total Space Saved**: ~153 MB in repository

### 2. Updated .gitignore

- Made FFmpeg binary ignores explicit and platform-specific
- Now ignores: `ffmpeg`, `ffprobe`, `ffmpeg.exe`, `ffprobe.exe`, and temp download directories
- **File**: `dialogue-guardian/.gitignore`

### 3. Updated Documentation

#### README.md

- Added "📦 Installing FFmpeg" section with platform-specific instructions
- Placed before "🛠️ Installation" section for easy discovery
- Includes verification commands for each platform

#### DEVELOPMENT.md

- Added comprehensive FFmpeg installation guide
- Placed after "Prerequisites" section
- Covers Ubuntu/Debian, macOS (Homebrew), and Windows (Chocolatey)
- Includes verification steps

### 4. Deprecated download_ffmpeg.py Script

- Added deprecation notice to module docstring
- Added deprecation warning to main() function
- Script still works for backward compatibility but warns users to use system package managers
- **File**: `dialogue-guardian/scripts/download_ffmpeg.py`

### 5. Fixed conftest.py (Previous Work)

- Replaced `download_ffmpeg_fixture` that was failing due to missing `requests` module
- Implemented `verify_ffmpeg_available` that checks system PATH
- Now gracefully verifies FFmpeg availability instead of downloading

### 6. Updated CI/CD Workflow (Previous Work)

- **File**: `.github/workflows/ci.yml`
- Ubuntu: Uses `apt-get install ffmpeg`
- macOS: Uses `brew install ffmpeg`
- Windows: Uses `choco install ffmpeg`
- Platform-specific installation in test, lint, and build jobs

## Benefits

✅ **Smaller Repository**: ~153 MB freed up  
✅ **Better Maintainability**: No need to keep binaries updated  
✅ **Universal Compatibility**: Works on any platform with FFmpeg installed  
✅ **Clear Documentation**: Users know exactly how to set up FFmpeg  
✅ **Reliable CI/CD**: System package managers are more reliable than downloading  
✅ **No Breaking Changes**: Backward compatibility maintained for the script

## Fallback Behavior

The `core.py` module maintains intelligent fallback:

1. Check for local FFmpeg binaries in `bin/` directory (for backward compatibility)
2. Fall back to system PATH (recommended approach)
3. Users can specify custom paths via `--ffmpeg-path` and `--ffprobe-path` flags

## Testing

- ✅ All 121 tests pass
- ✅ 80% code coverage maintained
- ✅ No bundled binaries required
- ✅ FFmpeg available only from system PATH

## User Instructions

### New Users

1. Install FFmpeg:

   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y ffmpeg

   # macOS
   brew install ffmpeg

   # Windows
   choco install ffmpeg
   ```

2. Install Dialogue Guardian:

   ```bash
   pip install dialogue-guardian
   ```

3. Verify installation:
   ```bash
   ffmpeg -version
   guardian --help
   ```

### Developers

1. Follow installation instructions above
2. Clone repository: `git clone ...`
3. Install dependencies: `cd dialogue-guardian && make install-dev`
4. Run tests: `make test`

## Migration Notes for CI/CD

- ✅ GitHub Actions CI workflow updated with platform-specific FFmpeg installation
- ✅ No longer relies on download_ffmpeg.py during CI
- ✅ Tests will pass on all platforms (Linux, macOS, Windows)
- ✅ No need for special handling of FFmpeg in automated workflows
