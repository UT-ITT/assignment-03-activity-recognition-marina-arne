# this program visualizes activities with pyglet

import activity_recognizer as activity
import matplotlib
from matplotlib import pyplot as plt
from sklearn import svm # scikit-learn
import seaborn as sns # for nice visualizations
import pandas as pd # for loading the data from csv
import numpy as np
from sklearn.preprocessing import scale, StandardScaler, MinMaxScaler
from sklearn import svm

#TODO's
# 1. import all training data (jumping, rowing, running, lifting)
# 2. split into two sets (train dataset, test data set)
# 3. preprocess data before training (e.g. filtering, normalization, transformation into frequency domain, ...)
# 4. train ML classifier
# 5. evaluate accuracy of model with test data set
# 6.  The  program should  then predict activities based on  sensor data  from  the DIPPID  device. The prediction  should 
# run continuously without requiring further intervention by the user. 
# 7. visualize fitness trainer with pyglet

