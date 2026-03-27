import re
import subprocess
import zipfile
import argparse
from pathlib import Path

def detect_silences(audio_file, noise_db=-35, min_silence_duration=0.4):
    """
    Runs FFmpeg with the silencedetect filter on the given audio file.
    Returns two lists: one for silence start times and one for silence end times.
    """
    cmd = [
        "ffmpeg",
        "-i", str(audio_file),
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence_duration}",
        "-f", "null", "-",
    ]
    process = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stderr_output = process.stderr

    # Regular expressions to extract silence start and end times
    silence_start_regex = re.compile(r"silence_start: (\d+(?:\.\d+)?)")
    silence_end_regex = re.compile(r"silence_end: (\d+(?:\.\d+)?)")

    silence_starts = [float(match.group(1))
                      for match in silence_start_regex.finditer(stderr_output)]
    silence_ends = [float(match.group(1))
                    for match in silence_end_regex.finditer(stderr_output)]

    return silence_starts, silence_ends

def get_audio_duration(audio_file):
    """
    Uses ffprobe to get the duration of the audio file.
    """
    cmd = [
        "ffprobe",
        "-i", str(audio_file),
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=p=0",
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {audio_file}: {result.stderr.strip()}")
    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError("Could not determine duration of the audio file.")

def split_audio(audio_file, silence_starts, silence_ends, outdir=None, min_segment_duration=0.1):
    """
    Given an audio file and lists of silence start/end times,
    compute the non-silent segments and use FFmpeg to extract them.
    Returns a list of generated segment filenames.
    """
    audio_path = Path(audio_file)
    output_dir = Path(outdir) if outdir else audio_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    duration = get_audio_duration(audio_path)
    segments = []
    segment_files = []

    current_start = 0.0

    for i in range(len(silence_starts)):
        seg_end = silence_starts[i]
        if seg_end - current_start > min_segment_duration:
            segments.append((current_start, seg_end))
        if i < len(silence_ends):
            current_start = silence_ends[i]

    if duration - current_start > min_segment_duration:
        segments.append((current_start, duration))

    if not segments:
        return segment_files

    for idx, (start, end) in enumerate(segments, start=1):
        output_file = output_dir / f"{audio_path.stem}_segment_{idx}{audio_path.suffix}"
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(audio_path),
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            str(output_file),
        ]
        print(f"Creating segment {idx}: {start:.2f} to {end:.2f} seconds as {output_file}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode != 0:
            print(f"FFmpeg segment creation failed for {output_file.name}")
            print(result.stderr)
            continue
        segment_files.append(str(output_file))
    
    return segment_files

def compress_segments(original_audio, segment_files, delete_segments=True):
    """
    Compresses the generated audio segments into a ZIP file.
    """
    original_path = Path(original_audio)
    zip_name = original_path.parent / f"{original_path.stem}_chopped.zip"
    
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in segment_files:
            file_path = Path(file)
            zipf.write(file_path, file_path.name)
            if delete_segments and file_path.exists():
                file_path.unlink()  # Remove the segment file after zipping
    
    print(f"Created ZIP archive: {zip_name}")

def process_directory(
    directory,
    outdir=None,
    noise_db=-35,
    min_silence_duration=0.4,
    min_segment_duration=0.1,
    zip_segments=True,
    keep_segments=False,
):
    """
    Processes all WAV files in the given directory.
    """
    input_dir = Path(directory)
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Audio directory does not exist or is not a directory: {directory}")

    audio_files = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
    if not audio_files:
        print(f"No .wav files found in: {directory}")
        return

    processed_count = 0
    failed_count = 0
    created_segments_total = 0

    for file_path in audio_files:
        filename = file_path.name
        if filename.lower().endswith(".wav"):
            print(f"\nProcessing file: {file_path}")

            try:
                silence_starts, silence_ends = detect_silences(
                    file_path,
                    noise_db=noise_db,
                    min_silence_duration=min_silence_duration,
                )
                print("Detected silence starts at:", silence_starts)
                print("Detected silence ends at:", silence_ends)

                segment_files = split_audio(
                    file_path,
                    silence_starts,
                    silence_ends,
                    outdir=outdir,
                    min_segment_duration=min_segment_duration,
                )
                print(f"Created {len(segment_files)} segments for {filename}")
                created_segments_total += len(segment_files)

                if segment_files and zip_segments:
                    compress_segments(file_path, segment_files, delete_segments=not keep_segments)
                processed_count += 1

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                failed_count += 1

    print("\nBatch completed.")
    print(f"Processed files: {processed_count}")
    print(f"Failed files: {failed_count}")
    print(f"Total segments created: {created_segments_total}")

def parse_arguments():
    """
    Parse command line arguments to get the audio files and IR files.
    """
    parser = argparse.ArgumentParser(description="Split WAV files on silence using FFmpeg.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--outdir", type=str, default=None, help="Optional directory for output segments.")
    parser.add_argument("--noise-db", type=float, default=-35, help="Silence threshold in dB for silencedetect.")
    parser.add_argument("--silence-dur", type=float, default=0.4, help="Minimum silence duration in seconds.")
    parser.add_argument("--min-segment-dur", type=float, default=0.1, help="Minimum output segment duration in seconds.")
    parser.add_argument("--no-zip", action="store_true", help="Do not zip generated segments.")
    parser.add_argument("--keep-segments", action="store_true", help="Keep segment files after creating ZIP.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    process_directory(
        args.audiodir,
        outdir=args.outdir,
        noise_db=args.noise_db,
        min_silence_duration=args.silence_dur,
        min_segment_duration=args.min_segment_dur,
        zip_segments=not args.no_zip,
        keep_segments=args.keep_segments,
    )
