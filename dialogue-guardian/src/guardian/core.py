"""
Core functionality for the Guardian media censoring system.
"""

import json
import logging
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

import srt


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
        ffmpeg_cmd: str = "ffmpeg",
        ffprobe_cmd: str = "ffprobe",
    ):
        """
        Initialize the GuardianProcessor.

        Args:
            matching_words: Custom list of words to censor. Uses default if
                None.
            ffmpeg_cmd: Path to ffmpeg executable.
            ffprobe_cmd: Path to ffprobe executable.
        """
        self.matching_words = matching_words if matching_words is not None else self.DEFAULT_MATCHING_WORDS
        self.ffmpeg_cmd = ffmpeg_cmd
        self.ffprobe_cmd = ffprobe_cmd

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
                    if stream.get("codec_name") == "subrip":
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

        srt_path = os.path.splitext(video_path)[0] + ".srt"

        # Check for language-specific SRT files if main one doesn't exist
        if not os.path.exists(srt_path):
            base_path = os.path.splitext(video_path)[0]
            for lang in ["en", "fr", "es", "de", "it"]:
                lang_srt_path = f"{base_path}.{lang}.srt"
                if os.path.exists(lang_srt_path):
                    srt_path = lang_srt_path
                    logging.info(f"Found language-specific SRT file: {srt_path}")
                    break

        # Try to load external SRT first
        subs = []
        if os.path.exists(srt_path):
            logging.info(f"Found external SRT file: {srt_path}")
            try:
                with open(srt_path, "r", encoding="utf-8-sig") as f:
                    srt_content = f.read()
                subs = list(srt.parse(srt_content))
            except Exception as e:
                logging.error(
                    f"Error reading or parsing external SRT file {srt_path}: {e}"
                )
                # If external SRT is problematic, try embedded
                if self.extract_embedded_srt(video_path, srt_path):
                    try:
                        with open(srt_path, "r", encoding="utf-8-sig") as f:
                            srt_content = f.read()
                        subs = list(srt.parse(srt_content))
                        logging.info(
                            f"Successfully loaded extracted SRT from {srt_path}"
                        )
                    except Exception as e:
                        logging.error(
                            f"Error parsing extracted SRT file {srt_path}: {e}"
                        )
                        return None
                else:
                    logging.error("No valid SRT file found. Cannot censor audio.")
                    return None
        else:
            logging.info(
                f"External SRT not found: {srt_path}. Attempting video extraction."
            )
            # If external SRT not found, try to extract embedded SRT
            if self.extract_embedded_srt(video_path, srt_path):
                try:
                    with open(srt_path, "r", encoding="utf-8-sig") as f:
                        srt_content = f.read()
                    subs = list(srt.parse(srt_content))
                    logging.info(f"Successfully loaded extracted SRT from {srt_path}")
                except Exception as e:
                    logging.error(
                        f"Error reading or parsing extracted SRT file {srt_path}: {e}"
                    )
                    return None
            else:
                logging.error("No SRT file found or extractable. Cannot censor audio.")
                return None

        if not subs:
            logging.warning(
                "No subtitles found in sources. No censoring will be applied."
            )
            audio_filter_graph = "anull"
        else:
            # Build a single regex pattern to find any phrases as whole words
            pattern = (
                r"\b("
                + "|".join(re.escape(word) for word in self.matching_words)
                + r")\b"
            )
            censor_pattern = re.compile(pattern, re.IGNORECASE)

            censor_segments = []

            for sub in subs:
                cleaned_text = re.sub(r"[^\w\s\']", "", sub.content).lower()
                if censor_pattern.search(cleaned_text):
                    logging.debug(
                        f'Match found in subtitle #{sub.index}: "{cleaned_text}"'
                    )
                    start_s = sub.start.total_seconds()
                    end_s = sub.end.total_seconds()
                    censor_segments.append((start_s, end_s))

            # Construct the FFmpeg audio filter graph
            filter_parts = []
            for start_s, end_s in censor_segments:
                filter_parts.append(
                    f"volume=enable='between(t,{start_s},{end_s})':volume=0"
                )

            audio_filter_graph = ",".join(filter_parts) if filter_parts else "anull"

        # Construct the FFmpeg command
        ffmpeg_command = [
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

        logging.info(f"Executing FFmpeg command: {' '.join(ffmpeg_command)}")
        try:
            process = subprocess.run(
                ffmpeg_command, check=True, capture_output=True, text=True
            )
            logging.info(f"FFmpeg stdout:\n{process.stdout}")
            logging.info(f"Successfully created censored video: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg command failed. Return code: {e.returncode}")
            logging.error(f"FFmpeg stdout:\n{e.stdout}")
            logging.error(f"FFmpeg stderr:\n{e.stderr}")
            return None
        except FileNotFoundError:
            logging.error(
                "Please ensure FFmpeg is installed and in your system's PATH."
            )
            return None

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
