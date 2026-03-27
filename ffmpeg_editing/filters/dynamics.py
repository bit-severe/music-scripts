from .base import EffectDefinition


def _compressor(params):
    return params.get("filter", "acompressor")


def _limiter(params):
    limit = params.get("limit", "0.8")
    return f"alimiter=limit={limit}"


def get_effect_definitions():
    return [
        EffectDefinition("compressor", "Dynamic range compression.", _compressor),
        EffectDefinition("limiter", "Peak limiting.", _limiter),
    ]
