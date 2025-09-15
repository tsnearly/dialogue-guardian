#!/usr/bin/env python3
"""
Extended CLI tests for guardian functionality
"""

import argparse
import io
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from guardian.cli import create_parser, main, setup_logging, validate_args


class TestGuardianCLIExtended(unittest.TestCase):
    """Extended test cases for Guardian CLI functionality"""

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

    def test_parser_help_message(self):
        """Test that parser help message is properly formatted"""
        parser = create_parser()
        help_text = parser.format_help()

        self.assertIn("Guardian", help_text)
        self.assertIn("INPUTFILE", help_text)
        self.assertIn("--output", help_text)
        self.assertIn("--debug", help_text)

    def test_parser_with_all_arguments(self):
        """Test parser with all possible arguments"""
        parser = create_parser()
        args = parser.parse_args(
            [
                "--input",
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
        self.assertEqual(args.logfile, ["custom.log"])
        self.assertEqual(args.ffmpeg, "/usr/bin/ffmpeg")
        self.assertEqual(args.ffprobe, "/usr/bin/ffprobe")

    def test_validate_args_with_relative_paths(self):
        """Test argument validation with relative paths"""
        try:
            # Create a relative path test
            rel_video = os.path.relpath(self.test_video)
            rel_output = os.path.join(os.path.relpath(self.temp_dir), "output.mp4")
        except ValueError:
            # This can happen on Windows if the temp dir is on a different drive
            # than the current working directory. In this case, we skip the test.
            self.skipTest("Temp directory is on a different drive.")
            return

        args = argparse.Namespace(inputfile=[rel_video], outputfile=rel_output)
        result = validate_args(args)
        self.assertTrue(result)

    def test_validate_args_output_same_as_input(self):
        """Test argument validation when output is same as input"""
        args = argparse.Namespace(
            inputfile=[self.test_video], outputfile=self.test_video
        )

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            result = validate_args(args)
            # Should still be valid, but might warn
            self.assertTrue(result)

    def test_validate_args_output_directory_creation(self):
        """Test that output directory validation works correctly"""
        # Test with a path in an existing directory
        output_in_temp = os.path.join(self.temp_dir, "subdir", "output.mp4")
        args = argparse.Namespace(
            inputfile=[self.test_video], outputfile=output_in_temp
        )

        with patch("sys.stderr", new_callable=io.StringIO):
            result = validate_args(args)
            # Should fail because subdir doesn't exist
            self.assertFalse(result)

    @patch("logging.basicConfig")
    @patch("logging.FileHandler")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_setup_logging_with_file_handler_error(
        self, mock_stderr, mock_file_handler, mock_basic_config
    ):
        """Test logging setup when file handler creation fails"""
        mock_file_handler.side_effect = PermissionError("Cannot create log file")

        # Should not raise exception, should fall back gracefully
        setup_logging(log_file=["/invalid/path/test.log"])

        # Should still call basicConfig
        mock_basic_config.assert_called()
        # Should print warning message
        self.assertIn("Warning: Could not create log file", mock_stderr.getvalue())

    @patch("sys.argv", ["guardian"])
    def test_main_no_arguments(self):
        """Test main execution with no arguments"""
        with self.assertRaises(SystemExit) as cm:
            main()

        # Should exit with error code due to missing required argument
        self.assertNotEqual(cm.exception.code, 0)

    @patch("sys.argv", ["guardian", "--help"])
    def test_main_help_argument(self):
        """Test main execution with help argument"""
        with self.assertRaises(SystemExit) as cm:
            main()

        # Help should exit with code 0
        self.assertEqual(cm.exception.code, 0)

    @patch(
        "sys.argv",
        ["guardian", "--input", "test.mp4", "--debug", "--log-file", "test.log"],
    )
    def test_main_with_logging_options(self):
        """Test main execution with logging options"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ) as mock_setup_logging, patch(
            "guardian.cli.GuardianProcessor"
        ) as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "builtins.print"
        ):

            mock_validate.return_value = True
            mock_processor = MagicMock()
            mock_processor.process_video.return_value = "/output/censored.mp4"
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 0)
            # Called setup_logging w/log_file and verbose (positional args)
            mock_setup_logging.assert_called_once_with(["test.log"], True)

    @patch(
        "sys.argv",
        ["guardian", "--input", "test.mp4", "--ffmpeg-path", "/custom/ffmpeg"],
    )
    def test_main_with_custom_ffmpeg_path(self):
        """Test main execution with custom FFmpeg path"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ), patch("guardian.cli.GuardianProcessor") as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "builtins.print"
        ):

            mock_validate.return_value = True
            mock_processor = MagicMock()
            mock_processor.process_video.return_value = "/output/censored.mp4"
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 0)
            # Should have created processor with custom ffmpeg path
            mock_processor_class.assert_called_once_with(
                ffmpeg_cmd="/custom/ffmpeg", ffprobe_cmd="ffprobe"
            )

    @patch(
        "sys.argv",
        ["guardian", "--input", "test.mp4", "--ffprobe-path", "/custom/ffprobe"],
    )
    def test_main_with_custom_ffprobe_path(self):
        """Test main execution with custom FFprobe path"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ), patch("guardian.cli.GuardianProcessor") as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "builtins.print"
        ):

            mock_validate.return_value = True
            mock_processor = MagicMock()
            mock_processor.process_video.return_value = "/output/censored.mp4"
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 0)
            # Should have created processor with custom ffprobe path
            mock_processor_class.assert_called_once_with(
                ffmpeg_cmd="ffmpeg", ffprobe_cmd="/custom/ffprobe"
            )

    @patch("sys.argv", ["guardian", "--input", "test.mp4"])
    def test_main_with_exception_during_processing(self):
        """Test main execution when an exception occurs during processing"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ), patch("guardian.cli.GuardianProcessor") as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "sys.stderr", new_callable=io.StringIO
        ) as mock_stderr:

            mock_validate.return_value = True
            mock_processor = MagicMock()
            mock_processor.process_video.side_effect = ValueError(
                "Invalid video format"
            )
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 1)
            self.assertIn("An unexpected error occurred:", mock_stderr.getvalue())
            # The error message contains the exception message, not the type name
            self.assertIn("Invalid video format", mock_stderr.getvalue())

    def test_validate_args_edge_case_paths(self):
        """Test argument validation with edge case paths"""
        # Test with empty string path
        args = argparse.Namespace(inputfile=[""], outputfile=None)
        with patch("sys.stderr", new_callable=io.StringIO):
            result = validate_args(args)
            self.assertFalse(result)

        # Test with None path (shouldn't happen in normal usage)
        args = argparse.Namespace(inputfile=[None], outputfile=None)
        with patch("sys.stderr", new_callable=io.StringIO):
            # This might raise an exception or handle gracefully
            try:
                result = validate_args(args)
                self.assertFalse(result)
            except (AttributeError, TypeError):
                # Expected if the function doesn't handle None gracefully
                pass

    def test_create_parser_argument_groups(self):
        """Test that parser creates proper argument groups"""
        parser = create_parser()

        # Check that required and optional arguments are properly set up
        required_actions = [action for action in parser._actions if action.required]
        optional_actions = [
            action
            for action in parser._actions
            if not action.required and action.dest != "help"
        ]

        # Should have at least one required argument (inputfile)
        self.assertGreater(len(required_actions), 0)
        self.assertEqual(required_actions[0].dest, "inputfile")
        # Should have several optional arguments
        self.assertGreater(len(optional_actions), 0)

    @patch("sys.argv", ["guardian", "--input", "test.mp4", "--output", ""])
    def test_main_with_empty_output_path(self):
        """Test main execution with empty output path"""
        with patch("guardian.cli.validate_args") as mock_validate, patch(
            "guardian.cli.setup_logging"
        ), patch("guardian.cli.GuardianProcessor") as mock_processor_class, patch(
            "os.path.exists", return_value=True
        ), patch(
            "os.path.abspath", side_effect=lambda x: "/abs/" + os.path.basename(x)
        ), patch(
            "builtins.print"
        ):

            mock_validate.return_value = True
            mock_processor = MagicMock()
            mock_processor.process_video.return_value = "/output/censored.mp4"
            mock_processor_class.return_value = mock_processor

            result = main()

            self.assertEqual(result, 0)
            # Should pass empty string as output path
            mock_processor.process_video.assert_called_once_with("/abs/test.mp4", "")


if __name__ == "__main__":
    unittest.main()
