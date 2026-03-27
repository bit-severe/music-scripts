import argparse
import random
import subprocess
from pathlib import Path

# Define effects with randomizable parameters
def generate_effects():
    return {
        "highpass": f"highpass=f={random.randint(500, 2000)}",
        "lowpass": f"lowpass=f={random.randint(200, 1000)}",
        "bandpass": f"bandpass=f={random.randint(500, 3000)}:w={random.randint(100, 500)}",
        "notch": f"bandreject=f={random.randint(500, 3000)}:w={random.randint(100, 500)}",
        "bass_boost": f"firequalizer=gain_entry='entry({random.randint(50, 150)}, {random.uniform(3, 9)})'",
        "treble_boost": f"firequalizer=gain_entry='entry({random.randint(5000, 12000)}, {random.uniform(3, 9)})'",
        "stereo_widen": f"stereotools=mlev={random.uniform(0.1, 0.7)}",
        "compressor": "acompressor",
        "limiter": "alimiter=limit=0.8",
        "bitcrusher": f"acrusher={random.randint(4, 12)}:{random.randint(2, 8)}:100:0",
        "flanger": "flanger",
        "phaser": "aphaser",
        "tremolo": f"tremolo=f={random.randint(5, 15)}:d={random.uniform(0.2, 0.8)}",
        "vibrato": f"vibrato=f={random.randint(3, 10)}:d={random.uniform(0.2, 1.0)}",
        "slapback_delay": f"adelay={random.randint(200, 800)}|{random.randint(200, 800)}",
        "chipmunk": "asetrate=48000*1.5, atempo=0.666666",
        "deep_voice": "asetrate=48000*0.8, atempo=1.25",
        "pitch_up": f"asetrate=44100*{random.uniform(1.1, 1.5)}, atempo={random.uniform(0.6, 0.9)}",
        "pitch_down": f"asetrate=44100*{random.uniform(0.7, 0.9)}, atempo={random.uniform(1.1, 1.4)}",
        "underwater": f"lowpass=f={random.randint(200, 700)},asetrate={random.randint(18000, 24000)}",
    }

def run_effect(audio_file, output_dir, effect_name, filter_str):
    audio_path = Path(audio_file)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    output_file = out_path / f"{audio_path.stem}_{effect_name}{audio_path.suffix}"
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
        print(f"Error applying {effect_name} effect:\n{result.stderr}")
        return False
    return True

def apply_effects(audio_file, output_dir, effect):
    """
    Applies multiple effects to an audio file and saves each effect as a separate file.
    """
    effects = generate_effects()
    if effect == "all":
        results = [run_effect(audio_file, output_dir, effect_name, filter_str) for effect_name, filter_str in effects.items()]
        return sum(1 for ok in results if ok), sum(1 for ok in results if not ok)

    if effect in effects:
        ok = run_effect(audio_file, output_dir, effect, effects[effect])
        return (1, 0) if ok else (0, 1)

    print("No valid effect provided. Skipping audio effect editing.")
    return 0, 0

def process_directory(audio_directory, output_directory, effect):
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
        success_count, failure_count = apply_effects(file_path, output_directory, effect)
        total_success += success_count
        total_failures += failure_count

    print("\nBatch completed.")
    print(f"Rendered files: {total_success}")
    print(f"Failed renders: {total_failures}")

def parse_arguments():
    """
    Parse command line arguments to get the audio files and output directory.
    """
    parser = argparse.ArgumentParser(description="Apply randomized ffmpeg effects to the files in a given directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--outdir", "--outputdir", dest="outdir", type=str, required=False, help="Path to save processed audio files. If not set, defaults to audiodir/effects_output.")
    parser.add_argument("--effect", type=str, required=False, default="all", choices=["all", "highpass", "lowpass", "bandpass", "notch", "bass_boost", "treble_boost", "stereo_widen", "compressor", "limiter", "bitcrusher", "flanger", "phaser", "tremolo", "vibrato", "slapback_delay", "chipmunk", "deep_voice", "pitch_up", "pitch_down", "underwater"], help="Specify the effect to be applied. Default is all.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    output_dir = args.outdir if args.outdir else str(Path(args.audiodir) / "effects_output")
    process_directory(args.audiodir, output_dir, args.effect)
