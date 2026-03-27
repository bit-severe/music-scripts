import subprocess

from ffmpeg_editing.filters import load_effects
from ffmpeg_editing.filters.base import EffectDefinition

EFFECT_UI_META = {
    "echo": {
        "defaults": {"in_gain": "0.8", "out_gain": "0.9", "delays": "1000", "decays": "0.3"},
        "hints": {
            "in_gain": "Input gain (0.0-1.0)",
            "out_gain": "Output gain (0.0-1.0)",
            "delays": "Delay in ms",
            "decays": "Decay factor (0.0-1.0)",
        },
    },
    "reverb": {
        "defaults": {"in_gain": "0.8", "out_gain": "0.7", "delays": "60", "decays": "0.4"},
        "hints": {
            "in_gain": "Input gain (0.0-1.0)",
            "out_gain": "Output gain (0.0-1.0)",
            "delays": "Delay in ms",
            "decays": "Decay factor (0.0-1.0)",
        },
    },
    "highpass": {"defaults": {"freq": "1000"}, "hints": {"freq": "Cutoff in Hz"}},
    "lowpass": {"defaults": {"freq": "500"}, "hints": {"freq": "Cutoff in Hz"}},
    "bandpass": {
        "defaults": {"freq": "1000", "width": "200"},
        "hints": {"freq": "Center freq in Hz", "width": "Bandwidth in Hz"},
    },
    "notch": {
        "defaults": {"freq": "1000", "width": "200"},
        "hints": {"freq": "Center freq in Hz", "width": "Bandwidth in Hz"},
    },
    "bass_boost": {
        "defaults": {"freq": "80", "gain": "6"},
        "hints": {"freq": "Boost freq in Hz", "gain": "Gain in dB"},
    },
    "treble_boost": {
        "defaults": {"freq": "6000", "gain": "6"},
        "hints": {"freq": "Boost freq in Hz", "gain": "Gain in dB"},
    },
    "chorus": {"defaults": {"filter": "chorus=0.7:0.9:55:0.4:0.25:2"}, "hints": {"filter": "Full FFmpeg chorus filter string"}},
    "tremolo": {"defaults": {"freq": "5"}, "hints": {"freq": "Modulation frequency (Hz)"}},
    "vibrato": {"defaults": {"freq": "7", "depth": "0.5"}, "hints": {"freq": "Modulation frequency (Hz)", "depth": "Depth (0.0-1.0)"}},
    "distortion": {
        "defaults": {"level_in": "3", "level_out": "1", "bits": "8", "mode": "log"},
        "hints": {
            "level_in": "Input gain",
            "level_out": "Output gain",
            "bits": "Bit depth (e.g. 4-16)",
            "mode": "Crusher mode (log/lin)",
        },
    },
    "bitcrusher": {
        "defaults": {"bits": "4", "mode": "log", "aa": "0.5", "samples": "64"},
        "hints": {"bits": "Bit depth", "mode": "Mode", "aa": "Anti-aliasing", "samples": "Sample window"},
    },
    "softclip": {
        "defaults": {"type": "hard", "threshold": "1", "output": "1"},
        "hints": {"type": "hard/soft", "threshold": "Clip threshold", "output": "Output gain"},
    },
    "slapback_delay": {
        "defaults": {"left_ms": "240", "right_ms": "240"},
        "hints": {"left_ms": "Left delay (ms)", "right_ms": "Right delay (ms)"},
    },
    "speed_up": {"defaults": {"factor": "1.5"}, "hints": {"factor": "Tempo factor (>1 faster)"}},
    "slow_down": {"defaults": {"factor": "0.75"}, "hints": {"factor": "Tempo factor (<1 slower)"}},
    "pitch_up": {
        "defaults": {"ratio": "1.189207", "sample_rate": "44100"},
        "hints": {"ratio": "Pitch ratio", "sample_rate": "Base sample rate"},
    },
    "pitch_down": {
        "defaults": {"ratio": "1.189207", "sample_rate": "44100"},
        "hints": {"ratio": "Pitch ratio", "sample_rate": "Base sample rate"},
    },
    "stereo_widen": {"defaults": {"width": "0.6"}, "hints": {"width": "Stereo width mix"}},
    "limiter": {"defaults": {"limit": "0.8"}, "hints": {"limit": "Limiter ceiling"}},
    "crystalizer": {"defaults": {"amount": "8"}, "hints": {"amount": "Effect amount"}},
    "wahwah": {"defaults": {"freq": "60"}, "hints": {"freq": "Sweep frequency"}},
    "loudnorm": {
        "defaults": {"i": "-16", "lra": "11", "tp": "-1.5"},
        "hints": {"i": "Target integrated LUFS", "lra": "Loudness range target", "tp": "True peak dB"},
    },
    "dynaudnorm": {
        "defaults": {"frame": "500", "gausssize": "31", "peak": "0.95"},
        "hints": {"frame": "Frame length (ms)", "gausssize": "Smoothing window", "peak": "Target peak (0.0-1.0)"},
    },
    "afftdn": {
        "defaults": {"noise_floor": "-50", "noise_reduction": "12"},
        "hints": {"noise_floor": "Noise floor dB", "noise_reduction": "Reduction amount dB"},
    },
    "silenceremove": {
        "defaults": {
            "start_periods": "1",
            "start_duration": "0.1",
            "start_threshold": "-50dB",
            "stop_periods": "-1",
            "stop_duration": "0.1",
            "stop_threshold": "-50dB",
        },
        "hints": {
            "start_periods": "Leading silence periods",
            "start_duration": "Leading silence duration (s)",
            "start_threshold": "Leading silence threshold",
            "stop_periods": "Trailing silence periods",
            "stop_duration": "Trailing silence duration (s)",
            "stop_threshold": "Trailing silence threshold",
        },
    },
    "pan": {
        "defaults": {"layout": "stereo", "channels": "c0=c0|c1=c1"},
        "hints": {"layout": "Output layout (mono/stereo)", "channels": "Channel mapping expression"},
    },
    "cleanup_voice": {
        "defaults": {"hp": "80", "lp": "12000", "noise_floor": "-45", "noise_reduction": "10"},
        "hints": {
            "hp": "High-pass cutoff (Hz)",
            "lp": "Low-pass cutoff (Hz)",
            "noise_floor": "Denoise noise floor (dB)",
            "noise_reduction": "Denoise amount (dB)",
        },
    },
    "lofi_print": {
        "defaults": {"hp": "120", "lp": "5000", "bits": "6", "noise_floor": "-55"},
        "hints": {
            "hp": "High-pass cutoff (Hz)",
            "lp": "Low-pass cutoff (Hz)",
            "bits": "Crusher bit depth",
            "noise_floor": "Texture denoise floor (dB)",
        },
    },
    "drum_smash": {
        "defaults": {"threshold": "0.04", "ratio": "12", "limit": "0.8"},
        "hints": {
            "threshold": "Compressor threshold",
            "ratio": "Compression ratio",
            "limit": "Limiter ceiling",
        },
    },
    "ambient_wash": {
        "defaults": {"delay_ms": "75", "decay": "0.35", "lp": "9000", "stereo": "0.7"},
        "hints": {
            "delay_ms": "Echo delay (ms)",
            "decay": "Echo decay",
            "lp": "Low-pass cutoff (Hz)",
            "stereo": "Stereo width",
        },
    },
    "radio_phone": {
        "defaults": {"center": "1400", "width": "2200", "noise_floor": "-50"},
        "hints": {
            "center": "Band center (Hz)",
            "width": "Band width (Hz)",
            "noise_floor": "Denoise floor (dB)",
        },
    },
    "vocal_podcast_polish": {
        "defaults": {
            "hp": "75",
            "de_noise_floor": "-50",
            "de_noise_reduction": "8",
            "comp_threshold": "0.09",
            "comp_ratio": "3",
            "limiter": "0.9",
            "loud_i": "-16",
        },
        "hints": {
            "hp": "High-pass cutoff (Hz)",
            "de_noise_floor": "Denoise floor (dB)",
            "de_noise_reduction": "Denoise amount (dB)",
            "comp_threshold": "Compressor threshold",
            "comp_ratio": "Compression ratio",
            "limiter": "Limiter ceiling",
            "loud_i": "Target loudness (LUFS)",
        },
    },
    "cinematic_pad": {
        "defaults": {"lp": "9500", "delay_ms": "120", "decay": "0.45", "stereo": "0.75"},
        "hints": {
            "lp": "Low-pass cutoff (Hz)",
            "delay_ms": "Echo delay (ms)",
            "decay": "Echo decay",
            "stereo": "Stereo width",
        },
    },
    "aggressive_808_bus": {
        "defaults": {"hp": "20", "bass_freq": "65", "bass_gain": "5", "sat_bits": "10", "limiter": "0.85"},
        "hints": {
            "hp": "High-pass cutoff (Hz)",
            "bass_freq": "Boost frequency (Hz)",
            "bass_gain": "Boost gain (dB)",
            "sat_bits": "Saturation/bit depth",
            "limiter": "Limiter ceiling",
        },
    },
    "lofi_tape_print": {
        "defaults": {"hp": "120", "lp": "4800", "wow_delay": "35", "wow_decay": "0.18", "bits": "7"},
        "hints": {
            "hp": "High-pass cutoff (Hz)",
            "lp": "Low-pass cutoff (Hz)",
            "wow_delay": "Modulation delay (ms)",
            "wow_decay": "Modulation decay",
            "bits": "Bit depth",
        },
    },
    "radio_voice_hard": {
        "defaults": {"center": "1550", "width": "2000", "comp_ratio": "5", "noise_floor": "-48"},
        "hints": {
            "center": "Band center (Hz)",
            "width": "Band width (Hz)",
            "comp_ratio": "Compression ratio",
            "noise_floor": "Denoise floor (dB)",
        },
    },
}

_NONE_EFFECT = EffectDefinition(
    name="none",
    description="No effect (copy input to output).",
    builder=lambda _params: "",
    mode="af",
)

_LOADED_EFFECTS = load_effects()
_LOADED_EFFECTS["none"] = _NONE_EFFECT


def available_effects():
    return sorted(_LOADED_EFFECTS.keys())


def effect_defaults(effect):
    definition = _LOADED_EFFECTS.get(effect)
    if not definition:
        raise ValueError(f"Unknown effect: {effect}")
    meta = EFFECT_UI_META.get(effect, {})
    return dict(meta.get("defaults", {}))


def effect_hints(effect):
    definition = _LOADED_EFFECTS.get(effect)
    if not definition:
        raise ValueError(f"Unknown effect: {effect}")
    meta = EFFECT_UI_META.get(effect, {})
    return dict(meta.get("hints", {}))


def render_with_effect(input_path, output_path, effect, user_params=None):
    if effect == "none":
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(input_path), str(output_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return
    effect_def = _LOADED_EFFECTS.get(effect)
    if not effect_def:
        raise ValueError(f"Unknown effect: {effect}")
    params = {}
    params.update(effect_defaults(effect))
    params.update(user_params or {})
    filter_expr = effect_def.builder(params)
    cmd = ["ffmpeg", "-y", "-i", str(input_path)]
    if effect_def.mode == "filter_complex":
        cmd.extend(["-filter_complex", filter_expr])
    else:
        cmd.extend(["-af", filter_expr])
    cmd.append(str(output_path))
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed while applying '{effect}':\n{result.stderr}")

