import os
import subprocess
import argparse

# Filters that alter pitch, tempo, or playback speed.
#     rubberband – High-quality pitch/time-stretching using the Rubber Band Library.
#     atempo – Adjusts tempo without affecting pitch.
#     asetrate – Changes playback speed.

EFFECTS = {
    "speed_up": "atempo=1.5",
    "slow_down": "atempo=0.75",
    "pitch_up": "asetrate=44100*1.189207,aresample=44100",
    "pitch_down": "asetrate=44100/1.189207,aresample=44100",
    "rubberband": "rubberband=tempo=0.5:pitch=0.5:transients=crisp:detector=percussive:phase=independent:window=standard:smoothing=off:formant=shifted:pitchq=quality:channels=apart"
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
    parser.add_argument("--effect", type=str, required=False, default="all", help="Specify the effect to be applied. Default is all", choices=["speed_up","slow_down","pitch_up","pitch_down"])
    return parser.parse_args()            

if __name__ == "__main__":
    args = parse_arguments()
    process_directory(args.audiodir, args.effect)
