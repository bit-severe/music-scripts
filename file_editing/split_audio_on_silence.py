import os
import re
import subprocess
import zipfile
import argparse

def detect_silences(audio_file):
    """
    Runs FFmpeg with the silencedetect filter on the given audio file.
    Returns two lists: one for silence start times and one for silence end times.
    """
    cmd = [
        'ffmpeg', '-i', audio_file,
        '-af', 'silencedetect=noise=-35dB:d=0.4',
        '-f', 'null', '-'
    ]
    process = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    stderr_output = process.stderr

    # Regular expressions to extract silence start and end times
    silence_start_regex = re.compile(r"silence_start: (\d+\.\d+)")
    silence_end_regex = re.compile(r"silence_end: (\d+\.\d+)")

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
        'ffprobe', '-i', audio_file,
        '-show_entries', 'format=duration',
        '-v', 'quiet', '-of', 'csv=p=0'
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError("Could not determine duration of the audio file.")

def split_audio(audio_file, silence_starts, silence_ends):
    """
    Given an audio file and lists of silence start/end times,
    compute the non-silent segments and use FFmpeg to extract them.
    Returns a list of generated segment filenames.
    """
    duration = get_audio_duration(audio_file)
    segments = []
    segment_files = []

    current_start = 0.0

    for i in range(len(silence_starts)):
        seg_end = silence_starts[i]
        if seg_end - current_start > 0.1:
            segments.append((current_start, seg_end))
        if i < len(silence_ends):
            current_start = silence_ends[i]

    if duration - current_start > 0.1:
        segments.append((current_start, duration))

    base, ext = os.path.splitext(audio_file)
    for idx, (start, end) in enumerate(segments, start=1):
        output_file = f"{base}_segment_{idx}{ext}"
        cmd = [
            'ffmpeg', '-y', '-i', audio_file,
            '-ss', str(start), '-to', str(end),
            '-c', 'copy', output_file
        ]
        print(f"Creating segment {idx}: {start:.2f} to {end:.2f} seconds as {output_file}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        segment_files.append(output_file)
    
    return segment_files

def compress_segments(original_audio, segment_files):
    """
    Compresses the generated audio segments into a ZIP file.
    """
    zip_name = f"{os.path.splitext(original_audio)[0]}_chopped.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in segment_files:
            zipf.write(file, os.path.basename(file))
            os.remove(file)  # Remove the segment file after zipping
    
    print(f"Created ZIP archive: {zip_name}")

def process_directory(directory):
    """
    Processes all WAV files in the given directory.
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(directory, filename)
            print(f"\nProcessing file: {file_path}")

            try:
                silence_starts, silence_ends = detect_silences(file_path)
                print("Detected silence starts at:", silence_starts)
                print("Detected silence ends at:", silence_ends)

                segment_files = split_audio(file_path, silence_starts, silence_ends)
                print(f"Created {len(segment_files)} segments for {filename}")

                if segment_files:
                    compress_segments(file_path, segment_files)

            except Exception as e:
                print(f"Error processing {filename}: {e}")

def parse_arguments():
    """
    Parse command line arguments to get the audio files and IR files.
    """
    parser = argparse.ArgumentParser(description="Split on silence audiois of the given directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    return parser.parse_args()                 

if __name__ == '__main__':
    args = parse_arguments()
    process_directory(args.audiodir)
