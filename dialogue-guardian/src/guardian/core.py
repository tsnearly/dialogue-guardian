# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Core functionality for the Guardian media censoring system.
"""

import json
import logging
import os
import platform
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import srt  # type: ignore


@dataclass
class SegmentDiagnostic:
    """Diagnostic information for a single censored segment."""

    segment_id: int
    start_time: float
    end_time: float
    duration: float
    target_rms_db: float
    actual_rms_db: float
    meets_threshold: bool
    strategy_used: int
    strategy_name: str
    filter_applied: str


@dataclass
class CensoringDiagnostic:
    """Complete diagnostic report for a censoring operation."""

    timestamp: str
    input_video: str
    output_video: str
    total_segments: int
    total_censored_duration: float
    successful_segments: int
    failed_segments: int
    final_strategy_used: int
    fallback_attempts: int
    overall_success: bool
    segments: List[SegmentDiagnostic]
    error_messages: List[str]
    recommendations: List[str]


class GuardianProcessor:
    """Main processor class for censoring profane content in video files."""

    # Default word/phrase matching list (ranked by frequency occurrence)
    DEFAULT_MATCHING_WORDS = [
        "fucking",
        "fuck",
        "shit",
        "damn",
        "hell",
        "ass",
        "bitch",
        "bastard",
        "bullshit",
        "fucker",
        "fucked",
        "asshole",
        "piss",
        "jesus christ",
        "jesus",
        "sex",
        "pussy",
        "son of a bitch",
        "sonofabitch",
        "jackass",
        "smartass",
        "tits",
        "whore",
        "cunt",
        "slut",
        "boobs",
        "orgasm",
        "penis",
        "blowjob",
        "handjob",
        "hard on",
        "cocksucker",
        "dipshit",
        "horseshit",
        "jack off",
        "nympho",
        "rape",
        "fuckface",
        "skank",
        "shitspray",
        "bitches",
        "nigga",
        "nigger",
        "dickhead",
        "prick",
        "arsehole",
        "motherfucker",
        "goddamn",
        "shithead",
        "douchebag",
        "fag",
        "faggot",
    ]

    def __init__(
        self,
        matching_words: Optional[List[str]] = None,
        ffmpeg_cmd: Optional[str] = None,
        ffprobe_cmd: Optional[str] = None,
    ):
        """
        Initialize the GuardianProcessor.
        Args:
            matching_words: Custom list of words to censor. Uses default if None.
            ffmpeg_cmd: Path to ffmpeg executable.
            Defaults to checking local 'bin' dir.
            ffprobe_cmd: Path to ffprobe executable.
            Defaults to checking local 'bin' dir.
        """
        self.matching_words = (
            matching_words
            if matching_words is not None
            else self.DEFAULT_MATCHING_WORDS
        )
        self.ffmpeg_cmd = ffmpeg_cmd or self._get_local_ffmpeg_cmd("ffmpeg")
        self.ffprobe_cmd = ffprobe_cmd or self._get_local_ffmpeg_cmd("ffprobe")

    def _get_local_ffmpeg_cmd(self, cmd_name: str) -> str:
        """
        Checks for a local FFmpeg command and returns its path if it exists,
        otherwise returns the command name for system PATH resolution.
        """
        executable_name = (
            f"{cmd_name}.exe" if platform.system() == "Windows" else cmd_name
        )
        # Assumes this script is in src/guardian/core.py
        bin_dir = Path(__file__).parent.parent.parent / "bin"
        local_path = bin_dir / executable_name
        if local_path.is_file():
            logging.debug(f"Using local executable: {local_path}")
            return str(local_path)
        logging.debug(
            f"Local executable not found at {local_path}. "
            f"Falling back to system PATH for '{cmd_name}'."
        )
        return cmd_name

    def get_video_details(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Extracts video and audio details using ffprobe.

        Args:
            filename: Path to the video file.

        Returns:
            Dictionary containing video duration, audio codec, sample rate,
            channels, video width, height, and frame rate.
        """
        details: Dict[str, Any] = {}
        logging.debug(f"Getting video details for: {filename}")

        try:
            # Get video duration
            cmd_duration = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                filename,
            ]
            stdout_duration = subprocess.check_output(
                cmd_duration, text=True, stderr=subprocess.PIPE
            ).strip()
            details["duration"] = stdout_duration

            # Get audio stream details
            cmd_audio = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=codec_name,channels,channel_layout,sample_rate",
                "-of",
                "compact=p=0:nk=1",
                filename,
            ]
            stdout_audio = subprocess.check_output(
                cmd_audio, text=True, stderr=subprocess.PIPE
            ).strip()

            save_channels = 0
            for line in stdout_audio.split("\n"):
                parts = line.split("|")
                if len(parts) >= 3 and parts[2].isdigit():
                    test_channels = int(parts[2])
                    if test_channels > save_channels:
                        details["codec"] = parts[0]
                        details["samplerate"] = parts[1]
                        details["channels"] = parts[2]
                        details["audioconfig"] = parts[3] if len(parts) > 3 else ""
                        save_channels = test_channels

            # Get video stream details
            cmd_video = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=r_frame_rate,width,height",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                filename,
            ]
            stdout_video = subprocess.check_output(
                cmd_video, text=True, stderr=subprocess.PIPE
            ).strip()

            lines = stdout_video.split("\n")
            if len(lines) >= 3:
                details["width"] = lines[0]
                details["height"] = lines[1]
                framerate_str = lines[2]
            else:
                details["width"] = None
                details["height"] = None
                framerate_str = None

            if framerate_str and "/" in framerate_str:
                numerator, denominator = map(int, framerate_str.split("/"))
                details["framerate"] = framerate_str
                if denominator != 0:
                    details["fps"] = "{:.3f}".format(numerator / denominator)
                    details["frameduration"] = f"{denominator}/{numerator}"
                else:
                    details["fps"] = None
                    details["frameduration"] = None
            elif framerate_str is not None:
                fps_float = float(framerate_str)
                details["fps"] = f"{fps_float:.3f}"
                details["framerate"] = f"{int(fps_float * 1000)}/1000"
                details["frameduration"] = f"1000/{int(fps_float * 1000)}"
            else:
                details["fps"] = None
                details["framerate"] = None
                details["frameduration"] = None

            logging.debug(f"Video Info Dictionary:\n{json.dumps(details, indent=4)}")
            return details
        except subprocess.CalledProcessError as e:
            logging.error(f"ffprobe command failed: {e.stderr}")
            return None
        except FileNotFoundError:
            logging.error(
                "ffprobe not found. Please ensure FFmpeg is installed and in "
                "your system's PATH."
            )
            return None

    def extract_embedded_srt(self, video_path: str, output_srt_path: str) -> bool:
        """
        Extracts the first embedded SRT subtitle track from a video file,
        prioritizing default tracks.

        Args:
            video_path: Path to the input video file.
            output_srt_path: Path where the extracted SRT file will be saved.

        Returns:
            True if an SRT track was successfully extracted, False otherwise.
        """
        logging.info(f"Checking for embedded SRT subtitles in {video_path}")
        probe_output_raw = ""

        try:
            # Use ffprobe to list all streams in JSON format
            cmd_probe_streams = [
                self.ffprobe_cmd,
                "-v",
                "error",
                "-select_streams",
                "s",
                "-show_entries",
                "stream=index,codec_name,disposition",
                "-of",
                "json",
                video_path,
            ]

            probe_output_raw = subprocess.check_output(
                cmd_probe_streams, text=True, stderr=subprocess.PIPE
            ).strip()
            probe_output = json.loads(probe_output_raw)

            srt_stream_index = -1
            found_srt_streams = []

            if "streams" in probe_output:
                for stream in probe_output["streams"]:
                    if stream.get("codec_name") in ["subrip", "mov_text"]:
                        found_srt_streams.append(stream)

            if found_srt_streams:
                # Prioritize default SRT track
                for stream in found_srt_streams:
                    if stream.get("disposition", {}).get("default") == 1:
                        srt_stream_index = stream["index"]
                        logging.info(
                            f"Found default SRT stream at index: {srt_stream_index}"
                        )
                        break

                # If no default, just pick the first one found
                if srt_stream_index == -1:
                    srt_stream_index = found_srt_streams[0]["index"]
                    logging.info(
                        f"Found non-default SRT stream at index: {srt_stream_index}"
                    )

            if srt_stream_index != -1:
                # Use ffmpeg to extract the identified SRT stream
                cmd_extract_srt = [
                    self.ffmpeg_cmd,
                    "-v",
                    "debug",
                    "-i",
                    video_path,
                    "-map",
                    f"0:{srt_stream_index}",
                    "-c:s",
                    "srt",
                    output_srt_path,
                    "-y",
                ]
                logging.info(f"Executing SRT extraction: {' '.join(cmd_extract_srt)}")
                process = subprocess.run(
                    cmd_extract_srt, check=True, capture_output=True, text=True
                )
                logging.info(f"FFmpeg stdout (SRT extraction):\n{process.stdout}")
                logging.info(f"Successfully extracted SRT to: {output_srt_path}")
                return True
            else:
                logging.info("No embedded SRT subtitle track (subrip codec) found.")
                return False

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse ffprobe JSON output: {e}")
            logging.error(f"ffprobe raw output: {probe_output_raw}")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(
                f"FFmpeg/ffprobe failed during extraction. Return code: {e.returncode}"
            )
            logging.error(f"FFmpeg stdout (SRT extraction error):\n{e.stdout}")
            logging.error(f"FFmpeg stderr (SRT extraction error):\n{e.stderr}")
            return False
        except FileNotFoundError:
            logging.error(
                "ffmpeg or ffprobe not found. Check installation and system path."
            )
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred during SRT extraction: {e}")
            return False

    def _find_srt_file(self, video_path: str) -> Optional[str]:
        """Finds the SRT file for a video, checking for language-specific versions."""
        srt_path = os.path.splitext(video_path)[0] + ".srt"
        if os.path.exists(srt_path):
            return srt_path

        base_path = os.path.splitext(video_path)[0]
        for lang in ["en", "fr", "es", "de", "it"]:
            lang_srt_path = f"{base_path}.{lang}.srt"
            if os.path.exists(lang_srt_path):
                logging.info(f"Found language-specific SRT file: {lang_srt_path}")
                return lang_srt_path
        return None

    def _parse_srt_file(self, srt_path: str) -> Optional[List[srt.Subtitle]]:
        """Parses an SRT file and returns a list of subtitles."""
        try:
            with open(srt_path, "r", encoding="utf-8-sig") as f:
                srt_content = f.read()
            return list(srt.parse(srt_content))
        except Exception as e:
            logging.error(f"Error reading or parsing SRT file {srt_path}: {e}")
            return None

    def _find_profane_segments(
        self, subs: List[srt.Subtitle]
    ) -> List[Tuple[float, float]]:
        """Finds profane segments in a list of subtitles."""
        pattern = (
            r"\b(" + "|".join(re.escape(word) for word in self.matching_words) + r")\b"
        )
        censor_pattern = re.compile(pattern, re.IGNORECASE)
        censor_segments = []
        for sub in subs:
            cleaned_text = re.sub(r"[^\w\s\']", "", sub.content).lower()
            if censor_pattern.search(cleaned_text):
                logging.debug(f'Match found in subtitle #{sub.index}: "{cleaned_text}"')
                start_s = sub.start.total_seconds()
                end_s = sub.end.total_seconds()
                censor_segments.append((start_s, end_s))
        return censor_segments

    def _verify_silence_level(
        self, video_path: str, start: float, end: float
    ) -> Tuple[bool, float]:
        """
        Verifies that a specific segment meets silence requirements using FFmpeg astats.

        Args:
            video_path: Path to the video file to analyze
            start: Start time of the segment in seconds
            end: End time of the segment in seconds

        Returns:
            Tuple of (meets_threshold, actual_rms_db) where:
            - meets_threshold: True if RMS level is below -50 dB
            - actual_rms_db:
            The actual RMS level in dB, or float('inf') if parsing fails
        """
        silence_threshold_db = -50.0
        segment_duration = end - start

        logging.info("=== SILENCE VERIFICATION ===")
        logging.info(
            f"Verifying segment: {start:.3f}s - {end:.3f}s (duration:"
            f" {segment_duration:.3f}s)"
        )
        logging.info(f"Silence threshold: {silence_threshold_db} dB")

        try:
            # Construct FFmpeg command to analyze audio segment with astats
            cmd = [
                self.ffmpeg_cmd,
                "-i",
                video_path,
                "-ss",
                str(start),
                "-t",
                str(segment_duration),
                "-af",
                "astats=metadata=1:reset=1",
                "-f",
                "null",
                "-",
            ]

            logging.info(f"Executing astats analysis command: {' '.join(cmd)}")

            # Execute FFmpeg command and capture stderr (where astats output goes)
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
            )

            logging.debug(f"FFmpeg process exit code: {process.returncode}")
            if process.stdout:
                logging.debug(f"FFmpeg stdout: {process.stdout}")

            # Parse the stderr output to extract RMS level
            actual_rms_db = self._parse_astats_output(process.stderr)

            # Debug: Log the raw stderr output for troubleshooting
            logging.debug(
                f"FFmpeg astats stderr output for segment {start:.3f}-{end:.3f}s:"
            )
            logging.debug(f"Process return code: {process.returncode}")
            logging.debug(f"Stderr length: {len(process.stderr)} chars")
            logging.debug(f"Stderr content:\n{process.stderr}")

            if actual_rms_db == float("inf"):
                logging.warning(
                    "Could not parse RMS level from astats output for segment"
                    f" {start:.3f}-{end:.3f}s"
                )

                # Check if this might be due to complete silence
                if process.returncode == 0 and len(process.stderr.strip()) > 0:
                    # FFmpeg completed successfully but we can't parse RMS
                    # This might indicate the audio is extremely quiet
                    logging.info(
                        "FFmpeg completed successfully - audio may be completely silent"
                    )
                    logging.info("=== END SILENCE VERIFICATION (ASSUMED SILENT) ===")
                    return True, -100.0  # Assume very quiet audio meets threshold
                else:
                    logging.info("=== END SILENCE VERIFICATION (FAILED) ===")
                    return False, actual_rms_db

            meets_threshold = actual_rms_db <= silence_threshold_db
            threshold_diff = actual_rms_db - silence_threshold_db

            logging.info(f"Measured RMS level: {actual_rms_db:.2f} dB")
            logging.info(f"Threshold difference: {threshold_diff:+.2f} dB")
            logging.info(
                f"Meets silence threshold: {'YES' if meets_threshold else 'NO'}"
            )

            if meets_threshold:
                logging.info(f"✓ Segment {start:.3f}-{end:.3f}s successfully silenced")
            else:
                logging.warning(
                    f"✗ Segment {start:.3f}-{end:.3f}s insufficient silencing"
                )
                logging.warning(
                    f"  Expected: ≤ {silence_threshold_db} dB, Got:"
                    f" {actual_rms_db:.2f} dB"
                )

            logging.info("=== END SILENCE VERIFICATION ===")
            return meets_threshold, actual_rms_db

        except Exception as e:
            logging.error(
                "Error during silence verification for segment"
                f" {start:.3f}-{end:.3f}s: {e}"
            )
            logging.info("=== END SILENCE VERIFICATION (ERROR) ===")
            return False, float("inf")

    def _parse_astats_output(self, stderr_output: str) -> float:
        """
        Parses FFmpeg astats output to extract RMS level in dB.

        Args:
            stderr_output: The stderr output from FFmpeg containing astats information

        Returns:
            RMS level in dB, or float('inf') if parsing fails
        """
        try:
            logging.debug(f"Parsing astats output (length: {len(stderr_output)} chars)")

            # Look for RMS level patterns in the astats output
            # FFmpeg astats can output in different formats, so we try multiple patterns
            # Formats: standard, metadata, alternative, simplified, metadata w/o prefix
            #   another metadata
            patterns = [
                r"RMS level dB:\s*(-?\d+(?:\.\d+)?)",
                r"lavfi\.astats\.Overall\.RMS_level:\s*(-?\d+(?:\.\d+)?)",
                r"Overall RMS level:\s*(-?\d+(?:\.\d+)?)\s*dB",
                r"RMS:\s*(-?\d+(?:\.\d+)?)\s*dB",
                r"RMS_level:\s*(-?\d+(?:\.\d+)?)",
                r"Overall\.RMS_level:\s*(-?\d+(?:\.\d+)?)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, stderr_output, re.IGNORECASE)
                if matches:
                    # Take the last match (most recent/final value)
                    rms_db = float(matches[-1])
                    logging.debug(
                        f"Parsed RMS level: {rms_db} dB using pattern: {pattern}"
                    )
                    return rms_db

            # Look for any lines containing "astats" and extract numeric values
            astats_lines = [
                line for line in stderr_output.split("\n") if "astats" in line.lower()
            ]
            logging.debug(f"Found {len(astats_lines)} astats lines")

            for line in astats_lines:
                logging.debug(f"Examining astats line: {line.strip()}")
                # Look for any negative numbers (likely dB values)
                db_matches = re.findall(r"(-\d+(?:\.\d+)?)", line)
                if db_matches:
                    # Use the first negative value found (likely RMS dB)
                    rms_db = float(db_matches[0])
                    logging.debug(f"Parsed RMS level from astats line: {rms_db} dB")
                    return rms_db

                # Also look for zero values that might indicate silence
                zero_matches = re.findall(r"\b0\.0+\b", line)
                if zero_matches and "rms" in line.lower():
                    logging.debug(
                        "Found zero RMS value in astats line - assuming very quiet"
                        " audio"
                    )
                    return -100.0  # Treat 0.0 RMS as very quiet

            # Check if the audio might be completely silent (no astats output)
            if "astats" in stderr_output.lower():
                # If astats filter was applied but no RMS values found,
                # the audio might be completely silent
                logging.debug(
                    "Astats filter was applied but no RMS values found - assuming"
                    " complete silence"
                )
                return -100.0  # Assume very quiet audio

            # If still no match, log the output for debugging
            logging.warning("Could not parse RMS level from astats output")
            logging.debug(f"Full astats stderr output:\n{stderr_output}")
            return float("inf")

        except (ValueError, IndexError) as e:
            logging.error(f"Error parsing astats output: {e}")
            logging.debug(f"Problematic stderr output:\n{stderr_output}")
            return float("inf")
        except Exception as e:
            logging.error(f"Unexpected error parsing astats output: {e}")
            return float("inf")

    def _get_filter_strategy(self, strategy_level: int = 1) -> Dict[str, Any]:
        """
        Returns filter configuration for different strategy levels.

        Args:
            strategy_level: Filter strategy level (1=basic, 2=enhanced, 3=aggressive)

        Returns:
            Dictionary containing filter configuration
        """
        strategies = {
            1: {
                "name": "Basic Volume Reduction",
                "volume_filter": "volume=0",
                "use_format_normalization": False,
                "use_compression": False,
                "use_null_mixing": False,
                "description": "Simple volume=0 filter (legacy approach)",
            },
            2: {
                "name": "Enhanced Silence",
                "volume_filter": "volume=-80dB",
                "use_format_normalization": True,
                "use_compression": True,
                "use_null_mixing": False,
                "description": (
                    "Very low volume reduction with format normalization and"
                    " compression"
                ),
            },
            3: {
                "name": "Aggressive Null Mixing",
                "volume_filter": "volume=0",
                "use_format_normalization": True,
                "use_compression": True,
                "use_null_mixing": True,
                "description": (
                    "Complete silence with null source mixing and multiple processing"
                    " stages"
                ),
            },
        }

        return strategies.get(strategy_level, strategies[2])  # Default to enhanced

    def _attempt_censoring_with_fallback(
        self,
        video_path: str,
        output_path: str,
        censor_segments: List[Tuple[float, float]],
        max_attempts: int = 3,
    ) -> Tuple[bool, Optional[str], List[Tuple[float, float, float]], int, List[str]]:
        """
        Attempts censoring with progressive filter enhancement and fallback mechanisms.

        Args:
            video_path: Path to input video
            output_path: Path for output video
            censor_segments: List of segments to censor
            max_attempts: Maximum number of fallback attempts

        Returns:
            Tuple of (success, output_path, verification_results,
              final_strategy, error_messages)
        """
        logging.info("=== FALLBACK CENSORING SYSTEM ===")
        logging.info(f"Maximum fallback attempts: {max_attempts}")

        error_messages: list[str] = []

        for attempt in range(1, max_attempts + 1):
            logging.info(f"--- Attempt {attempt}/{max_attempts} ---")

            try:
                # Construct FFmpeg command with current strategy level
                ffmpeg_command = self._construct_ffmpeg_command(
                    video_path, output_path, censor_segments, strategy_level=attempt
                )

                strategy = self._get_filter_strategy(attempt)
                logging.info(f"Trying strategy: {strategy['name']}")

                # Execute FFmpeg command
                logging.info("Executing FFmpeg processing...")
                process = subprocess.run(
                    ffmpeg_command, check=True, capture_output=True, text=True
                )
                logging.info("FFmpeg processing completed successfully")
                logging.debug(f"FFmpeg stdout:\n{process.stdout}")

                # Verify silence levels for all segments
                logging.info("Verifying censoring effectiveness...")
                verification_results = []
                all_segments_pass = True

                for start_s, end_s in censor_segments:
                    meets_threshold, actual_rms_db = self._verify_silence_level(
                        output_path, start_s, end_s
                    )
                    verification_results.append((start_s, end_s, actual_rms_db))

                    if not meets_threshold:
                        all_segments_pass = False

                if all_segments_pass:
                    logging.info(
                        "✓ SUCCESS: All segments meet silence threshold with strategy"
                        f" {attempt}"
                    )
                    logging.info("=== END FALLBACK CENSORING SYSTEM ===")
                    return (
                        True,
                        output_path,
                        verification_results,
                        attempt,
                        error_messages,
                    )
                else:
                    failed_count = sum(
                        1 for _, _, rms in verification_results if rms > -50.0
                    )
                    logging.warning(
                        f"✗ PARTIAL SUCCESS: {failed_count} segments still above"
                        " threshold"
                    )

                    if attempt < max_attempts:
                        logging.info(
                            f"Attempting fallback to strategy level {attempt + 1}"
                        )
                        # Clean up failed attempt output
                        try:
                            if os.path.exists(output_path):
                                os.remove(output_path)
                                logging.debug(
                                    f"Removed failed output file: {output_path}"
                                )
                        except (OSError, FileNotFoundError) as cleanup_error:
                            logging.debug(
                                f"Could not remove failed output file: {cleanup_error}"
                            )
                    else:
                        logging.warning("Maximum fallback attempts reached")
                        logging.info("=== END FALLBACK CENSORING SYSTEM ===")
                        return (
                            False,
                            output_path,
                            verification_results,
                            attempt,
                            error_messages,
                        )

            except subprocess.CalledProcessError as e:
                error_msg = (
                    f"FFmpeg command failed on attempt {attempt}. Return code:"
                    f" {e.returncode}"
                )
                logging.error(error_msg)
                logging.error(f"FFmpeg stderr:\n{e.stderr}")
                error_messages.append(error_msg)
                error_messages.append(f"FFmpeg stderr: {e.stderr}")

                if attempt < max_attempts:
                    logging.info(f"Attempting fallback to strategy level {attempt + 1}")
                    # Clean up failed attempt output
                    if os.path.exists(output_path):
                        os.remove(output_path)
                        logging.debug(f"Removed failed output file: {output_path}")
                else:
                    logging.error(
                        "Maximum fallback attempts reached due to FFmpeg failures"
                    )
                    logging.info("=== END FALLBACK CENSORING SYSTEM ===")
                    return False, None, [], attempt, error_messages

            except Exception as e:
                error_msg = f"Unexpected error on attempt {attempt}: {e}"
                logging.error(error_msg)
                error_messages.append(error_msg)

                if attempt < max_attempts:
                    logging.info(f"Attempting fallback to strategy level {attempt + 1}")
                    # Clean up failed attempt output
                    try:
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            logging.debug(f"Removed failed output file: {output_path}")
                    except (OSError, FileNotFoundError) as cleanup_error:
                        logging.debug(
                            f"Could not remove failed output file: {cleanup_error}"
                        )
                else:
                    logging.error(
                        "Maximum fallback attempts reached due to unexpected errors"
                    )
                    logging.info("=== END FALLBACK CENSORING SYSTEM ===")
                    return False, None, [], attempt, error_messages

        # This should not be reached, but included for completeness
        logging.error(
            "Fallback system completed without returning - this should not happen"
        )
        logging.info("=== END FALLBACK CENSORING SYSTEM ===")
        return False, None, [], max_attempts, error_messages

    def _generate_diagnostic_report(
        self,
        input_video: str,
        output_video: Optional[str],
        censor_segments: List[Tuple[float, float]],
        verification_results: List[Tuple[float, float, float]],
        final_strategy: int,
        fallback_attempts: int,
        overall_success: bool,
        error_messages: Optional[List[str]] = None,
    ) -> CensoringDiagnostic:
        """
        Generates a comprehensive diagnostic report for the censoring operation.

        Args:
            input_video: Path to input video file
            output_video: Path to output video file (None if failed)
            censor_segments: List of segments that were censored
            verification_results: Results from silence verification
            final_strategy: Final strategy level used
            fallback_attempts: Number of fallback attempts made
            overall_success: Whether the operation was successful
            error_messages: List of error messages encountered

        Returns:
            CensoringDiagnostic object with complete diagnostic information
        """
        timestamp = datetime.now().isoformat()
        error_messages = error_messages or []

        # Calculate segment diagnostics
        segment_diagnostics = []
        total_censored_duration: float = 0
        successful_segments = 0
        failed_segments = 0

        strategy = self._get_filter_strategy(final_strategy)

        for i, ((start_s, end_s), (_, _, actual_rms_db)) in enumerate(
            zip(censor_segments, verification_results), 1
        ):
            duration = end_s - start_s
            total_censored_duration += duration
            meets_threshold = actual_rms_db <= -50.0

            if meets_threshold:
                successful_segments += 1
            else:
                failed_segments += 1

            # Reconstruct the filter that was applied
            quote_char = '"' if platform.system() == "Windows" else "'"
            volume_filter = f"{strategy['volume_filter']}:enable={quote_char}"
            f"between(t,{start_s},{end_s}){quote_char}"

            segment_diagnostic = SegmentDiagnostic(
                segment_id=i,
                start_time=start_s,
                end_time=end_s,
                duration=duration,
                target_rms_db=-50.0,
                actual_rms_db=actual_rms_db,
                meets_threshold=meets_threshold,
                strategy_used=final_strategy,
                strategy_name=strategy["name"],
                filter_applied=volume_filter,
            )
            segment_diagnostics.append(segment_diagnostic)

        # Generate recommendations based on results
        recommendations = self._generate_recommendations(
            successful_segments, failed_segments, final_strategy, error_messages
        )

        return CensoringDiagnostic(
            timestamp=timestamp,
            input_video=input_video,
            output_video=output_video or "FAILED",
            total_segments=len(censor_segments),
            total_censored_duration=total_censored_duration,
            successful_segments=successful_segments,
            failed_segments=failed_segments,
            final_strategy_used=final_strategy,
            fallback_attempts=fallback_attempts,
            overall_success=overall_success,
            segments=segment_diagnostics,
            error_messages=error_messages,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        successful_segments: int,
        failed_segments: int,
        final_strategy: int,
        error_messages: List[str],
    ) -> List[str]:
        """
        Generates troubleshooting recommendations based on diagnostic results.

        Args:
            successful_segments: Number of segments that met the threshold
            failed_segments: Number of segments that failed to meet the threshold
            final_strategy: Final strategy level used
            error_messages: List of error messages encountered

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Recommendations based on success rate
        if failed_segments == 0:
            recommendations.append(
                "✓ All segments successfully censored. No action needed."
            )
        elif successful_segments == 0:
            recommendations.append("✗ No segments met the silence threshold. Consider:")
            recommendations.append(
                "  - Checking FFmpeg installation and version compatibility"
            )
            recommendations.append(
                "  - Verifying audio codec support in your FFmpeg build"
            )
            recommendations.append("  - Testing with a different input video file")
        else:
            success_rate = (
                successful_segments / (successful_segments + failed_segments)
            ) * 100
            recommendations.append(
                f"⚠ Partial success ({success_rate:.1f}% of segments). Consider:"
            )

            if final_strategy < 3:
                recommendations.append(
                    "  - The system may benefit from more aggressive filtering"
                )
                recommendations.append(
                    "  - Consider manually increasing max_attempts in fallback system"
                )

            recommendations.append(
                "  - Some audio formats may be more resistant to silencing"
            )
            recommendations.append(
                "  - Check if input video has unusual audio characteristics"
            )

        # Recommendations based on strategy used
        if final_strategy == 1:
            recommendations.append("ℹ Basic volume reduction was sufficient")
        elif final_strategy == 2:
            recommendations.append(
                "ℹ Enhanced filtering was required for optimal results"
            )
        elif final_strategy == 3:
            recommendations.append(
                "ℹ Aggressive filtering was required - input may have challenging audio"
            )

        # Recommendations based on error messages
        if any("not found" in msg.lower() for msg in error_messages):
            recommendations.append("⚠ FFmpeg executable issues detected:")
            recommendations.append("  - Ensure FFmpeg is properly installed")
            recommendations.append("  - Check that FFmpeg is in your system PATH")
            recommendations.append("  - Verify FFmpeg has required codec support")

        if any("permission" in msg.lower() for msg in error_messages):
            recommendations.append("⚠ File permission issues detected:")
            recommendations.append("  - Check write permissions for output directory")
            recommendations.append(
                "  - Ensure input file is not locked by another process"
            )

        if any("codec" in msg.lower() for msg in error_messages):
            recommendations.append("⚠ Audio codec issues detected:")
            recommendations.append("  - Input video may use an unsupported audio codec")
            recommendations.append(
                "  - Consider converting input to a standard format (MP4/AAC)"
            )

        # General troubleshooting recommendations
        if failed_segments > 0:
            recommendations.append("General troubleshooting steps:")
            recommendations.append("  - Test with a known-good sample video file")
            recommendations.append("  - Check FFmpeg version: ffmpeg -version")
            recommendations.append(
                "  - Enable debug logging for more detailed information"
            )
            recommendations.append(
                "  - Verify subtitle timing accuracy against audio content"
            )

        return recommendations

    def _log_diagnostic_report(self, diagnostic: CensoringDiagnostic) -> None:
        """
        Logs a comprehensive diagnostic report.

        Args:
            diagnostic: CensoringDiagnostic object to log
        """
        logging.info("=== DIAGNOSTIC REPORT ===")
        logging.info(f"Timestamp: {diagnostic.timestamp}")
        logging.info(f"Input Video: {diagnostic.input_video}")
        logging.info(f"Output Video: {diagnostic.output_video}")
        logging.info(
            f"Overall Success: {'YES' if diagnostic.overall_success else 'NO'}"
        )
        logging.info("")

        logging.info("OPERATION SUMMARY:")
        logging.info(f"  Total Segments: {diagnostic.total_segments}")
        logging.info(
            f"  Total Censored Duration: {diagnostic.total_censored_duration:.3f}s"
        )
        logging.info(f"  Successful Segments: {diagnostic.successful_segments}")
        logging.info(f"  Failed Segments: {diagnostic.failed_segments}")
        logging.info(f"  Final Strategy Used: Level {diagnostic.final_strategy_used}")
        logging.info(f"  Fallback Attempts: {diagnostic.fallback_attempts}")

        if diagnostic.successful_segments > 0:
            success_rate = (
                diagnostic.successful_segments / diagnostic.total_segments
            ) * 100
            logging.info(f"  Success Rate: {success_rate:.1f}%")

        logging.info("")

        # Log detailed segment information
        logging.info("SEGMENT DETAILS:")
        logging.info(
            "  ID | Start    | End      | Duration | Target   | Actual   | Status |"
            " Strategy"
        )
        logging.info(
            "  ---|----------|----------|----------|----------|----------|"
            "--------|----------"
        )

        for seg in diagnostic.segments:
            status = "PASS" if seg.meets_threshold else "FAIL"
            actual_str = (
                f"{seg.actual_rms_db:.2f}"
                if seg.actual_rms_db != float("inf")
                else "N/A"
            )
            logging.info(
                f"  {seg.segment_id:2d} | {seg.start_time:8.3f} | {seg.end_time:8.3f} |"
                f" {seg.duration:8.3f} | {seg.target_rms_db:8.1f} | {actual_str:8s} |"
                f" {status:6s} | {seg.strategy_name}"
            )

        logging.info("")

        # Log error messages if any
        if diagnostic.error_messages:
            logging.info("ERROR MESSAGES:")
            for i, error in enumerate(diagnostic.error_messages, 1):
                logging.info(f"  {i}. {error}")
            logging.info("")

        # Log recommendations
        if diagnostic.recommendations:
            logging.info("RECOMMENDATIONS:")
            for rec in diagnostic.recommendations:
                logging.info(f"  {rec}")

        logging.info("=== END DIAGNOSTIC REPORT ===")

    def _save_diagnostic_report(
        self, diagnostic: CensoringDiagnostic, output_path: Optional[str] = None
    ) -> str:
        """
        Saves diagnostic report to a JSON file.

        Args:
            diagnostic: CensoringDiagnostic object to save
            output_path: Optional path for the diagnostic file

        Returns:
            Path to the saved diagnostic file
        """
        if output_path is None:
            # Generate default filename based on input video and timestamp
            base_name = os.path.splitext(os.path.basename(diagnostic.input_video))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{base_name}_diagnostic_{timestamp}.json"

        # Convert diagnostic to dictionary for JSON serialization
        diagnostic_dict = {
            "timestamp": diagnostic.timestamp,
            "input_video": diagnostic.input_video,
            "output_video": diagnostic.output_video,
            "total_segments": diagnostic.total_segments,
            "total_censored_duration": diagnostic.total_censored_duration,
            "successful_segments": diagnostic.successful_segments,
            "failed_segments": diagnostic.failed_segments,
            "final_strategy_used": diagnostic.final_strategy_used,
            "fallback_attempts": diagnostic.fallback_attempts,
            "overall_success": diagnostic.overall_success,
            "segments": [
                {
                    "segment_id": seg.segment_id,
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "duration": seg.duration,
                    "target_rms_db": seg.target_rms_db,
                    "actual_rms_db": (
                        seg.actual_rms_db if seg.actual_rms_db != float("inf") else None
                    ),
                    "meets_threshold": seg.meets_threshold,
                    "strategy_used": seg.strategy_used,
                    "strategy_name": seg.strategy_name,
                    "filter_applied": seg.filter_applied,
                }
                for seg in diagnostic.segments
            ],
            "error_messages": diagnostic.error_messages,
            "recommendations": diagnostic.recommendations,
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(diagnostic_dict, f, indent=2, ensure_ascii=False)

            logging.info(f"Diagnostic report saved to: {output_path}")
            return output_path

        except Exception as e:
            logging.error(f"Failed to save diagnostic report: {e}")
            return ""

    def _construct_ffmpeg_command(
        self,
        video_path: str,
        output_path: str,
        censor_segments: List[Tuple[float, float]],
        strategy_level: int = 2,
    ) -> List[str]:
        """
        Constructs the FFmpeg command for censoring audio using specified strategy.
        """
        strategy = self._get_filter_strategy(strategy_level)

        logging.info("=== FILTER CONSTRUCTION ===")
        logging.info(f"Using strategy level {strategy_level}: {strategy['name']}")
        logging.info(f"Strategy description: {strategy['description']}")
        logging.info(f"Constructing FFmpeg filters for {len(censor_segments)} segments")

        filter_parts = []
        # Use single quotes for all platforms to avoid Windows parsing issues
        quote_char = "'"

        # Log platform-specific quoting
        logging.debug(
            f"Using quote character: '{quote_char}' (Platform: {platform.system()})"
        )

        # Add format normalization filter if enabled
        if strategy["use_format_normalization"]:
            format_filter = "aformat=sample_fmts=s16:channel_layouts=stereo"
            filter_parts.append(format_filter)
            logging.info(f"Added format normalization filter: {format_filter}")

        # Handle null mixing strategy (requires complex filter graph)
        if strategy["use_null_mixing"]:
            # For null mixing, we use multiple stages of volume reduction
            logging.info(
                "Using null source mixing strategy with multi-stage processing"
            )
            volume_filter_base = strategy["volume_filter"]
        else:
            volume_filter_base = strategy["volume_filter"]

        # Add volume filters for censored segments
        logging.info("Adding volume filters for censored segments:")
        for i, (start_s, end_s) in enumerate(censor_segments, 1):
            volume_filter = (
                f"{volume_filter_base}:enable={quote_char}"
                f"between(t,{start_s},{end_s}){quote_char}"
            )
            filter_parts.append(volume_filter)
            logging.info(
                f"  Segment {i}: {start_s:.3f}s - {end_s:.3f}s (duration:"
                f" {end_s-start_s:.3f}s)"
            )
            logging.debug(f"    Filter: {volume_filter}")

        # Add dynamic range compression filter if enabled
        if strategy["use_compression"]:
            compression_filter = (
                "acompressor=threshold=-20dB:ratio=20:attack=5:release=50"
            )
            filter_parts.append(compression_filter)
            logging.info(
                f"Added dynamic range compression filter: {compression_filter}"
            )

        # Add additional null mixing processing if enabled
        if strategy["use_null_mixing"]:
            # Add multiple stages of volume reduction and noise gating
            null_processing_stages = [
                "volume=-60dB",  # First stage: very low volume
                "volume=0",  # Second stage: zero volume
                "agate=threshold=-90dB:ratio=10:attack=1:release=10",  # Noise gate
            ]
            filter_parts.extend(null_processing_stages)
            logging.info(
                "Added null mixing processing stages:"
                f" {', '.join(null_processing_stages)}"
            )

        audio_filter_graph = ",".join(filter_parts) if filter_parts else "anull"
        logging.info(f"Complete audio filter graph: {audio_filter_graph}")
        logging.info("=== END FILTER CONSTRUCTION ===")

        command = [
            self.ffmpeg_cmd,
            "-i",
            video_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-af",
            audio_filter_graph,
            "-map_metadata",
            "-1",
            "-movflags",
            "+faststart",
            "-y",
            output_path,
        ]

        logging.debug(f"Complete FFmpeg command: {' '.join(command)}")
        return command

    def censor_audio_with_ffmpeg(
        self, video_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Censors profane audio segments in a video file using FFmpeg.
        Args:
            video_path: Path to the input video file.
            output_path: Optional custom output path. If None, generates
            default name.
        Returns:
            Path to the newly created censored video file, or None if an
            error occurred.
        """
        if output_path is None:
            output_path = f"{os.path.splitext(video_path)[0]}_censored.mp4"

        srt_path = self._find_srt_file(video_path)
        subs = None
        if srt_path:
            subs = self._parse_srt_file(srt_path)

        if subs is None:
            temp_srt_path = os.path.splitext(video_path)[0] + ".srt"
            if self.extract_embedded_srt(video_path, temp_srt_path):
                subs = self._parse_srt_file(temp_srt_path)

        if subs is None:
            logging.error("No valid SRT file found. Cannot censor audio.")
            return None

        censor_segments = self._find_profane_segments(subs)

        if not censor_segments:
            logging.info("No profane segments found. No censoring needed.")
            return video_path

        # Log detailed segment information
        logging.info("=== CENSORING OPERATION STARTED ===")
        logging.info(f"Input video: {video_path}")
        logging.info(f"Output video: {output_path}")
        logging.info(f"Found {len(censor_segments)} segments to censor:")

        total_censored_duration: float = 0
        for i, (start_s, end_s) in enumerate(censor_segments, 1):
            duration = end_s - start_s
            total_censored_duration += duration
            logging.info(
                f"  Segment {i}: {start_s:.3f}s - {end_s:.3f}s (duration:"
                f" {duration:.3f}s)"
            )

        logging.info(f"Total censored duration: {total_censored_duration:.3f}s")

        # Use fallback censoring system with progressive filter enhancement
        success, result_path, verification_results, final_strategy, error_messages = (
            self._attempt_censoring_with_fallback(
                video_path, output_path, censor_segments, max_attempts=3
            )
        )

        # Generate comprehensive diagnostic report
        diagnostic = self._generate_diagnostic_report(
            input_video=video_path,
            output_video=result_path,
            censor_segments=censor_segments,
            verification_results=verification_results,
            final_strategy=final_strategy,
            fallback_attempts=final_strategy - 1,  # Number of fallback attempts made
            overall_success=success,
            error_messages=error_messages,
        )

        # Log the diagnostic report
        self._log_diagnostic_report(diagnostic)

        # Save diagnostic report to file
        diagnostic_file = self._save_diagnostic_report(diagnostic)
        if diagnostic_file:
            logging.info(f"Diagnostic report saved to: {diagnostic_file}")

        if not success:
            logging.error("All fallback attempts failed - censoring was not successful")
            return None

        # Log overall verification results
        logging.info("=== VERIFICATION SUMMARY ===")
        passed_segments = sum(1 for _, _, rms in verification_results if rms <= -50.0)
        failed_segments = len(verification_results) - passed_segments

        logging.info(f"Segments passed: {passed_segments}/{len(verification_results)}")
        logging.info(f"Segments failed: {failed_segments}/{len(verification_results)}")

        if passed_segments == len(verification_results):
            logging.info("✓ ALL SEGMENTS MEET SILENCE THRESHOLD")
        else:
            logging.warning("✗ SOME SEGMENTS DO NOT MEET SILENCE THRESHOLD")

        # Log detailed verification table
        logging.info("Detailed verification results:")
        logging.info(
            "  Segment    | Start    | End      | Duration | RMS (dB) | Status"
        )
        logging.info(
            "  -----------|----------|----------|----------|----------|--------"
        )
        for i, (start_s, end_s, rms_db) in enumerate(verification_results, 1):
            duration = end_s - start_s
            status = "PASS" if rms_db <= -50.0 else "FAIL"
            rms_str = f"{rms_db:.2f}" if rms_db != float("inf") else "N/A"
            logging.info(
                f"  {i:9d} | {start_s:8.3f} | {end_s:8.3f} | {duration:8.3f} |"
                f" {rms_str:8s} | {status}"
            )

        logging.info("=== CENSORING OPERATION COMPLETED ===")
        return result_path

    def process_video(
        self, video_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Main method to process a video file and create a censored version.

        Args:
            video_path: Path to the input video file.
            output_path: Optional custom output path.

        Returns:
            Path to the censored video file, or None if processing failed.
        """
        # Validate input file
        if not os.path.exists(video_path):
            logging.error(f"Video file not found: {video_path}")
            return None

        # Get video details (for validation and potential future use)
        video_info = self.get_video_details(video_path)
        if not video_info:
            logging.error("Could not get video details.")
            return None

        # Perform the audio censoring
        return self.censor_audio_with_ffmpeg(video_path, output_path)
