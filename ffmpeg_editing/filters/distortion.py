from .base import EffectDefinition


def _distortion(params):
    level_in = params.get("level_in", "3")
    level_out = params.get("level_out", "1")
    bits = params.get("bits", "8")
    mode = params.get("mode", "log")
    return f"acrusher=level_in={level_in}:level_out={level_out}:bits={bits}:mode={mode}"


def _bitcrusher(params):
    bits = params.get("bits", "4")
    mode = params.get("mode", "log")
    aa = params.get("aa", "0.5")
    samples = params.get("samples", "64")
    return f"acrusher=bits={bits}:mode={mode}:aa={aa}:samples={samples}"


def _softclip(params):
    clip_type = params.get("type", "hard")
    threshold = params.get("threshold", "1")
    output = params.get("output", "1")
    return f"asoftclip=type={clip_type}:threshold={threshold}:output={output}"


def get_effect_definitions():
    return [
        EffectDefinition("distortion", "Acrusher-based distortion.", _distortion),
        EffectDefinition("bitcrusher", "Bit depth and sample reduction.", _bitcrusher),
        EffectDefinition("softclip", "Soft/hard clipping.", _softclip),
    ]
