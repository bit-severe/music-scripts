from .base import EffectDefinition


def _echo(params):
    in_gain = params.get("in_gain", "0.8")
    out_gain = params.get("out_gain", "0.9")
    delays = params.get("delays", "1000")
    decays = params.get("decays", "0.3")
    return f"aecho={in_gain}:{out_gain}:{delays}:{decays}"


def _reverb(params):
    in_gain = params.get("in_gain", "0.8")
    out_gain = params.get("out_gain", "0.7")
    delays = params.get("delays", "60")
    decays = params.get("decays", "0.4")
    return f"aecho={in_gain}:{out_gain}:{delays}:{decays}"


def _chorus(params):
    return params.get("filter", "chorus=0.7:0.9:55:0.4:0.25:2")


def get_effect_definitions():
    return [
        EffectDefinition("echo", "Echo effect using aecho.", _echo),
        EffectDefinition("reverb", "Simple reverb-style echo.", _reverb),
        EffectDefinition("chorus", "Chorus modulation.", _chorus),
    ]
