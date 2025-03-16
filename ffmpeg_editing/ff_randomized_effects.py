import os
import subprocess
import argparse
import random

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

def apply_effects(audio_file, output_dir, effect):
    """
    Applies multiple effects to an audio file and saves each effect as a separate file.
    """
    effects = generate_effects()
    base, ext = os.path.splitext(os.path.basename(audio_file))
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if effect == "all":
        for effect_name, filter_str in effects.items():
            output_file = os.path.join(output_dir, f"{base}_{effect_name}{ext}")
            cmd = [
                "ffmpeg", "-y", "-i", audio_file,
                "-af", filter_str,
                output_file
            ]
            print(f"Applying {effect_name} effect -> {output_file}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"Error applying {effect_name} effect:\n{result.stderr}")
    elif effect in effects.keys():
        filter_str = effects.get(effect)
        output_file = os.path.join(output_dir, f"{base}_{effect}{ext}")
        cmd = [
            "ffmpeg", "-y", "-i", audio_file,
            "-af", filter_str,
            output_file
        ]
        print(f"Applying {effect} effect -> {output_file}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error applying {effect_name} effect:\n{result.stderr}")
    else:
        print("No effect key provided. Skipping audio effect editing")

def process_directory(audio_directory, output_directory, effect):
    """
    Processes all WAV files in the given directory.
    """
    for filename in os.listdir(audio_directory):
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(audio_directory, filename)
            print(f"\nProcessing: {file_path}")
            apply_effects(file_path, output_directory, effect)

def parse_arguments():
    """
    Parse command line arguments to get the audio files and output directory.
    """
    parser = argparse.ArgumentParser(description="Apply randomized ffmpeg effects to the files in a given directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--outputdir", type=str, required=False, help="Path to save processed audio files. If not set, defaults to audiodir/effects_output.")
    parser.add_argument("--effect", type=str, required=False, default="all", help="Specify the effect to be applied. Default is all")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    output_dir = args.outputdir if args.outputdir else os.path.join(args.audiodir, "effects_output")
    process_directory(args.audiodir, output_dir, args.effect)
