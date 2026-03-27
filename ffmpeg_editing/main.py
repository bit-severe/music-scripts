import argparse
import subprocess
import sys
from pathlib import Path

try:
    from filters import load_effects
except ImportError:
    from ffmpeg_editing.filters import load_effects


def parse_key_values(values):
    parsed = {}
    for item in values or []:
        if "=" not in item:
            raise ValueError(f"Invalid --param '{item}'. Use key=value format.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid --param '{item}'. Key cannot be empty.")
        parsed[key] = value
    return parsed


def build_ffmpeg_command(input_file, output_file, effect_definition, params):
    filter_expr = effect_definition.builder(params)
    cmd = ["ffmpeg", "-y", "-i", str(input_file)]
    if effect_definition.mode == "filter_complex":
        cmd.extend(["-filter_complex", filter_expr])
    else:
        cmd.extend(["-af", filter_expr])
    cmd.append(str(output_file))
    return cmd


def ensure_unique_path(path):
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def process_one_file(input_file, effect_name, effect_definition, params, outdir):
    output_dir = Path(outdir) if outdir else input_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = ensure_unique_path(output_dir / f"{input_file.stem}_{effect_name}{input_file.suffix}")
    cmd = build_ffmpeg_command(input_file, output_file, effect_definition, params)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"FFmpeg failed with exit code {result.returncode}")
    return output_file


def parse_args(effect_names):
    parser = argparse.ArgumentParser(
        description="Apply a modular FFmpeg effect to WAV files."
    )
    parser.add_argument("--effect", choices=sorted(effect_names), help="Effect name to apply.")
    parser.add_argument("--input", type=str, help="Path to a single input WAV file.")
    parser.add_argument("--audiodir", type=str, help="Path to input directory containing WAV files.")
    parser.add_argument("--outdir", type=str, default=None, help="Optional output directory for rendered files.")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Effect parameter as key=value. Repeat for multiple params.",
    )
    parser.add_argument("--list-effects", action="store_true", help="List available effects and exit.")
    args = parser.parse_args()

    if args.list_effects:
        return args

    if not args.effect:
        parser.error("--effect is required unless --list-effects is used.")
    if bool(args.input) == bool(args.audiodir):
        parser.error("Provide exactly one of --input or --audiodir.")
    return args


def main():
    effects = load_effects()
    args = parse_args(effects.keys())

    if args.list_effects:
        print("Available effects:")
        for name in sorted(effects):
            print(f"- {name}: {effects[name].description}")
        return 0

    params = parse_key_values(args.param)
    effect_definition = effects[args.effect]

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists() or not input_path.is_file() or input_path.suffix.lower() != ".wav":
            raise FileNotFoundError(f"Invalid input WAV file: {args.input}")
        output_file = process_one_file(input_path, args.effect, effect_definition, params, args.outdir)
        print(f"Rendered: {output_file}")
        return 0

    input_dir = Path(args.audiodir)
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Invalid audio directory: {args.audiodir}")

    audio_files = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
    if not audio_files:
        print(f"No WAV files found in: {input_dir}")
        return 0

    successes = 0
    failures = 0
    for audio_file in audio_files:
        print(f"\nProcessing: {audio_file}")
        try:
            output_file = process_one_file(audio_file, args.effect, effect_definition, params, args.outdir)
            print(f"Rendered: {output_file}")
            successes += 1
        except Exception as exc:
            print(f"Failed: {audio_file.name} -> {exc}")
            failures += 1

    print("\nBatch completed.")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as err:
        print(f"Error: {err}")
        raise SystemExit(1)
