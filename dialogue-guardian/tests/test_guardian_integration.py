#!/usr/bin/env python3
"""
Integration tests for guardian functionality
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

from guardian.core import GuardianProcessor


class TestGuardianIntegration(unittest.TestCase):
    """Integration test cases for Guardian functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = GuardianProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.test_video_path = os.path.join(self.temp_dir, "test.mp4")
        self.test_srt_path = os.path.join(self.temp_dir, "test.srt")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.check_output")
    def test_get_video_details_complex_framerate(self, mock_check_output):
        """Test video details with complex framerate calculations"""
        mock_check_output.side_effect = [
            "120.5",  # duration
            "aac|44100|2|stereo",  # audio info
            "1920\n1080\n25",  # video info with simple framerate
        ]

        result = self.processor.get_video_details(self.test_video_path)

        self.assertIsNotNone(result)
        self.assertEqual(result["fps"], "25.000")
        self.assertEqual(result["framerate"], "25000/1000")

    @patch("subprocess.check_output")
    def test_get_video_details_missing_video_info(self, mock_check_output):
        """Test video details when video stream info is incomplete"""
        mock_check_output.side_effect = [
            "120.5",  # duration
            "aac|44100|2|stereo",  # audio info
            "1920",  # incomplete video info
        ]

        result = self.processor.get_video_details(self.test_video_path)

        self.assertIsNotNone(result)
        self.assertIsNone(result["width"])
        self.assertIsNone(result["height"])
        self.assertIsNone(result["fps"])

    @patch("subprocess.check_output")
    def test_get_video_details_multiple_audio_streams(self, mock_check_output):
        """Test video details with multiple audio streams"""
        mock_check_output.side_effect = [
            "120.5",  # duration
            "aac|44100|1|mono\naac|48000|6|5.1",  # multiple audio streams
            "1920\n1080\n30000/1001",  # video info
        ]

        result = self.processor.get_video_details(self.test_video_path)

        self.assertIsNotNone(result)
        # Should pick the stream with more channels (6 > 1)
        self.assertEqual(result["channels"], "6")
        self.assertEqual(result["samplerate"], "48000")
        self.assertEqual(result["audioconfig"], "5.1")

    @patch("subprocess.check_output")
    @patch("json.loads")
    def test_extract_embedded_srt_multiple_streams(
        self, mock_json_loads, mock_check_output
    ):
        """Test SRT extraction with multiple subtitle streams"""
        mock_check_output.return_value = '{"streams": []}'
        mock_json_loads.return_value = {
            "streams": [
                {
                    "index": 2,
                    "codec_name": "subrip",
                    "disposition": {"default": 0},
                },
                {
                    "index": 3,
                    "codec_name": "subrip",
                    "disposition": {"default": 1},
                },
            ]
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            result = self.processor.extract_embedded_srt(
                self.test_video_path, self.test_srt_path
            )

        self.assertTrue(result)
        # Should use the default stream (index 3)
        call_args = mock_run.call_args[0][0]
        self.assertIn("0:3", call_args)

    @patch("subprocess.check_output")
    @patch("json.loads")
    def test_extract_embedded_srt_no_default_stream(
        self, mock_json_loads, mock_check_output
    ):
        """Test SRT extraction when no default stream is available"""
        mock_check_output.return_value = '{"streams": []}'
        mock_json_loads.return_value = {
            "streams": [
                {
                    "index": 2,
                    "codec_name": "subrip",
                    "disposition": {"default": 0},
                },
                {
                    "index": 4,
                    "codec_name": "subrip",
                    "disposition": {"default": 0},
                },
            ]
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            result = self.processor.extract_embedded_srt(
                self.test_video_path, self.test_srt_path
            )

        self.assertTrue(result)
        # Should use the first stream found (index 2)
        call_args = mock_run.call_args[0][0]
        self.assertIn("0:2", call_args)

    @patch("subprocess.run")
    def test_extract_embedded_srt_ffmpeg_failure(self, mock_run):
        """Test SRT extraction when ffmpeg fails"""
        with patch("subprocess.check_output") as mock_check_output, patch(
            "json.loads"
        ) as mock_json:
            mock_check_output.return_value = '{"streams": []}'
            mock_json.return_value = {
                "streams": [
                    {
                        "index": 2,
                        "codec_name": "subrip",
                        "disposition": {"default": 1},
                    }
                ]
            }
            import subprocess

            mock_run.side_effect = subprocess.CalledProcessError(
                1, "ffmpeg", "Extraction failed"
            )

            result = self.processor.extract_embedded_srt(
                self.test_video_path, self.test_srt_path
            )

        self.assertFalse(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    def test_censor_audio_language_specific_srt(
        self, mock_srt_parse, mock_file, mock_exists
    ):
        """Test audio censoring with language-specific SRT files"""

        # Mock file existence - main SRT doesn't exist, but English one does
        def exists_side_effect(path):
            return path.endswith(".en.srt")

        mock_exists.side_effect = exists_side_effect

        # Mock SRT parsing
        mock_subtitle = MagicMock()
        mock_subtitle.start.total_seconds.return_value = 10.0
        mock_subtitle.end.total_seconds.return_value = 15.0
        mock_subtitle.content = "This is fucking bad"
        mock_subtitle.index = 1
        mock_srt_parse.return_value = [mock_subtitle]

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertIsNotNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    def test_censor_audio_srt_parsing_error(
        self, mock_srt_parse, mock_file, mock_exists
    ):
        """Test audio censoring when SRT parsing fails"""
        mock_exists.return_value = True
        mock_srt_parse.side_effect = Exception("Parsing failed")

        with patch.object(self.processor, "extract_embedded_srt") as mock_extract:
            mock_extract.return_value = False

            result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    def test_censor_audio_external_srt_error_with_successful_extraction(
        self, mock_srt_parse, mock_file, mock_exists
    ):
        """Test fallback to embedded SRT when external SRT has errors"""
        mock_exists.return_value = True

        # First call (external SRT) fails, second call (extracted SRT) succeeds
        mock_subtitle = MagicMock()
        mock_subtitle.start.total_seconds.return_value = 10.0
        mock_subtitle.end.total_seconds.return_value = 15.0
        mock_subtitle.content = "This is fucking bad"
        mock_subtitle.index = 1

        mock_srt_parse.side_effect = [
            Exception("External SRT parsing failed"),
            [mock_subtitle],
        ]

        with patch.object(
            self.processor, "extract_embedded_srt"
        ) as mock_extract, patch("subprocess.run") as mock_run:
            mock_extract.return_value = True
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertIsNotNone(result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    def test_censor_audio_empty_subtitles(self, mock_srt_parse, mock_file, mock_exists):
        """Test audio censoring when subtitles are empty"""
        mock_exists.return_value = True
        mock_srt_parse.return_value = []

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertIsNotNone(result)
        # Should use anull filter when no subtitles
        call_args = mock_run.call_args[0][0]
        af_index = call_args.index("-af")
        self.assertEqual(call_args[af_index + 1], "anull")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("srt.parse")
    def test_censor_audio_complex_profanity_patterns(
        self, mock_srt_parse, mock_file, mock_exists
    ):
        """Test audio censoring with complex profanity patterns"""
        mock_exists.return_value = True

        # Create subtitles with various profanity patterns
        subtitles = []
        for i, content in enumerate(
            [
                "This is fucking terrible!",  # Basic profanity
                "What the hell is going on?",  # Common phrase
                "Jesus Christ, that's bad",  # Religious profanity
                "You're such a smartass",  # Compound word
                "Clean content here",  # No profanity
            ],
            1,
        ):
            mock_subtitle = MagicMock()
            mock_subtitle.start.total_seconds.return_value = i * 10.0
            mock_subtitle.end.total_seconds.return_value = i * 10.0 + 5.0
            mock_subtitle.content = content
            mock_subtitle.index = i
            subtitles.append(mock_subtitle)

        mock_srt_parse.return_value = subtitles

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

            result = self.processor.censor_audio_with_ffmpeg(self.test_video_path)

        self.assertIsNotNone(result)
        # Should have multiple volume filters for profane segments
        call_args = mock_run.call_args[0][0]
        af_index = call_args.index("-af")
        filter_string = call_args[af_index + 1]
        # Should contain multiple volume filters
        self.assertIn("volume=enable=", filter_string)
        # Should have commas separating multiple filters
        volume_count = filter_string.count("volume=enable=")
        self.assertGreater(volume_count, 1)

    def test_custom_matching_words(self):
        """Test processor with custom matching words"""
        custom_words = ["badword", "anotherbad"]
        processor = GuardianProcessor(matching_words=custom_words)

        self.assertEqual(processor.matching_words, custom_words)
        self.assertNotEqual(
            processor.matching_words, GuardianProcessor.DEFAULT_MATCHING_WORDS
        )

    def test_custom_ffmpeg_paths(self):
        """Test processor with custom FFmpeg paths"""
        processor = GuardianProcessor(
            ffmpeg_cmd="/custom/ffmpeg", ffprobe_cmd="/custom/ffprobe"
        )

        self.assertEqual(processor.ffmpeg_cmd, "/custom/ffmpeg")
        self.assertEqual(processor.ffprobe_cmd, "/custom/ffprobe")


if __name__ == "__main__":
    unittest.main()
