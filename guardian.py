import subprocess
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
import uuid
import json
import srt
from xml.dom.minidom import parseString
from pathlib import Path

# --- Word/Phrase Matching List (ranked by frequency occurance) ---
matching_words = [
    'fucking', 'fuck', 'shit', 'damn', 'hell', 'ass', 'bitch', 'bastard',
    'bullshit', 'fucker', 'fucked', 'asshole', 'piss', 'jesus christ',
    'jesus', 'sex', 'pussy', 'son of a bitch', 'sonofabitch', 'jackass',
    'smartass', 'tits', 'whore', 'cunt', 'slut', 'boobs', 'orgasm',
    'penis', 'blowjob', 'handjob', 'hard on', 'cocksucker', 'dipshit',
    'horseshit', 'jack off', 'nympho', 'rape', 'fuckface', 'skank',
    'shitspray', 'bitches', 'nigga', 'nigger', 'dickhead', 'prick', 
    'arsehole', 'motherfucker', 'goddamn', 'shithead', 'douchebag', 'fag', 'faggot'
]
ffprobe_cmd = '/Users/Shared/FFmpegTools/ffprobe'

def get_video_details(filename):
    details = {}
    logging.debug(f"Getting video details for: {filename}")
    cmd = [ffprobe_cmd, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename]
    ffprobe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = ffprobe.communicate()
    details["duration"] = stdout.strip()

    cmd = [ffprobe_cmd, "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name,channels,channel_layout,sample_rate", "-of", "compact=p=0:nk=1", filename]
    ffprobe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = ffprobe.communicate()
    save_channels = 0
    for line in stdout.strip().split('\n'):
        parts = line.split('|')
        if len(parts) >= 3 and parts[2].isdigit():
            test_channels = int(parts[2])
            if test_channels > save_channels:
                details["codec"] = parts[0]; details["samplerate"] = parts[1]; details["channels"] = parts[2]
                details["audioconfig"] = parts[3] if len(parts) > 3 else ""
                save_channels = test_channels

    cmd = [ffprobe_cmd, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,width,height", "-of", "default=noprint_wrappers=1:nokey=1", filename]
    ffprobe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = ffprobe.communicate()
    lines = stdout.strip().split('\n')
    if len(lines) >= 3:
        details["width"] = lines[0]
        details["height"] = lines[1]
        framerate_str = lines[2]
    else:
        details["width"] = None
        details["height"] = None
        framerate_str = None # Initialize to None to avoid UnboundLocalError

    if framerate_str and '/' in framerate_str:
        numerator, denominator = map(int, framerate_str.split('/'))
        details["framerate"] = framerate_str
        details["fps"] = "{:.3f}".format(numerator / denominator)
        details["frameduration"] = f'{denominator}/{numerator}'
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

def create_fcpxml(video_path, video_info):
    root = ET.Element("fcpxml", version="1.9")
    resources = ET.SubElement(root, "resources")
    
    # --- RATIONAL TIME LOGIC ---
    frame_dur_num, timebase = map(int, video_info['frameduration'].split('/'))
    total_duration_s = float(video_info['duration'])
    frame_duration_s = frame_dur_num / timebase
    
    num_total_frames = int(total_duration_s / frame_duration_s)
    total_duration_ticks = num_total_frames * frame_dur_num
    duration_str = f"{total_duration_ticks}/{timebase}s"
    logging.debug(f"Precise rational duration: {duration_str} ({num_total_frames} frames)")

    def time_s_to_rational_str(time_s):
        # Floor the frame calculation to ensure we don't exceed the intended time
        num_frames = int(float(time_s) // frame_duration_s)
        time_ticks = num_frames * frame_dur_num
        return f"{time_ticks}/{timebase}s"

    # --- XML Construction using separate format IDs ---
    format_name = f"FFVideoFormat{video_info['height']}p{video_info['fps'].replace('.', '_')}"
    format_id_asset = "r1"
    format_id_sequence = "r2" # Use a separate ID for the sequence

    # Asset Format
    ET.SubElement(resources, "format", id=format_id_asset, name=format_name, frameDuration=f"{frame_dur_num}/{timebase}s", width=video_info['width'], height=video_info['height'])
    # Sequence Format (identical, but separate)
    ET.SubElement(resources, "format", id=format_id_sequence, name=format_name, frameDuration=f"{frame_dur_num}/{timebase}s", width=video_info['width'], height=video_info['height'])
    
    asset_id = "r3"
    asset = ET.SubElement(resources, "asset", id=asset_id, name=os.path.basename(video_path), duration=duration_str, hasVideo="1", hasAudio="1", format=format_id_asset, audioChannels=video_info['channels'], audioRate=video_info['samplerate'])
    
    ET.SubElement(asset, "media-rep", kind="original-media", src=Path(video_path).as_uri())

    library = ET.SubElement(root, "library", location="file:///Users/Shared/")
    event = ET.SubElement(library, "event", name="Imported Media")
    
    project_name = os.path.splitext(os.path.basename(video_path))[0]
    project = ET.SubElement(event, "project", name=project_name)
    
    audio_layout = 'stereo' if int(video_info['channels']) <= 2 else 'surround'
    # Convert any numeric sample rate to the correct FCPXML 'k' format
    sample_rate_num = int(video_info['samplerate'])
    k_value = sample_rate_num / 1000.0

    # Format as an integer (e.g., "48k") if it's a whole number, else format as a float (e.g., "44.1k")
    if k_value == int(k_value):
        audio_rate_str = f"{int(k_value)}k"
    else:
        audio_rate_str = f"{k_value}k"

    sequence = ET.SubElement(project, "sequence", 
                             format=format_id_sequence, 
                             duration=duration_str, 
                             tcFormat="NDF",
                             audioLayout=audio_layout,
                             audioRate=audio_rate_str)   
    spine = ET.SubElement(sequence, "spine")
    asset_clip = ET.SubElement(spine, "asset-clip", ref=asset_id, name=project_name, format=format_id_asset, duration=duration_str)
    
    adjust_volume = ET.SubElement(asset_clip, "adjust-volume")
    volume_param = ET.SubElement(adjust_volume, "param", name="amount")
    keyframe_anim = ET.SubElement(volume_param, "keyframeAnimation")
    
    keyframes = [(time_s_to_rational_str(0), '0dB')]

    srt_path = os.path.splitext(video_path)[0] + '.srt'
    try:
        with open(srt_path, 'r', encoding='utf-8-sig') as f:
            srt_content = f.read()
        subs = list(srt.parse(srt_content)) # The library does all the work
    except FileNotFoundError:
        logging.error(f"SRT file not found: {srt_path}"); return tree

    # Build a single regex pattern to find any of the words/phrases as whole words.
    pattern = r'\b(' + '|'.join(re.escape(word) for word in matching_words) + r')\b'
    censor_pattern = re.compile(pattern, re.IGNORECASE)
    fade_s = 0.2

    for sub in subs:
        # Clean the content from the object
        cleaned_text = re.sub(r'[^\w\s\']', '', sub.content).lower()
    
        if censor_pattern.search(cleaned_text):
            logging.debug(f"Match found in subtitle #{sub.index}: \"{cleaned_text}\"")
            try:
                # Get start/end times directly in seconds from timedelta objects
                start_s = sub.start.total_seconds()
                end_s = sub.end.total_seconds()

                # The keyframe generation logic is the same, but now it's triggered correctly
                keyframes.extend([
                    (time_s_to_rational_str(start_s - fade_s), '0dB'),
                    (time_s_to_rational_str(start_s), '-96dB'),
                    (time_s_to_rational_str(end_s), '-96dB'),
                    (time_s_to_rational_str(end_s + fade_s), '0dB')
                ])
            except (ValueError, KeyError) as e:
                logging.error(f"Could not process subtitle #{sub.get('index', 'N/A')}: {e}")
                continue
    
    final_keyframes = sorted(list(dict.fromkeys(keyframes)), key=lambda x: int(x[0].split('/')[0]))
    logging.info(f"Generated {len(final_keyframes)} unique keyframes for volume adjustment.")
    
    for time_str, value_val in final_keyframes:
        ET.SubElement(keyframe_anim, "keyframe", time=time_str, value=value_val)

    tree = ET.ElementTree(root)
    prettyxml = parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="    ")
    
    fcpxml_path = os.path.splitext(video_path)[0] + '.fcpxml'
    logging.info(f"Writing FCPXML to: {fcpxml_path}")
    with open(fcpxml_path, "w", encoding="utf-8") as f: f.write(prettyxml)
    return tree

if __name__ == "__main__":

    if len(sys.argv) != 2: print("Usage: python guardian.py <videofile>"); sys.exit(1)

    script_fullpath = sys.argv[0]
    script_filename = os.path.basename(script_fullpath)
    log_file = f"{os.path.splitext(script_filename)[0]}.log"
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_file, mode='w'), logging.StreamHandler()])
    
    filepath = os.path.abspath(sys.argv[1])
    logging.info(f"Processing file: {filepath}")
    
    video_info = get_video_details(filepath)
    if not video_info:
        logging.error("Could not get video details. Exiting."); sys.exit(1)

    create_fcpxml(filepath, video_info)
    logging.info("Script finished successfully.")