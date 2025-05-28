import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import date
import simpleaudio as sa

MODULE_OPTIONS = [
    "Granul~", "RingMod", "SpectralDelay", "Glitch", "Delay", "Distortion",
    "PitchShift", "TimeStretch", "Reverb", "BitCrusher"
]

def preview_audio(path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
    except Exception as e:
        messagebox.showerror("Playback Error", str(e))

def save_sample_data():
    filepath = file_path_var.get()
    out_folder = folder_path_var.get()

    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Select a valid audio file.")
        return
    if not out_folder or not os.path.isdir(out_folder):
        messagebox.showerror("Error", "Select a valid output folder.")
        return

    src = source_entry.get().strip()
    selected_modules = [mod for mod, var in module_vars.items() if var.get()]
    if not selected_modules:
        messagebox.showerror("Error", "Select at least one module.")
        return

    key_params = params_entry.get().strip()
    tags = tags_entry.get().strip()
    ideas = ideas_entry.get().strip()

    modules_tag = "_".join([m.lower() for m in selected_modules])
    new_name = f"{src}__{modules_tag}.wav"
    new_path = os.path.join(out_folder, new_name)

    # Move and rename file
    os.rename(filepath, new_path)

    # Append to log
    log_path = os.path.join(out_folder, "sample_log.txt")
    entry = f"""---
Filename: {new_name}
Source: {src}
Modules: {', '.join(selected_modules)}
Key Params: {key_params}
Tags: {tags}
Ideas: {ideas}
Date: {date.today().isoformat()}
---\n"""

    with open(log_path, "a") as logfile:
        logfile.write(entry)

    messagebox.showinfo("Success", f"Saved and logged:\n{new_name}")

def browse_file():
    path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if path:
        file_path_var.set(path)

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path_var.set(folder)

def set_widget_colors(widget, bg, fg):
    try:
        widget.configure(bg=bg, fg=fg)
    except:
        pass
    for child in widget.winfo_children():
        set_widget_colors(child, bg, fg)

def toggle_dark_mode():
    if dark_mode_var.get():
        bg, fg = "#2e2e2e", "#f0f0f0"
    else:
        bg, fg = "SystemButtonFace", "black"
    root.configure(bg=bg)
    set_widget_colors(root, bg, fg)

# === GUI ===
root = tk.Tk()
root.title("Sample Logger")

file_path_var = tk.StringVar()
folder_path_var = tk.StringVar()
dark_mode_var = tk.BooleanVar()

tk.Label(root, text="Input .wav file:").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=file_path_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)
tk.Button(root, text="▶ Play", command=lambda: preview_audio(file_path_var.get())).grid(row=0, column=3)

tk.Label(root, text="Output folder:").grid(row=1, column=0, sticky="w")
tk.Entry(root, textvariable=folder_path_var, width=50).grid(row=1, column=1)
tk.Button(root, text="Select Folder", command=browse_folder).grid(row=1, column=2)

tk.Label(root, text="Source (e.g. C_chord_1):").grid(row=2, column=0, sticky="w")
source_entry = tk.Entry(root, width=30)
source_entry.grid(row=2, column=1, sticky="w")

tk.Label(root, text="Modules used:").grid(row=3, column=0, sticky="nw")
module_vars = {}
mod_frame = tk.Frame(root)
mod_frame.grid(row=3, column=1, columnspan=3, sticky="w")
for i, mod in enumerate(MODULE_OPTIONS):
    var = tk.BooleanVar()
    cb = tk.Checkbutton(mod_frame, text=mod, variable=var)
    cb.grid(row=i // 3, column=i % 3, sticky="w")
    module_vars[mod] = var

tk.Label(root, text="Key Params:").grid(row=4, column=0, sticky="w")
params_entry = tk.Entry(root, width=50)
params_entry.grid(row=4, column=1, columnspan=3, sticky="w")

tk.Label(root, text="Tags:").grid(row=5, column=0, sticky="w")
tags_entry = tk.Entry(root, width=50)
tags_entry.grid(row=5, column=1, columnspan=3, sticky="w")

tk.Label(root, text="Ideas:").grid(row=6, column=0, sticky="w")
ideas_entry = tk.Entry(root, width=50)
ideas_entry.grid(row=6, column=1, columnspan=3, sticky="w")

tk.Button(root, text="Log Sample", command=save_sample_data).grid(row=7, column=1, pady=10)
tk.Checkbutton(root, text="Dark Mode", variable=dark_mode_var, command=toggle_dark_mode).grid(row=7, column=2)

root.mainloop()
