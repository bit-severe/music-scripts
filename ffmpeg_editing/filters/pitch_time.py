from .base import EffectDefinition


def _speed_up(params):
    factor = params.get("factor", "1.5")
    return f"atempo={factor}"


def _slow_down(params):
    factor = params.get("factor", "0.75")
    return f"atempo={factor}"


def _pitch_up(params):
    ratio = params.get("ratio", "1.189207")
    sample_rate = params.get("sample_rate", "44100")
    return f"asetrate={sample_rate}*{ratio},aresample={sample_rate}"


def _pitch_down(params):
    ratio = params.get("ratio", "1.189207")
    sample_rate = params.get("sample_rate", "44100")
    return f"asetrate={sample_rate}/{ratio},aresample={sample_rate}"


def get_effect_definitions():
    return [
        EffectDefinition("speed_up", "Increase tempo.", _speed_up),
        EffectDefinition("slow_down", "Decrease tempo.", _slow_down),
        EffectDefinition("pitch_up", "Raise pitch with asetrate.", _pitch_up),
        EffectDefinition("pitch_down", "Lower pitch with asetrate.", _pitch_down),
    ]
