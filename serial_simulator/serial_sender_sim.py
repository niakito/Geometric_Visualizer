'''
Serial Sender Simulator

Generates a set of points and simulates LDR weight reading.
Sends their evolution to the visualizer.
'''

import time
import serial
import numpy as np

# comunication configuration
SERIAL_PORT = "/dev/pts/4"
BAUD_RATE = 9600

WIDTH, HEIGHT = 600, 600
MARGIN = 40
NUM_POINTS = 5
FPS = 30
DT = 1.0 / FPS
SEND_INTERVAL = 0.05

# mode configuration
ALGORITHMS = ["3CH", "DEL", "VOR"]
CURRENT = 0
ALGORITHM = ALGORITHMS[CURRENT]

# ldr parameters
ADC_MIN = 0
ADC_MAX = 1023
LDR_NOISE_STD = 4.0 # ldr/adc noise → gaussian std dev

# serial init
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(1)

# generate everyth%
np.random.seed(int(time.time()))
positions = np.random.uniform(MARGIN, WIDTH - MARGIN, size=(NUM_POINTS, 2))
ldr_base_values = np.random.uniform(300, 900, size=NUM_POINTS) # ldrs base state 4 each point 
ldr_phases = np.random.uniform(0, 2 * np.pi, size=NUM_POINTS)  # osc. frequency

print(f"Serial simulator running in {SERIAL_PORT}")

# mode: noise
# simulates adc conversion + gaussian noise
def read_ldr_with_noise(base_readings: np.ndarray) -> np.ndarray:
    noise = np.random.normal(0.0, LDR_NOISE_STD, size=base_readings.shape)
    measured = base_readings + noise
    clipped = np.clip(np.round(measured), ADC_MIN, ADC_MAX).astype(int)
    
    return clipped

# main
try:
    t = 0.0

    while True:
        t += DT

        # '''
        # simulate algorithm change ?
        if np.random.rand() < 0.005:
            CURRENT = (CURRENT+1) % len(ALGORITHMS)
            ALGORITHM = ALGORITHMS[CURRENT]
        # '''

        # sin wave over each ldr → base + osc.(sin(t&freq.))
        dynamic_light = ldr_base_values + 200 * np.sin(1.5 * t + ldr_phases)
        weights = read_ldr_with_noise(dynamic_light)

        # ALGORITHM;x1,y1,w1;x2,y2,w2;...\n
        serialized_pts = ";".join(
            f"{int(round(x))},{int(round(y))},{w}"
            for (x, y), w in zip(positions, weights)
        )
        message = f"{ALGORITHM};{serialized_pts}\n"

        ser.write(message.encode("utf-8"))
        time.sleep(SEND_INTERVAL)

except KeyboardInterrupt:
    ser.close()
    print("\nSTOOOPPP.")