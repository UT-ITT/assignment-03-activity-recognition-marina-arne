# this program recognizes activities
import activity_recognizer as activity
import matplotlib
from matplotlib import pyplot as plt
from sklearn import svm # scikit-learn
import seaborn as sns # for nice visualizations
import pandas as pd # for loading the data from csv
import numpy as np
from sklearn.preprocessing import scale, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn import svm
import glob 
import joblib
from sklearn.svm import SVC
import os
import argparse

#TODO's
# 1. import all training data (jumping, rowing, running, lifting)
# 2. split into two sets (train dataset, test data set)
# 3. preprocess data before training (e.g. filtering, normalization, transformation into frequency domain, ...)
# 4. train ML classifier
# 5. evaluate accuracy of model with test data set
# 6.  The  program should  then predict activities based on  sensor data  from  the DIPPID  device. The prediction  should 
# run continuously without requiring further intervention by the user. 
# 7. visualize fitness trainer with pyglet

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, default="./dataset")
args = parser.parse_args()

path = args.data

# prepare data for edge cases (contains double columns, missing values etc.)
dataset_csv = glob.glob(os.path.join(path, "*.csv"))
print("pray to any god that it works")

df_list = []
class_dict = {"rowing": 0, 
              "running": 1, 
              "lifting": 2,
              "jumpingjacks": 3}

col_structure = ['id', 'timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']

for file_path in dataset_csv:
    df = pd.read_csv(file_path)
    # iterate through every file and delete false columns
    keep_indices = [col for col in col_structure if col in df.columns]
    df_cleanup = df[keep_indices]
    # checking for rows with 0 and columns with 1
    df_cleaned = df_cleanup.dropna(axis=0)
    # get exercise from filename and row with corresponding classification
    file_name = os.path.basename(file_path)
    name_cut = file_name.replace(".csv", "")
    name_split = name_cut.split("-")
    # filter out every file that doesn't match filenaming convention
    try:
        exercise = name_split[1]
        if exercise in class_dict:
            class_exercise = class_dict.get(exercise)
            df_cleaned["classification"] = class_exercise
            df_list.append(df_cleaned)
    except IndexError:
        pass
print("lets see if the prayer worked")
# join all lists
df_collection = pd.concat(df_list, ignore_index=True)
# randomize dataset before split (42 as seed since it's the answer of the universe)
train_set, test_set = train_test_split(df_collection, test_size=0.30, random_state=42)

train_set.to_csv("train_set.csv", index=False)
test_set.to_csv("test_set.csv", index=False)
print("finally the test dataset and training dataset was created! Now lets do some training!")

"""
# mean removal train data
train_data = pd.read_csv("train_set.csv")

scaler = StandardScaler()
scaled_samples = scaler.fit_transform(train_data[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']])

train_mean = train_data.copy()
train_mean[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']] = scaled_samples
# minmax scaler
mms = MinMaxScaler()
mms.fit(train_mean[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']])

# normalized
scaled_samples = mms.transform(train_mean[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']])
train_normalized = train_mean.copy()
train_normalized[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']] = scaled_samples

# train ML classifier
x_train = train_normalized[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']]
y_train = train_normalized['classification']

clf = SVC(kernel='linear')
clf.fit(x_train, y_train)

joblib.dump(clf, 'svm_model.pkl')
joblib.dump(scaler, 'std_scaler.pkl')
joblib.dump(mms, 'minmax_scaler.pkl')

"""