from .base import EffectDefinition


def _loudnorm(params):
    i = params.get("i", "-16")
    lra = params.get("lra", "11")
    tp = params.get("tp", "-1.5")
    return f"loudnorm=I={i}:LRA={lra}:TP={tp}"


def _dynaudnorm(params):
    frame = params.get("frame", "500")
    gausssize = params.get("gausssize", "31")
    peak = params.get("peak", "0.95")
    return f"dynaudnorm=f={frame}:g={gausssize}:p={peak}"


def _afftdn(params):
    noise_floor = params.get("noise_floor", "-50")
    noise_reduction = params.get("noise_reduction", "12")
    return f"afftdn=nf={noise_floor}:nr={noise_reduction}"


def _silenceremove(params):
    start_periods = params.get("start_periods", "1")
    start_duration = params.get("start_duration", "0.1")
    start_threshold = params.get("start_threshold", "-50dB")
    stop_periods = params.get("stop_periods", "-1")
    stop_duration = params.get("stop_duration", "0.1")
    stop_threshold = params.get("stop_threshold", "-50dB")
    return (
        "silenceremove="
        f"start_periods={start_periods}:start_duration={start_duration}:start_threshold={start_threshold}:"
        f"stop_periods={stop_periods}:stop_duration={stop_duration}:stop_threshold={stop_threshold}"
    )


def _pan(params):
    layout = params.get("layout", "stereo")
    channels = params.get("channels", "c0=c0|c1=c1")
    return f"pan={layout}|{channels}"


def get_effect_definitions():
    return [
        EffectDefinition("loudnorm", "EBU R128 loudness normalization.", _loudnorm),
        EffectDefinition("dynaudnorm", "Dynamic audio normalization.", _dynaudnorm),
        EffectDefinition("afftdn", "FFT denoise.", _afftdn),
        EffectDefinition("silenceremove", "Trim leading/trailing silence.", _silenceremove),
        EffectDefinition("pan", "Channel routing and downmix/upmix.", _pan),
    ]
