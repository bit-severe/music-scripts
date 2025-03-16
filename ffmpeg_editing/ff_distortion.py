import os
import subprocess
import argparse

# Define effects and their FFmpeg filters
EFFECTS = {
    "distortion": "acrusher=level_in=3:level_out=1:bits=8:mode=log",
    "bitcrusher": "acrusher=bits=4:mode=log:aa=0.5:samples=64",
    "asoftclip": "type=hard:threshold=1:output=1:param=1:oversample=1"
}

def apply_effects(audio_file, effect):
    """
    Applies multiple effects to an audio file and saves each effect as a separate file.
    """
    base, ext = os.path.splitext(audio_file)
    if effect == "all":
        for effect_name, filter_str in EFFECTS.items():
            output_file = f"{base}_{effect_name}{ext}"
            cmd = [
                "ffmpeg", "-y", "-i", audio_file,
                "-af", filter_str,
                output_file
            ]
            print(f"Applying {effect_name} effect -> {output_file}")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif effect in EFFECTS.keys():
        filter_str = EFFECTS.get(effect)
        output_file = f"{base}_{effect}{ext}"
        cmd = [
            "ffmpeg", "-y", "-i", audio_file,
            "-af", filter_str,
            output_file
        ]
        print(f"Applying {effect} effect -> {output_file}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print("No effect key provided. Skipping audio effect editing")            

def process_directory(audio_directory, effect):
    """
    Processes all WAV files in the given directory.
    """
    for filename in os.listdir(audio_directory):
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(audio_directory, filename)
            print(f"\nProcessing: {file_path}")
            apply_effects(file_path, effect)
   

def parse_arguments():
    """
    Parse command line arguments to get the audio files and IR files.
    """
    parser = argparse.ArgumentParser(description="Apply ffmpeg effects to the files of a given directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--effect", type=str, required=False, default="all", help="Specify the effect to be applied. Default is all", choices=["distortion","bitcrusher","asoftclip"])
    return parser.parse_args()            

if __name__ == "__main__":
    args = parse_arguments()
    process_directory(args.audiodir, args.effect)
