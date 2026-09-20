import os
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from config import load_ffmpeg_dir, save_ffmpeg_dir
from downloader import (
    DownloadError,
    DownloadStopped,
    RESOLUTION_OPTIONS,
    YouTubeDownloader,
)


class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        """Initialize the main application window, state, and UI widgets."""
        super().__init__()

        self.title("Bulk YouTube Downloader")
        self.geometry("600x450")
        self.resizable(False, False)

        self.file_path = ""
        self.output_folder = os.getcwd()
        self.ffmpeg_dir = load_ffmpeg_dir()
        self.downloader = YouTubeDownloader(self.log_message, self.ffmpeg_dir)

        self._build_file_selection()
        self._build_output_selection()
        self._build_ffmpeg_selection()
        self._build_resolution_selection()
        self._build_download_button()
        self._build_log_box()

    def _build_file_selection(self):
        """Create the file-picker section for selecting the URL list text file."""
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(fill="x", padx=30, pady=10)

        self.btn_browse = ctk.CTkButton(
            self.file_frame,
            text="Select URL Text File",
            command=self.select_file,
        )
        self.btn_browse.pack(side="left", padx=10, pady=10)

        self.lbl_file = ctk.CTkLabel(
            self.file_frame,
            text="No file selected",
            text_color="gray",
        )
        self.lbl_file.pack(side="left", padx=10, pady=10)

    def _build_output_selection(self):
        """Create the output-folder selector and display the current destination."""
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.pack(fill="x", padx=30, pady=10)

        self.btn_output = ctk.CTkButton(
            self.output_frame,
            text="Select Output Folder",
            command=self.select_output_folder,
        )
        self.btn_output.pack(side="left", padx=10, pady=10)

        self.lbl_output = ctk.CTkLabel(
            self.output_frame,
            text=self.output_folder,
            text_color="gray",
        )
        self.lbl_output.pack(side="left", padx=10, pady=10)

    def _build_resolution_selection(self):
        """Create the resolution selector that determines the yt-dlp format choice."""
        self.res_frame = ctk.CTkFrame(self)
        self.res_frame.pack(fill="x", padx=30, pady=10)

        self.lbl_res = ctk.CTkLabel(self.res_frame, text="Target Resolution:")
        self.lbl_res.pack(side="left", padx=15, pady=15)

        self.res_dropdown = ctk.CTkComboBox(
            self.res_frame,
            values=list(RESOLUTION_OPTIONS.keys()),
            width=220,
        )
        self.res_dropdown.pack(side="right", padx=15, pady=15)
        self.res_dropdown.set("Best Available (Default)")

    def _build_ffmpeg_selection(self):
        """Create the FFmpeg folder selector and show the currently configured path."""
        self.ffmpeg_frame = ctk.CTkFrame(self)
        self.ffmpeg_frame.pack(fill="x", padx=30, pady=10)

        self.btn_ffmpeg = ctk.CTkButton(
            self.ffmpeg_frame,
            text="Select FFmpeg Bin Folder",
            command=self.select_ffmpeg_folder,
        )
        self.btn_ffmpeg.pack(side="left", padx=10, pady=10)

        self.lbl_ffmpeg = ctk.CTkLabel(
            self.ffmpeg_frame,
            text=self.ffmpeg_dir,
            text_color="gray",
        )
        self.lbl_ffmpeg.pack(side="left", padx=10, pady=10)

    def _build_download_button(self):
        """Create the start, stop, and restart controls for the bulk download workflow."""
        self.download_buttons = ctk.CTkFrame(self)
        self.download_buttons.pack(pady=20)

        self.btn_download = ctk.CTkButton(
            self.download_buttons,
            text="Start Bulk Download",
            command=self.start_download_thread,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.btn_download.pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(
            self.download_buttons,
            text="Stop Download",
            command=self.stop_download,
            state="disabled",
            fg_color="firebrick",
            hover_color="darkred",
        )
        self.btn_stop.pack(side="left", padx=5)

        self.btn_restart = ctk.CTkButton(
            self.download_buttons,
            text="Restart Download",
            command=self.start_download_thread,
            state="disabled",
        )
        self.btn_restart.pack(side="left", padx=5)

    def _build_log_box(self):
        """Create the textbox used to show progress and error output from the downloader."""
        self.log_textbox = ctk.CTkTextbox(self, width=540, height=120)
        self.log_textbox.pack(padx=30, pady=5)
        self.log_textbox.insert("0.0", "Logs will appear here...\n")
        self.log_textbox.configure(state="disabled")

    def select_file(self):
        """Open a file dialog and save the selected text file containing video URLs."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.lbl_file.configure(
                text=os.path.basename(file_path),
                text_color=("black", "white"),
            )

    def select_output_folder(self):
        """Open a folder dialog and update the destination used for downloaded files."""
        output_folder = filedialog.askdirectory(initialdir=self.output_folder)
        if output_folder:
            self.output_folder = output_folder
            self.lbl_output.configure(
                text=output_folder,
                text_color=("black", "white"),
            )

    def select_ffmpeg_folder(self):
        """Validate and save a user-selected FFmpeg bin directory before using it."""
        ffmpeg_dir = filedialog.askdirectory(initialdir=self.ffmpeg_dir)
        if not ffmpeg_dir:
            return

        if not os.path.isfile(os.path.join(ffmpeg_dir, "ffmpeg.exe")):
            messagebox.showerror(
                "Invalid FFmpeg Folder",
                "The selected folder must contain ffmpeg.exe.",
            )
            return

        self.ffmpeg_dir = ffmpeg_dir
        self.downloader.ffmpeg_dir = ffmpeg_dir
        save_ffmpeg_dir(ffmpeg_dir)
        self.lbl_ffmpeg.configure(
            text=ffmpeg_dir,
            text_color=("black", "white"),
        )

    def log_message(self, message):
        """Write a status or error message into the log textbox and scroll it into view."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def start_download_thread(self):
        """Validate the inputs and start the bulk download in a background thread."""
        if not self.file_path:
            messagebox.showerror(
                "Error",
                "Please select a text file containing the URLs.",
            )
            return

        if not self.downloader.ffmpeg_available():
            messagebox.showerror(
                "Error",
            f"FFmpeg was not found in:\n{self.ffmpeg_dir}",
            )
            return

        self.btn_download.configure(state="disabled", text="Downloading...")
        self.btn_restart.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        threading.Thread(target=self.run_bulk_download, daemon=True).start()

    def stop_download(self):
        """Stop the active download by asking the downloader to terminate the running process."""
        self.downloader.stop()

    def run_bulk_download(self):
        """Execute the queue in the background and update the UI after success or failure."""
        try:
            self.downloader.download(
                self.file_path,
                self.output_folder,
                self.res_dropdown.get(),
            )
            messagebox.showinfo("Success", "Bulk download task completed successfully!")
        except DownloadStopped:
            self.log_message("Download stopped. Restart to continue from the last completed file.")
        except DownloadError as error:
            self.log_message(f"Critical Error: {error}")
            messagebox.showerror("Error", str(error))
        finally:
            self.btn_download.configure(state="normal", text="Start Bulk Download")
            self.btn_stop.configure(state="disabled")
            self.btn_restart.configure(state="normal")
