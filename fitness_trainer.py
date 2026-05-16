# this program visualizes activities with pyglet
import sys
import time
import pyglet
from pyglet import font
from pyglet.image.animation import Animation
import joblib
import numpy as np
import collections
import pandas as pd

from DIPPID import SensorUDP

# import font
font.add_file('./assets/Play-Regular.ttf')
play_reg = font.load('Play')

PORT = 5700

sensor = SensorUDP(PORT)
WIDTH_SIZE = 900
HEIGHT_SIZE = 1200

TARGET_TIME = 5.0
current_streak_time = 0.0
last_activity = "Waiting for the moves..."
prediction_buffer = collections.deque(maxlen=10)

win = pyglet.window.Window(WIDTH_SIZE, HEIGHT_SIZE)

pyglet.gl.glClearColor(1, 1, 1, 1)

class_dict_reverse = {0: "rowing", 1: "running", 2: "lifting", 3: "jumpingjacks"}
current_activity = "Waiting for the moves..."

try:
    pipeline = joblib.load("svm_pipeline.pkl")
except FileNotFoundError:
    print("No training found")
    sys.exit(1)
# looping images correlating to activity
try: 
    file_mapping = {
        "jumpingjacks": "jumpingjack",
        "lifting": "lifting",
        "rowing": "rowing",
        "running": "running"
    }
    activity_animations = {}

    for act, file_prefix in file_mapping.items():
        img1 = pyglet.image.load(f'assets/{file_prefix}_1.png')
        img2 = pyglet.image.load(f'assets/{file_prefix}_2.png')

        img1.anchor_x = img1.width // 2
        img1.anchor_y = img1.height // 2
        img2.anchor_x = img2.width // 2
        img2.anchor_y = img2.height // 2

        activity_animations[act] = Animation.from_image_sequence(
            [img1, img2], duration=0.4, loop=True # type: ignore
        )
except FileNotFoundError as e:
    print("No imagerinos found")
    activity_animations = {}

current_sprite = None
# text labels
activity_label = pyglet.text.Label(
    text = current_activity, font_name='Play', font_size=36,
    x=win.width // 2, y = win.height - 100,
    anchor_x='center', anchor_y='center', color=(0, 0, 100, 255)
)

status_label = pyglet.text.Label(
    text=f"Target: {TARGET_TIME}s", font_name='Play', font_size=24,
    x=win.width // 2, y=win.height - 150,
    anchor_x='center', anchor_y='center', color=(50, 50, 50, 255) 
)


features = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z', 'acc_mag', 'gyro_mag']
 
# get activity data
def update_prediction(dt):
    global current_activity, current_streak_time, last_activity, current_sprite
    
    accel = sensor.get_value("accelerometer")
    gyro = sensor.get_value("gyroscope")

    if accel is None or gyro is None:
        return
    # current data
    current_data = {
        "timestamp": time.time(),
        "acc_x": accel.get("x", 0),
        "acc_y": accel.get("y", 0),
        "acc_z": accel.get("z", 0),
        "gyro_x": gyro.get("x", 0),
        "gyro_y": gyro.get("y", 0),
        "gyro_z": gyro.get("z", 0),
        "acc_mag": np.sqrt( accel.get("x", 0)**2 +  accel.get("y", 0)**2 +  accel.get("z", 0)**2),
        "gyro_mag": np.sqrt(gyro.get("x", 0)**2 + gyro.get("y", 0)**2 + gyro.get("z", 0)**2)
    }
    
    df_live = pd.DataFrame([current_data])
    # predicting live DIPPID Data (labeling) 
    try:
        # labeling process
        prediction = pipeline.predict(df_live[features])[0]
        prediction_buffer.append(prediction)
        
        most_common_prediction = collections.Counter(prediction_buffer).most_common(1)[0][0]
        smoothed_activity = class_dict_reverse.get(most_common_prediction, "Unknown")
        # check last values for correlating sprites
        if smoothed_activity == last_activity:
            current_streak_time += dt
        
        else:
            current_streak_time = 0.0
            last_activity = smoothed_activity

            if smoothed_activity in activity_animations:
                current_sprite = pyglet.sprite.Sprite(
                    img=activity_animations[smoothed_activity], 
                    x=win.width // 2, 
                    y=win.height // 2 - 50
                )
            else:
                current_sprite = None

        activity_label.text = f"Activity: {smoothed_activity}"
        # fitness goal achieved
        if current_streak_time >= TARGET_TIME:
            status_label.text = f"EXQUISITE! {TARGET_TIME}s reached!"
            status_label.color = (0, 150, 0, 255) 
        else:
            status_label.text = f"Don't you dare give up: {current_streak_time:.1f}s / {TARGET_TIME}s"
            status_label.color = (50, 50, 50, 255) 
            
    except Exception as e:
        print("Can't predict these moves man")

@win.event
def on_draw():
    win.clear()
    activity_label.draw()
    status_label.draw()

    if current_sprite is not None:
        current_sprite.draw()

@win.event
def on_close():
    print("Trainingsession done")
    sensor.disconnect()

if __name__ == "__main__":
    pyglet.clock.schedule_interval(update_prediction, 0.1)
    pyglet.app.run()


    

