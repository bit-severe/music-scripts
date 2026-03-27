from .base import EffectDefinition


def _flanger(params):
    return params.get("filter", "flanger")


def _phaser(params):
    return params.get("filter", "aphaser")


def _tremolo(params):
    freq = params.get("freq", "5")
    return f"tremolo={freq}"


def _vibrato(params):
    freq = params.get("freq", "7")
    depth = params.get("depth", "0.5")
    return f"vibrato=f={freq}:d={depth}"


def get_effect_definitions():
    return [
        EffectDefinition("flanger", "Flanger modulation.", _flanger),
        EffectDefinition("phaser", "Phaser modulation.", _phaser),
        EffectDefinition("tremolo", "Amplitude modulation tremolo.", _tremolo),
        EffectDefinition("vibrato", "Pitch modulation vibrato.", _vibrato),
    ]
