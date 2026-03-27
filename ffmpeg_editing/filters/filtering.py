from .base import EffectDefinition


def _highpass(params):
    freq = params.get("freq", "1000")
    return f"highpass=f={freq}"


def _lowpass(params):
    freq = params.get("freq", "500")
    return f"lowpass=f={freq}"


def _bandpass(params):
    freq = params.get("freq", "1000")
    width = params.get("width", "200")
    return f"bandpass=f={freq}:w={width}"


def _notch(params):
    freq = params.get("freq", "1000")
    width = params.get("width", "200")
    return f"bandreject=f={freq}:w={width}"


def _bass_boost(params):
    freq = params.get("freq", "80")
    gain = params.get("gain", "6")
    return f"firequalizer=gain_entry='entry({freq},{gain})'"


def _treble_boost(params):
    freq = params.get("freq", "6000")
    gain = params.get("gain", "6")
    return f"firequalizer=gain_entry='entry({freq},{gain})'"


def get_effect_definitions():
    return [
        EffectDefinition("highpass", "High-pass filter.", _highpass),
        EffectDefinition("lowpass", "Low-pass filter.", _lowpass),
        EffectDefinition("bandpass", "Band-pass filter.", _bandpass),
        EffectDefinition("notch", "Band-reject (notch) filter.", _notch),
        EffectDefinition("bass_boost", "Low-frequency boost using firequalizer.", _bass_boost),
        EffectDefinition("treble_boost", "High-frequency boost using firequalizer.", _treble_boost),
    ]
