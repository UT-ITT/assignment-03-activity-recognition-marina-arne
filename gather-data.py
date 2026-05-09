import sys
import time
import os

import pandas as pd

from DIPPID import SensorUDP

CAPTURE_DURATION = 10   # seconds
TARGET_HZ = 100
DEFAULT_PORT = 5700
VALID_ACTIVITIES = {"running", "rowing", "lifting", "jumpingjacks"}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def parse_args():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1].lower()
    activity = sys.argv[2].lower()
    number = sys.argv[3]
    port = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_PORT
    if activity not in VALID_ACTIVITIES:
        print(f"Warning: '{activity}' is not a standard activity {sorted(VALID_ACTIVITIES)}")
    return name, activity, number, port


def make_callbacks(sensor, recording_state):
    """Return (on_button, on_accelerometer) closures that share recording_state dict."""

    def on_button(value):
        if value == 1 and not recording_state["active"]:
            print(f"\n[START] Recording '{recording_state['activity']}' "
                  f"for {CAPTURE_DURATION} s  →  {recording_state['filename']}")
            recording_state["rows"] = []
            recording_state["start"] = time.time()
            recording_state["active"] = True

    def on_accelerometer(_):
        if not recording_state["active"]:
            return
        acc = sensor.get_value("accelerometer")
        gyro = sensor.get_value("gyroscope")
        if acc is None or gyro is None:
            return
        recording_state["rows"].append({
            "timestamp": time.time(),
            "acc_x":  acc.get("x", 0.0),
            "acc_y":  acc.get("y", 0.0),
            "acc_z":  acc.get("z", 0.0),
            "gyro_x": gyro.get("x", 0.0),
            "gyro_y": gyro.get("y", 0.0),
            "gyro_z": gyro.get("z", 0.0),
        })

    return on_button, on_accelerometer


def wait_for_capture(recording_state):
    """Block until 10 s of data have been collected. Returns False if interrupted."""
    try:
        while True:
            if recording_state["active"]:
                if (time.time() - recording_state["start"]) >= CAPTURE_DURATION:
                    print("[STOP]  Capture finished.")
                    return True
            time.sleep(0.005)
    except KeyboardInterrupt:
        print("\nAborted by user – no file saved.")
        return False


def resample_and_save(rows, filename):
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.set_index("timestamp").sort_index()

    period_ms = 1000 // TARGET_HZ
    df_rs = (df
             .resample(f"{period_ms}ms")
             .mean()
             .interpolate(method="time")
             .dropna())

    df_rs.reset_index(inplace=True)
    df_rs.insert(0, "id", range(len(df_rs)))
    df_rs.to_csv(filename, index=False, sep=";", decimal=",")
    print(f"Saved {len(df_rs)} rows at {TARGET_HZ} Hz  →  {filename}")


def main():
    name, activity, number, port = parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    filename = os.path.join(DATA_DIR, f"{name}-{activity}-{number}.csv")

    print(f"Connecting to DIPPID on UDP port {port} ...")
    sensor = SensorUDP(port)
    time.sleep(1)  # allow sensor to start sending

    recording_state = {
        "active": False,
        "start": None,
        "rows": [],
        "activity": activity,
        "filename": filename,
    }

    on_button, on_accelerometer = make_callbacks(sensor, recording_state)
    sensor.register_callback("button_1", on_button)
    sensor.register_callback("accelerometer", on_accelerometer)

    print(f"Ready. Press Button 1 on the DIPPID device to start a {CAPTURE_DURATION}-second recording.")
    print("(Press Ctrl+C to quit without saving)\n")

    captured = wait_for_capture(recording_state)
    sensor.disconnect()

    if not captured:
        sys.exit(0)

    if not recording_state["rows"]:
        print("No sensor data was captured. Make sure the DIPPID device is sending data.")
        sys.exit(1)

    resample_and_save(recording_state["rows"], filename)


if __name__ == "__main__":
    main()
