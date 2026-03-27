import argparse
import subprocess
from pathlib import Path

# Define effects and their FFmpeg filters
EFFECTS = {
    "distortion": "acrusher=level_in=3:level_out=1:bits=8:mode=log",
    "bitcrusher": "acrusher=bits=4:mode=log:aa=0.5:samples=64",
    "asoftclip": "type=hard:threshold=1:output=1:param=1:oversample=1"
}

def run_effect(audio_file, effect_name, filter_str, outdir=None):
    audio_path = Path(audio_file)
    output_parent = Path(outdir) if outdir else audio_path.parent
    output_parent.mkdir(parents=True, exist_ok=True)
    output_file = output_parent / f"{audio_path.stem}_{effect_name}{audio_path.suffix}"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(audio_path),
        "-af",
        filter_str,
        str(output_file),
    ]
    print(f"Applying {effect_name} effect -> {output_file}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        print(f"FFmpeg failed for {audio_path.name} with effect '{effect_name}'.")
        print(result.stderr)
        return False
    return True

def apply_effects(audio_file, effect, outdir=None):
    if effect == "all":
        results = [run_effect(audio_file, effect_name, filter_str, outdir=outdir) for effect_name, filter_str in EFFECTS.items()]
        return sum(1 for ok in results if ok), sum(1 for ok in results if not ok)

    if effect in EFFECTS:
        ok = run_effect(audio_file, effect, EFFECTS[effect], outdir=outdir)
        return (1, 0) if ok else (0, 1)

    print("No valid effect provided. Skipping audio effect editing.")
    return 0, 0

def process_directory(audio_directory, effect, outdir=None):
    """
    Processes all WAV files in the given directory.
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
        success_count, failure_count = apply_effects(file_path, effect, outdir=outdir)
        total_success += success_count
        total_failures += failure_count

    print("\nBatch completed.")
    print(f"Rendered files: {total_success}")
    print(f"Failed renders: {total_failures}")
   

def parse_arguments():
    """
    Parse command line arguments to get the audio files and IR files.
    """
    parser = argparse.ArgumentParser(description="Apply FFmpeg distortion effects to WAV files in a directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--outdir", type=str, default=None, help="Optional directory for rendered files.")
    parser.add_argument("--effect", type=str, required=False, default="all", help="Specify the effect to apply. Default is all.", choices=["all", "distortion", "bitcrusher", "asoftclip"])
    return parser.parse_args()            

if __name__ == "__main__":
    args = parse_arguments()
    process_directory(args.audiodir, args.effect, outdir=args.outdir)
