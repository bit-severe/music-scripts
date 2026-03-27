import argparse
import subprocess
from pathlib import Path

def apply_ir_reverb(audio_file, ir_file, outdir=None, dry=10.0, wet=5.0):
    """
    Applies impulse response reverb to an audio file using FFmpeg.
    
    Parameters:
    - audio_file (str): Path to the input WAV file.
    - ir_file (str): Path to the impulse response WAV file.
    
    Output:
    - Creates a new file.
    """
    audio_path = Path(audio_file)
    ir_path = Path(ir_file)
    output_parent = Path(outdir) if outdir else audio_path.parent
    output_parent.mkdir(parents=True, exist_ok=True)
    output_file = output_parent / f"{audio_path.stem}_{ir_path.stem}{audio_path.suffix}"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(audio_path),
        "-i", str(ir_path),
        "-filter_complex", f"[0] [1] afir=dry={dry}:wet={wet}",
        str(output_file),
    ]

    print(f"Applying IR reverb: {audio_path} with {ir_path} -> {output_file}")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"FFmpeg failed for {audio_path.name} with IR {ir_path.name}.")
        print(exc.stderr)
        return None

    return str(output_file)

def impulse_responses(file_path, ir_dir, outdir=None, dry=10.0, wet=5.0):
    """
    Applies each impulse response in ir_dir to each WAV file in audio_dir.
    """
    ir_path = Path(ir_dir)
    ir_files = sorted([p for p in ir_path.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])

    if not ir_files:
        print(f"No .wav impulse responses found in: {ir_dir}")
        return 0, 0

    success_count = 0
    failure_count = 0

    for ir_file in ir_files:
        output = apply_ir_reverb(file_path, ir_file, outdir=outdir, dry=dry, wet=wet)
        if output is None:
            failure_count += 1
        else:
            success_count += 1
    return success_count, failure_count

def process_directory(audio_directory, ir_directory, outdir=None, dry=10.0, wet=5.0):
    """
    Processes all WAV files in the given directory.
    """
    audio_path = Path(audio_directory)
    ir_path = Path(ir_directory)

    if not audio_path.exists() or not audio_path.is_dir():
        raise FileNotFoundError(f"Audio directory does not exist or is not a directory: {audio_directory}")
    if not ir_path.exists() or not ir_path.is_dir():
        raise FileNotFoundError(f"Impulse response directory does not exist or is not a directory: {ir_directory}")

    audio_files = sorted([p for p in audio_path.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
    if not audio_files:
        print(f"No .wav files found in: {audio_directory}")
        return

    total_success = 0
    total_failures = 0

    for file_path in audio_files:
        print(f"\nProcessing: {file_path}")
        success_count, failure_count = impulse_responses(
            file_path, ir_directory, outdir=outdir, dry=dry, wet=wet
        )
        total_success += success_count
        total_failures += failure_count

    print("\nBatch completed.")
    print(f"Generated files: {total_success}")
    print(f"Failed renders: {total_failures}")

def parse_arguments():
    """
    Parse command line arguments to get the audio files and IR files.
    """
    parser = argparse.ArgumentParser(description="Apply IR convolution reverb with FFmpeg to WAV files.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--irdir", type=str, required=True, help="Path to impulse response files.")
    parser.add_argument("--outdir", type=str, default=None, help="Optional directory for rendered files.")
    parser.add_argument("--dry", type=float, default=10.0, help="Dry signal amount for afir filter.")
    parser.add_argument("--wet", type=float, default=5.0, help="Wet signal amount for afir filter.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    process_directory(args.audiodir, args.irdir, outdir=args.outdir, dry=args.dry, wet=args.wet)
