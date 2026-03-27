from .base import EffectDefinition


def _stereo_widen(params):
    width = params.get("width", "0.6")
    return f"stereotools=mlev={width}"


def get_effect_definitions():
    return [
        EffectDefinition("stereo_widen", "Stereo widening.", _stereo_widen),
    ]
