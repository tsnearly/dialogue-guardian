#!/usr/bin/env python3
"""
Unit tests for guardian.cli module
"""

import argparse
import io
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from guardian.cli import create_parser, main, setup_logging, validate_args


class TestGuardianCLI(unittest.TestCase):
    """Test cases for Guardian CLI functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        # Create a dummy video file for testing
        with open(self.test_video, "w") as f:
            f.write("dummy video content")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_parser(self):
        """Test argument parser creation"""
        parser = create_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.prog, "guardian")

    def test_parser_required_arguments(self):
        """Test parser with required arguments"""
        parser = create_parser()
        args = parser.parse_args([self.test_video])
        self.assertEqual(args.inputfile, [self.test_video])
        self.assertFalse(args.debug)
        self.assertIsNone(args.outputfile)

    def test_parser_optional_arguments(self):
        """Test parser with optional arguments"""
        parser = create_parser()
        args = parser.parse_args(
            [
                self.test_video,
                "--output",
                "/custom/output.mp4",
                "--debug",
                "--log-file",
                "custom.log",
                "--ffmpeg-path",
                "/usr/bin/ffmpeg",
                "--ffprobe-path",
                "/usr/bin/ffprobe",
            ]
        )

        self.assertEqual(args.inputfile, [self.test_video])
        self.assertEqual(args.outputfile, "/custom/output.mp4")
        self.assertTrue(args.debug)
        self.assertEqual(args.log_file, ["custom.log"])
        self.assertEqual(args.ffmpeg_path, "/usr/bin/ffmpeg")
        self.assertEqual(args.ffprobe_path, "/usr/bin/ffprobe")

    def test_parser_short_arguments(self):
        """Test parser with short argument forms"""
        parser = create_parser()
        args = parser.parse_args([self.test_video, "-o", "/output.mp4", "-d"])

        self.assertEqual(args.outputfile, "/output.mp4")
        self.assertTrue(args.debug)

    def test_validate_args_valid_file(self):
        """Test argument validation with valid file"""
        args = argparse.Namespace(inputfile=[self.test_video], outputfile=None)

        result = validate_args(args)
        self.assertTrue(result)

    def test_validate_args_invalid_file(self):
        """Test argument validation with non-existent file"""
        args = argparse.Namespace(inputfile=["/nonexistent/file.mp4"], outputfile=None)

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            result = validate_args(args)
            self.assertFalse(result)
            self.assertIn("Video file not found", mock_stderr.getvalue())

    def test_validate_args_invalid_output_dir(self):
        """Test argument validation with invalid output directory"""
        args = argparse.Namespace(
            inputfile=[self.test_video], outputfile="/nonexistent/dir/output.mp4"
        )

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            result = validate_args(args)
            self.assertFalse(result)
            self.assertIn("Output directory does not exist", mock_stderr.getvalue())

    def test_validate_args_valid_output_dir(self):
        """Test argument validation with valid output directory"""
        output_path = os.path.join(self.temp_dir, "output.mp4")
        args = argparse.Namespace(inputfile=[self.test_video], outputfile=output_path)

        result = validate_args(args)
        self.assertTrue(result)

    @patch("logging.basicConfig")
    def test_setup_logging_default(self, mock_basic_config):
        """Test logging setup with default parameters"""
        setup_logging()

        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        self.assertEqual(call_args[1]["level"], 20)  # INFO level

    @patch("logging.basicConfig")
    def test_setup_logging_verbose(self, mock_basic_config):
        """Test logging setup with verbose mode"""
        setup_logging(debug=True)

        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        self.assertEqual(call_args[1]["level"], 10)  # DEBUG level

    @patch("logging.basicConfig")
    def test_setup_logging_custom_file(self, mock_basic_config):
        """Test logging setup with custom log file"""
        setup_logging(log_file=["custom.log"])

        mock_basic_config.assert_called_once()

    @patch("sys.argv", ["guardian", "test.mp4"])
    def test_main_success(self):
        """Test successful main execution"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ) as _mock_setup_logging, patch(
            "guardian.cli.GuardianProcessor"
        ) as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "builtins.print"
        ) as mock_print:

            # Mock validation
            mock_validate.return_value = True

            # Mock processor
            mock_processor = MagicMock()
            mock_processor.process_video.return_value = "/output/censored.mp4"
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 0)
            self.assertIn("Censored video created", mock_print.call_args[0][0])

    @patch("guardian.cli.validate_args")
    @patch("sys.argv", ["guardian", "nonexistent.mp4"])
    def test_main_validation_failure(self, mock_validate):
        """Test main execution with validation failure"""
        mock_validate.return_value = False

        result = main()

        self.assertEqual(result, 1)

    @patch("sys.argv", ["guardian", "test.mp4"])
    def test_main_processing_failure(self):
        """Test main execution with processing failure"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ) as _mock_setup_logging, patch(
            "guardian.cli.GuardianProcessor"
        ) as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "sys.stderr", new_callable=io.StringIO
        ) as mock_stderr:

            # Mock validation
            mock_validate.return_value = True

            # Mock processor failure
            mock_processor = MagicMock()
            mock_processor.process_video.return_value = None
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 1)
            self.assertIn("Censoring process failed for file", mock_stderr.getvalue())

    @patch("sys.argv", ["guardian", "test.mp4"])
    def test_main_keyboard_interrupt(self):
        """Test main execution with keyboard interrupt"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ) as _mock_setup_logging, patch(
            "guardian.cli.GuardianProcessor"
        ) as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "sys.stderr", new_callable=io.StringIO
        ) as mock_stderr:

            # Mock validation
            mock_validate.return_value = True

            # Mock processor to raise KeyboardInterrupt
            mock_processor = MagicMock()
            mock_processor.process_video.side_effect = KeyboardInterrupt()
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 1)
            self.assertIn("Process interrupted by user", mock_stderr.getvalue())

    @patch("sys.argv", ["guardian", "test.mp4"])
    def test_main_unexpected_error(self):
        """Test main execution with unexpected error"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ) as _mock_setup_logging, patch(
            "guardian.cli.GuardianProcessor"
        ) as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "sys.stderr", new_callable=io.StringIO
        ) as mock_stderr:

            # Mock validation
            mock_validate.return_value = True

            # Mock processor to raise unexpected error
            mock_processor = MagicMock()
            mock_processor.process_video.side_effect = RuntimeError("Unexpected error")
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 1)
            self.assertIn(
                "An unexpected error occurred processing file", 
                mock_stderr.getvalue()
            )

    @patch("sys.argv", ["guardian", "--version"])
    def test_version_argument(self):
        """Test version argument"""
        parser = create_parser()

        with self.assertRaises(SystemExit) as cm:
            parser.parse_args(["--version"])

        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
