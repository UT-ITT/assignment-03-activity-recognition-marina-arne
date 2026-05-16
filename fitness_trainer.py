# this program visualizes activities with pyglet
import sys
import time
import pyglet
from pyglet import font, resource
from pyglet.image.animation import Animation
import joblib
import numpy as np
import collections
import pandas as pd

from DIPPID import SensorUDP

#TODO
#scale pictures for window
#print accuracy
#add background


# import font
font.add_file('./assets/Play-Regular.ttf')
play_reg = font.load('Play')

PORT = 5700

sensor = SensorUDP(PORT)
WIDTH_SIZE = 600
HEIGHT_SIZE = 800

bg_batch = pyglet.graphics.Batch()
sprite_batch = pyglet.graphics.Batch()
ui_batch = pyglet.graphics.Batch()
gym_bg = resource.image("assets/gym.png")
bg_sprite = pyglet.sprite.Sprite(img=gym_bg, batch=bg_batch)

bg_sprite.scale_x = WIDTH_SIZE / gym_bg.width
bg_sprite.scale_y = HEIGHT_SIZE / gym_bg.height

win = pyglet.window.Window(WIDTH_SIZE, HEIGHT_SIZE, caption="Gymarino")

pyglet.gl.glClearColor(1, 1, 1, 1)


TARGET_TIME = 10.0
current_streak_time = 0.0
last_activity = "Waiting for the moves..."
prediction_buffer = collections.deque(maxlen=10)

# game logic
GAME_PLAYLIST = ["rowing", "running", "lifting", "jumpingjacks"]
current_game_index = 0
game_timer = 0.0

correct_frames = 0
total_frames = 0
last_exercise_score = ""



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
instruction_label = pyglet.text.Label(
    text = "GET READY", font_name='Play', font_size=42,
    x=win.width // 2, y = win.height - 100,
    anchor_x='center', anchor_y='center', color=(255, 0, 100, 255),
    batch=ui_batch
)

timer_label = pyglet.text.Label(
    text = "", font_name='Play', font_size=36,
    x=win.width // 2, y = win.height - 160,
    anchor_x='center', anchor_y='center', color=(50, 50, 50, 255),
    batch=ui_batch
)

feedback_label = pyglet.text.Label(
    text = "", font_name='Play', font_size=36,
    # height in 60er steps since 60 is a nice number
    x=win.width // 2, y = win.height - 220,
    anchor_x='center', anchor_y='center', color=(100, 100, 100, 255),
    batch=ui_batch
)

scoreboard_label = pyglet.text.Label(
    text = "Score will appear here", font_name='Play', font_size=36,
    x=win.width // 2, y = 100,
    anchor_x='center', anchor_y='center', color=(100, 100, 255, 255),
    batch=ui_batch
)

features = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z', 'acc_mag', 'gyro_mag']
 
# get activity data
def update_prediction(dt):
    global game_timer, current_game_index, correct_frames, total_frames, last_exercise_score, last_activity, current_sprite
    
# game over check
    if current_game_index >=len(GAME_PLAYLIST):
        instruction_label.text = "Lets rest a bit and see how good (or maybe bad) you were hehe"
        instruction_label.color = (0, 180, 0, 255)
        timer_label.text = "DAAAAMN, somebody knows how to work it!"
        feedback_label.text = ""
        # deleting sprites after use
        if current_sprite is not None:
            current_sprite.delete()

        current_sprite = None
        return
    
    target_activity = GAME_PLAYLIST[current_game_index]

    instruction_label.text = f"MOVE NOW: {target_activity.upper()}"
    instruction_label.color = (255, 0, 100, 255)


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
        if smoothed_activity != last_activity:
            last_activity = smoothed_activity

            if current_sprite is not None:
                current_sprite.delete()

            if smoothed_activity in activity_animations:
                current_sprite = pyglet.sprite.Sprite(
                    img = activity_animations[smoothed_activity],
                    x = win.width // 2, y = win.height // 2 - 50,
                    batch=sprite_batch
                )

                current_sprite.scale = 0.5
                
            else:
                current_sprite = None
        
        game_timer += dt
        total_frames += 1
        # activity feedback 
        if smoothed_activity == target_activity:
            correct_frames += 1
            feedback_label.text = "OFFICER ARREST THEM, because they killed it"
            feedback_label.color = (0, 180, 0, 255)
        else:
            feedback_label.text = f"Somebody can't follow instruuuctions. WRONG WORKOUT! (Detecting{smoothed_activity})"
            feedback_label.color = (200, 0, 0, 255)

        time_left = max(0.0, TARGET_TIME - game_timer)
        timer_label.text = f"Time Left: {time_left:.1f}s"
        # activity score feedback
        if game_timer > TARGET_TIME:
            accuracy = (correct_frames / total_frames) * 100
            
            if accuracy > 90: rating = "PERFECT"
            elif accuracy > 75: rating = "GREAT"
            elif accuracy > 50: rating = "GOOD"
            else: rating = "OK"

            last_exercise_score = f"Last Workout ({target_activity}): {accuracy:.1f}% Match - {rating}"
            scoreboard_label.text = last_exercise_score

            current_game_index += 1
            game_timer = 0.0
            correct_frames = 0
            total_frames = 0
            prediction_buffer.clear()
            
    except Exception as e:
        print("Can't predict these moves man")

@win.event
def on_draw():
    win.clear()
    bg_batch.draw()
    sprite_batch.draw()
    ui_batch.draw()

@win.event
def on_close():
    print("Trainingsession done")
    sensor.disconnect()

if __name__ == "__main__":
    pyglet.clock.schedule_interval(update_prediction, 0.1)
    pyglet.app.run()

