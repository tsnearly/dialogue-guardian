# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Script to download and extract FFmpeg for the current platform.
"""
import platform
import re
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path

import requests

# Define a common 'bin' directory at the project root
ROOT_DIR = Path(__file__).parent.parent
BIN_DIR = ROOT_DIR / "bin"
FFMPEG_URLS = {
    "Windows": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    "Darwin": [
        "https://evermeet.cx/ffmpeg/get/zip",
        "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip",
    ],
    "Linux": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
}
CHUNK_SIZE = 8192


def get_ffmpeg_urls():
    """
    Returns the appropriate FFmpeg download URL for the current OS.
    """
    system = platform.system()
    return FFMPEG_URLS.get(system)


def download_file(url, target_dir):
    """
    Downloads a file from a URL to a target directory.
    """
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            content_disposition = r.headers.get("content-disposition")
            filename_from_header = None
            if content_disposition:
                fname = re.findall("filename=(.+)", content_disposition)
                if fname:
                    filename_from_header = fname[0].strip('"')

            if filename_from_header:
                local_filename = filename_from_header
            else:
                # Fallback to URL, with special handling for evermeet.cx
                url_part = url.split("/")[-1]
                if "evermeet.cx" in url and url_part == "zip":
                    if "ffprobe" in url:
                        local_filename = "ffprobe.zip"
                    else:
                        local_filename = "ffmpeg.zip"
                else:
                    local_filename = url_part

            download_path = target_dir / local_filename
            print(f"Downloading {url} to {download_path}...")

            with open(download_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
        print("Download complete.")
        return download_path
    except Exception as e:
        print(f"ERROR: Failed to download {url}: {e}")
        raise


def extract_archive(archive_path, extract_dir):
    """
    Extracts an archive to a specified directory.
    """
    print(f"Extracting {archive_path} to {extract_dir}...")
    try:
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
        elif archive_path.suffix == ".xz":
            with tarfile.open(archive_path, "r:xz") as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
        print("Extraction complete.")

        # Debug: List extracted contents
        print("Extracted contents:")
        for item in extract_dir.rglob("*"):
            if item.is_file():
                print(f"  File: {item.relative_to(extract_dir)}")
            elif item.is_dir():
                print(f"  Dir:  {item.relative_to(extract_dir)}/")

    except Exception as e:
        print(f"ERROR: Failed to extract {archive_path}: {e}")
        raise


def find_and_move_binaries(extract_dir, archive_path):
    """
    Finds and moves the ffmpeg and ffprobe binaries to the bin directory.
    """
    system = platform.system()
    ffmpeg_bin_dir = None

    if system == "Windows":
        # The archive extracts into a versioned directory, find it dynamically
        extracted_folders = [d for d in extract_dir.iterdir() if d.is_dir()]
        if len(extracted_folders) == 1:
            ffmpeg_bin_dir = extracted_folders[0] / "bin"
        else:
            print(f"ERROR: Expected one directory in {extract_dir}, but found {len(extracted_folders)}.")
            return False
    elif system == "Darwin":
        # The zip file extracts the binaries directly
        ffmpeg_bin_dir = extract_dir
    else:  # Linux
        # The tarball extracts into a versioned directory
        extracted_folders = [d for d in extract_dir.iterdir() if d.is_dir()]
        if len(extracted_folders) == 1:
            ffmpeg_bin_dir = extracted_folders[0]
        else:
            print(f"ERROR: Expected one directory in {extract_dir}, but found {len(extracted_folders)}.")
            return False

    print(f"Searching for binaries in {ffmpeg_bin_dir}...")
    if not ffmpeg_bin_dir or not ffmpeg_bin_dir.exists():
        print("ERROR: Binary directory not found.")
        return False

    moved_ffmpeg = False
    moved_ffprobe = False
    for f in ffmpeg_bin_dir.iterdir():
        if f.is_file():
            if f.name in ("ffmpeg", "ffmpeg.exe"):
                print(f"Moving {f.name} to {BIN_DIR}")
                target_path = BIN_DIR / f.name
                shutil.move(str(f), str(target_path))
                # Set executable permissions on Unix-like systems
                if platform.system() != "Windows":
                    target_path.chmod(0o755)
                    print(f"Set executable permissions for {target_path}")
                moved_ffmpeg = True
            elif f.name in ("ffprobe", "ffprobe.exe"):
                print(f"Moving {f.name} to {BIN_DIR}")
                target_path = BIN_DIR / f.name
                shutil.move(str(f), str(target_path))
                # Set executable permissions on Unix-like systems
                if platform.system() != "Windows":
                    target_path.chmod(0o755)
                    print(f"Set executable permissions for {target_path}")
                moved_ffprobe = True

    if not moved_ffmpeg or not moved_ffprobe:
        print("ERROR: Failed to find both ffmpeg and ffprobe executables.")
        return False

    print("Successfully moved binaries and set permissions.")
    return True


def main():
    """
    Main function to download and set up FFmpeg.
    """
    BIN_DIR.mkdir(exist_ok=True)

    if any(
        f.name.startswith("ffmpeg") for f in BIN_DIR.iterdir()
    ) and any(
        f.name.startswith("ffprobe") for f in BIN_DIR.iterdir()
    ):
        print("FFmpeg and ffprobe already found in bin directory. Skipping download.")
        return

    urls = get_ffmpeg_urls()
    if not urls:
        print(f"Unsupported OS: {platform.system()}")
        sys.exit(1)

    if isinstance(urls, str):
        urls = [urls]

    temp_dir = BIN_DIR / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(exist_ok=True)

    try:
        archive_path = None
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)

        for url in urls:
            archive_path = download_file(url, temp_dir)
            extract_archive(archive_path, extract_dir)

        success = find_and_move_binaries(extract_dir, archive_path)

        if not success:
            sys.exit(1)

    finally:
        print("Cleaning up temporary files...")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        print("Done.")


if __name__ == "__main__":
    main()
