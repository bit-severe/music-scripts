from .base import EffectDefinition


def _cleanup_voice(params):
    hp = params.get("hp", "80")
    lp = params.get("lp", "12000")
    noise_floor = params.get("noise_floor", "-45")
    noise_reduction = params.get("noise_reduction", "10")
    return (
        f"highpass=f={hp},"
        f"lowpass=f={lp},"
        f"afftdn=nf={noise_floor}:nr={noise_reduction},"
        "acompressor=threshold=0.1:ratio=3:attack=20:release=120"
    )


def _lofi_print(params):
    hp = params.get("hp", "120")
    lp = params.get("lp", "5000")
    bits = params.get("bits", "6")
    noise_floor = params.get("noise_floor", "-55")
    return (
        f"highpass=f={hp},"
        f"lowpass=f={lp},"
        f"acrusher=bits={bits}:mode=log:aa=0.3:samples=48,"
        f"afftdn=nf={noise_floor}:nr=6"
    )


def _drum_smash(params):
    threshold = params.get("threshold", "0.04")
    ratio = params.get("ratio", "12")
    limit = params.get("limit", "0.8")
    return (
        f"acompressor=threshold={threshold}:ratio={ratio}:attack=3:release=45:makeup=4,"
        f"alimiter=limit={limit},"
        "firequalizer=gain_entry='entry(80,4);entry(6000,2)'"
    )


def _ambient_wash(params):
    delay_ms = params.get("delay_ms", "75")
    decay = params.get("decay", "0.35")
    lp = params.get("lp", "9000")
    stereo = params.get("stereo", "0.7")
    return (
        f"aecho=0.8:0.7:{delay_ms}:{decay},"
        f"lowpass=f={lp},"
        f"stereotools=mlev={stereo}"
    )


def _radio_phone(params):
    center = params.get("center", "1400")
    width = params.get("width", "2200")
    noise_floor = params.get("noise_floor", "-50")
    return (
        f"bandpass=f={center}:w={width},"
        "compand=attacks=0.02:decays=0.2:points=-80/-60|-20/-20|0/-8,"
        f"afftdn=nf={noise_floor}:nr=8"
    )


def get_effect_definitions():
    return [
        EffectDefinition("cleanup_voice", "Voice cleanup chain: HP/LP + denoise + compression.", _cleanup_voice),
        EffectDefinition("lofi_print", "Lo-fi chain: tone shaping + bitcrush + texture.", _lofi_print),
        EffectDefinition("drum_smash", "Aggressive drum chain: compression + limiting + EQ lift.", _drum_smash),
        EffectDefinition("ambient_wash", "Ambient chain: short echo + lowpass + widening.", _ambient_wash),
        EffectDefinition("radio_phone", "Band-limited radio/phone style chain.", _radio_phone),
    ]
