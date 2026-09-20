import os
import subprocess
from typing import Callable

RESOLUTION_OPTIONS = {
    "Best Available (Default)": "bestvideo+bestaudio/best",
    "2160p": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
    "1440p": "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "Audio Only (MP3)": "bestaudio",
}


class DownloadError(Exception):
    """Raised when a download cannot be started or completed."""


class DownloadStopped(Exception):
    """Raised when the active download is stopped by the user."""


class YouTubeDownloader:
    def __init__(self, log_callback: Callable[[str], None], ffmpeg_dir):
        """Store the UI log callback and FFmpeg path for the current download session."""
        self.log_callback = log_callback
        self.ffmpeg_dir = ffmpeg_dir
        self.process = None

    def ffmpeg_available(self):
        """Check whether the ffmpeg.exe executable exists in the configured bin folder."""
        return os.path.isfile(os.path.join(self.ffmpeg_dir, "ffmpeg.exe"))

    def download(self, url_file, output_folder, resolution_label):
        """Run yt-dlp against the selected URL list and stream progress to the UI log."""
        if not self.ffmpeg_available():
            raise DownloadError(f"FFmpeg was not found in:\n{self.ffmpeg_dir}")

        format_string = RESOLUTION_OPTIONS[resolution_label]
        command = [
            "yt-dlp",
            "-a", url_file,
            "--download-archive", os.path.join(output_folder, "archive.txt"),
            "--sleep-interval", "5",
            "--max-sleep-interval", "15",
            "-f", format_string,
            "-o", os.path.join(output_folder, "%(title)s.%(ext)s"),
            "--ffmpeg-location", self.ffmpeg_dir,
            "--ignore-errors",
        ]

        if "Audio Only" in resolution_label:
            command.extend(["--extract-audio", "--audio-format", "mp3"])
        else:
            command.extend(["--merge-output-format", "mp4", "--remux-video", "mp4"])

        self.log_callback(f"Starting queue using format: {resolution_label}")

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except OSError as error:
            raise DownloadError(str(error)) from error

        self.process = process

        try:
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.log_callback(line)
        finally:
            process.wait()
            self.process = None

        if process.returncode != 0:
            raise DownloadStopped()

        self.log_callback("--- Bulk Download Completed! ---")

    def stop(self):
        """Terminate the active download process if it is still running."""
        if self.process and self.process.poll() is None:
            self.log_callback("Stopping download...")
            self.process.terminate()
