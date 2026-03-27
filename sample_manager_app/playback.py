import subprocess
import time


_preview_process = None
_playback_start_monotonic = None
_playback_offset_seconds = 0.0


def stop_audio():
    global _preview_process, _playback_start_monotonic, _playback_offset_seconds
    if _preview_process is None:
        return
    try:
        _preview_process.terminate()
    except Exception:
        pass
    _preview_process = None
    _playback_start_monotonic = None
    _playback_offset_seconds = 0.0


def preview_audio(file_path, start_seconds=0.0):
    global _preview_process, _playback_start_monotonic, _playback_offset_seconds
    stop_audio()
    start_seconds = max(0.0, float(start_seconds))
    cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", "-ss", str(start_seconds), str(file_path)]
    kwargs = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.PIPE,
    }
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    _preview_process = subprocess.Popen(cmd, **kwargs)
    _playback_start_monotonic = time.monotonic()
    _playback_offset_seconds = start_seconds


def get_playback_position():
    if _preview_process is None:
        return None
    if _preview_process.poll() is not None:
        return None
    if _playback_start_monotonic is None:
        return None
    return _playback_offset_seconds + (time.monotonic() - _playback_start_monotonic)

