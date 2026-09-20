import json
import os


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(PROJECT_DIR, "config.json")
DEFAULT_FFMPEG_DIR = os.path.join(PROJECT_DIR, "ffmpeg", "bin")


def load_ffmpeg_dir():
    """Return the saved FFmpeg folder if it exists; otherwise use the bundled default."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return DEFAULT_FFMPEG_DIR

    return config.get("ffmpeg_dir", DEFAULT_FFMPEG_DIR)


def save_ffmpeg_dir(ffmpeg_dir):
    """Persist the selected FFmpeg bin folder to the app configuration file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
        json.dump({"ffmpeg_dir": ffmpeg_dir}, config_file, indent=2)
