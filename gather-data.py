import sys
import time
import os

import pandas as pd

from DIPPID import SensorUDP

CAPTURE_DURATION = 10   # seconds
PORT = 5700

rows = []
recording = False
start_time = 0.0
sensor = SensorUDP(PORT)

# user interaction DIPPID app
def on_button(value):
    global recording, rows, start_time
    if value == 1 and not recording:
        rows = []
        start_time = time.time()
        recording = True
        print("Lets gather some dataaaa")
# get activity data
def on_accel(_):
    global recording, rows
    if not recording:
        return
    
    accel = sensor.get_value("accelerometer")
    gyro = sensor.get_value("gyroscope")

    if accel is None or gyro is None:
        return
    
    rows.append({
        "timestamp": time.time(),
        "acc_x": accel.get("x", 0),
        "acc_y": accel.get("y", 0),
        "acc_z": accel.get("z", 0),
        "gyro_x": gyro.get("x", 0),
        "gyro_y": gyro.get("y", 0),
        "gyro_z": gyro.get("z", 0),
    })

if len(sys.argv) != 3:
    print("Usage: python gather-data.py <name> <number>")
    sys.exit(1)

name = sys.argv[1]
number = sys.argv[2]

valid_activities = ["running", "rowing", "lifting", "jumpingjacks"]

print("\n Choose your activity!!!")
# selection of activities
for i, act in enumerate(valid_activities):
    print(f"[{i+1}] {act}")

while True:
    choice = input("Please enter number: ")
    if choice.isdigit() and 1 <= int(choice) <= len(valid_activities):
        activity = valid_activities[int(choice) - 1]
        break
    else:
        print("Not a valid number >:((((")

print(f"\n selected: {activity}")

filename = f"data/{name}-{activity}-{number}.csv"
os.makedirs("data", exist_ok=True)

print(f"Connecting to port {PORT}")
time.sleep(1)

sensor.register_callback("button_1", on_button)
sensor.register_callback("accelerometer", on_accel)

print("Ready. Time to make some nooooooise!")
# record activity for only 10 seconds
try:
    while True:
        if recording and (time.time() - start_time >= CAPTURE_DURATION):
            recording = False
            print("Great job!!")
            break
        time.sleep(0.01)
except KeyboardInterrupt:
    print("Canceled :(")
    sensor.disconnect()
    sys.exit(0)

sensor.disconnect()
# resampling to 100 Hz
df = pd.DataFrame(rows)
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
df = df.set_index("timestamp").sort_index()
df = df.resample("10ms").mean().interpolate(method="time").dropna()
df = df.reset_index()
# convert timestamp
df["timestamp"] = df["timestamp"].astype("int64") // 10**3
df.insert(0, "id", range(len(df)))
# file save 
df.to_csv(filename, index=False, sep=",", decimal=".")
print(f"Saved: {filename} ({len(df)} rows)")