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

wave_map = {
    0: "saw",
    1: "pulse",
    2: "wh_noise"
}

def lfo_modulate_cutoff(shape="sine", rate=0.1, depth=800, base_cutoff=1000, duration=6.0):
    """
    Uses an LFO to modulate the cutoff frequency.
    
    :param shape: "sine", "triangle", "square", or "random"
    :param rate: Frequency of the LFO in Hz
    :param depth: Max variation in cutoff frequency
    :param base_cutoff: Base cutoff frequency
    :param duration: Time in seconds to run
    """
    sampling_rate = 30  # Updates per second
    start_time = time.time()

    while time.time() - start_time < duration:
        t = time.time()

        if shape == "sine":
            lfo_value = np.sin(2 * np.pi * rate * t) * depth
        elif shape == "triangle":
            lfo_value = abs((t % (1 / rate)) * 2 - 1) * 2 - 1
        elif shape == "square":
            lfo_value = 1 if np.sin(2 * np.pi * rate * t) > 0 else -1
        elif shape == "random":
            lfo_value = random.uniform(-1, 1) * depth
        else:
            raise ValueError("Invalid LFO shape. Use 'sine', 'triangle', 'square', or 'random'.")

        cutoff = max(50, base_cutoff + lfo_value)  # Ensure cutoff doesn't go below 50 Hz
        client.send_message("/subtractive/global/cutoff", cutoff)
        time.sleep(1 / sampling_rate)   

def generative_modulate_cutoff(base_cutoff=1000, duration=6.0, depth=10):
    """
    Uses a generative approach (random walk + stochastic jumps) to modulate the cutoff frequency.
    
    :param base_cutoff: Base cutoff frequency
    :param duration: Time in seconds to run
    """
    cutoff = base_cutoff
    start_time = time.time()
    while time.time() - start_time < duration:
        
        step = random.choice([-50, -25, 0, 25, 50])  # Small gradual changes
        if random.random() < 0.1:  # 10% chance of a bigger jump
            step = random.choice([-200, 200])

        cutoff = max(50, min(5000, cutoff + step * depth))
        client.send_message("/subtractive/global/cutoff", cutoff)

        sleep_time = random.uniform(0.05, 0.1)
        time.sleep(sleep_time)

# OSC messages to trigger the synth
filename_postfix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
client.send_message("/start_recording", [f"subtractive_synth_{filename_postfix}.wav"])
print("Started recording...")
for _ in range(20):
    freq = round(random.gammavariate(5, 40), 2)
    env_type = random.randint(0, 3)
    wave_type = random.randint(0, 2)
    duration = round(random.uniform(1.0, 6.0), 2)
    client.send_message("/subtractive/rlpfsynth", [freq, env_type, wave_type, duration])
    resonance = round(random.uniform(0.5, 0.95), 2)   
    print(f"Resonance is: {resonance}")
    client.send_message("/subtractive/global/resonance", resonance)
    options = ["sine", "triangle", "square", "random"]
    if random.randint(0, 1) == 1:
        cutoff = generative_modulate_cutoff(round(random.uniform(80, 1500), 2), duration)
    else:
        cutoff = lfo_modulate_cutoff(random.choice(options), round(random.uniform(0.35, 0.9), 2) , round(random.uniform(200, 1000), 2) , round(random.uniform(80, 1500), 2), duration)    

    print(f"OSC RLPF Synth -> freq={freq} | envelope={env_map.get(env_type)} | wave_type={wave_map.get(wave_type)} | duration={duration} ")
    time.sleep(duration)
client.send_message("/stop_recording", [])
print("Stopped recording and saved the file.")
