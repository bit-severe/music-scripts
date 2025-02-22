from pythonosc.udp_client import SimpleUDPClient
import numpy as np
import time
from datetime import datetime
import random

sc_ip = "127.0.0.1"
sc_port = 57120

client = SimpleUDPClient(sc_ip, sc_port)

env_map = {
    0: "percussive",
    1: "adsr",
    2: "triangle",
    3: "sine"
}

def generate_coefficients(formula_type, num_partials, inharm):
    """Generate inharmonicity coefficients based on formula type."""
    n = np.arange(1, num_partials + 1)
    if formula_type == "quadratic":
        factors = n + inharm * (n * (n - 1) / 2)
    elif formula_type == "multiplicative":
        factors = n * (1 + inharm * (n - 1))
    elif formula_type == "exponential":
        factors = n ** (1 + inharm)
    elif formula_type == "quadratic_diff":
        factors = n + inharm * (n ** 2 - n)
    elif formula_type == "square_root":
        factors = n + inharm * np.sqrt(n)
    elif formula_type == "logarithmic":
        factors = n + inharm * np.log(n + 1)
    else:
        factors = n

    return factors.tolist()  # Convert NumPy array to Python list

# OSC messages to trigger the synth
filename_postfix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
client.send_message("/start_recording", [f"additive_phm_synth_{filename_postfix}.wav"])
print("Started recording...")
for _ in range(20):
    freq = round(random.gammavariate(5, 40), 2)
    env_type = random.randint(0, 3)
    duration = round(random.uniform(1.0, 3.0), 2)
    shift = round(random.uniform(0.5, 1.0), 2)
    phase_modulation = random.randint(1, 80)
    options = ["quadratic", "multiplicative", "exponential", "quadratic_diff", "square_root", "logarithmic", "harmonic"]
    formula_type = random.choice(options)
    coeffs = generate_coefficients(formula_type, 15, random.uniform(0.01, 3.5))
    print(f"OSC -> freq={freq} | envelope={env_map.get(env_type)} | shift={shift} | inharm_formula={formula_type} | duration={duration} | phase_mod={phase_modulation}")
    filename = f"{freq}f_{env_map.get(env_type)}-env_{formula_type}-inhrm_{phase_modulation}pm_{duration}dur"
    client.send_message("/additive/coeffs", coeffs)
    client.send_message("/additive_synth", [freq, env_type, shift, duration, phase_modulation, filename])
    time.sleep(duration * 1.5)
client.send_message("/stop_recording", [])
print("Stopped recording and saved the file.")
