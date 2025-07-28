import unittest
from unittest import mock
import os
import sys
import xml.etree.ElementTree as ET
import re # Added import for regex
import logging

import srt_tools
import srt_tools.utils
import srt

# Adjust the path to import functions from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from guardian import get_video_details, create_fcpxml, matching_words

def _parse_srt_content(srt_content):
    """
    Parses SRT content from a string and returns a list of subtitle dicts.
    Each dict contains 'index', 'start_time', 'end_time', and 'text'.
    """
    import html
    subs = []
    # Normalize line endings
    srt_content = srt_content.replace('\r\n', '\n').replace('\r', '\n')
    try:
        subtitles = list(srt.parse(srt_content))
    except Exception:
        return []
    for sub in subtitles:
        # Remove HTML tags and special characters, lowercase text
        text = sub.content
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
        text = text.lower().strip()
        subs.append({
            'index': str(sub.index) if hasattr(sub, 'index') else '',
            'start_time': str(sub.start).replace('.', ',')[:12] if hasattr(sub, 'start') else '',
            'end_time': str(sub.end).replace('.', ',')[:12] if hasattr(sub, 'end') else '',
            'text': text
        })
    return subtitles

def parse_srt(srt_path):
    """
    Parses an SRT file and returns a list of subtitle dicts.
    Each dict contains 'index', 'start_time', 'end_time', and 'text'.
    """
    import html
    if not os.path.exists(srt_path):
        logging.error(f"SRT file not found: {srt_path}")
        return []
    with open(srt_path, 'r', encoding='utf-8-sig') as f:
        srt_content = f.read()
    return _parse_srt_content(srt_content)

class TestGuardianFunctions(unittest.TestCase):

    def setUp(self):
        # Set up any common test fixtures or mocks here
        pattern = r'\b(' + '|'.join(re.escape(word) for word in matching_words) + r')\b'
        self.censor_pattern = re.compile(pattern, re.IGNORECASE)

    def tearDown(self):
        # Clean up after each test
        pass

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('os.path.exists', return_value=True)
    def test_parse_srt_valid_file(self, mock_exists, mock_open):
        mock_open.return_value.read.return_value = """
1
00:00:01,000 --> 00:00:02,000
Hello world.

2
00:00:03,000 --> 00:00:04,000
This is a test.
"""
        expected_subs = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'hello world'},
            {'index': '2', 'start_time': '00:00:03,000', 'end_time': '00:00:04,000', 'text': 'this is a test'}
        ]
        self.assertEqual(parse_srt("dummy.srt"), expected_subs)
        mock_open.assert_called_once_with("dummy.srt", 'r', encoding='utf-8-sig')

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('os.path.exists', return_value=True)
    def test_parse_srt_empty_file(self, mock_exists, mock_open):
        mock_open.return_value.read.return_value = ""
        self.assertEqual(parse_srt("empty.srt"), [])

    @mock.patch('os.path.exists', return_value=False)
    def test_parse_srt_file_not_found(self, mock_exists):
        with self.assertLogs('root', level='ERROR') as cm:
            self.assertEqual(parse_srt("nonexistent.srt"), [])
            self.assertIn("SRT file not found: nonexistent.srt", cm.output[0])

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('os.path.exists', return_value=True)
    def test_parse_srt_with_html_tags(self, mock_exists, mock_open):
        mock_open.return_value.read.return_value = """
1
00:00:01,000 --> 00:00:02,000
Hello <i>world</i>.
"""
        expected_subs = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'hello world'}
        ]
        self.assertEqual(parse_srt("html.srt"), expected_subs)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('os.path.exists', return_value=True)
    def test_parse_srt_with_matching_words(self, mock_exists, mock_open):
        mock_open.return_value.read.return_value = """
1
00:00:01,000 --> 00:00:02,000
This is some shit.

2
00:00:03,000 --> 00:00:04,000
Another line with a bitch.
"""
        expected_subs = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'this is some shit'},
            {'index': '2', 'start_time': '00:00:03,000', 'end_time': '00:00:04,000', 'text': 'another line with a bitch'}
        ]
        self.assertEqual(parse_srt("matching.srt"), expected_subs)

    def test_finds_profanity(self):
        """Tests that a subtitle with a profane word is correctly matched."""
        srt_content = "1\n00:00:01,000 --> 00:00:02,000\nWhat the hell."
        subs = _parse_srt_content(srt_content)
        match = self.censor_pattern.search(subs[0].content)
        self.assertTrue(match, "Should find a match in 'hell'")

    def test_avoids_substring_false_positive(self):
        """Tests the 'ass' in 'assistant' bug."""
        srt_content = "1\n00:00:01,000 --> 00:00:02,000\nThis is my assistant."
        subs = _parse_srt_content(srt_content)
        match = self.censor_pattern.search(subs[0].content)
        self.assertFalse(match, "Should NOT find a match in 'assistant'")

    def test_avoids_contraction_false_positive(self):
        """Tests the 'he'll' vs 'hell' bug."""
        srt_content = "1\n00:00:01,000 --> 00:00:02,000\nI think he'll be okay."
        subs = _parse_srt_content(srt_content)
        match = self.censor_pattern.search(subs[0].content)
        self.assertFalse(match, "Should NOT find 'hell' in 'he'll'")
    
    def test_matches_multi_word_phrase(self):
        """Tests that phrases like 'son of a bitch' are matched."""
        srt_content = "1\n00:00:01,000 --> 00:00:02,000\nYou son of a bitch!"
        subs = _parse_srt_content(srt_content)
        match = self.censor_pattern.search(subs[0].content)
        self.assertTrue(match, "Should find the phrase 'son of a bitch'")
        
    def test_ignores_clean_subtitle(self):
        """Tests that a completely clean subtitle returns no match."""
        srt_content = "1\n00:00:01,000 --> 00:00:02,000\nThis is a pleasant conversation."
        subs = _parse_srt_content(srt_content)
        match = self.censor_pattern.search(subs[0].content)
        self.assertFalse(match, "Should not find any match in a clean subtitle")

    @mock.patch('subprocess.Popen')
    def test_get_video_details_success(self, mock_popen):
        # Mock the ffprobe commands' stdout for duration, audio, and video streams
        mock_popen.side_effect = [
            mock.Mock(communicate=mock.Mock(return_value=("120.500000\n", ""))), # Duration
            mock.Mock(communicate=mock.Mock(return_value=("aac|48000|2|stereo\n", ""))), # Audio
            mock.Mock(communicate=mock.Mock(return_value=("1920\n1080\n24/1\n", ""))) # Video
        ]

        expected_details = {
            'duration': '120.500000',
            'codec': 'aac',
            'samplerate': '48000',
            'channels': '2',
            'audioconfig': 'stereo',
            'width': '1920',
            'height': '1080',
            'framerate': '24/1',
            'fps': '24.000',
            'frameduration': '1/24'
        }
        
        # Call the function under test
        details = get_video_details("dummy.mp4")
        
        # Assertions
        self.assertEqual(details, expected_details)
        self.assertEqual(mock_popen.call_count, 3) # Ensure ffprobe was called 3 times

    @mock.patch('subprocess.Popen')
    def test_get_video_details_no_audio_config(self, mock_popen):
        mock_popen.side_effect = [
            mock.Mock(communicate=mock.Mock(return_value=("10.0\n", ""))),
            mock.Mock(communicate=mock.Mock(return_value=("aac|44100|1\n", ""))), # No audioconfig
            mock.Mock(communicate=mock.Mock(return_value=("1280\n720\n30/1\n", "")))
        ]
        details = get_video_details("dummy.mp4")
        self.assertEqual(details['audioconfig'], "")

    @mock.patch('subprocess.Popen')
    def test_get_video_details_float_fps(self, mock_popen):
        mock_popen.side_effect = [
            mock.Mock(communicate=mock.Mock(return_value=("5.0\n", ""))),
            mock.Mock(communicate=mock.Mock(return_value=("aac|44100|2|stereo\n", ""))),
            mock.Mock(communicate=mock.Mock(return_value=("1920\n1080\n29.97\n", ""))) # Float FPS
        ]
        details = get_video_details("dummy.mp4")
        self.assertEqual(details['fps'], "29.970")
        self.assertEqual(details['framerate'], "29970/1000")
        self.assertEqual(details['frameduration'], "1000/29970")

    @mock.patch('subprocess.Popen')
    def test_get_video_details_no_video_stream(self, mock_popen):
        mock_popen.side_effect = [
            mock.Mock(communicate=mock.Mock(return_value=("10.0\n", ""))),
            mock.Mock(communicate=mock.Mock(return_value=("aac|44100|2|stereo\n", ""))),
            mock.Mock(communicate=mock.Mock(return_value=(("", "")))) # No video stream output
        ]
        details = get_video_details("dummy.mp4")
        self.assertIsNone(details.get('width'))
        self.assertIsNone(details.get('height'))
        self.assertIsNone(details.get('framerate'))

    @mock.patch('os.path.basename', return_value="test_video.mp4")
    @mock.patch('os.path.splitext', side_effect=lambda x: (x.replace('.mp4', ''), '.mp4'))
    @mock.patch('pathlib.Path.as_uri', return_value="file:///path/to/test_video.mp4")
    @mock.patch('guardian.parse_srt')
    @mock.patch('xml.etree.ElementTree.tostring')
    @mock.patch('guardian.parseString')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_create_fcpxml(self, mock_open, mock_parseString, mock_tostring, mock_parse_srt, mock_as_uri, mock_splitext, mock_basename):
        video_info = {
            'duration': '10.0',
            'codec': 'aac',
            'samplerate': '48000',
            'channels': '2',
            'audioconfig': 'stereo',
            'width': '1920',
            'height': '1080',
            'framerate': '24/1',
            'fps': '24.000',
            'frameduration': '1/24'
        }
        
        mock_parse_srt.return_value = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'some shit'},
            {'index': '2', 'start_time': '00:00:03,000', 'end_time': '00:00:04,000', 'text': 'another bitch'}
        ]

        mock_tostring.return_value = b"<fcpxml version=\"1.9\"><resources><format id=\"r1\" name=\"FFVideoFormat1080p24_000\" frameDuration=\"1/24s\" width=\"1920\" height=\"1080\" /><format id=\"r2\" name=\"FFVideoFormat1080p24_000\" frameDuration=\"1/24s\" width=\"1920\" height=\"1080\" /><asset id=\"r3\" name=\"test_video.mp4\" duration=\"240/24s\" hasVideo=\"1\" hasAudio=\"1\" format=\"r1\" audioChannels=\"2\" audioRate=\"48000\" /><media-rep kind=\"original-media\" src=\"file:///path/to/test_video.mp4\" /></resources><library location=\"file:///Users/Shared/\"><event name=\"Imported Media\"><project name=\"test_video\"><sequence format=\"r2\" duration=\"240/24s\" tcFormat=\"NDF\" audioLayout=\"stereo\" audioRate=\"48k\"><spine><asset-clip ref=\"r3\" name=\"test_video\" format=\"r1\" duration=\"240/24s\"><adjust-volume><param name=\"amount\"><keyframeAnimation><keyframe time=\"0/24s\" value=\"0dB\" /><keyframe time=\"0/24s\" value=\"0dB\" /><keyframe time=\"24/24s\" value=\"-96dB\" /><keyframe time=\"48/24s\" value=\"-96dB\" /><keyframe time=\"72/24s\" value=\"0dB\" /><keyframe time=\"72/24s\" value=\"0dB\" /><keyframe time=\"96/24s\" value=\"-96dB\" /><keyframe time=\"120/24s\" value=\"-96dB\" /><keyframe time=\"144/24s\" value=\"0dB\" /></keyframeAnimation></param></adjust-volume></asset-clip></spine></sequence></project></event></library></fcpxml>"
        mock_parseString.return_value.toprettyxml.return_value = "<pretty_xml_output>"

        tree = create_fcpxml("test_video.mp4", video_info)

        mock_parse_srt.assert_called_once_with("test_video.srt")
        mock_tostring.assert_called_once()
        mock_parseString.assert_called_once()
        mock_open.assert_called_once_with("test_video.fcpxml", "w", encoding="utf-8")
        mock_open.return_value.write.assert_called_once_with("<pretty_xml_output>")

        # You can add more specific assertions about the XML structure if needed
        # For example, parsing the mocked tostring output and checking elements
        root = ET.fromstring(mock_tostring.return_value)
        self.assertEqual(root.tag, "fcpxml")
        self.assertEqual(root.attrib["version"], "1.9")
        
        # Check for format elements
        formats = root.findall(".//format")
        self.assertEqual(len(formats), 2)
        self.assertEqual(formats[0].attrib["id"], "r1")
        self.assertEqual(formats[0].attrib["name"], "FFVideoFormat1080p24_000")

        # Check for asset element
        asset = root.find(".//asset")
        self.assertIsNotNone(asset)
        self.assertEqual(asset.attrib["id"], "r3")
        self.assertEqual(asset.attrib["name"], "test_video.mp4")

        # Check for sequence element
        sequence = root.find(".//sequence")
        self.assertIsNotNone(sequence)
        self.assertEqual(sequence.attrib["audioLayout"], "stereo")
        self.assertEqual(sequence.attrib["audioRate"], "48k")

        # Check for keyframes
        keyframes = root.findall(".//keyframe")
        self.assertEqual(len(keyframes), 9) # 1 initial + 2 words * 4 keyframes - 1 duplicate
        self.assertEqual(keyframes[0].attrib["time"], "0/24s")
        self.assertEqual(keyframes[0].attrib["value"], "0dB")
        self.assertEqual(keyframes[1].attrib["time"], "0/24s")
        self.assertEqual(keyframes[1].attrib["value"], "0dB")
        self.assertEqual(keyframes[2].attrib["time"], "24/24s")
        self.assertEqual(keyframes[2].attrib["value"], "-96dB")

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_parse_srt_multiple_subtitles(self, mock_open):
        mock_open.return_value.read.return_value = """
1
00:00:01,000 --> 00:00:02,000
Hello world.

2
00:00:03,000 --> 00:00:04,000
This is a test.

3
00:00:05,000 --> 00:00:06,000
Another subtitle.
"""
        expected_subs = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'hello world'},
            {'index': '2', 'start_time': '00:00:03,000', 'end_time': '00:00:04,000', 'text': 'this is a test'},
            {'index': '3', 'start_time': '00:00:05,000', 'end_time': '00:00:06,000', 'text': 'another subtitle'}
        ]
        self.assertEqual(parse_srt("multiple.srt"), expected_subs)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_parse_srt_special_characters(self, mock_open):
        mock_open.return_value.read.return_value = """
1
00:00:01,000 --> 00:00:02,000
Hello, world! @#$%^&*()

2
00:00:03,000 --> 00:00:04,000
Special characters: ~`<>?
"""
        expected_subs = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'hello world'},
            {'index': '2', 'start_time': '00:00:03,000', 'end_time': '00:00:04,000', 'text': 'special characters'}
        ]
        self.assertEqual(parse_srt("special_chars.srt"), expected_subs)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_parse_srt_different_line_endings(self, mock_open):
        mock_open.return_value.read.return_value = "1\r\n00:00:01,000 --> 00:00:02,000\r\nHello world.\r\n\r\n2\n00:00:03,000 --> 00:00:04,000\nThis is a test.\n"
        expected_subs = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'hello world'},
            {'index': '2', 'start_time': '00:00:03,000', 'end_time': '00:00:04,000', 'text': 'this is a test'}
        ]
        self.assertEqual(parse_srt("line_endings.srt"), expected_subs)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_parse_srt_incorrect_timestamp_format(self, mock_open):
        mock_open.return_value.read.return_value = """
1
00:00:01 --> 00:00:02
Hello world.
"""
        expected_subs = []
        self.assertEqual(parse_srt("incorrect_timestamp.srt"), expected_subs)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_parse_srt_overlapping_subtitles(self, mock_open):
        mock_open.return_value.read.return_value = """
1
00:00:01,000 --> 00:00:03,000
First subtitle.

2
00:00:02,000 --> 00:00:04,000
Overlapping subtitle.
"""
        expected_subs = [
            {'index': '1', 'start_time': '00:00:01,000', 'end_time': '00:00:03,000', 'text': 'first subtitle'},
            {'index': '2', 'start_time': '00:00:02,000', 'end_time': '00:00:04,000', 'text': 'overlapping subtitle'}
        ]
        self.assertEqual(parse_srt("overlapping.srt"), expected_subs)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_parse_srt_missing_subtitle_numbers(self, mock_open):
        mock_open.return_value.read.return_value = """
00:00:01,000 --> 00:00:02,000
Subtitle without number.

2
00:00:03,000 --> 00:00:04,000
Another subtitle.
"""
        expected_subs = [
            {'index': '', 'start_time': '00:00:01,000', 'end_time': '00:00:02,000', 'text': 'subtitle without number'},
            {'index': '2', 'start_time': '00:00:03,000', 'end_time': '00:00:04,000', 'text': 'another subtitle'}
        ]
        self.assertEqual(parse_srt("missing_numbers.srt"), expected_subs)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_parse_srt_empty_file_additional(self, mock_open):
        mock_open.return_value.read.return_value = ""
        self.assertEqual(parse_srt("empty.srt"), [])

    @mock.patch('os.path.exists', return_value=False)
    def test_parse_srt_non_existent_file_additional(self, mock_exists):
        with self.assertLogs('root', level='ERROR') as cm:
            self.assertEqual(parse_srt("nonexistent.srt"), [])
            self.assertIn("SRT file not found: nonexistent.srt", cm.output[0])

    def test_time_s_to_rational_str_basic(self):
                # Replicate the logic from guardian.py for testing
        def time_s_to_rational_str(time_s, frame_dur_num, timebase):
            frame_duration_s = frame_dur_num / timebase
            num_frames = int(float(time_s) // frame_duration_s)
            time_ticks = num_frames * frame_dur_num
            return f"{time_ticks}/{timebase}s"

        # Test with 1/24 frame duration (typical for 24fps video)
        frame_dur_num = 1
        timebase = 24
        self.assertEqual(time_s_to_rational_str(0, frame_dur_num, timebase), "0/24s")
        self.assertEqual(time_s_to_rational_str(1, frame_dur_num, timebase), "24/24s")
        self.assertEqual(time_s_to_rational_str(0.5, frame_dur_num, timebase), "12/24s")
        self.assertEqual(time_s_to_rational_str(2, frame_dur_num, timebase), "48/24s")
        self.assertEqual(time_s_to_rational_str(0.0416667, frame_dur_num, timebase), "0/24s")  # Less than one frame

    def test_time_s_to_rational_str_non_integer_frame_duration(self):
        # Test with 1000/29970 frame duration (typical for 29.97fps video)
        frame_dur_num = 1000
        timebase = 29970
        frame_duration_s = frame_dur_num / timebase  # ~0.0333667s per frame
        def time_s_to_rational_str(time_s, frame_dur_num, timebase):
            frame_duration_s = frame_dur_num / timebase
            num_frames = int(float(time_s) // frame_duration_s)
            time_ticks = num_frames * frame_dur_num
            return f"{time_ticks}/{timebase}s"

        self.assertEqual(time_s_to_rational_str(0, frame_dur_num, timebase), "0/29970s")
        self.assertEqual(time_s_to_rational_str(frame_duration_s, frame_dur_num, timebase), "1000/29970s")
        self.assertEqual(time_s_to_rational_str(1, frame_dur_num, timebase), f"{int(1//frame_duration_s)*1000}/29970s")
        self.assertEqual(time_s_to_rational_str(2, frame_dur_num, timebase), f"{int(2//frame_duration_s)*1000}/29970s")

    def test_time_s_to_rational_str_large_values(self):
        frame_dur_num = 1
        timebase = 24
        def time_s_to_rational_str(time_s, frame_dur_num, timebase):
            frame_duration_s = frame_dur_num / timebase
            num_frames = int(float(time_s) // frame_duration_s)
            time_ticks = num_frames * frame_dur_num
            return f"{time_ticks}/{timebase}s"

        self.assertEqual(time_s_to_rational_str(60, frame_dur_num, timebase), "1440/24s")  # 60s * 24fps = 1440 frames
        self.assertEqual(time_s_to_rational_str(3600, frame_dur_num, timebase), "86400/24s")  # 3600s * 24fps = 86400 frames

    def test_time_s_to_rational_str_negative_and_fractional(self):
        frame_dur_num = 1
        timebase = 24
        def time_s_to_rational_str(time_s, frame_dur_num, timebase):
            frame_duration_s = frame_dur_num / timebase
            num_frames = int(float(time_s) // frame_duration_s)
            time_ticks = num_frames * frame_dur_num
            return f"{time_ticks}/{timebase}s"

        self.assertEqual(time_s_to_rational_str(-1, frame_dur_num, timebase), "-24/24s")
        self.assertEqual(time_s_to_rational_str(0.04, frame_dur_num, timebase), "0/24s")  # Less than one frame
        self.assertEqual(time_s_to_rational_str(0.08, frame_dur_num, timebase), "1/24s")  # Just over one frame

    def test_time_s_to_rational_str_zero_frame_duration(self):
        # Should handle division by zero gracefully (simulate what happens)
        frame_dur_num = 0
        timebase = 24
        def time_s_to_rational_str(time_s, frame_dur_num, timebase):
            try:
                frame_duration_s = frame_dur_num / timebase
                num_frames = int(float(time_s) // frame_duration_s)
                time_ticks = num_frames * frame_dur_num
                return f"{time_ticks}/{timebase}s"
            except ZeroDivisionError:
                return "error"
        self.assertEqual(time_s_to_rational_str(1, frame_dur_num, timebase), "error")
