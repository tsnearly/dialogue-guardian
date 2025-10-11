#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Complete integration testing for audio censoring effectiveness.
This script tests the enhanced censoring system with sample media files.
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple

# Add the src directory to the path so we can import guardian
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from guardian.core import GuardianProcessor


def setup_logging():
    """Set up detailed logging for integration testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('integration_test.log')
        ]
    )


def test_sample_media_censoring():
    """
    Test enhanced censoring with existing sample.mp4 and sample.srt files.
    Requirements: 1.4, 3.1, 3.3
    """
    print("=" * 60)
    print("INTEGRATION TEST: Sample Media Censoring")
    print("=" * 60)
    
    # Set up paths - adjust for tests subdirectory
    samples_dir = Path(__file__).parent.parent / "samples"
    test_video = samples_dir / "sample.mp4"
    test_srt = samples_dir / "sample.srt"
    
    # Verify sample files exist
    if not test_video.exists():
        print(f"❌ ERROR: Sample video not found at {test_video}")
        return False
    
    if not test_srt.exists():
        print(f"❌ ERROR: Sample SRT not found at {test_srt}")
        return False
    
    print(f"✓ Sample video found: {test_video}")
    print(f"✓ Sample SRT found: {test_srt}")
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "censored_sample.mp4"
        
        # Initialize processor
        processor = GuardianProcessor()
        
        # Test video details extraction
        print("\n--- Testing Video Details Extraction ---")
        details = processor.get_video_details(str(test_video))
        if details:
            print(f"✓ Video duration: {details.get('duration', 'Unknown')}s")
            print(f"✓ Video resolution: {details.get('width', 'Unknown')}x{details.get('height', 'Unknown')}")
            print(f"✓ Video FPS: {details.get('fps', 'Unknown')}")
            print(f"✓ Audio codec: {details.get('codec', 'Unknown')}")
            print(f"✓ Audio channels: {details.get('channels', 'Unknown')}")
        else:
            print("❌ ERROR: Could not extract video details")
            return False
        
        # Test SRT parsing and profanity detection
        print("\n--- Testing SRT Parsing and Profanity Detection ---")
        srt_path = processor._find_srt_file(str(test_video))
        if srt_path:
            print(f"✓ Found SRT file: {srt_path}")
            
            subtitles = processor._parse_srt_file(srt_path)
            if subtitles:
                print(f"✓ Parsed {len(subtitles)} subtitle entries")
                
                # Find profane segments
                profane_segments = processor._find_profane_segments(subtitles)
                print(f"✓ Found {len(profane_segments)} profane segments:")
                
                for i, (start, end) in enumerate(profane_segments, 1):
                    duration = end - start
                    print(f"  {i}. {start:.3f}s - {end:.3f}s (duration: {duration:.3f}s)")
                    
                    # Find the subtitle content for this segment
                    for sub in subtitles:
                        sub_start = sub.start.total_seconds()
                        sub_end = sub.end.total_seconds()
                        if abs(sub_start - start) < 0.1 and abs(sub_end - end) < 0.1:
                            print(f"     Content: \"{sub.content.strip()}\"")
                            break
                
                if not profane_segments:
                    print("⚠️  WARNING: No profane segments found in sample SRT")
                    print("   This may indicate an issue with profanity detection")
                    return False
                    
            else:
                print("❌ ERROR: Could not parse SRT file")
                return False
        else:
            print("❌ ERROR: Could not find SRT file")
            return False
        
        # Test enhanced censoring
        print("\n--- Testing Enhanced Audio Censoring ---")
        result = processor.censor_audio_with_ffmpeg(str(test_video), str(output_path))
        
        if result is None:
            print("❌ ERROR: Censoring failed - returned None")
            return False
        
        if not output_path.exists():
            print(f"❌ ERROR: Output file not created at {output_path}")
            return False
        
        print(f"✓ Censoring completed successfully")
        print(f"✓ Output file created: {output_path}")
        
        # Verify output video properties
        print("\n--- Verifying Output Video Properties ---")
        output_details = processor.get_video_details(str(output_path))
        if output_details:
            print(f"✓ Output duration: {output_details.get('duration', 'Unknown')}s")
            print(f"✓ Output resolution: {output_details.get('width', 'Unknown')}x{output_details.get('height', 'Unknown')}")
            
            # Compare with input
            input_duration = float(details.get('duration', 0))
            output_duration = float(output_details.get('duration', 0))
            duration_diff = abs(input_duration - output_duration)
            
            if duration_diff < 0.1:
                print(f"✓ Duration preserved (diff: {duration_diff:.3f}s)")
            else:
                print(f"⚠️  WARNING: Duration changed significantly (diff: {duration_diff:.3f}s)")
            
            if (details.get('width') == output_details.get('width') and 
                details.get('height') == output_details.get('height')):
                print("✓ Video resolution preserved")
            else:
                print("⚠️  WARNING: Video resolution changed")
        else:
            print("❌ ERROR: Could not extract output video details")
            return False
        
        # Test silence verification
        print("\n--- Testing Silence Verification ---")
        verification_passed = True
        
        for i, (start, end) in enumerate(profane_segments, 1):
            print(f"\nVerifying segment {i}: {start:.3f}s - {end:.3f}s")
            meets_threshold, actual_rms_db = processor._verify_silence_level(
                str(output_path), start, end
            )
            
            if meets_threshold:
                print(f"✓ Segment {i} meets silence threshold: {actual_rms_db:.2f} dB")
            else:
                print(f"❌ Segment {i} fails silence threshold: {actual_rms_db:.2f} dB (should be ≤ -50 dB)")
                verification_passed = False
        
        if verification_passed:
            print("\n✓ All segments meet silence requirements")
        else:
            print("\n❌ Some segments fail silence requirements")
            return False
        
        # Test file size comparison
        print("\n--- File Size Analysis ---")
        input_size = test_video.stat().st_size
        output_size = output_path.stat().st_size
        size_ratio = output_size / input_size
        
        print(f"Input file size: {input_size:,} bytes")
        print(f"Output file size: {output_size:,} bytes")
        print(f"Size ratio: {size_ratio:.3f}")
        
        if 0.8 <= size_ratio <= 1.2:
            print("✓ Output file size is reasonable")
        else:
            print("⚠️  WARNING: Significant file size change")
    
    print("\n" + "=" * 60)
    print("✅ SAMPLE MEDIA CENSORING TEST PASSED")
    print("=" * 60)
    return True


def test_profanity_pattern_variations():
    """
    Test censoring effectiveness across different profanity patterns.
    Requirements: 1.4, 3.1, 3.3
    """
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Profanity Pattern Variations")
    print("=" * 60)
    
    # Create test SRT content with various profanity patterns
    test_patterns = [
        ("Basic profanity", "This is fucking terrible!"),
        ("Common phrase", "What the hell is going on?"),
        ("Religious profanity", "Jesus Christ, that's bad"),
        ("Compound word", "You're such a smartass"),
        ("Multiple words", "This damn bullshit is fucking annoying"),
        ("Case variations", "FUCK this SHIT"),
        ("Punctuation", "What the fuck?! This is shit."),
        ("Clean content", "This is perfectly fine content"),
    ]
    
    processor = GuardianProcessor()
    
    print("Testing profanity detection patterns:")
    
    for i, (description, content) in enumerate(test_patterns, 1):
        print(f"\n{i}. {description}: \"{content}\"")
        
        # Create a mock subtitle
        import srt
        from datetime import timedelta
        
        subtitle = srt.Subtitle(
            index=i,
            start=timedelta(seconds=i*5),
            end=timedelta(seconds=i*5 + 3),
            content=content
        )
        
        # Test profanity detection
        profane_segments = processor._find_profane_segments([subtitle])
        
        if description == "Clean content":
            if not profane_segments:
                print("   ✓ Correctly identified as clean")
            else:
                print("   ❌ Incorrectly flagged as profane")
                return False
        else:
            if profane_segments:
                start, end = profane_segments[0]
                print(f"   ✓ Detected profanity: {start:.1f}s - {end:.1f}s")
            else:
                print("   ❌ Failed to detect profanity")
                return False
    
    print("\n✅ PROFANITY PATTERN VARIATIONS TEST PASSED")
    return True


def test_audio_format_compatibility():
    """
    Test enhanced censoring with different audio configurations.
    Requirements: 3.1, 3.2, 3.3
    """
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Audio Format Compatibility")
    print("=" * 60)
    
    samples_dir = Path(__file__).parent.parent / "samples"
    test_video = samples_dir / "sample.mp4"
    
    if not test_video.exists():
        print(f"❌ ERROR: Sample video not found at {test_video}")
        return False
    
    processor = GuardianProcessor()
    
    # Test different filter strategies
    print("Testing filter strategy compatibility:")
    
    strategies = [1, 2, 3]  # Basic, Enhanced, Aggressive
    strategy_names = ["Basic Volume Reduction", "Enhanced Silence", "Aggressive Null Mixing"]
    
    for strategy_level, strategy_name in zip(strategies, strategy_names):
        print(f"\n--- Testing Strategy {strategy_level}: {strategy_name} ---")
        
        strategy_config = processor._get_filter_strategy(strategy_level)
        print(f"Strategy description: {strategy_config['description']}")
        print(f"Volume filter: {strategy_config['volume_filter']}")
        print(f"Format normalization: {strategy_config['use_format_normalization']}")
        print(f"Compression: {strategy_config['use_compression']}")
        print(f"Null mixing: {strategy_config['use_null_mixing']}")
        
        # Test filter construction
        test_segments = [(2.0, 4.8), (6.0, 6.8)]  # From sample.srt
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / f"test_strategy_{strategy_level}.mp4"
            
            try:
                # Construct FFmpeg command
                ffmpeg_command = processor._construct_ffmpeg_command(
                    str(test_video), str(output_path), test_segments, strategy_level=strategy_level
                )
                
                print(f"✓ Filter construction successful for strategy {strategy_level}")
                
                # Test if the command contains expected filter elements
                command_str = ' '.join(ffmpeg_command)
                
                if strategy_level >= 2:
                    if 'aformat' in command_str:
                        print("✓ Format normalization filter present")
                    else:
                        print("⚠️  Format normalization filter missing")
                
                if strategy_level >= 3:
                    if 'anullsrc' in command_str or 'acompand' in command_str:
                        print("✓ Advanced filtering present")
                    else:
                        print("⚠️  Advanced filtering missing")
                
            except Exception as e:
                print(f"❌ ERROR: Filter construction failed for strategy {strategy_level}: {e}")
                return False
    
    print("\n✅ AUDIO FORMAT COMPATIBILITY TEST PASSED")
    return True


def main():
    """Run all integration tests."""
    print("DIALOGUE GUARDIAN - COMPLETE INTEGRATION TESTING")
    print("Testing enhanced audio censoring effectiveness")
    print("=" * 60)
    
    setup_logging()
    
    # Track test results
    tests = [
        ("Sample Media Censoring", test_sample_media_censoring),
        ("Profanity Pattern Variations", test_profanity_pattern_variations),
        ("Audio Format Compatibility", test_audio_format_compatibility),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED with exception: {e}")
            logging.exception(f"Test {test_name} failed with exception")
    
    # Final summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("Enhanced audio censoring system is working correctly.")
        return True
    else:
        print(f"\n💥 {failed} INTEGRATION TESTS FAILED!")
        print("Please review the test output and fix the issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)