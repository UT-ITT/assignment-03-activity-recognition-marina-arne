# this program visualizes activities with pyglet

import sys
import time
import os
import pyglet
import joblib

import pandas as pd

from DIPPID import SensorUDP

PORT = 5700


sensor = SensorUDP(PORT)
WIDTH_SIZE = 600
HEIGHT_SIZE = 800

win = pyglet.window.Window(WIDTH_SIZE, HEIGHT_SIZE)
win_popup = None

class_dict_reverse = {0: "rowing", 1: "running", 2: "lifting", 3: "jumpingjacks"}

try:
    clf = joblib.load('svm_model.pkl')
    scaler = joblib.load('std_scaler.pkl')
    mms = joblib.load('minmax_scaler.pkl')
except FileNotFoundError:
    print("No training found")
    sys.exit(1)

# get activity data
def on_accel(_):
    
    accel = sensor.get_value("accelerometer")
    gyro = sensor.get_value("gyroscope")

    if accel is None or gyro is None:
        return
    
    current_data = {"timestamp": time.time(),
    "acc_x": accel.get("x", 0),
    "acc_y": accel.get("y", 0),
    "acc_z": accel.get("z", 0),
    "gyro_x": gyro.get("x", 0),
    "gyro_y": gyro.get("y", 0),
    "gyro_z": gyro.get("z", 0)
    }
    
    df_live = pd.DataFrame([current_data])
    
    scaled_std = scaler.transform(df_live)
    scaled_live = mms.transform(scaled_std)
    prediction = clf.predict(scaled_live)[0]
    class_dict_reverse.get(prediction, "Unknown")
    print(class_dict_reverse.get(prediction, "Unknown"))
    



####https://www.datacamp.com/tutorial/svm-classification-scikit-learn-python


sensor.disconnect()

win.event
def on_draw():
    win.clear()

    

