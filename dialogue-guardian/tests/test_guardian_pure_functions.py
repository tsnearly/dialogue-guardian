#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Unit tests for pure functions extracted from guardian.core module.
These tests don't use mocks and test the actual logic.
"""

import unittest
from datetime import timedelta

import srt

from guardian.core import GuardianProcessor


class TestGuardianPureFunctions(unittest.TestCase):
    """Test cases for pure functions that don't require mocking"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = GuardianProcessor()

    def test_parse_duration(self):
        """Test parsing duration output from ffprobe"""
        duration_output = "120.5"
        result = self.processor._parse_duration(duration_output)

        expected = {"duration": "120.5"}
        self.assertEqual(result, expected)

    def test_parse_duration_with_whitespace(self):
        """Test parsing duration output with whitespace"""
        duration_output = "  120.5  \n"
        result = self.processor._parse_duration(duration_output)

        expected = {"duration": "120.5"}
        self.assertEqual(result, expected)

    def test_parse_duration_empty(self):
        """Test parsing empty duration output"""
        duration_output = ""
        result = self.processor._parse_duration(duration_output)

        expected = {"duration": ""}
        self.assertEqual(result, expected)

    def test_parse_audio_streams_single_stream(self):
        """Test parsing single audio stream"""
        ffprobe_output = "aac|44100|2|stereo"
        result = self.processor._parse_audio_streams(ffprobe_output)

        expected = {
            "codec": "aac",
            "samplerate": "44100",
            "channels": "2",
            "audioconfig": "stereo",
        }
        self.assertEqual(result, expected)

    def test_parse_audio_streams_multiple_streams(self):
        """Test parsing multiple audio streams - picks one with most channels"""
        ffprobe_output = "aac|44100|1|mono\naac|48000|6|5.1\nmp3|22050|2|stereo"
        result = self.processor._parse_audio_streams(ffprobe_output)

        # Should pick the 6-channel stream
        expected = {
            "codec": "aac",
            "samplerate": "48000",
            "channels": "6",
            "audioconfig": "5.1",
        }
        self.assertEqual(result, expected)

    def test_parse_audio_streams_malformed_data(self):
        """Test parsing malformed audio stream data"""
        ffprobe_output = "malformed|data\n|incomplete|\naac|44100|2|stereo"
        result = self.processor._parse_audio_streams(ffprobe_output)

        # Should pick the valid stream
        expected = {
            "codec": "aac",
            "samplerate": "44100",
            "channels": "2",
            "audioconfig": "stereo",
        }
        self.assertEqual(result, expected)

    def test_parse_audio_streams_non_numeric_channels(self):
        """Test parsing audio streams with non-numeric channel data"""
        ffprobe_output = "aac|44100|unknown|stereo\naac|48000|2|stereo"
        result = self.processor._parse_audio_streams(ffprobe_output)

        # Should skip non-numeric and pick valid stream
        expected = {
            "codec": "aac",
            "samplerate": "48000",
            "channels": "2",
            "audioconfig": "stereo",
        }
        self.assertEqual(result, expected)

    def test_parse_audio_streams_empty_input(self):
        """Test parsing empty audio stream data"""
        result = self.processor._parse_audio_streams("")

        expected = {"codec": "", "samplerate": "", "channels": "", "audioconfig": ""}
        self.assertEqual(result, expected)

    def test_parse_framerate_info_fraction_format(self):
        """Test parsing framerate in fraction format"""
        result = self.processor._parse_framerate_info("30000/1001")

        expected = {
            "framerate": "30000/1001",
            "fps": "29.970",
            "frameduration": "1001/30000",
        }
        self.assertEqual(result, expected)

    def test_parse_framerate_info_decimal_format(self):
        """Test parsing framerate in decimal format"""
        result = self.processor._parse_framerate_info("24.0")

        expected = {
            "framerate": "24000/1000",
            "fps": "24.000",
            "frameduration": "1000/24000",
        }
        self.assertEqual(result, expected)

    def test_parse_framerate_info_division_by_zero(self):
        """Test parsing framerate with zero denominator"""
        result = self.processor._parse_framerate_info("30000/0")

        expected = {"framerate": None, "fps": None, "frameduration": None}
        self.assertEqual(result, expected)

    def test_parse_framerate_info_invalid_format(self):
        """Test parsing invalid framerate format"""
        result = self.processor._parse_framerate_info("invalid")

        expected = {"framerate": None, "fps": None, "frameduration": None}
        self.assertEqual(result, expected)

    def test_parse_framerate_info_none_input(self):
        """Test parsing None framerate"""
        result = self.processor._parse_framerate_info(None)

        expected = {"framerate": None, "fps": None, "frameduration": None}
        self.assertEqual(result, expected)

    def test_parse_video_stream_output_complete(self):
        """Test parsing complete video stream output"""
        ffprobe_output = "1920\n1080\n30000/1001"
        result = self.processor._parse_video_stream_output(ffprobe_output)

        expected = {
            "width": "1920",
            "height": "1080",
            "framerate": "30000/1001",
            "fps": "29.970",
            "frameduration": "1001/30000",
        }
        self.assertEqual(result, expected)

    def test_parse_video_stream_output_incomplete(self):
        """Test parsing incomplete video stream output"""
        ffprobe_output = "1920"
        result = self.processor._parse_video_stream_output(ffprobe_output)

        expected = {
            "width": "1920",
            "height": None,
            "framerate": None,
            "fps": None,
            "frameduration": None,
        }
        self.assertEqual(result, expected)

    def test_parse_ffprobe_streams_valid_json(self):
        """Test parsing valid JSON from ffprobe"""
        json_output = '{"streams": [{"index": 2, "codec_name": "subrip"}]}'
        result = self.processor._parse_ffprobe_streams(json_output)

        expected = [{"index": 2, "codec_name": "subrip"}]
        self.assertEqual(result, expected)

    def test_parse_ffprobe_streams_invalid_json(self):
        """Test parsing invalid JSON from ffprobe"""
        json_output = "invalid json"
        result = self.processor._parse_ffprobe_streams(json_output)

        self.assertEqual(result, [])

    def test_parse_ffprobe_streams_no_streams_key(self):
        """Test parsing JSON without streams key"""
        json_output = '{"format": {"duration": "120.5"}}'
        result = self.processor._parse_ffprobe_streams(json_output)

        self.assertEqual(result, [])

    def test_find_srt_streams(self):
        """Test filtering streams to find SRT-compatible ones"""
        streams = [
            {"index": 0, "codec_name": "h264"},
            {"index": 1, "codec_name": "aac"},
            {"index": 2, "codec_name": "subrip"},
            {"index": 3, "codec_name": "mov_text"},
            {"index": 4, "codec_name": "ass"},
        ]

        result = self.processor._find_srt_streams(streams)

        expected = [
            {"index": 2, "codec_name": "subrip"},
            {"index": 3, "codec_name": "mov_text"},
        ]
        self.assertEqual(result, expected)

    def test_find_srt_streams_none_found(self):
        """Test filtering streams when no SRT streams exist"""
        streams = [
            {"index": 0, "codec_name": "h264"},
            {"index": 1, "codec_name": "aac"},
        ]

        result = self.processor._find_srt_streams(streams)
        self.assertEqual(result, [])

    def test_select_best_srt_stream_with_default(self):
        """Test selecting best SRT stream when default exists"""
        srt_streams = [
            {"index": 2, "codec_name": "subrip", "disposition": {"default": 0}},
            {"index": 3, "codec_name": "subrip", "disposition": {"default": 1}},
            {"index": 4, "codec_name": "subrip", "disposition": {"default": 0}},
        ]

        result = self.processor._select_best_srt_stream(srt_streams)
        self.assertEqual(result, 3)

    def test_select_best_srt_stream_no_default(self):
        """Test selecting best SRT stream when no default exists"""
        srt_streams = [
            {"index": 2, "codec_name": "subrip", "disposition": {"default": 0}},
            {"index": 4, "codec_name": "subrip", "disposition": {"default": 0}},
        ]

        result = self.processor._select_best_srt_stream(srt_streams)
        self.assertEqual(result, 2)  # Should pick first one

    def test_select_best_srt_stream_empty_list(self):
        """Test selecting best SRT stream from empty list"""
        result = self.processor._select_best_srt_stream([])
        self.assertIsNone(result)

    def test_generate_srt_candidates(self):
        """Test generating SRT file candidates"""
        video_path = "/path/to/video.mp4"
        result = self.processor._generate_srt_candidates(video_path)

        expected = [
            "/path/to/video.srt",
            "/path/to/video.en.srt",
            "/path/to/video.fr.srt",
            "/path/to/video.es.srt",
            "/path/to/video.de.srt",
            "/path/to/video.it.srt",
        ]
        self.assertEqual(result, expected)

    def test_clean_subtitle_text(self):
        """Test cleaning subtitle text"""
        test_cases = [
            ("Hello, world!", "hello world"),
            ("What the f*ck?!", "what the fck"),
            ("Test... with [brackets]", "test with brackets"),
            ("UPPERCASE text", "uppercase text"),
            ("Text with 'apostrophes'", "text with 'apostrophes'"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor._clean_subtitle_text(input_text)
                self.assertEqual(result, expected)

    def test_build_profanity_pattern(self):
        """Test building profanity regex pattern"""
        words = ["fucking", "fuck", "shit", "damn"]
        pattern = self.processor._build_profanity_pattern(words)

        # Test that it matches expected words (need word boundaries)
        self.assertTrue(pattern.search("this is fucking bad"))  # Should match "fucking"
        self.assertTrue(pattern.search("this is fuck bad"))  # Should match "fuck"
        self.assertTrue(pattern.search("SHIT happens"))
        self.assertTrue(pattern.search("damn it"))

        # Test that it doesn't match partial words
        self.assertFalse(pattern.search("shitty"))  # Should not match partial
        self.assertFalse(pattern.search("damnation"))  # Should not match partial

        # Test case insensitivity
        self.assertTrue(pattern.search("FUCK"))
        self.assertTrue(pattern.search("Shit"))

    def test_build_profanity_pattern_empty_words(self):
        """Test building profanity pattern with empty word list"""
        pattern = self.processor._build_profanity_pattern([])

        # Should not match anything
        self.assertFalse(pattern.search("any text"))
        self.assertFalse(pattern.search("fuck shit damn"))

    def test_contains_profanity(self):
        """Test profanity detection in text"""
        words = ["fucking", "fuck", "shit", "damn"]
        pattern = self.processor._build_profanity_pattern(words)

        test_cases = [
            ("this is fucking bad", True),  # Should match "fucking"
            ("this is fuck bad", True),  # Should match "fuck"
            ("clean content", False),
            ("what the hell", False),  # "hell" not in our test words
            ("damn it", True),
            ("", False),
            ("this is shit", True),  # Exact word match
            ("shitty content", False),  # Partial word should not match
        ]

        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.processor._contains_profanity(text, pattern)
                self.assertEqual(result, expected)

    def test_build_volume_filters(self):
        """Test building volume filter strings"""
        segments = [(1.0, 2.0), (5.0, 7.5)]
        volume_setting = "volume=0"

        result = self.processor._build_volume_filters(segments, volume_setting)

        expected = [
            "volume=0:enable='between(t,1.0,2.0)'",
            "volume=0:enable='between(t,5.0,7.5)'",
        ]
        self.assertEqual(result, expected)

    def test_build_volume_filters_custom_quote(self):
        """Test building volume filters with custom quote character"""
        segments = [(1.0, 2.0)]
        volume_setting = "volume=-80dB"
        quote_char = '"'

        result = self.processor._build_volume_filters(
            segments, volume_setting, quote_char
        )

        expected = ['volume=-80dB:enable="between(t,1.0,2.0)"']
        self.assertEqual(result, expected)

    def test_build_volume_filters_empty_segments(self):
        """Test building volume filters with no segments"""
        result = self.processor._build_volume_filters([], "volume=0")
        self.assertEqual(result, [])

    def test_build_audio_filter_chain_basic_strategy(self):
        """Test building audio filter chain with basic strategy"""
        segments = [(1.0, 2.0), (5.0, 6.0)]

        result = self.processor._build_audio_filter_chain(segments, strategy_level=1)

        expected = (
            "volume=0:enable='between(t,1.0,2.0)',volume=0:enable='between(t,5.0,6.0)'"
        )
        self.assertEqual(result, expected)

    def test_build_audio_filter_chain_enhanced_strategy(self):
        """Test building audio filter chain with enhanced strategy"""
        segments = [(1.0, 2.0)]

        result = self.processor._build_audio_filter_chain(segments, strategy_level=2)

        # Should include format normalization and compression
        self.assertIn("aformat=sample_fmts=s16:channel_layouts=stereo", result)
        self.assertIn("volume=-80dB:enable='between(t,1.0,2.0)'", result)
        self.assertIn(
            "acompressor=threshold=-20dB:ratio=20:attack=5:release=50", result
        )

    def test_build_audio_filter_chain_aggressive_strategy(self):
        """Test building audio filter chain with aggressive strategy"""
        segments = [(1.0, 2.0)]

        result = self.processor._build_audio_filter_chain(segments, strategy_level=3)

        # Should include all filters plus null mixing
        self.assertIn("aformat=sample_fmts=s16:channel_layouts=stereo", result)
        self.assertIn("volume=0:enable='between(t,1.0,2.0)'", result)
        self.assertIn(
            "acompressor=threshold=-20dB:ratio=20:attack=5:release=50", result
        )
        self.assertIn("volume=-60dB", result)
        self.assertIn("agate=threshold=-90dB", result)

    def test_build_audio_filter_chain_no_segments(self):
        """Test building audio filter chain with no segments"""
        result = self.processor._build_audio_filter_chain([], strategy_level=2)

        # Should include format normalization and compression, no volume filters
        self.assertIn("aformat=sample_fmts=s16:channel_layouts=stereo", result)
        self.assertIn(
            "acompressor=threshold=-20dB:ratio=20:attack=5:release=50", result
        )
        self.assertNotIn("volume=", result)

    def test_build_ffmpeg_base_command(self):
        """Test building base FFmpeg command"""
        video_path = "/input/video.mp4"
        output_path = "/output/censored.mp4"
        audio_filter = "volume=0:enable='between(t,1.0,2.0)'"

        result = self.processor._build_ffmpeg_base_command(
            video_path, output_path, audio_filter
        )

        # Check key components
        self.assertIn(video_path, result)
        self.assertIn(output_path, result)
        self.assertIn(audio_filter, result)
        self.assertIn("-c:v", result)
        self.assertIn("copy", result)
        self.assertIn("-c:a", result)
        self.assertIn("aac", result)
        self.assertIn("-af", result)

    def test_find_profane_segments_integration(self):
        """Test complete profane segment detection with real subtitles"""
        # Create test subtitles
        subtitles = [
            srt.Subtitle(
                index=1,
                start=timedelta(seconds=1),
                end=timedelta(seconds=3),
                content="This is fucking terrible!",
            ),
            srt.Subtitle(
                index=2,
                start=timedelta(seconds=5),
                end=timedelta(seconds=7),
                content="Clean content here",
            ),
            srt.Subtitle(
                index=3,
                start=timedelta(seconds=10),
                end=timedelta(seconds=12),
                content="What the hell is this shit?",
            ),
        ]

        result = self.processor._find_profane_segments(subtitles)

        # Should find 2 profane segments
        expected = [(1.0, 3.0), (10.0, 12.0)]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
