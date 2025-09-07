#!/usr/bin/env python3
"""
Unit tests for guardian.py
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

# Import the functions we want to test
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guardian import (
    get_video_details,
    create_fcpxml,
    matching_words
)

class TestGuardian(unittest.TestCase):
    """Test cases for guardian.py functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_video_path = "/test/video.mp4"
        self.test_srt_path = "/test/video.srt"
        self.temp_dir = tempfile.mkdtemp()
        self.video_info = {
            "duration": "120.5",
            "codec": "aac",
            "samplerate": "48000",
            "channels": "2",
            "audioconfig": "stereo",
            "width": "1920",
            "height": "1080",
            "framerate": "30000/1001",
            "fps": "29.970",
            "frameduration": "1001/30000"
        }

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('subprocess.Popen')
    def test_get_video_details_success(self, mock_popen):
        """Test successful video details extraction"""
        # Mock ffprobe responses
        mock_process = MagicMock()
        mock_process.communicate.side_effect = [
            ("120.5\n", ""),  # duration
            ("aac|48000|2|stereo\n", ""),  # audio info
            ("1920\n1080\n30000/1001\n", "")  # video info
        ]
        mock_popen.return_value = mock_process

        with patch('guardian.ffprobe_cmd', './ffprobe'):
            result = get_video_details(self.test_video_path)

        self.assertIsNotNone(result)
        self.assertEqual(result['duration'], "120.5")
        self.assertEqual(result['width'], "1920")
        self.assertEqual(result['height'], "1080")
        self.assertEqual(result['fps'], "29.970")
        self.assertEqual(result['channels'], "2")

    @patch('subprocess.Popen')
    def test_get_video_details_integer_framerate(self, mock_popen):
        """Test video details extraction with integer framerate"""
        mock_process = MagicMock()
        mock_process.communicate.side_effect = [
            ("60.0\n", ""),
            ("pcm_s16le|44100|1|mono\n", ""),
            ("1280\n720\n30\n", "")
        ]
        mock_popen.return_value = mock_process

        with patch('guardian.ffprobe_cmd', './ffprobe'):
            result = get_video_details(self.test_video_path)

        self.assertEqual(result['fps'], "30.000")
        self.assertEqual(result['framerate'], "30000/1000")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_fcpxml_no_srt(self, mock_file, mock_exists):
        """Test FCPXML creation when no SRT file is found"""
        mock_exists.return_value = False
        
        tree = create_fcpxml(self.test_video_path, self.video_info)
        
        # Check that the XML was created but has no keyframes other than the initial one
        self.assertIsNotNone(tree)
        root = tree.getroot()
        keyframes = root.findall(".//keyframe")
        self.assertEqual(len(keyframes), 1)
        self.assertEqual(keyframes[0].get("value"), "0dB")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="1\n00:00:05,500 --> 00:00:07,000\nThis is a fucking test.\n")
    @patch('srt.parse')
    def test_create_fcpxml_with_profanity(self, mock_srt_parse, mock_open_file, mock_exists):
        """Test FCPXML creation with a profane SRT file"""
        mock_exists.return_value = True
        
        mock_subtitle = MagicMock()
        mock_subtitle.start.total_seconds.return_value = 5.5
        mock_subtitle.end.total_seconds.return_value = 7.0
        mock_subtitle.content = "This is a fucking test."
        mock_subtitle.index = 1
        mock_srt_parse.return_value = [mock_subtitle]

        tree = create_fcpxml(self.test_video_path, self.video_info)
        
        self.assertIsNotNone(tree)
        root = tree.getroot()
        keyframes = root.findall(".//keyframe")
        
        # Expected keyframes: initial, fade out, mute start, mute end, fade in
        self.assertTrue(len(keyframes) > 1) 
        
        values = [k.get("value") for k in keyframes]
        self.assertIn('-96dB', values)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="1\n00:00:05,500 --> 00:00:07,000\nThis is a clean test.\n")
    @patch('srt.parse')
    def test_create_fcpxml_no_profanity(self, mock_srt_parse, mock_open_file, mock_exists):
        """Test FCPXML creation with a clean SRT file"""
        mock_exists.return_value = True

        mock_subtitle = MagicMock()
        mock_subtitle.start.total_seconds.return_value = 5.5
        mock_subtitle.end.total_seconds.return_value = 7.0
        mock_subtitle.content = "This is a clean test."
        mock_subtitle.index = 1
        mock_srt_parse.return_value = [mock_subtitle]

        tree = create_fcpxml(self.test_video_path, self.video_info)
        
        self.assertIsNotNone(tree)
        root = tree.getroot()
        keyframes = root.findall(".//keyframe")
        
        # Only the initial keyframe should exist
        self.assertEqual(len(keyframes), 1)
        self.assertEqual(keyframes[0].get("value"), "0dB")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="1\n00:00:01,000 --> 00:00:02,000\nWhat the hell?\n")
    @patch('srt.parse')
    def test_create_fcpxml_language_srt(self, mock_srt_parse, mock_open_file, mock_exists):
        """Test FCPXML creation with a language-specific SRT file"""
        # .srt is false, .en.srt is true
        mock_exists.side_effect = [False, True]
        
        mock_subtitle = MagicMock()
        mock_subtitle.start.total_seconds.return_value = 1.0
        mock_subtitle.end.total_seconds.return_value = 2.0
        mock_subtitle.content = "What the hell?"
        mock_subtitle.index = 1
        mock_srt_parse.return_value = [mock_subtitle]

        create_fcpxml(self.test_video_path, self.video_info)

        # Check that open was called with the .en.srt path
        expected_path = os.path.splitext(self.test_video_path)[0] + '.en.srt'
        from unittest.mock import call
        self.assertIn(call(expected_path, 'r', encoding='utf-8-sig'), mock_open_file.call_args_list)

    def test_xml_structure(self):
        """Test the basic structure of the generated FCPXML"""
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', new_callable=mock_open), \
             patch('srt.parse') as mock_srt_parse:
            
            mock_exists.return_value = False # No SRT
            mock_srt_parse.return_value = []

            tree = create_fcpxml(self.test_video_path, self.video_info)
            root = tree.getroot()

            self.assertEqual(root.tag, 'fcpxml')
            self.assertIsNotNone(root.find("resources"))
            self.assertIsNotNone(root.find("library/event/project/sequence/spine"))
            
            # Check that format is correctly referenced
            asset_clip = root.find(".//asset-clip")
            self.assertIsNotNone(asset_clip)
            format_id = asset_clip.get("format")
            self.assertTrue(format_id.startswith("r"))


if __name__ == '__main__':
    unittest.main()
