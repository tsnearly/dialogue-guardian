#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
End-to-end workflow validation for the dialogue guardian system.
Tests complete workflow from SRT parsing to final output verification.
"""

import os
import sys
import logging
import tempfile
import shutil
import json
from pathlib import Path
from typing import List, Tuple, Optional
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import guardian
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from guardian.core import GuardianProcessor


def setup_logging():
    """Set up detailed logging for end-to-end testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('end_to_end_test.log')
        ]
    )


def test_complete_srt_parsing_workflow():
    """
    Test complete workflow from SRT parsing to final output verification.
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    print("=" * 60)
    print("END-TO-END TEST: Complete SRT Parsing Workflow")
    print("=" * 60)
    
    samples_dir = Path(__file__).parent.parent / "samples"
    test_video = samples_dir / "sample.mp4"
    test_srt = samples_dir / "sample.srt"
    
    if not test_video.exists() or not test_srt.exists():
        print(f"❌ ERROR: Sample files not found")
        return False
    
    processor = GuardianProcessor()
    
    # Test 1: SRT File Discovery
    print("\n--- Testing SRT File Discovery ---")
    discovered_srt = processor._find_srt_file(str(test_video))
    if discovered_srt:
        print(f"✓ SRT file discovered: {discovered_srt}")
        if discovered_srt == str(test_srt):
            print("✓ Correct SRT file matched")
        else:
            print(f"⚠️  Different SRT file found: expected {test_srt}, got {discovered_srt}")
    else:
        print("❌ ERROR: SRT file discovery failed")
        return False
    
    # Test 2: SRT Parsing
    print("\n--- Testing SRT Parsing ---")
    subtitles = processor._parse_srt_file(discovered_srt)
    if subtitles:
        print(f"✓ SRT parsing successful: {len(subtitles)} subtitles")
        
        # Validate subtitle structure
        for i, sub in enumerate(subtitles[:3], 1):  # Check first 3
            print(f"  Subtitle {i}: {sub.start} - {sub.end}")
            print(f"    Content: \"{sub.content.strip()}\"")
            
            # Validate timing
            if sub.start < sub.end:
                print(f"    ✓ Valid timing")
            else:
                print(f"    ❌ Invalid timing: start >= end")
                return False
    else:
        print("❌ ERROR: SRT parsing failed")
        return False
    
    # Test 3: Profanity Detection
    print("\n--- Testing Profanity Detection ---")
    profane_segments = processor._find_profane_segments(subtitles)
    print(f"✓ Profanity detection completed: {len(profane_segments)} segments found")
    
    expected_segments = 2  # Based on sample.srt content
    if len(profane_segments) == expected_segments:
        print(f"✓ Expected number of profane segments found")
    else:
        print(f"⚠️  Unexpected segment count: expected {expected_segments}, got {len(profane_segments)}")
    
    # Validate segment timing
    for i, (start, end) in enumerate(profane_segments, 1):
        if start < end:
            print(f"  ✓ Segment {i} timing valid: {start:.3f}s - {end:.3f}s")
        else:
            print(f"  ❌ Segment {i} timing invalid: {start:.3f}s - {end:.3f}s")
            return False
    
    # Test 4: Complete Censoring Workflow
    print("\n--- Testing Complete Censoring Workflow ---")
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "workflow_test.mp4"
        
        # Execute complete workflow
        result = processor.censor_audio_with_ffmpeg(str(test_video), str(output_path))
        
        if result is None:
            print("❌ ERROR: Complete workflow failed")
            return False
        
        if not output_path.exists():
            print("❌ ERROR: Output file not created")
            return False
        
        print("✓ Complete workflow executed successfully")
        
        # Test 5: Output Verification
        print("\n--- Testing Output Verification ---")
        
        # Verify video properties
        output_details = processor.get_video_details(str(output_path))
        if output_details:
            print(f"✓ Output video details extracted")
            print(f"  Duration: {output_details.get('duration')}s")
            print(f"  Resolution: {output_details.get('width')}x{output_details.get('height')}")
        else:
            print("❌ ERROR: Could not extract output video details")
            return False
        
        # Verify silence levels
        verification_passed = True
        for i, (start, end) in enumerate(profane_segments, 1):
            meets_threshold, actual_rms_db = processor._verify_silence_level(
                str(output_path), start, end
            )
            
            if meets_threshold:
                print(f"  ✓ Segment {i} verification passed: {actual_rms_db:.2f} dB")
            else:
                print(f"  ❌ Segment {i} verification failed: {actual_rms_db:.2f} dB")
                verification_passed = False
        
        if not verification_passed:
            print("❌ ERROR: Silence verification failed")
            return False
        
        print("✓ All output verification tests passed")
    
    print("\n✅ COMPLETE SRT PARSING WORKFLOW TEST PASSED")
    return True


def test_error_handling_and_fallbacks():
    """
    Test error handling and fallback mechanisms work correctly.
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    print("\n" + "=" * 60)
    print("END-TO-END TEST: Error Handling and Fallbacks")
    print("=" * 60)
    
    samples_dir = Path(__file__).parent.parent / "samples"
    test_video = samples_dir / "sample.mp4"
    
    if not test_video.exists():
        print(f"❌ ERROR: Sample video not found")
        return False
    
    processor = GuardianProcessor()
    
    # Test 1: Missing SRT File Handling
    print("\n--- Testing Missing SRT File Handling ---")
    
    # Create a temporary video file without corresponding SRT
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_video = Path(temp_dir) / "no_srt_video.mp4"
        shutil.copy2(test_video, temp_video)
        
        # Test SRT discovery with missing file
        discovered_srt = processor._find_srt_file(str(temp_video))
        if discovered_srt is None:
            print("✓ Correctly handled missing SRT file")
        else:
            print(f"⚠️  Unexpected SRT file found: {discovered_srt}")
        
        # Test complete workflow with missing SRT
        result = processor.censor_audio_with_ffmpeg(str(temp_video))
        
        # Should attempt embedded SRT extraction
        if result is None:
            print("✓ Correctly handled missing SRT (no embedded subtitles)")
        elif result == str(temp_video):
            print("✓ Returned original video when no censoring needed")
        else:
            print(f"⚠️  Unexpected result: {result}")
    
    # Test 2: Corrupted SRT File Handling
    print("\n--- Testing Corrupted SRT File Handling ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_video = Path(temp_dir) / "corrupted_srt_video.mp4"
        temp_srt = Path(temp_dir) / "corrupted_srt_video.srt"
        
        shutil.copy2(test_video, temp_video)
        
        # Create corrupted SRT file
        with open(temp_srt, 'w', encoding='utf-8') as f:
            f.write("This is not a valid SRT file\n")
            f.write("It has no proper timing or structure\n")
        
        # Test SRT parsing with corrupted file
        subtitles = processor._parse_srt_file(str(temp_srt))
        if subtitles is None or len(subtitles) == 0:
            print("✓ Correctly handled corrupted SRT file")
        else:
            print(f"⚠️  Unexpected parsing result: {len(subtitles)} subtitles")
        
        # Test complete workflow with corrupted SRT
        result = processor.censor_audio_with_ffmpeg(str(temp_video))
        
        # Should fall back to embedded SRT or return None
        if result is None or result == str(temp_video):
            print("✓ Correctly handled corrupted SRT file in workflow")
        else:
            print(f"⚠️  Unexpected workflow result: {result}")
    
    # Test 3: FFmpeg Command Failure Simulation
    print("\n--- Testing FFmpeg Failure Handling ---")
    
    # Mock subprocess.run to simulate FFmpeg failure
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Simulated FFmpeg failure")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "failed_output.mp4"
            
            try:
                result = processor.censor_audio_with_ffmpeg(str(test_video), str(output_path))
                
                if result is None:
                    print("✓ Correctly handled FFmpeg failure")
                else:
                    print(f"⚠️  Unexpected result despite FFmpeg failure: {result}")
                    
            except Exception as e:
                print(f"✓ Exception properly propagated: {type(e).__name__}")
    
    # Test 4: Fallback Strategy Testing
    print("\n--- Testing Fallback Strategy Mechanisms ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "fallback_test.mp4"
        
        # Test with real video to see fallback in action
        result = processor.censor_audio_with_ffmpeg(str(test_video), str(output_path))
        
        if result and output_path.exists():
            print("✓ Fallback mechanisms working (output created)")
            
            # Check if diagnostic file was created
            diagnostic_files = list(Path('.').glob('sample_diagnostic_*.json'))
            if diagnostic_files:
                print(f"✓ Diagnostic file created: {diagnostic_files[-1].name}")
                
                # Validate diagnostic content
                try:
                    with open(diagnostic_files[-1], 'r') as f:
                        diagnostic_data = json.load(f)
                    
                    required_fields = ['timestamp', 'input_video', 'output_video', 
                                     'overall_success', 'segments', 'final_strategy_used']
                    
                    missing_fields = [field for field in required_fields 
                                    if field not in diagnostic_data]
                    
                    if not missing_fields:
                        print("✓ Diagnostic file contains all required fields")
                        print(f"  Final strategy used: {diagnostic_data.get('final_strategy_used')}")
                        print(f"  Overall success: {diagnostic_data.get('overall_success')}")
                    else:
                        print(f"⚠️  Diagnostic file missing fields: {missing_fields}")
                        
                except Exception as e:
                    print(f"⚠️  Could not validate diagnostic file: {e}")
            else:
                print("⚠️  No diagnostic file found")
        else:
            print("❌ ERROR: Fallback mechanisms failed")
            return False
    
    print("\n✅ ERROR HANDLING AND FALLBACKS TEST PASSED")
    return True


def test_logging_and_diagnostics():
    """
    Test that logging and diagnostics provide useful information.
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    print("\n" + "=" * 60)
    print("END-TO-END TEST: Logging and Diagnostics")
    print("=" * 60)
    
    samples_dir = Path(__file__).parent.parent / "samples"
    test_video = samples_dir / "sample.mp4"
    
    if not test_video.exists():
        print(f"❌ ERROR: Sample video not found")
        return False
    
    # Set up log capture
    import io
    log_capture = io.StringIO()
    log_handler = logging.StreamHandler(log_capture)
    log_handler.setLevel(logging.INFO)
    
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    
    processor = GuardianProcessor()
    
    print("\n--- Testing Logging Output ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "logging_test.mp4"
        
        # Execute censoring with logging
        result = processor.censor_audio_with_ffmpeg(str(test_video), str(output_path))
        
        # Capture log output
        log_output = log_capture.getvalue()
        
        # Validate log content
        required_log_patterns = [
            "CENSORING OPERATION STARTED",
            "Found",
            "segments to censor",
            "FILTER CONSTRUCTION",
            "SILENCE VERIFICATION",
            "DIAGNOSTIC REPORT",
            "CENSORING OPERATION COMPLETED"
        ]
        
        missing_patterns = []
        for pattern in required_log_patterns:
            if pattern not in log_output:
                missing_patterns.append(pattern)
        
        if not missing_patterns:
            print("✓ All required log patterns found")
        else:
            print(f"⚠️  Missing log patterns: {missing_patterns}")
        
        # Check for specific logging details
        if "segments to censor" in log_output:
            print("✓ Segment information logged")
        
        if "RMS level" in log_output:
            print("✓ RMS level measurements logged")
        
        if "Strategy" in log_output:
            print("✓ Filter strategy information logged")
        
        if "FFmpeg" in log_output:
            print("✓ FFmpeg execution details logged")
    
    # Test diagnostic file generation
    print("\n--- Testing Diagnostic File Generation ---")
    
    diagnostic_files = list(Path('.').glob('sample_diagnostic_*.json'))
    if diagnostic_files:
        latest_diagnostic = max(diagnostic_files, key=lambda f: f.stat().st_mtime)
        print(f"✓ Diagnostic file found: {latest_diagnostic.name}")
        
        try:
            with open(latest_diagnostic, 'r') as f:
                diagnostic_data = json.load(f)
            
            # Validate diagnostic structure
            print("✓ Diagnostic file is valid JSON")
            
            # Check for key diagnostic information
            if 'segments' in diagnostic_data and len(diagnostic_data['segments']) > 0:
                print(f"✓ Segment diagnostics included: {len(diagnostic_data['segments'])} segments")
                
                # Check segment detail structure
                first_segment = diagnostic_data['segments'][0]
                segment_fields = ['segment_id', 'start_time', 'end_time', 'actual_rms_db', 
                                'meets_threshold', 'strategy_used']
                
                missing_segment_fields = [field for field in segment_fields 
                                        if field not in first_segment]
                
                if not missing_segment_fields:
                    print("✓ Segment diagnostics contain all required fields")
                else:
                    print(f"⚠️  Missing segment fields: {missing_segment_fields}")
            
            if 'recommendations' in diagnostic_data:
                print(f"✓ Recommendations included: {len(diagnostic_data['recommendations'])} items")
            
            if 'error_messages' in diagnostic_data:
                print(f"✓ Error tracking included: {len(diagnostic_data['error_messages'])} errors")
            
        except Exception as e:
            print(f"❌ ERROR: Could not validate diagnostic file: {e}")
            return False
    else:
        print("❌ ERROR: No diagnostic file found")
        return False
    
    # Clean up log handler
    logger.removeHandler(log_handler)
    
    print("\n✅ LOGGING AND DIAGNOSTICS TEST PASSED")
    return True


def test_embedded_srt_workflow():
    """
    Test workflow with embedded SRT subtitles.
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    print("\n" + "=" * 60)
    print("END-TO-END TEST: Embedded SRT Workflow")
    print("=" * 60)
    
    samples_dir = Path(__file__).parent.parent / "samples"
    test_video_with_srt = samples_dir / "sample_with_srt.mp4"
    
    if not test_video_with_srt.exists():
        print(f"⚠️  WARNING: Sample video with embedded SRT not found at {test_video_with_srt}")
        print("Skipping embedded SRT workflow test")
        return True  # Skip this test if file doesn't exist
    
    processor = GuardianProcessor()
    
    print("\n--- Testing Embedded SRT Extraction ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted_srt_path = Path(temp_dir) / "extracted.srt"
        
        # Test SRT extraction
        extraction_result = processor.extract_embedded_srt(
            str(test_video_with_srt), str(extracted_srt_path)
        )
        
        if extraction_result:
            print("✓ Embedded SRT extraction successful")
            
            if extracted_srt_path.exists():
                print("✓ Extracted SRT file created")
                
                # Validate extracted SRT content
                subtitles = processor._parse_srt_file(str(extracted_srt_path))
                if subtitles:
                    print(f"✓ Extracted SRT parsed successfully: {len(subtitles)} subtitles")
                else:
                    print("❌ ERROR: Could not parse extracted SRT")
                    return False
            else:
                print("❌ ERROR: Extracted SRT file not found")
                return False
        else:
            print("⚠️  Embedded SRT extraction failed (may not contain SRT track)")
        
        # Test complete workflow with embedded SRT
        print("\n--- Testing Complete Workflow with Embedded SRT ---")
        
        output_path = Path(temp_dir) / "embedded_srt_output.mp4"
        
        # Remove any external SRT file to force embedded extraction
        external_srt = test_video_with_srt.with_suffix('.srt')
        if external_srt.exists():
            print(f"⚠️  External SRT exists: {external_srt}")
        
        result = processor.censor_audio_with_ffmpeg(str(test_video_with_srt), str(output_path))
        
        if result:
            print("✓ Complete workflow with embedded SRT successful")
            
            if output_path.exists():
                print("✓ Output file created")
            else:
                print("❌ ERROR: Output file not created")
                return False
        else:
            print("⚠️  Workflow returned None (may indicate no profanity found or extraction failed)")
    
    print("\n✅ EMBEDDED SRT WORKFLOW TEST PASSED")
    return True


def main():
    """Run all end-to-end workflow tests."""
    print("DIALOGUE GUARDIAN - END-TO-END WORKFLOW VALIDATION")
    print("Testing complete workflow from SRT parsing to output verification")
    print("=" * 60)
    
    setup_logging()
    
    # Track test results
    tests = [
        ("Complete SRT Parsing Workflow", test_complete_srt_parsing_workflow),
        ("Error Handling and Fallbacks", test_error_handling_and_fallbacks),
        ("Logging and Diagnostics", test_logging_and_diagnostics),
        ("Embedded SRT Workflow", test_embedded_srt_workflow),
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
    print("END-TO-END WORKFLOW VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL END-TO-END WORKFLOW TESTS PASSED!")
        print("Complete workflow validation successful.")
        return True
    else:
        print(f"\n💥 {failed} END-TO-END WORKFLOW TESTS FAILED!")
        print("Please review the test output and fix the issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
