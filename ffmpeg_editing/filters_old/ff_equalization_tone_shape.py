import argparse
import subprocess
from pathlib import Path

# Define effects and their FFmpeg filters
EFFECTS = {
    "highpass": "highpass=f=1000",
    "lowpass": "lowpass=f=500",
    "bandpass": "bandpass=f=1000:w=200",  # Band-pass at 1kHz with 200Hz width
    "notch": "bandreject=f=1000:w=200",  # Notch filter at 1kHz
    "bass_boost": "firequalizer=gain_entry='entry(80, 6)'",
    "treble_boost": "firequalizer=gain_entry='entry(6000, 6)'",
    "midrange_cut": "firequalizer=gain_entry='entry(1000, -6)'",
    "presence_boost": "firequalizer=gain_entry='entry(4000, 5)'",
    "air_boost": "firequalizer=gain_entry='entry(12000, 4)'",
    "crystalizer": "crystalizer=3"
}

def run_effect(audio_file, effect_name, filter_str, outdir):
    """
    Applies one effect to a file and writes the result.
    """
    audio_path = Path(audio_file)
    output_dir = Path(outdir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{audio_path.stem}_{effect_name}{audio_path.suffix}"
    cmd = ["ffmpeg", "-y", "-i", str(audio_path), "-af", filter_str, str(output_file)]
    print(f"Applying {effect_name} effect -> {output_file}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        print(f"FFmpeg failed for {audio_path.name} with effect '{effect_name}'.")
        print(result.stderr)
        return False
    return True

def apply_effects(audio_file, effect, outdir):
    """
    Applies selected effect(s) to an audio file.
    """
    if effect == "all":
        results = [run_effect(audio_file, effect_name, filter_str, outdir=outdir) for effect_name, filter_str in EFFECTS.items()]
        return sum(1 for ok in results if ok), sum(1 for ok in results if not ok)
    if effect in EFFECTS:
        ok = run_effect(audio_file, effect, EFFECTS[effect], outdir=outdir)
        return (1, 0) if ok else (0, 1)
    print("No valid effect provided. Skipping processing.")
    return 0, 0

def process_directory(audio_directory, effect, outdir):
    """
    Processes all WAV files in the given directory and saves the outputs to the specified folder.
    """
    input_dir = Path(audio_directory)
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Audio directory does not exist or is not a directory: {audio_directory}")

    audio_files = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
    if not audio_files:
        print(f"No .wav files found in: {audio_directory}")
        return

    total_success = 0
    total_failures = 0
    for file_path in audio_files:
        print(f"\nProcessing: {file_path}")
        success_count, failure_count = apply_effects(file_path, effect, outdir)
        total_success += success_count
        total_failures += failure_count

    print("\nBatch completed.")
    print(f"Rendered files: {total_success}")
    print(f"Failed renders: {total_failures}")

def parse_arguments():
    """
    Parse command line arguments to get the audio files and output directory.
    """
    parser = argparse.ArgumentParser(description="Apply FFmpeg effects to all WAV files in a directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--effect", type=str, required=False, default="all",
                        choices=["all", "highpass", "lowpass", "bandpass", "notch", "bass_boost", "midrange_cut", "treble_boost", "presence_boost", "air_boost", "crystalizer"],
                        help="Specify the effect to be applied. Default is 'all'.")
    parser.add_argument("--outdir", "--outputdir", dest="outdir", type=str, required=False,
                        help="Path to save processed audio files. Default is inside audiodir as 'processed'.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    output_dir = args.outdir if args.outdir else str(Path(args.audiodir) / "processed")

    process_directory(args.audiodir, args.effect, output_dir)
