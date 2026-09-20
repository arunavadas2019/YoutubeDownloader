# Bulk YouTube Downloader

A Windows desktop application for downloading multiple YouTube videos from a text file. It uses `yt-dlp`, supports selectable output resolutions, converts video downloads to MP4, and can extract audio as MP3.

Download Executable [YouTube Downloader](./dist/)

## Features

- Download multiple URLs from a text file
- Select the output folder
- Select 480p, 720p, 1080p, 1440p, 2160p, or best available quality
- Save video downloads as MP4
- Extract audio as MP3
- Select and persist the FFmpeg `bin` folder
- Stop an active download
- Restart a stopped download from the last completed URL
- Keep a download archive to skip completed URLs

## Requirements

- Windows
- Python 3.12 or newer
- FFmpeg with `ffmpeg.exe` in its `bin` folder
- Internet access

Python dependencies are listed in [requirements.txt](requirements.txt). PyInstaller is included for building the executable.

## Setup

Open Command Prompt in the project directory and create the virtual environment:

```Command Prompt
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
Start the App:
```Command Prompt
py src\app.py 
```

## FFmpeg Setup

The application needs the FFmpeg `bin` folder, containing at least `ffmpeg.exe`. For example:

```text
ffmpeg\bin\ffmpeg.exe
ffmpeg\bin\ffprobe.exe
```

Start the application and click **Select FFmpeg Bin Folder**. Select the folder containing `ffmpeg.exe`. The selected path is saved in `config.json` and reused on future launches.

If no configuration has been saved, the application checks the bundled default path:

```text
ffmpeg\bin
```

## Running the Application

```powershell
.\.venv\Scripts\python.exe src\app.py
```

Workflow:

1. Create a text file with one video URL per line.
2. Click **Select URL Text File**.
3. Select the FFmpeg `bin` folder if it has not been configured yet.
4. Select an output folder.
5. Choose the desired resolution.
6. Click **Start Bulk Download**.

## Stop and Restart

Click **Stop Download** to terminate the active `yt-dlp` process. Click **Restart Download** to run the queue again.

Completed URLs are recorded in `archive.txt` in the selected output folder. When the queue is restarted, `yt-dlp` uses this archive to skip URLs that were already completed.

## Building an Executable

PyInstaller is configured by [app.spec](app.spec). Build the Windows executable with:

```powershell
.\.venv\Scripts\pyinstaller.exe app.spec --clean
```

The generated files are placed in `build` and `dist`. The built application still needs access to FFmpeg. Select the FFmpeg `bin` folder when the application starts, or place FFmpeg at the bundled default location before packaging.

## Project Structure

```text
2785607/
  src/
    app.py          Application entry point
    ui.py           CustomTkinter user interface
    downloader.py   yt-dlp process and download logic
    config.py       FFmpeg path configuration persistence
  ffmpeg/           Optional bundled FFmpeg directory
    bin/
  requirements.txt  Python dependencies
  app.spec          PyInstaller build configuration
  config.json       User-specific FFmpeg path, created at runtime
```

## Troubleshooting

### FFmpeg was not found

Select the folder that directly contains `ffmpeg.exe`, not the parent FFmpeg folder. For example, select:

```text
F:\sw\ffmpeg-...\bin
```

### Downloads do not restart from the beginning

This is expected when `archive.txt` exists. Delete `archive.txt` from the selected output folder only if you intentionally want already completed URLs to be downloaded again.

### `yt-dlp` cannot be started

Activate the virtual environment or run the application with `.venv\Scripts\python.exe`. Then reinstall dependencies:

```powershell
python -m pip install -r requirements.txt
```
