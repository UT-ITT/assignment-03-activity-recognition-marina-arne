# this program visualizes activities with pyglet

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
import os

#TODO's
# 1. import all training data (jumping, rowing, running, lifting)
# 2. split into two sets (train dataset, test data set)
# 3. preprocess data before training (e.g. filtering, normalization, transformation into frequency domain, ...)
# 4. train ML classifier
# 5. evaluate accuracy of model with test data set
# 6.  The  program should  then predict activities based on  sensor data  from  the DIPPID  device. The prediction  should 
# run continuously without requiring further intervention by the user. 
# 7. visualize fitness trainer with pyglet

path = "./dataset"

# prepare klarazwettler data (contains twice id column)
klara_path = "./klarazwettler"

klara_csv = glob.glob(os.path.join(klara_path, "*.csv"))
# iterate through every file and delete the second id column and save in folder dataset
for file_path in klara_csv:
    df = pd.read_csv(file_path)
    keep_indices = [i for i in range(len(df.columns)) if i != 2]
    df_cleanup = df.iloc[:, keep_indices]

    file_names = os.path.basename(file_path)
    target_path = os.path.join(path, file_names)

    df_cleanup.to_csv(target_path, index=False)
print("done? lets cheeeck")

# prepare all data for edge case (missing values of some columns)
# you can read more in the readme.md file under the subsection "Preperation of Dataset"

cleanup_path = "./dataset-cleaned"

dataset_csv = glob.glob(os.path.join(path, "*.csv"))
print("pray to any god that it works")

for file_path in dataset_csv:
    df = pd.read_csv(file_path)
    # checking for rows with 0 and columns with 1
    df_cleaned = df.dropna(axis=0)

    file_names = os.path.basename(file_path)
    target_path = os.path.join(cleanup_path, file_names)

    df_cleaned.to_csv(target_path, index=False)
print("lets see if the prayer worked")

join_csv = glob.glob(os.path.join(cleanup_path, "*.csv"))

df_list = []
class_dict = {"rowing": 0, 
              "running": 1, 
              "lifting": 2,
              "jumpingjacks": 3}


# go through every file, take the exercise from filename and add as new column classification with correlated indicies
for file_path in join_csv:
    file_name = os.path.basename(file_path)
    name_cut = file_name.replace(".csv", "")
    name_split = name_cut.split("-")
    exercise = name_split[1]
    class_exercise = class_dict.get(exercise)
    df_temp = pd.read_csv(file_path)
    df_temp["classification"] = class_exercise
    df_list.append(df_temp)

#df_list = [pd.read_csv(file) for file in join_csv]
df_collection = pd.concat(df_list, ignore_index=True)
# randomize before splitting dataset into to 70% training, 30% test 
train_set, test_set = train_test_split(df_collection, test_size=0.30, random_state=42)

train_set.to_csv("train_set.csv", index=False)
test_set.to_csv("test_set.csv", index=False)
print("finally the test dataset and training dataset was created! Now lets go to work!")


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
scaled_samples = s.transform(train_mean[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']])
train_normalized = train_mean.copy()
train_normalized[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']] = scaled_samples

# train ML classifier


