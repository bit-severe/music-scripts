from pythonosc.udp_client import SimpleUDPClient
import time
import random

# SuperCollider listens on 127.0.0.1, port 57120
sc_ip = "127.0.0.1"
sc_port = 57120

# Create an OSC client
client = SimpleUDPClient(sc_ip, sc_port)

# Send OSC messages to trigger the synth
for _ in range(20):
    freq = random.choice([220, 330, 440, 550, 660])  # Random frequency
    amp = random.uniform(0.2, 0.8)  # Random amplitude
    client.send_message("/synth_control", [freq, amp])  # Send OSC message
    time.sleep(0.5)  # Delay between notes
