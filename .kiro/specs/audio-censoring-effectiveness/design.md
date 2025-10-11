# Design Document

## Overview

The audio censoring effectiveness issue stems from the current FFmpeg volume filter implementation not achieving sufficient silence levels. The system currently uses `volume=0` which reduces audio but doesn't create the complete silence required for broadcast standards. This design addresses the problem by implementing more effective audio filtering techniques and improving verification mechanisms.

## Architecture

The solution involves three main components:

1. **Enhanced Audio Filter Chain**: Replace the simple `volume=0` filter with a more comprehensive approach using multiple FFmpeg filters
2. **Silence Verification System**: Implement robust verification to ensure censored segments meet the -50 dB threshold
3. **Improved Logging and Diagnostics**: Add detailed logging for troubleshooting and validation

### Current vs. Proposed Architecture

**Current Flow:**
```
Profane Segments → volume=0 filter → Output (-28 dB achieved)
```

**Proposed Flow:**
```
Profane Segments → Enhanced Filter Chain → Verification → Output (-50+ dB achieved)
```

## Components and Interfaces

### 1. Enhanced Audio Filter Construction

**Component**: `_construct_ffmpeg_command` method enhancement

**Current Implementation:**
```python
filter_parts.append(f"volume=0:enable={quote_char}between(t,{start_s},{end_s}){quote_char}")
```

**Proposed Implementation:**
- Use `volume=-inf` instead of `volume=0` for true silence
- Add `aformat` filter to ensure consistent audio format
- Implement `anullsrc` overlay for complete silence guarantee
- Add `acompand` filter for dynamic range compression to eliminate residual audio

**Interface Changes:**
- `_construct_ffmpeg_command` will accept additional parameters for filter configuration
- New method `_create_silence_filter` for generating optimal silence filters
- Enhanced error handling for filter validation

### 2. Silence Verification System

**Component**: New `_verify_silence_level` method

**Functionality:**
- Execute FFmpeg `astats` analysis on censored segments
- Parse RMS level output using regex patterns
- Validate against -50 dB threshold
- Return detailed verification results

**Interface:**
```python
def _verify_silence_level(self, video_path: str, start: float, end: float) -> Tuple[bool, float]:
    """
    Verifies that a specific segment meets silence requirements.
    Returns: (meets_threshold, actual_rms_db)
    """
```

### 3. Improved Filter Chain Architecture

**Primary Filter Strategy:**
1. **Volume Reduction**: `volume=-inf` for mathematical silence
2. **Format Normalization**: `aformat=sample_fmts=s16:channel_layouts=stereo` 
3. **Null Source Mixing**: Mix with `anullsrc` to ensure complete silence
4. **Dynamic Range Control**: `acompand` to eliminate any residual signals

**Filter Chain Example:**
```
volume=-inf:enable='between(t,6.0,6.8)',aformat=sample_fmts=s16,acompand=attacks=0.1:decays=0.8:points=-90/-90|-60/-60|-30/-30|-20/-20
```

## Data Models

### AudioCensoringConfig
```python
@dataclass
class AudioCensoringConfig:
    silence_threshold_db: float = -50.0
    volume_filter: str = "-inf"
    use_null_source_mixing: bool = True
    use_dynamic_compression: bool = True
    verification_enabled: bool = True
```

### CensoringResult
```python
@dataclass
class CensoringResult:
    success: bool
    output_path: Optional[str]
    censored_segments: List[Tuple[float, float]]
    verification_results: List[Tuple[float, float, float]]  # (start, end, rms_db)
    error_message: Optional[str]
```

## Error Handling

### Filter Construction Errors
- Validate FFmpeg filter syntax before execution
- Provide fallback to simpler filters if complex chains fail
- Log detailed error information for troubleshooting

### Verification Failures
- Retry with more aggressive filtering if initial attempt fails
- Implement progressive filter enhancement (volume=0 → volume=-inf → null mixing)
- Provide diagnostic information about why silence wasn't achieved

### Platform-Specific Handling
- Handle Windows vs. Unix quoting differences in filter parameters
- Adapt filter chains based on available FFmpeg version capabilities
- Provide platform-specific error messages and solutions

## Testing Strategy

### Unit Tests
- Test filter construction with various segment configurations
- Validate silence verification logic with mock FFmpeg outputs
- Test error handling scenarios and fallback mechanisms

### Integration Tests
- Enhance existing `test_censor_audio_with_ffmpeg_integration` to pass consistently
- Add tests for different audio formats and configurations
- Test verification system with known audio samples

### Performance Tests
- Measure processing time impact of enhanced filter chains
- Validate memory usage with large video files
- Test concurrent processing scenarios

### Verification Tests
- Create test audio samples with known RMS levels
- Validate astats parsing accuracy
- Test threshold detection with edge cases

## Implementation Phases

### Phase 1: Enhanced Filter Implementation
- Replace `volume=0` with `volume=-inf`
- Add format normalization filters
- Update filter chain construction logic

### Phase 2: Verification System
- Implement `_verify_silence_level` method
- Add astats parsing and validation
- Integrate verification into main processing flow

### Phase 3: Error Handling and Diagnostics
- Add comprehensive logging
- Implement fallback mechanisms
- Create diagnostic reporting system

### Phase 4: Testing and Validation
- Update integration tests
- Add comprehensive test coverage
- Validate against various media formats