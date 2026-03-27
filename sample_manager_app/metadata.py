from mutagen.id3 import COMM, ID3NoHeaderError, TCON, TIT2, TPE1, TPE2
from mutagen.wave import WAVE


def frame_text(frame):
    if frame is None:
        return ""
    value = getattr(frame, "text", "")
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def write_wav_metadata(path, title, source, author, effect, modules, key_params, tags, notes):
    audio = WAVE(str(path))
    try:
        if audio.tags is None:
            audio.add_tags()
    except ID3NoHeaderError:
        audio.add_tags()

    comment_parts = []
    if effect and effect != "none":
        comment_parts.append(f"Effect: {effect}")
    if modules:
        comment_parts.append(f"Modules: {modules}")
    if key_params:
        comment_parts.append(f"Key Params: {key_params}")
    if notes:
        comment_parts.append(f"Notes: {notes}")
    comment_text = " | ".join(comment_parts)

    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=source))
    audio.tags.add(TPE2(encoding=3, text=author))
    audio.tags.add(TCON(encoding=3, text=tags or ""))
    audio.tags.add(COMM(encoding=3, lang="eng", desc="Notes", text=comment_text))
    audio.save()


def read_wav_metadata(path):
    audio = WAVE(str(path))
    tags = audio.tags
    if not tags:
        return None
    return {
        "title": frame_text(tags.get("TIT2")),
        "source": frame_text(tags.get("TPE1")),
        "author": frame_text(tags.get("TPE2")),
        "tags": frame_text(tags.get("TCON")),
        "notes": frame_text(tags.get("COMM::eng")) or frame_text(tags.get("COMM")),
    }

