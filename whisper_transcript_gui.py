#!/usr/bin/env python3
"""Drag-and-drop MP4 files to transcribe with OpenAI Whisper."""

from __future__ import annotations

import ctypes
import os
import re
import shutil
import subprocess
import sys
import time
import tkinter as tk
from ctypes import wintypes
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_DIR = Path(__file__).resolve().parent
TRANSCRIPT_DIR = APP_DIR / "transcripts"
DEFAULT_MODEL = "turbo"
VIDEO_EXTENSIONS = {".mp4", ".m4v", ".mov", ".mkv", ".webm", ".avi", ".wav", ".mp3", ".m4a"}
POLL_MS = 400
_WHISPER_PYTHON: str | None = None


def _python_has_whisper(python_exe: str) -> bool:
    try:
        result = subprocess.run(
            [python_exe, "-c", "import whisper"],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _candidate_python_executables() -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()

    def add(path: str | Path | None) -> None:
        if not path:
            return
        resolved = str(Path(path).resolve())
        if resolved not in seen:
            seen.add(resolved)
            candidates.append(resolved)

    add(sys.executable)
    add(os.environ.get("WHISPER_PYTHON"))
    add(r"C:\Users\Andre\AppData\Local\Programs\Python\Python311\python.exe")

    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["py", "-0p"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "python.exe" in line.lower():
                        add(line.rsplit(maxsplit=1)[-1].strip())
        except (OSError, subprocess.TimeoutExpired):
            pass

    return candidates


def whisper_python() -> str:
    global _WHISPER_PYTHON
    if _WHISPER_PYTHON is not None:
        return _WHISPER_PYTHON

    for candidate in _candidate_python_executables():
        if _python_has_whisper(candidate):
            _WHISPER_PYTHON = candidate
            return candidate

    raise RuntimeError(
        "Whisper is not installed for any Python on this PC.\n"
        "Install it with:\n"
        "  py -3.11 -m pip install openai-whisper"
    )


def _subprocess_env() -> dict[str, str]:
    """Ensure ffmpeg is on PATH for the Whisper child process."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        winget_root = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
        if winget_root.is_dir():
            for candidate in winget_root.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
                ffmpeg = str(candidate)
                break
    if ffmpeg:
        ffmpeg_dir = str(Path(ffmpeg).parent)
        env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")
    return env


class WindowsDropTarget:
    """Native Windows drag-and-drop via WM_DROPFILES (no windnd / no extra threads)."""

    WM_DROPFILES = 0x0233
    GWL_WNDPROC = -4
    LRESULT = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long

    def __init__(self) -> None:
        self._user32 = ctypes.windll.user32
        self._shell32 = ctypes.windll.shell32
        self._pending_paths: list[str] = []
        self._hooks: dict[int, dict[str, object]] = {}
        self._wndproc_type = ctypes.WINFUNCTYPE(
            self.LRESULT,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        )

        self._user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
        self._user32.SetWindowLongPtrW.restype = ctypes.c_void_p
        self._user32.CallWindowProcW.argtypes = [
            ctypes.c_void_p,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        self._user32.CallWindowProcW.restype = self.LRESULT
        self._shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]
        self._shell32.DragAcceptFiles.restype = None
        self._shell32.DragQueryFileW.argtypes = [
            wintypes.HANDLE,
            wintypes.UINT,
            wintypes.LPWSTR,
            wintypes.UINT,
        ]
        self._shell32.DragQueryFileW.restype = wintypes.UINT
        self._shell32.DragFinish.argtypes = [wintypes.HANDLE]
        self._shell32.DragFinish.restype = None

    def register(self, widget: tk.Misc, callback) -> None:
        if sys.platform != "win32":
            return

        widget.update_idletasks()
        hwnd = int(widget.winfo_id())
        if hwnd in self._hooks:
            self._hooks[hwnd]["callback"] = callback
            return

        def wndproc(h_wnd, msg, w_param, l_param):
            if msg == self.WM_DROPFILES:
                self._pending_paths.extend(self._read_drop_paths(w_param))
                self._shell32.DragFinish(w_param)
                return 0
            return self._user32.CallWindowProcW(old_proc, h_wnd, msg, w_param, l_param)

        proc = self._wndproc_type(wndproc)
        old_proc = self._user32.SetWindowLongPtrW(
            wintypes.HWND(hwnd),
            self.GWL_WNDPROC,
            ctypes.cast(proc, ctypes.c_void_p),
        )
        self._shell32.DragAcceptFiles(wintypes.HWND(hwnd), True)
        self._hooks[hwnd] = {"proc": proc, "old_proc": old_proc, "callback": callback}

    def poll(self, widget: tk.Misc) -> None:
        if not self._pending_paths:
            return
        paths = self._pending_paths[:]
        self._pending_paths.clear()
        callback = self._hooks.get(int(widget.winfo_id()), {}).get("callback")
        if callback is not None:
            callback(paths)

    def _read_drop_paths(self, drop_handle) -> list[str]:
        count = self._shell32.DragQueryFileW(drop_handle, 0xFFFFFFFF, None, 0)
        paths: list[str] = []
        buffer = ctypes.create_unicode_buffer(32768)
        for index in range(count):
            length = self._shell32.DragQueryFileW(drop_handle, index, buffer, len(buffer))
            if length:
                paths.append(buffer.value)
        return paths


class WhisperTranscriptApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Whisper Transcript")
        self.root.geometry("720x520")
        self.root.minsize(560, 420)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.model_name = tk.StringVar(value=DEFAULT_MODEL)
        self.current_model = DEFAULT_MODEL
        self.status_text = tk.StringVar(value="Ready — drag a video file to begin")
        self.drop_hint = tk.StringVar(value="Drag MP4 files here")

        self.pending_jobs: list[tuple[Path, str, Path]] = []
        self.transcripts: list[dict[str, Path]] = []
        self.active_proc: subprocess.Popen[str] | None = None
        self.current_job: tuple[Path, str, Path] | None = None
        self.job_started_at = 0.0
        self.stderr_log_path: Path | None = None
        self._stderr_handle = None
        self.last_progress_percent = 0.0
        self.shutting_down = False
        self.drop_target = WindowsDropTarget() if sys.platform == "win32" else None

        TRANSCRIPT_DIR.mkdir(exist_ok=True)

        self._build_ui()

        if self.drop_target is not None:
            self.drop_target.register(self.root, self._on_drop)
            self.drop_target.register(self.drop_frame, self._on_drop)
            self._poll_drop_queue()
        else:
            self.drop_hint.set("Drag-and-drop unavailable — use Browse Files")

    def _build_ui(self) -> None:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")

        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            outer,
            text="Whisper Transcript",
            font=("Segoe UI", 18, "bold"),
        )
        header.pack(anchor=tk.W)

        subtitle = ttk.Label(
            outer,
            text="Drop video or audio files here, or use Browse Folder to transcribe every file in a folder.",
            wraplength=640,
        )
        subtitle.pack(anchor=tk.W, pady=(4, 12))

        controls = ttk.Frame(outer)
        controls.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(controls, text="Model:").pack(side=tk.LEFT)
        model_box = ttk.Combobox(
            controls,
            textvariable=self.model_name,
            values=["tiny", "base", "small", "medium", "large", "turbo"],
            state="readonly",
            width=10,
        )
        model_box.pack(side=tk.LEFT, padx=(8, 12))
        model_box.bind("<<ComboboxSelected>>", self._on_model_change)

        ttk.Button(controls, text="Browse Files…", command=self._browse_files).pack(side=tk.LEFT)
        ttk.Button(controls, text="Browse Folder…", command=self._browse_folder).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(controls, text="Open Transcripts Folder", command=self._open_transcripts_folder).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        self.drop_frame = tk.Frame(
            outer,
            bg="#e8eef8",
            highlightbackground="#4f6ef7",
            highlightthickness=2,
            bd=0,
        )
        self.drop_frame.pack(fill=tk.X, pady=(0, 12), ipady=28)

        self.drop_label = tk.Label(
            self.drop_frame,
            textvariable=self.drop_hint,
            bg="#e8eef8",
            fg="#1e293b",
            font=("Segoe UI", 12),
        )
        self.drop_label.pack()

        self.progress_frame = ttk.LabelFrame(outer, text="Transcription Progress", padding=10)
        progress_row = ttk.Frame(self.progress_frame)
        progress_row.pack(fill=tk.X)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            progress_row,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            length=520,
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.percent_label = ttk.Label(
            progress_row,
            text="0%",
            width=5,
            font=("Segoe UI", 12, "bold"),
        )
        self.percent_label.pack(side=tk.LEFT, padx=(10, 0))

        self.progress_label = ttk.Label(self.progress_frame, text="Waiting to start…")
        self.progress_label.pack(anchor=tk.W, pady=(8, 0))

        list_header = ttk.Label(outer, text="Transcripts", font=("Segoe UI", 11, "bold"))
        list_header.pack(anchor=tk.W)

        list_frame = ttk.Frame(outer)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 12))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            activestyle="none",
            font=("Segoe UI", 11),
            selectbackground="#4f6ef7",
            selectforeground="white",
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self._open_selected_transcript)
        self.listbox.bind("<Return>", self._open_selected_transcript)

        hint = ttk.Label(outer, text="Double-click a transcript to open it in Notepad.")
        hint.pack(anchor=tk.W)

        self.status_bar = ttk.Label(outer, textvariable=self.status_text, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(8, 0))

        self._load_existing_transcripts()

    def _poll_drop_queue(self) -> None:
        if self.shutting_down:
            return
        if self.drop_target is not None:
            self.drop_target.poll(self.root)
        self.root.after(100, self._poll_drop_queue)

    def _format_elapsed(self) -> str:
        elapsed = max(0, int(time.time() - self.job_started_at))
        minutes, seconds = divmod(elapsed, 60)
        return f"{minutes}:{seconds:02d}"

    def _set_progress_percent(self, percent: float) -> None:
        clamped = max(self.last_progress_percent, max(0.0, min(100.0, percent)))
        self.last_progress_percent = clamped
        self.progress_var.set(clamped)
        self.percent_label.config(text=f"{int(clamped)}%")

    def _start_progress(self, video_path: Path) -> None:
        self.last_progress_percent = 0.0
        self._set_progress_percent(0)
        self.progress_frame.pack(fill=tk.X, pady=(0, 12), after=self.drop_frame)
        queue_note = f" ({len(self.pending_jobs)} more queued)" if self.pending_jobs else ""
        message = f"Starting {video_path.name}{queue_note}"
        self.progress_label.config(text=message)
        self.status_text.set(message)
        self.root.update_idletasks()

    def _read_stderr_log(self) -> str:
        if self.stderr_log_path is None or not self.stderr_log_path.exists():
            return ""
        try:
            with open(self.stderr_log_path, "r", encoding="utf-8", errors="replace") as log_file:
                return log_file.read()
        except OSError:
            return ""

    def _update_progress(self, video_path: Path) -> None:
        elapsed = self._format_elapsed()
        queue_note = f" ({len(self.pending_jobs)} more queued)" if self.pending_jobs else ""
        whisper_percent = self._parse_whisper_progress(self._read_stderr_log())

        if whisper_percent is not None:
            self.last_progress_percent = max(self.last_progress_percent, float(whisper_percent))
            detail = (
                f"Transcribing {video_path.name} — {int(self.last_progress_percent)}% complete"
                f" — {elapsed} elapsed{queue_note}"
            )
        elif self.last_progress_percent > 0:
            detail = (
                f"Transcribing {video_path.name} — {int(self.last_progress_percent)}% complete"
                f" — {elapsed} elapsed{queue_note}"
            )
        else:
            loading_seconds = time.time() - self.job_started_at
            self.last_progress_percent = min(5.0, loading_seconds * 0.2)
            if loading_seconds < 30:
                detail = f"Loading Whisper model — {elapsed} elapsed{queue_note}"
            else:
                detail = f"Starting transcription — {elapsed} elapsed{queue_note}"

        self._set_progress_percent(self.last_progress_percent)
        self.progress_label.config(text=detail)
        self.status_text.set(detail)

    def _stop_progress(self, message: str | None = None) -> None:
        if self.progress_frame.winfo_ismapped():
            self._set_progress_percent(100)
            self.root.update_idletasks()
        self.progress_frame.pack_forget()
        if message is not None:
            self.status_text.set(message)

    def _open_stderr_log(self) -> None:
        self._close_stderr_log()
        self.stderr_log_path = TRANSCRIPT_DIR / f".whisper-{os.getpid()}-{int(time.time())}.log"
        self._stderr_handle = open(self.stderr_log_path, "w+", encoding="utf-8", errors="replace")

    def _close_stderr_log(self) -> None:
        if self._stderr_handle is not None:
            self._stderr_handle.close()
            self._stderr_handle = None
        if self.stderr_log_path is not None and self.stderr_log_path.exists():
            try:
                self.stderr_log_path.unlink()
            except OSError:
                pass
        self.stderr_log_path = None

    def _read_all_stderr(self) -> str:
        if self._stderr_handle is None:
            return ""
        self._stderr_handle.flush()
        self._stderr_handle.seek(0)
        return self._stderr_handle.read()

    @staticmethod
    def _parse_whisper_progress(text: str) -> int | None:
        matches = re.findall(r"(\d+)%\|", text)
        if matches:
            return min(100, int(matches[-1]))
        return None

    def _load_existing_transcripts(self) -> None:
        for txt in sorted(TRANSCRIPT_DIR.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True):
            self._add_transcript_entry(txt.stem, txt, insert_at_end=False)

    def _add_transcript_entry(self, label: str, transcript_path: Path, insert_at_end: bool = True) -> None:
        if any(item["path"] == transcript_path for item in self.transcripts):
            return
        entry = {"label": label, "path": transcript_path}
        if insert_at_end:
            self.transcripts.append(entry)
            self.listbox.insert(tk.END, label)
        else:
            self.transcripts.insert(0, entry)
            self.listbox.insert(0, label)

    @property
    def processing(self) -> bool:
        return self.active_proc is not None

    def _on_model_change(self, _event=None) -> None:
        if self.processing:
            messagebox.showinfo(
                "Model change",
                "Wait for the current transcription to finish before changing models.",
            )
            self.model_name.set(self.current_model)
            return
        self.current_model = self.model_name.get()
        self.status_text.set(f"Model set to {self.current_model}.")

    @staticmethod
    def _normalize_dropped_path(raw) -> Path:
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", errors="ignore")
        else:
            text = str(raw)
        text = text.rstrip("\x00").strip().strip('"')
        return Path(text)

    @staticmethod
    def _reserve_transcript_path(video_path: Path) -> Path:
        final_path = TRANSCRIPT_DIR / f"{video_path.stem}.txt"
        counter = 2
        while final_path.exists():
            final_path = TRANSCRIPT_DIR / f"{video_path.stem} ({counter}).txt"
            counter += 1
        return final_path

    @staticmethod
    def _media_files_in_folder(folder: Path) -> list[Path]:
        if not folder.is_dir():
            return []
        files = [
            path
            for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
        ]
        return sorted(files, key=lambda path: path.name.lower())

    @staticmethod
    def _expand_media_paths(paths) -> list[Path]:
        expanded: list[Path] = []
        for path in paths:
            if path.is_dir():
                expanded.extend(WhisperTranscriptApp._media_files_in_folder(path))
            else:
                expanded.append(path)
        return expanded

    def _browse_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select video or audio files",
            filetypes=[
                ("Media files", "*.mp4 *.m4v *.mov *.mkv *.webm *.avi *.wav *.mp3 *.m4a"),
                ("All files", "*.*"),
            ],
        )
        self._enqueue_paths(Path(p) for p in paths)

    def _browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select a folder of video or audio files")
        if not folder:
            return
        media_files = self._media_files_in_folder(Path(folder))
        if not media_files:
            messagebox.showinfo(
                "No media files",
                "That folder does not contain any supported video or audio files.",
            )
            return
        self._enqueue_paths(media_files)

    def _on_drop(self, files) -> None:
        paths = [self._normalize_dropped_path(raw) for raw in files]
        self._enqueue_paths(paths)

    def _enqueue_paths(self, paths) -> None:
        added = 0
        for path in self._expand_media_paths(paths):
            if path.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            if not path.is_file():
                continue
            final_path = self._reserve_transcript_path(path)
            self.pending_jobs.append((path, self.current_model, final_path))
            added += 1
        if added:
            if self.processing:
                self.status_text.set(f"Queued {added} more file(s). {len(self.pending_jobs)} waiting.")
            else:
                self.status_text.set(f"Queued {added} file(s). Starting…")
            self._start_next_job()
        elif paths:
            messagebox.showwarning(
                "Unsupported file",
                "Please choose supported media files or a folder containing MP4, MOV, MKV, WAV, or MP3 files.",
            )

    def _whisper_command(self, video_path: Path, model_name: str) -> list[str]:
        return [
            whisper_python(),
            "-m",
            "whisper",
            str(video_path),
            "--model",
            model_name,
            "--output_dir",
            str(TRANSCRIPT_DIR),
            "--output_format",
            "txt",
            "--verbose",
            "False",
        ]

    def _find_transcript_output(self, video_path: Path) -> Path | None:
        expected = TRANSCRIPT_DIR / f"{video_path.stem}.txt"
        if expected.exists():
            return expected

        for candidate in TRANSCRIPT_DIR.glob("*.txt"):
            if candidate.stem == video_path.stem:
                return candidate

        recent: list[Path] = []
        for candidate in TRANSCRIPT_DIR.glob("*.txt"):
            if candidate.stat().st_mtime >= self.job_started_at - 1:
                recent.append(candidate)
        if len(recent) == 1:
            return recent[0]
        return None

    @staticmethod
    def _format_whisper_failure(stderr: str, stdout: str) -> str:
        detail = (stderr or stdout or "").strip()
        if not detail:
            return "Whisper finished but no transcript file was created."
        lines = [line for line in detail.splitlines() if line.strip()]
        for line in reversed(lines):
            if "Skipping " in line or "Error" in line or "error" in line:
                return line.strip()
        return lines[-1] if lines else "Whisper finished but no transcript file was created."

    def _start_next_job(self) -> None:
        if self.shutting_down or self.active_proc is not None or not self.pending_jobs:
            return

        video_path, model_name, final_path = self.pending_jobs.pop(0)
        self.current_job = (video_path, model_name, final_path)
        self.job_started_at = time.time()
        self._open_stderr_log()
        self._start_progress(video_path)

        try:
            self.active_proc = subprocess.Popen(
                self._whisper_command(video_path, model_name),
                stdout=subprocess.DEVNULL,
                stderr=self._stderr_handle,
                env=_subprocess_env(),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
        except Exception as exc:
            self._close_stderr_log()
            self._stop_progress(f"Error on {video_path.name}")
            self._finish_job_with_error(video_path, exc)
            return

        self.root.after(POLL_MS, self._poll_active_process)

    def _poll_active_process(self) -> None:
        if self.shutting_down or self.active_proc is None or self.current_job is None:
            return

        if self.active_proc.poll() is None:
            if self.current_job is not None:
                self._update_progress(self.current_job[0])
            self.root.after(POLL_MS, self._poll_active_process)
            return

        video_path, _model_name, final_path = self.current_job
        stderr = self._read_all_stderr()
        return_code = self.active_proc.returncode
        self.active_proc = None
        self.current_job = None
        self._close_stderr_log()

        if return_code != 0:
            detail = stderr.strip() or "Whisper failed"
            self._stop_progress(f"Error on {video_path.name}")
            self._finish_job_with_error(video_path, RuntimeError(detail[-3000:]))
            return

        output_path = self._find_transcript_output(video_path)
        if output_path is None:
            self._stop_progress(f"Error on {video_path.name}")
            self._finish_job_with_error(
                video_path,
                RuntimeError(self._format_whisper_failure(stderr, "")),
            )
            return

        try:
            if output_path != final_path:
                output_path.rename(final_path)
            self._add_transcript_entry(video_path.name, final_path)
            self._stop_progress(f"Finished {video_path.name}")
        except Exception as exc:
            self._stop_progress(f"Error on {video_path.name}")
            self._finish_job_with_error(video_path, exc)
            return

        self._start_next_job()

    def _finish_job_with_error(self, video_path: Path, exc: Exception) -> None:
        messagebox.showerror("Transcription error", f"Failed to transcribe {video_path.name}:\n{exc}")
        self._close_stderr_log()
        self.active_proc = None
        self.current_job = None
        self._start_next_job()

    def _open_selected_transcript(self, _event=None) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index < 0 or index >= len(self.transcripts):
            return
        transcript_path = self.transcripts[index]["path"]
        if not transcript_path.exists():
            messagebox.showerror("Missing file", f"Transcript not found:\n{transcript_path}")
            return
        subprocess.Popen(["notepad.exe", str(transcript_path)])

    def _open_transcripts_folder(self) -> None:
        subprocess.Popen(["explorer.exe", str(TRANSCRIPT_DIR)])

    def _on_close(self) -> None:
        self.shutting_down = True
        if self.active_proc is not None and self.active_proc.poll() is None:
            self.active_proc.terminate()
        self._close_stderr_log()
        self.root.destroy()


def main() -> int:
    root = tk.Tk()
    WhisperTranscriptApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
