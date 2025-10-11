<!--
SPDX-FileCopyrightText: 2025 Tony Snearly
SPDX-License-Identifier: OSL-3.0
-->

# Code Refactoring Summary

## Overview

This document summarizes the major code refactoring completed to improve testability, maintainability, and code quality in the Dialogue Guardian project.

## Problem Statement

The original codebase had several issues that hindered effective testing and maintenance:

- **Large monolithic functions** mixing I/O operations with business logic
- **Heavy reliance on mocks** in tests, which hid real logic bugs
- **Complex parsing logic** buried inside subprocess calls
- **Difficult debugging** due to tightly coupled code
- **Poor testability** of core business logic

## Solution: Extract Pure Functions

The solution involved **extracting complex business logic into pure functions** that can be tested independently without mocks.

## Refactoring Results

### 📊 Coverage Improvement
- **Before**: 84.78% coverage (mostly testing mock interactions)
- **After**: 86% coverage (testing actual business logic)
- **Added**: 34 new pure function tests with real data

### 🧪 Test Quality Enhancement
- **Before**: Tests primarily validated mock setups and interactions
- **After**: Tests validate actual parsing, filtering, and processing logic
- **Benefit**: Real bugs are now caught by tests instead of being hidden by mocks

## Extracted Pure Functions

### 1. Video Details Parsing Functions

**Before**: Single monolithic `get_video_details()` function (120+ lines)
```python
def get_video_details(self, filename: str) -> Optional[Dict[str, Any]]:
    # Mixed subprocess calls with complex parsing logic
    # Hard to test individual parsing components
```

**After**: Modular functions with separated concerns
```python
def _parse_duration(self, duration_output: str) -> Dict[str, str]:
    """Pure function - testable without mocks"""
    
def _parse_audio_streams(self, ffprobe_output: str) -> Dict[str, str]:
    """Pure function - testable without mocks"""
    
def _parse_framerate_info(self, framerate_str: Optional[str]) -> Dict[str, Optional[str]]:
    """Pure function - testable without mocks"""
    
def _parse_video_stream_output(self, ffprobe_output: str) -> Dict[str, Optional[str]]:
    """Pure function - testable without mocks"""
```

### 2. SRT Processing Functions

**Before**: Complex logic mixed with subprocess calls
```python
def extract_embedded_srt(self, video_path: str, output_srt_path: str) -> bool:
    # JSON parsing, stream filtering, and selection logic all mixed together
```

**After**: Separated pure functions
```python
def _parse_ffprobe_streams(self, json_output: str) -> List[Dict[str, Any]]:
def _find_srt_streams(self, streams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
def _select_best_srt_stream(self, srt_streams: List[Dict[str, Any]]) -> Optional[int]:
def _generate_srt_candidates(self, video_path: str) -> List[str]:
```

### 3. Profanity Detection Functions

**Before**: Regex logic buried in subtitle processing
```python
def _find_profane_segments(self, subs: List[srt.Subtitle]) -> List[Tuple[float, float]]:
    # Text cleaning, regex compilation, and matching all mixed together
```

**After**: Modular text processing functions
```python
def _clean_subtitle_text(self, content: str) -> str:
def _build_profanity_pattern(self, words: List[str]) -> re.Pattern[str]:
def _contains_profanity(self, text: str, pattern: re.Pattern[str]) -> bool:
```

### 4. FFmpeg Command Construction Functions

**Before**: Complex filter building mixed with command construction
```python
def _construct_ffmpeg_command(self, video_path: str, output_path: str, 
                             censor_segments: List[Tuple[float, float]], 
                             strategy_level: int = 2) -> List[str]:
    # 80+ lines of mixed filter building and command construction
```

**After**: Separated filter building and command construction
```python
def _build_volume_filters(self, segments: List[Tuple[float, float]], 
                         volume_setting: str) -> List[str]:
def _build_audio_filter_chain(self, segments: List[Tuple[float, float]], 
                             strategy_level: int) -> str:
def _build_ffmpeg_base_command(self, video_path: str, output_path: str, 
                              audio_filter_graph: str) -> List[str]:
```

## Test Examples

### Before: Mock-Heavy Tests
```python
@patch("subprocess.check_output")
def test_get_video_details_multiple_audio_streams(self, mock_check_output):
    mock_check_output.side_effect = [
        "120.5",  # duration
        "aac|44100|1|mono\naac|48000|6|5.1",  # multiple audio streams
        "1920\n1080\n30000/1001",  # video info
    ]
    result = self.processor.get_video_details(self.test_video_path)
    # This tests the mock setup, not the actual parsing logic
    # Problems: Hides parsing bugs, doesn't test edge cases, complex mock setup
```

### After: Multiple Pure Function Tests
The single mock-heavy test was replaced with **multiple focused pure function tests** that validate each component with real data:

```python
# Test 1: Duration parsing (from "120.5" mock)
def test_parse_duration(self):
    """Test duration parsing with real data"""
    duration_output = "120.5"
    result = self.processor._parse_duration(duration_output)
    
    expected = {"duration": "120.5"}
    self.assertEqual(result, expected)

def test_parse_duration_with_whitespace(self):
    """Test duration parsing handles whitespace correctly"""
    duration_output = "  120.5  \n"
    result = self.processor._parse_duration(duration_output)
    
    expected = {"duration": "120.5"}
    self.assertEqual(result, expected)

# Test 2: Audio stream parsing (from "aac|44100|1|mono\naac|48000|6|5.1" mock)
def test_parse_audio_streams_multiple_streams(self):
    """Test audio stream selection logic - should pick the one with most channels"""
    ffprobe_output = "aac|44100|1|mono\naac|48000|6|5.1"
    result = self.processor._parse_audio_streams(ffprobe_output)
    
    # Should pick the 6-channel stream
    expected = {
        "codec": "aac", "samplerate": "48000", "channels": "6", "audioconfig": "5.1"
    }
    self.assertEqual(result, expected)

# Test 3: Video info parsing (from "1920\n1080\n30000/1001" mock)
def test_parse_video_stream_output_complete(self):
    """Test video dimension and framerate parsing with real data"""
    ffprobe_output = "1920\n1080\n30000/1001"
    result = self.processor._parse_video_stream_output(ffprobe_output)
    
    expected = {
        "width": "1920", "height": "1080", "framerate": "30000/1001",
        "fps": "29.970", "frameduration": "1001/30000"
    }
    self.assertEqual(result, expected)

# Additional edge case tests that weren't possible with mocks
def test_parse_framerate_info_division_by_zero(self):
    """Test edge case: division by zero in framerate calculation"""
    result = self.processor._parse_framerate_info("30000/0")
    
    # Should handle gracefully without crashing
    expected = {"framerate": None, "fps": None, "frameduration": None}
    self.assertEqual(result, expected)

def test_parse_audio_streams_malformed_data(self):
    """Test parsing malformed audio stream data"""
    ffprobe_output = "malformed|data\n|incomplete|\naac|44100|2|stereo"
    result = self.processor._parse_audio_streams(ffprobe_output)
    
    # Should skip malformed data and pick the valid stream
    expected = {
        "codec": "aac", "samplerate": "44100", "channels": "2", "audioconfig": "stereo"
    }
    self.assertEqual(result, expected)
```

**Key Improvement**: One mock-heavy test became **6+ focused tests** that validate:
- Duration parsing with real data (from the "120.5" mock) - including whitespace handling
- Audio stream selection logic with real data (from the audio streams mock)
- Video dimension and framerate parsing with real data (from the video info mock)
- Edge cases like division by zero (not possible with mocks)
- Error handling with malformed data (not possible with mocks)
- Whitespace and edge case handling for all parsing functions

## Benefits Achieved

### 1. **Better Bug Detection**
- **Before**: Mocks could hide parsing bugs and edge cases
- **After**: Real data testing catches actual parsing issues

### 2. **Improved Maintainability**
- **Before**: Large functions were hard to understand and modify
- **After**: Small, focused functions with clear responsibilities

### 3. **Enhanced Testability**
- **Before**: Complex mock setups required for testing
- **After**: Direct function calls with real data

### 4. **Easier Debugging**
- **Before**: Issues were hard to isolate in large functions
- **After**: Problems can be pinpointed to specific pure functions

### 5. **Better Code Reuse**
- **Before**: Logic was tightly coupled to specific contexts
- **After**: Pure functions can be reused in different scenarios

## Edge Cases Now Covered

The pure function tests cover many edge cases that were previously untested:

### Video Processing Edge Cases
- **Division by zero** in framerate calculations (`30000/0` → graceful handling)
- **Malformed data** in audio stream parsing (incomplete pipe-separated values)
- **Empty inputs** and null values (empty ffprobe output)
- **Non-numeric channels** in audio streams (`aac|44100|unknown|stereo`)
- **Incomplete video info** (missing height/framerate data)

### SRT Processing Edge Cases  
- **Invalid JSON** in stream parsing (malformed ffprobe JSON output)
- **Missing streams key** in JSON response
- **Empty stream lists** and null stream selections
- **Multiple subtitle tracks** with default/non-default prioritization

### Profanity Detection Edge Cases
- **Special characters** in subtitle text (`What the f*ck?!`)
- **Complex profanity patterns** with case variations (`FUCKING`, `Shit`, `damn`)
- **Word boundaries** (ensuring "fucking" matches but "shitty" doesn't match "shit")
- **Empty word lists** (graceful pattern compilation)
- **Punctuation handling** in text cleaning

### FFmpeg Command Construction Edge Cases
- **Empty segment lists** (no profanity found)
- **Multiple overlapping segments** with complex timing
- **Different strategy levels** (Basic → Enhanced → Aggressive)
- **Custom quote characters** for cross-platform compatibility

## File Changes

### New Files Added
- `tests/test_guardian_pure_functions.py` - 34 pure function tests

### Modified Files
- `src/guardian/core.py` - Extracted pure functions from monolithic methods
- `tests/test_guardian_integration.py` - Updated test expectations for improved parsing
- `README.md` - Updated to reflect improved testing and architecture
- `DEVELOPMENT.md` - Added pure function testing guidelines and architecture documentation
- `TESTING.md` - Added pure function test documentation

## Metrics

### Test Statistics
- **Total Tests**: 118 (was ~81)
- **Pure Function Tests**: 37 (new) - including 3 duration parsing tests
- **Test Coverage**: 86% (improved from 84.78%)
- **Core Module Coverage**: 84% (improved quality of coverage)
- **CLI Coverage**: 99% (68/69 lines)

### Test Quality Improvements
- **Mock Dependency Reduction**: Core business logic now tested without mocks
- **Real Data Testing**: Parsing functions tested with actual ffprobe output formats
- **Edge Case Coverage**: Division by zero, malformed data, empty inputs, special characters
- **Comprehensive Validation**: Each extracted function has multiple test scenarios

### Code Quality
- **Functions Extracted**: 16 pure functions (including duration parsing)
- **Lines of Code Tested**: Significantly more actual business logic now tested
- **Mock Dependency**: Eliminated mocks for all core parsing logic (duration, audio, video, profanity, FFmpeg)

## Future Recommendations

1. **Continue Pure Function Extraction**: Look for other areas where complex logic can be extracted into pure functions

2. **Expand Edge Case Testing**: Add more edge case tests as they are discovered

3. **Performance Testing**: Consider adding performance tests for the pure functions

4. **Documentation**: Keep documentation updated as more refactoring is done

## Conclusion

This refactoring significantly improved the codebase quality by:
- **Separating concerns** between I/O and business logic
- **Improving testability** through pure function extraction
- **Enhancing maintainability** with modular design
- **Increasing confidence** in the correctness of core logic

The result is a more robust, testable, and maintainable codebase that will be easier to extend and debug in the future.