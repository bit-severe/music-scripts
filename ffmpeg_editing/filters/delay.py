from .base import EffectDefinition


def _slapback_delay(params):
    left_ms = params.get("left_ms", "240")
    right_ms = params.get("right_ms", left_ms)
    return f"adelay={left_ms}|{right_ms}"


def get_effect_definitions():
    return [
        EffectDefinition("slapback_delay", "Short stereo slapback delay.", _slapback_delay),
    ]
