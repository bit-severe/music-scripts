from .base import EffectDefinition


def _reverse(params):
    return params.get("filter", "areverse")


def _crystalizer(params):
    amount = params.get("amount", "8")
    return f"crystalizer={amount}"


def _wahwah(params):
    freq = params.get("freq", "60")
    return f"wahwah={freq}"


def get_effect_definitions():
    return [
        EffectDefinition("reverse", "Reverse audio playback.", _reverse),
        EffectDefinition("crystalizer", "Harmonic crystalizer effect.", _crystalizer),
        EffectDefinition("wahwah", "Wah-wah filter sweep.", _wahwah),
    ]
