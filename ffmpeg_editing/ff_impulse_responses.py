import os
import subprocess
import argparse

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
        "-filter_complex", "[0] [1] afir=dry=10:wet=5",
        output_file
    ]

    print(f"Applying IR reverb: {audio_file} with {ir_file} -> {output_file}")
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return output_file

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
            if ir_directory != "":
                impulse_responses(file_path, ir_directory)
            else:
                print("No Impulse Response directory provided.")    

def parse_arguments():
    """
    Parse command line arguments to get the audio files and IR files.
    """
    parser = argparse.ArgumentParser(description="Apply ffmpeg effects to the files of a given directory.")
    parser.add_argument("--audiodir", type=str, required=True, help="Path to audio files.")
    parser.add_argument("--irdir", type=str, required=True, default="", help="Path to impulse response files.")
    return parser.parse_args()            

if __name__ == "__main__":
    args = parse_arguments()
    process_directory(args.audiodir, args.irdir)
