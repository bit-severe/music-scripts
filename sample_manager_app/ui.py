import tkinter as tk
from datetime import date
from pathlib import Path
import subprocess
from tkinter import filedialog, messagebox, ttk

from .effects import available_effects, effect_defaults, effect_hints, render_with_effect
from .metadata import read_wav_metadata, write_wav_metadata
from .playback import get_playback_position, preview_audio, stop_audio


def sanitize_filename(value):
    clean = "".join(c if c.isalnum() or c in ("_", "-", " ") else "_" for c in value.strip())
    clean = "_".join(clean.split())
    return clean or "sample"


def ensure_unique_path(path):
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def format_seconds(value):
    total = max(0.0, float(value))
    minutes = int(total // 60)
    seconds = total - (minutes * 60)
    return f"{minutes:02d}:{seconds:05.2f}"


class SampleManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sample Manager")
        self.style = ttk.Style(root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.file_path_var = tk.StringVar()
        self.folder_path_var = tk.StringVar()
        self.dark_mode_var = tk.BooleanVar()
        self.effect_var = tk.StringVar(value="none")
        self.effect_param_vars = {}

        self.auto_output_name = ""
        self.default_outdir_hint_var = tk.StringVar(value="")
        self.default_name_hint_var = tk.StringVar(value="")
        self.waveform_duration_var = tk.StringVar(value="Duration: --:--.--")
        self.waveform_cursor_var = tk.StringVar(value="Cursor: --:--.--")
        self.waveform_status_var = tk.StringVar(value="Waveform: Select a WAV file.")
        self.waveform_samples = []
        self.waveform_duration = 0.0
        self.waveform_cursor_line = None
        self.waveform_playback_line = None
        self.waveform_cache = {}
        self.current_waveform_path = None
        self.current_bg = "SystemButtonFace"
        self.current_fg = "black"

        self._build_ui()
        self.toggle_dark_mode()
        self._schedule_playback_pin_update()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        tk.Label(self.root, text="Input .wav file:").grid(row=0, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.file_path_var, width=50).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2)
        tk.Button(self.root, text="▶ Play", command=self.on_play).grid(row=0, column=3)
        tk.Button(self.root, text="■ Stop", command=stop_audio).grid(row=0, column=4)
        tk.Button(self.root, text="View Metadata", command=self.on_view_metadata).grid(row=0, column=5)

        tk.Label(self.root, text="Output folder:").grid(row=1, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.folder_path_var, width=50).grid(row=1, column=1)
        tk.Button(self.root, text="Select Folder", command=self.browse_folder).grid(row=1, column=2)
        tk.Label(self.root, textvariable=self.default_outdir_hint_var).grid(row=1, column=3, columnspan=3, sticky="w")

        tk.Label(self.root, text="Author (optional):").grid(row=2, column=0, sticky="w")
        self.author_entry = tk.Entry(self.root, width=30)
        self.author_entry.grid(row=2, column=1, sticky="w")

        tk.Label(self.root, text="Output file name:").grid(row=3, column=0, sticky="w")
        self.output_name_entry = tk.Entry(self.root, width=30)
        self.output_name_entry.grid(row=3, column=1, sticky="w")
        tk.Label(self.root, textvariable=self.default_name_hint_var).grid(row=3, column=2, columnspan=4, sticky="w")

        tk.Label(self.root, text="FFmpeg effect:").grid(row=4, column=0, sticky="w")
        effect_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.effect_var,
            values=available_effects(),
            state="readonly",
            width=28,
        )
        effect_dropdown.grid(row=4, column=1, sticky="w")
        effect_dropdown.bind("<<ComboboxSelected>>", self.on_effect_changed)

        tk.Label(self.root, text="Effect params:").grid(row=5, column=0, sticky="nw")
        self.effect_params_frame = ttk.Frame(self.root)
        self.effect_params_frame.grid(row=5, column=1, columnspan=3, sticky="w")

        tk.Label(self.root, text="Key Params:").grid(row=6, column=0, sticky="w")
        self.params_entry = tk.Entry(self.root, width=50)
        self.params_entry.grid(row=6, column=1, columnspan=3, sticky="w")

        tk.Label(self.root, text="Tags:").grid(row=7, column=0, sticky="w")
        self.tags_entry = tk.Entry(self.root, width=50)
        self.tags_entry.grid(row=7, column=1, columnspan=3, sticky="w")

        tk.Label(self.root, text="Notes:").grid(row=8, column=0, sticky="w")
        self.notes_entry = tk.Entry(self.root, width=50)
        self.notes_entry.grid(row=8, column=1, columnspan=3, sticky="w")

        tk.Button(self.root, text="Process + Save", command=self.save_sample_data).grid(row=9, column=1, pady=10)
        ttk.Checkbutton(
            self.root,
            text="Dark Mode",
            variable=self.dark_mode_var,
            command=self.toggle_dark_mode,
            style="App.TCheckbutton",
        ).grid(row=9, column=2)

        waveform_frame = ttk.Frame(self.root)
        waveform_frame.grid(row=10, column=0, columnspan=7, sticky="ew", padx=4, pady=(8, 4))
        tk.Label(waveform_frame, textvariable=self.waveform_status_var).grid(row=0, column=0, sticky="w")
        tk.Label(waveform_frame, textvariable=self.waveform_duration_var).grid(row=0, column=1, sticky="w", padx=(20, 0))
        tk.Label(waveform_frame, textvariable=self.waveform_cursor_var).grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.waveform_canvas = tk.Canvas(waveform_frame, width=980, height=220)
        self.waveform_canvas.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.waveform_canvas.bind("<Motion>", self.on_waveform_motion)
        self.waveform_canvas.bind("<Button-1>", self.on_waveform_click)

        self.refresh_effect_param_fields()

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            self.file_path_var.set(path)
            selected = Path(path)
            default_outdir = selected.parent / f"{selected.stem}_ffmpeg_edits"
            default_outdir.mkdir(parents=True, exist_ok=True)
            self.folder_path_var.set(str(default_outdir))
            self.default_outdir_hint_var.set(f"Default: {default_outdir}")
            self.update_default_output_name(force=True)
            self.load_waveform(selected)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path_var.set(folder)
            self.default_outdir_hint_var.set(f"Default: {folder}")

    def on_effect_changed(self, _event=None):
        self.refresh_effect_param_fields()
        self.update_default_output_name(force=False)

    def update_default_output_name(self, force=False):
        file_path = Path(self.file_path_var.get().strip()) if self.file_path_var.get().strip() else None
        if not file_path or not file_path.exists():
            return
        current_name = self.output_name_entry.get().strip()
        if not force and current_name and current_name != self.auto_output_name:
            # User has manually changed the output name; preserve it.
            return

        effect = self.effect_var.get().strip().lower() or "none"
        base_name = sanitize_filename(f"{file_path.stem}_{effect}")
        out_folder = Path(self.folder_path_var.get().strip()) if self.folder_path_var.get().strip() else file_path.parent
        out_folder.mkdir(parents=True, exist_ok=True)

        candidate = out_folder / f"{base_name}.wav"
        unique = ensure_unique_path(candidate)
        auto_name = unique.stem

        self.output_name_entry.delete(0, tk.END)
        self.output_name_entry.insert(0, auto_name)
        self.auto_output_name = auto_name
        self.default_name_hint_var.set(f"Default: {auto_name}")

    def refresh_effect_param_fields(self):
        for child in self.effect_params_frame.winfo_children():
            child.destroy()
        self.effect_param_vars = {}

        effect = self.effect_var.get().strip().lower()
        defaults = effect_defaults(effect)
        hints = effect_hints(effect)
        if not defaults:
            tk.Label(self.effect_params_frame, text="No parameters for this effect.").grid(row=0, column=0, sticky="w")
            return

        for idx, (key, default_value) in enumerate(defaults.items()):
            tk.Label(self.effect_params_frame, text=f"{key}:").grid(row=idx, column=0, sticky="w", padx=(0, 6), pady=1)
            var = tk.StringVar(value=str(default_value))
            tk.Entry(self.effect_params_frame, textvariable=var, width=24).grid(row=idx, column=1, sticky="w", pady=1)
            hint = hints.get(key, "")
            if hint:
                tk.Label(self.effect_params_frame, text=hint).grid(row=idx, column=2, sticky="w", padx=(8, 0), pady=1)
            self.effect_param_vars[key] = var
        # Ensure newly created dynamic controls receive the current theme.
        self.set_widget_colors(self.effect_params_frame, self.current_bg, self.current_fg)

    def on_play(self, start_seconds=0.0):
        path = self.file_path_var.get().strip()
        file_path = Path(path)
        if not path or not file_path.exists() or file_path.suffix.lower() != ".wav":
            messagebox.showerror("Playback Error", "Select a valid .wav file first.")
            return
        try:
            preview_audio(file_path, start_seconds=start_seconds)
        except FileNotFoundError:
            messagebox.showerror("Playback Error", "ffplay was not found. Install FFmpeg and add ffplay to PATH.")
        except Exception as exc:
            messagebox.showerror("Playback Error", str(exc))

    def on_view_metadata(self):
        path = self.file_path_var.get().strip()
        file_path = Path(path)
        if not path or not file_path.exists() or file_path.suffix.lower() != ".wav":
            messagebox.showerror("Metadata Error", "Select a valid .wav file first.")
            return
        try:
            info = read_wav_metadata(file_path)
            if not info:
                messagebox.showinfo("Embedded Metadata", "No embedded metadata found in this WAV file.")
                return
            msg = (
                f"File: {file_path.name}\n"
                f"Title: {info['title']}\n"
                f"Source: {info['source']}\n"
                f"Author: {info['author']}\n"
                f"Tags: {info['tags']}\n"
                f"Notes: {info['notes']}"
            )
            messagebox.showinfo("Embedded Metadata", msg)
        except Exception as exc:
            messagebox.showerror("Metadata Error", str(exc))

    def load_waveform(self, file_path):
        try:
            cache_key = self._waveform_cache_key(file_path)
            if cache_key in self.waveform_cache:
                samples, duration = self.waveform_cache[cache_key]
            else:
                samples, duration = self._decode_samples_with_ffmpeg(file_path)
                self.waveform_cache[cache_key] = (samples, duration)
            self.waveform_samples = samples
            self.waveform_duration = duration
            self.current_waveform_path = file_path
            self.waveform_duration_var.set(f"Duration: {format_seconds(duration)}")
            self.waveform_cursor_var.set("Cursor: 00:00.00")
            self.waveform_status_var.set(f"Waveform: {file_path.name}")
            self.draw_waveform()
        except Exception as exc:
            self.waveform_samples = []
            self.waveform_duration = 0.0
            self.current_waveform_path = None
            self.waveform_status_var.set(f"Waveform: {exc}")
            self.waveform_duration_var.set("Duration: --:--.--")
            self.waveform_cursor_var.set("Cursor: --:--.--")
            self.draw_waveform()

    def _waveform_cache_key(self, file_path):
        stat = file_path.stat()
        return (str(file_path.resolve()), stat.st_mtime_ns, stat.st_size)

    def _decode_samples_with_ffmpeg(self, file_path):
        # Decode to mono 16-bit PCM for display so non-16-bit WAVs are supported.
        decode_cmd = [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(file_path),
            "-f",
            "s16le",
            "-ac",
            "1",
            "-ar",
            "22050",
            "pipe:1",
        ]
        decode_result = subprocess.run(
            decode_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if decode_result.returncode != 0:
            raise RuntimeError(f"Could not decode waveform: {decode_result.stderr.decode(errors='ignore').strip()}")
        raw = decode_result.stdout
        if len(raw) < 2:
            raise RuntimeError("Decoded waveform is empty.")
        samples = [
            int.from_bytes(raw[i : i + 2], byteorder="little", signed=True)
            for i in range(0, len(raw) - 1, 2)
        ]
        duration = len(samples) / 22050.0
        return samples, duration

    def draw_waveform(self):
        self.waveform_canvas.delete("all")
        width = max(1, int(self.waveform_canvas.winfo_width()))
        height = max(1, int(self.waveform_canvas.winfo_height()))
        center_y = height // 2
        self.waveform_canvas.create_line(0, center_y, width, center_y)
        if not self.waveform_samples:
            self.waveform_canvas.create_text(12, 12, text="No waveform loaded", anchor="nw")
            self.waveform_cursor_line = None
            self.waveform_playback_line = None
            return
        max_amp = max(abs(v) for v in self.waveform_samples) or 1
        step = max(1, len(self.waveform_samples) // max(1, width - 1))
        sampled = self.waveform_samples[::step]
        if len(sampled) < 2:
            self.waveform_canvas.create_text(12, 12, text="Waveform too short", anchor="nw")
            self.waveform_cursor_line = None
            return
        last_x = 0
        last_y = center_y
        for x, amp in enumerate(sampled[:width]):
            y = center_y - int((amp / max_amp) * (height * 0.45))
            self.waveform_canvas.create_line(last_x, last_y, x, y)
            last_x, last_y = x, y
        self.waveform_cursor_line = self.waveform_canvas.create_line(0, 0, 0, height, dash=(3, 2))
        self.waveform_playback_line = self.waveform_canvas.create_line(0, 0, 0, height, fill="#ff5555")

    def _update_waveform_cursor(self, event_x):
        width = max(1, int(self.waveform_canvas.winfo_width()))
        x = max(0, min(width - 1, int(event_x)))
        if self.waveform_cursor_line is not None:
            self.waveform_canvas.coords(self.waveform_cursor_line, x, 0, x, int(self.waveform_canvas.winfo_height()))
        if self.waveform_duration > 0:
            t = (x / max(1, width - 1)) * self.waveform_duration
            self.waveform_cursor_var.set(f"Cursor: {format_seconds(t)}")

    def on_waveform_motion(self, event):
        self._update_waveform_cursor(event.x)

    def on_waveform_click(self, event):
        self._update_waveform_cursor(event.x)
        if self.waveform_duration <= 0:
            return
        width = max(1, int(self.waveform_canvas.winfo_width()))
        click_x = max(0, min(width - 1, int(event.x)))
        t = (click_x / max(1, width - 1)) * self.waveform_duration
        self.on_play(start_seconds=t)

    def _update_playback_pin(self):
        if self.waveform_playback_line is None or self.waveform_duration <= 0:
            return
        position = get_playback_position()
        if position is None:
            return
        width = max(1, int(self.waveform_canvas.winfo_width()))
        clamped = max(0.0, min(self.waveform_duration, position))
        x = int((clamped / self.waveform_duration) * max(1, width - 1))
        self.waveform_canvas.coords(self.waveform_playback_line, x, 0, x, int(self.waveform_canvas.winfo_height()))
        self.waveform_cursor_var.set(f"Cursor: {format_seconds(clamped)}")

    def _schedule_playback_pin_update(self):
        self._update_playback_pin()
        self.root.after(50, self._schedule_playback_pin_update)

    def save_sample_data(self):
        filepath = Path(self.file_path_var.get())
        out_folder = Path(self.folder_path_var.get())
        if not filepath.exists() or filepath.suffix.lower() != ".wav":
            messagebox.showerror("Error", "Select a valid audio file.")
            return
        if not str(out_folder).strip():
            messagebox.showerror("Error", "Select a valid output folder.")
            return
        out_folder.mkdir(parents=True, exist_ok=True)

        author = self.author_entry.get().strip()
        output_name = self.output_name_entry.get().strip()
        effect = self.effect_var.get().strip().lower()
        if not output_name:
            messagebox.showerror("Error", "Output file name cannot be empty.")
            return

        effect_params = {key: var.get().strip() for key, var in self.effect_param_vars.items()}

        safe_name = sanitize_filename(output_name)
        new_path = ensure_unique_path(out_folder / f"{safe_name}.wav")
        new_name = new_path.name

        key_params = self.params_entry.get().strip()
        tags = self.tags_entry.get().strip()
        notes = self.notes_entry.get().strip()

        log_path = out_folder / "sample_log.txt"
        entry = f"""---
Filename: {new_name}
Author: {author}
Effect: {effect}
Effect Params: {effect_params}
Key Params: {key_params}
Tags: {tags}
Notes: {notes}
Date: {date.today().isoformat()}
---\n"""
        try:
            render_with_effect(filepath, new_path, effect, effect_params)
            write_wav_metadata(
                new_path,
                title=new_name,
                source="",
                author=author,
                effect=f"{effect} {effect_params}".strip(),
                modules="",
                key_params=key_params,
                tags=tags,
                notes=notes,
            )
            with log_path.open("a", encoding="utf-8") as logfile:
                logfile.write(entry)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save sample data:\n{exc}")
            return
        messagebox.showinfo("Success", f"Processed, saved, and logged:\n{new_name}")

    def set_widget_colors(self, widget, bg, fg):
        widget_class = widget.winfo_class()
        try:
            if widget_class == "Entry":
                widget.configure(
                    bg=bg,
                    fg=fg,
                    insertbackground=fg,
                    disabledbackground=bg,
                    disabledforeground=fg,
                    highlightbackground=bg,
                    highlightcolor=fg,
                )
            elif widget_class == "Button":
                widget.configure(
                    bg=bg,
                    fg=fg,
                    activebackground=bg,
                    activeforeground=fg,
                    highlightbackground=bg,
                    highlightcolor=bg,
                )
            elif widget_class in ("Frame", "Label"):
                widget.configure(bg=bg, fg=fg, highlightbackground=bg, highlightcolor=bg)
            else:
                widget.configure(bg=bg, fg=fg)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self.set_widget_colors(child, bg, fg)

    def apply_ttk_theme(self, bg, fg):
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure(
            "App.TCheckbutton",
            background=bg,
            foreground=fg,
            focuscolor=bg,
            borderwidth=0,
            relief="flat",
        )
        self.style.map(
            "App.TCheckbutton",
            background=[("active", bg), ("selected", bg)],
            foreground=[("active", fg), ("selected", fg)],
        )

    def toggle_dark_mode(self):
        if self.dark_mode_var.get():
            bg, fg = "#2e2e2e", "#f0f0f0"
        else:
            bg, fg = "SystemButtonFace", "black"
        self.current_bg = bg
        self.current_fg = fg
        self.root.option_add("*selectColor", bg)
        self.apply_ttk_theme(bg, fg)
        self.root.configure(bg=bg)
        self.set_widget_colors(self.root, bg, fg)

    def on_close(self):
        stop_audio()
        self.root.destroy()


def run():
    root = tk.Tk()
    SampleManagerApp(root)
    root.mainloop()

