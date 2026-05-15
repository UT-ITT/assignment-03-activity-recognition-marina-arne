import argparse
import os
import random
import time
from collections import deque

import pandas as pd
import pyglet
from activity_recognizer import ActivityRecognizer, VALID_ACTIVITIES
from DIPPID import SensorUDP


class LiveSensorStream:
    def __init__(self, buffer_seconds=2):
        self.buffer_seconds = buffer_seconds
        self.sample_rate = 100
        self.buffer = deque(maxlen=buffer_seconds * self.sample_rate)
        self.accel = None
        self.gyro = None

    def append(self):
        if self.accel is None or self.gyro is None:
            return
        self.buffer.append({
            "acc_x": float(self.accel.get("x", 0)),
            "acc_y": float(self.accel.get("y", 0)),
            "acc_z": float(self.accel.get("z", 0)),
            "gyro_x": float(self.gyro.get("x", 0)),
            "gyro_y": float(self.gyro.get("y", 0)),
            "gyro_z": float(self.gyro.get("z", 0)),
        })

    def on_accel(self, value):
        self.accel = value
        self.append()

    def on_gyro(self, value):
        self.gyro = value
        self.append()

    def to_dataframe(self):
        return pd.DataFrame(list(self.buffer))

    def has_data(self):
        return len(self.buffer) >= self.buffer.maxlen // 2



class DemoSensorStream(LiveSensorStream):
    def __init__(self, csv_path, interval=0.01):
        super().__init__()
        self.data = pd.read_csv(csv_path)[["acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"]].dropna().reset_index(drop=True)
        self.index = 0
        self.interval = interval

    def start(self):
        pyglet.clock.schedule_interval(self._tick, self.interval)

    def _tick(self, dt):
        if self.index >= len(self.data):
            self.index = 0
        row = self.data.iloc[self.index].to_dict()
        self.buffer.append({
            "acc_x": float(row["acc_x"]),
            "acc_y": float(row["acc_y"]),
            "acc_z": float(row["acc_z"]),
            "gyro_x": float(row["gyro_x"]),
            "gyro_y": float(row["gyro_y"]),
            "gyro_z": float(row["gyro_z"]),
        })
        self.index += 1


class FitnessTrainerApp:
    def __init__(self, recognizer, sensor, target_duration=20):
        self.recognizer = recognizer
        self.sensor = sensor
        self.window = pyglet.window.Window(width=900, height=500, caption="Fitness Trainer")
        self.window.push_handlers(self)
        self.target_duration = target_duration
        self.target_activity = random.choice(VALID_ACTIVITIES)
        self.target_start = time.time()
        self.prediction = "waiting"
        self.confidence = 0.0
        self.correct_time = 0.0

        font_size = 20
        self.labels = {
            "title": pyglet.text.Label("Fitness Trainer", font_name="Arial", font_size=28, x=20, y=450),
            "target": pyglet.text.Label("", font_name="Arial", font_size=18, x=20, y=400),
            "prediction": pyglet.text.Label("", font_name="Arial", font_size=20, x=20, y=330, color=(255, 215, 0, 255)),
            "confidence": pyglet.text.Label("", font_name="Arial", font_size=16, x=20, y=280),
            "feedback": pyglet.text.Label("", font_name="Arial", font_size=18, x=20, y=230, color=(144, 238, 144, 255)),
            "help": pyglet.text.Label("Press ESC or Q to exit", font_name="Arial", font_size=12, x=20, y=20),
        }

        pyglet.clock.schedule_interval(self.update, 0.15)

    def update(self, dt):
        if isinstance(self.sensor, DemoSensorStream):
            if self.sensor.buffer:
                self.predict()
            return
        
        if self.sensor.has_data():
            self.predict()

    def predict(self):
        try:
            df = self.sensor.to_dataframe()
            if df.empty:
                return
            
            pred, probs = self.recognizer.predict(df)
            self.prediction = pred
            self.confidence = float(max(probs)) if probs is not None else 0.0
            
            if pred == self.target_activity:
                self.correct_time += 0.15
            else:
                self.correct_time = max(0, self.correct_time - 0.15)
            
            if time.time() - self.target_start >= self.target_duration:
                self.target_activity = random.choice(VALID_ACTIVITIES)
                self.target_start = time.time()
                self.correct_time = 0.0
        except Exception as e:
            pass

    def on_draw(self):
        self.window.clear()
        pyglet.gl.glClearColor(0.1, 0.1, 0.15, 1.0)
        
        sec_left = max(0, int(self.target_duration - (time.time() - self.target_start)))
        self.labels["target"].text = f"Target: {self.target_activity} | Next in {sec_left}s"
        self.labels["prediction"].text = f"Prediction: {self.prediction}"
        self.labels["confidence"].text = f"Confidence: {self.confidence:.2f} | Samples: {len(self.sensor.buffer)}"
        
        if self.correct_time >= 5.0:
            self.labels["feedback"].text = "Great! Correct!"
        elif self.prediction == self.target_activity:
            self.labels["feedback"].text = "Good, keep it up!"
        else:
            self.labels["feedback"].text = f"Try: {self.target_activity}"
        
        for label in self.labels.values():
            label.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol in (pyglet.window.key.ESCAPE, pyglet.window.key.Q):
            pyglet.app.exit()

    def run(self):
        if isinstance(self.sensor, DemoSensorStream):
            self.sensor.start()
        pyglet.app.run()



def resolve_dirs(dirs):
    """Resolve data directories, check relative/absolute paths"""
    resolved = []
    for d in dirs:
        if os.path.exists(d):
            resolved.append(d)
        elif os.path.exists(f"../{d}"):
            resolved.append(f"../{d}")
        else:
            resolved.append(d)
    return resolved


def main():
    parser = argparse.ArgumentParser(description="Fitness Trainer - Activity Recognition")
    parser.add_argument("--data-dir", nargs="*", default=["data"], help="Data directories")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode with CSV file")
    parser.add_argument("--sample", type=str, help="CSV file for demo mode")
    parser.add_argument("--port", type=int, default=5700, help="UDP port for DIPPID")
    parser.add_argument("--session-duration", type=int, default=20, help="Duration between target changes")
    
    args = parser.parse_args()
    
    data_dirs = resolve_dirs(args.data_dir)
    print(f"Loading from: {data_dirs}")
    
    recognizer = ActivityRecognizer(data_dirs=data_dirs)
    result = recognizer.train()
    
    print(f"\nModel: {result['model']}")
    print(f"Samples: {result['samples']}")
    print(f"Accuracy: {result['accuracy']}")
    print(result["report"])

    if args.demo:
        sample_path = args.sample or "data/arne/arne-running-1.csv"
        if not os.path.exists(sample_path):
            print(f"Error: {sample_path} not found")
            return
        sensor = DemoSensorStream(sample_path)
    else:
        sensor = LiveSensorStream()
        device = SensorUDP(args.port)
        device.register_callback("accelerometer", sensor.on_accel)
        device.register_callback("gyroscope", sensor.on_gyro)

    app = FitnessTrainerApp(recognizer, sensor, target_duration=args.session_duration)
    app.run()


if __name__ == "__main__":
    main()
