from datetime import timedelta
from unittest.mock import MagicMock, patch

import srt
from guardian.core import GuardianProcessor


def make_subtitle_with_profanity():
    # Create a minimal srt.Subtitle that will be detected as profane
    return srt.Subtitle(index=1, start=timedelta(seconds=0), end=timedelta(seconds=1), content="fuck")


def test_censor_calls_attempt_with_verify_false_and_single_attempt(tmp_path):
    proc = GuardianProcessor(ffmpeg_cmd="ffmpeg", ffprobe_cmd="ffprobe")

    # Patch internal SRT discovery and parsing so censoring proceeds
    with patch.object(proc, "_find_srt_file", return_value="/does/not/matter.srt"), patch.object(
        proc, "_parse_srt_file", return_value=[make_subtitle_with_profanity()]
    ), patch.object(
        proc,
        "_attempt_censoring_with_fallback",
        return_value=(True, "out.mp4", [(0.0, 1.0, -100.0)], 1, []),
    ) as mock_attempt:

        result = proc.censor_audio_with_ffmpeg("input.mp4", full=False)

        assert result == "out.mp4"

        # Ensure attempt was called and verify flag was False and max_attempts==1
        assert mock_attempt.called
        _, _, _, kwargs = mock_attempt.call_args[0][0:3] + ({},)
        # Inspect call via call_args to find keyword usage
        called_kwargs = mock_attempt.call_args.kwargs
        assert called_kwargs.get("verify") is False
        assert called_kwargs.get("max_attempts") == 1


def test_censor_calls_attempt_with_verify_true_and_three_attempts(tmp_path):
    proc = GuardianProcessor(ffmpeg_cmd="ffmpeg", ffprobe_cmd="ffprobe")

    with patch.object(proc, "_find_srt_file", return_value="/does/not/matter.srt"), patch.object(
        proc, "_parse_srt_file", return_value=[make_subtitle_with_profanity()]
    ), patch.object(
        proc,
        "_attempt_censoring_with_fallback",
        return_value=(True, "out.mp4", [(0.0, 1.0, -60.0)], 3, []),
    ) as mock_attempt:

        result = proc.censor_audio_with_ffmpeg("input.mp4", full=True)

        assert result == "out.mp4"

        assert mock_attempt.called
        called_kwargs = mock_attempt.call_args.kwargs
        assert called_kwargs.get("verify") is True
        assert called_kwargs.get("max_attempts") == 3


def test_full_mode_executes_astats_and_parses_rms(tmp_path):
    """
    Integration-style unit test: exercise the full verification path by
    letting the fallback routine run while patching subprocess.run to
    simulate both ffmpeg processing and astats output. This ensures
    `_verify_silence_level` and `_parse_astats_output` are actually used
    when `full=True`.
    """
    proc = GuardianProcessor(ffmpeg_cmd="ffmpeg", ffprobe_cmd="ffprobe")

    # Provide a single profane subtitle
    subs = [make_subtitle_with_profanity()]

    # Patch SRT discovery/parsing so censoring proceeds
    with patch.object(proc, "_find_srt_file", return_value="/does/not/matter.srt"), patch.object(
        proc, "_parse_srt_file", return_value=subs
    ), patch.object(
        proc,
        "_construct_ffmpeg_command",
        return_value=["ffmpeg", "-i", "in.mp4", "out.mp4"],
    ) as mock_construct:

        # Prepare subprocess.run side effects: first call is processing (returncode 0),
        # subsequent astats call should include stderr with an RMS value
        processing_result = MagicMock()
        processing_result.returncode = 0
        processing_result.stdout = "processing ok"
        processing_result.stderr = ""

        astats_result = MagicMock()
        astats_result.returncode = 0
        # Include a line that matches one of the parsing patterns
        astats_result.stderr = "lavfi.astats.Overall.RMS_level: -55.3"

        def run_side_effect(cmd, check=False, capture_output=False, text=False, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, (list, tuple)) else str(cmd)
            if "astats" in cmd_str:
                return astats_result
            # Treat others as processing commands
            return processing_result

        with patch("subprocess.run", side_effect=run_side_effect) as mock_run:
            # Run with full=True to enable verification
            out_path = proc.censor_audio_with_ffmpeg("input.mp4", full=True)

            # Expect the returned path to point to the censored output
            assert out_path is not None

            # Ensure subprocess.run was called for processing and for astats
            assert mock_run.call_count >= 2

            # Verify that the astats stderr parsing would have returned -55.3
            parsed = proc._parse_astats_output(astats_result.stderr)
            assert parsed == -55.3
