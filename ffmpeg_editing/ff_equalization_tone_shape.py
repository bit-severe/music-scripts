import os
import subprocess
import argparse

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

def apply_effects(audio_file, effect, output_folder):
    """
    Applies multiple effects to an audio file and saves each effect as a separate file inside the output folder.
    """
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    os.makedirs(output_folder, exist_ok=True)  # Ensure output directory exists

    if effect == "all":
        for effect_name, filter_str in EFFECTS.items():
            output_file = os.path.join(output_folder, f"{base_name}_{effect_name}.wav")
            cmd = ["ffmpeg", "-y", "-i", audio_file, "-af", filter_str, output_file]
            print(f"Applying {effect_name} effect -> {output_file}")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif effect in EFFECTS.keys():
        output_file = os.path.join(output_folder, f"{base_name}_{effect}.wav")
        cmd = ["ffmpeg", "-y", "-i", audio_file, "-af", EFFECTS[effect], output_file]
        print(f"Applying {effect} effect -> {output_file}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print("No valid effect provided. Skipping processing.")

def process_directory(audio_directory, effect, output_folder):
    """
    Processes all WAV files in the given directory and saves the outputs to the specified folder.
    """
    os.makedirs(output_folder, exist_ok=True)  # Ensure output directory exists
    for filename in os.listdir(audio_directory):
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(audio_directory, filename)
            print(f"\nProcessing: {file_path}")
            apply_effects(file_path, effect, output_folder)

def parse_arguments():
    """
    Parse command line arguments to get the audio files and output directory.
    """
    parser = argparse.ArgumentParser(description="Apply FFmpeg effects to all WAV files in a directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--effect", type=str, required=False, default="all",
                        choices=["highpass", "lowpass", "bandpass", "notch", "bass_boost", "midrange_cut", "treble_boost", "presence_boost", "air_boost", "crystalizer"],
                        help="Specify the effect to be applied. Default is 'all'.")
    parser.add_argument("--outputdir", type=str, required=False,
                        help="Path to save processed audio files. Default is inside audiodir as 'processed'.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    output_dir = args.outputdir if args.outputdir else os.path.join(args.audiodir, "processed")

    process_directory(args.audiodir, args.effect, output_dir)
