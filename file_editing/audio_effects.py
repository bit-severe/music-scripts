import os
import subprocess
import argparse

# Define effects and their FFmpeg filters
EFFECTS = {
    "reverb": "aecho=0.8:0.88:6:0.4, aecho=0.6:0.75:12:0.3, aecho=0.5:0.55:12:0.2",
    "echo": "aecho=0.8:0.9:1000:0.3",
    "highpass": "highpass=f=1000",
    "lowpass": "lowpass=f=500",
    "speed_up": "atempo=1.5",
    "slow_down": "atempo=0.75",
    "pitch_up": "asetrate=44100*1.189207,aresample=44100",
    "pitch_down": "asetrate=44100/1.189207,aresample=44100",
    "distortion": "acrusher=level_in=3:level_out=1:bits=8:mode=log",
    "flanger": "flanger",
    "phaser": "aphaser",
    "chorus": "chorus=0.7:0.9:55:0.4:0.25:2",
    "tremolo": "tremolo=5",
    "bass_boost": "firequalizer=gain_entry='entry(80, 6)'",
    "treble_boost": "firequalizer=gain_entry='entry(6000, 6)'",
    "compressor": "acompressor",
    "limiter": "alimiter",
    "wahwah": "wahwah=60",
    "stereo_widen": "stereotools=mlev=0.03",
    "bitcrusher": "acrusher=8:4:100:0",
    "robot_voice": "ringmod=frequency=30"
}

def apply_ir_reverb(audio_file, ir_file):
    """
    Applies impulse response reverb to an audio file using FFmpeg.
    
    Parameters:
    - audio_file (str): Path to the input WAV file.
    - ir_file (str): Path to the impulse response WAV file.
    
    Output:
    - Creates a new file.
    """
    base_audio, ext_audio = os.path.splitext(audio_file)
    base_ir = os.path.splitext(os.path.basename(ir_file))[0]
    output_file = f"{base_audio}_{base_ir}{ext_audio}"

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_file,
        "-i", ir_file,
        "-filter_complex", "[0] [1] afir=dry=10:wet=10",
        output_file
    ]

    print(f"Applying IR reverb: {audio_file} with {ir_file} -> {output_file}")
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return output_file

def apply_effects(audio_file):
    """
    Applies multiple effects to an audio file and saves each effect as a separate file.
    """
    base, ext = os.path.splitext(audio_file)

    for effect_name, filter_str in EFFECTS.items():
        output_file = f"{base}_{effect_name}{ext}"
        cmd = [
            "ffmpeg", "-y", "-i", audio_file,
            "-af", filter_str,
            output_file
        ]
        print(f"Applying {effect_name} effect -> {output_file}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def impulse_responses(file_path, ir_dir):
    """
    Applies each impulse response in ir_dir to each WAV file in audio_dir.
    """
    ir_files = [os.path.join(ir_dir, f) for f in os.listdir(ir_dir) if f.endswith('.wav')]

    for ir_file in ir_files:
        apply_ir_reverb(file_path, ir_file)        

def process_directory(audio_directory, ir_directory):
    """
    Processes all WAV files in the given directory.
    """
    for filename in os.listdir(audio_directory):
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(audio_directory, filename)
            print(f"\nProcessing: {file_path}")
            apply_effects(file_path)
            impulse_responses(file_path, ir_directory)

def parse_arguments():
    """
    Parse command line arguments to get the audio files and IR files.
    """
    parser = argparse.ArgumentParser(description="Apply ffmpeg effects to the files of a given directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--irdir", type=str, required=True, help="Path to impulse response files.")
    return parser.parse_args()            

if __name__ == "__main__":
    args = parse_arguments()
    process_directory(args.audiodir, args.irdir)
