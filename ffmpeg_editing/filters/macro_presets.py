from .base import EffectDefinition


def _vocal_podcast_polish(params):
    hp = params.get("hp", "75")
    de_noise_floor = params.get("de_noise_floor", "-50")
    de_noise_reduction = params.get("de_noise_reduction", "8")
    comp_threshold = params.get("comp_threshold", "0.09")
    comp_ratio = params.get("comp_ratio", "3")
    limiter = params.get("limiter", "0.9")
    loud_i = params.get("loud_i", "-16")
    return (
        f"highpass=f={hp},"
        f"afftdn=nf={de_noise_floor}:nr={de_noise_reduction},"
        f"acompressor=threshold={comp_threshold}:ratio={comp_ratio}:attack=20:release=120:makeup=3,"
        f"alimiter=limit={limiter},"
        f"loudnorm=I={loud_i}:LRA=11:TP=-1.5"
    )


def _cinematic_pad(params):
    lp = params.get("lp", "9500")
    delay_ms = params.get("delay_ms", "120")
    decay = params.get("decay", "0.45")
    stereo = params.get("stereo", "0.75")
    return (
        f"lowpass=f={lp},"
        f"aecho=0.8:0.7:{delay_ms}:{decay},"
        f"stereotools=mlev={stereo},"
        "dynaudnorm=f=500:g=31:p=0.95"
    )


def _aggressive_808_bus(params):
    hp = params.get("hp", "20")
    bass_freq = params.get("bass_freq", "65")
    bass_gain = params.get("bass_gain", "5")
    sat_bits = params.get("sat_bits", "10")
    limiter = params.get("limiter", "0.85")
    return (
        f"highpass=f={hp},"
        f"firequalizer=gain_entry='entry({bass_freq},{bass_gain})',"
        f"acrusher=bits={sat_bits}:mode=log:aa=0.25:samples=32,"
        f"alimiter=limit={limiter}"
    )


def _lofi_tape_print(params):
    hp = params.get("hp", "120")
    lp = params.get("lp", "4800")
    wow_delay = params.get("wow_delay", "35")
    wow_decay = params.get("wow_decay", "0.18")
    bits = params.get("bits", "7")
    return (
        f"highpass=f={hp},"
        f"lowpass=f={lp},"
        f"aecho=0.8:0.7:{wow_delay}:{wow_decay},"
        f"acrusher=bits={bits}:mode=log:aa=0.4:samples=48"
    )


def _radio_voice_hard(params):
    center = params.get("center", "1550")
    width = params.get("width", "2000")
    comp_ratio = params.get("comp_ratio", "5")
    noise_floor = params.get("noise_floor", "-48")
    return (
        f"bandpass=f={center}:w={width},"
        f"acompressor=threshold=0.08:ratio={comp_ratio}:attack=8:release=60:makeup=4,"
        f"afftdn=nf={noise_floor}:nr=10"
    )


def get_effect_definitions():
    return [
        EffectDefinition("vocal_podcast_polish", "Speech chain: cleanup, compression, loudness target.", _vocal_podcast_polish),
        EffectDefinition("cinematic_pad", "Atmospheric chain for pads and textures.", _cinematic_pad),
        EffectDefinition("aggressive_808_bus", "Heavy 808 chain with saturation and limiting.", _aggressive_808_bus),
        EffectDefinition("lofi_tape_print", "Lo-fi tape-style coloration chain.", _lofi_tape_print),
        EffectDefinition("radio_voice_hard", "Aggressive radio/phone speech chain.", _radio_voice_hard),
    ]
