[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/CjRQqtHi)

# Repo Structure

## Assignment
This repository contains all files for the Assignment No. 03

The Assignment No. 03 is split into following exercises:
1. Gathering Training Data (5P)
2. Activity Recognition (10P)

## Folder Structure
* **`assets/`**: pictures and font used in `fitness_trainer.py`
* **`dataset-only-acc/`**: csv files of all people with only acceleration data
* **`dataset/`**: csv files of all people from: https://github.com/UT-ITT/assignment-03-training-data-join-this-team-to-upload-your-data
* **`team-data/`**: contains only csv files of team members
* **`tutor-dataset/`**: here should be the csv files be paste into of tutors dataset

---
## Virtual Environment

This project is written in **Python** and was developed using **Python 3.14.4**. 

To run the project locally, please follow these initialization steps:

1. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   ```
   *(Note: Depending on your system, you might need to use `python` or explicitly `python3.14` instead).*

2. **Activate the Virtual Environment:**
   Before installing any dependencies or running the scripts, you must activate the newly created environment:

   * **Mac / Linux:**
     ```bash
     source venv/bin/activate
     ```
   * **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   * **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

   Once activated, you should see `(venv)` at the beginning of your command line prompt.

3. **Install Dependencies:**
   Innstall all the required packages from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

Your setup is now complete and the project is ready to go!

---
# 1. Gathering Training Data

The file **`gather-data.py`** captures IMU sensor data from a DIPPID device and saves it as a CSV file for activity recognition training.

## Start Guide:

1. **Start in Terminal:**
   ```bash
   python3 gather-data.py <name> <number>
   ```
   *Example:* `python3 gather-data.py gymarino 1`

2. **Select activity to capture data from selection list via numbers:**
   ```text
   [1] running
   [2] rowing
   [3] lifting
   [4] jumpingjacks
   ```

3. Press **Button 1** on DIPPID Device to start the 10 seconds capture.
4. Have fun doing something good for science (and your health).

### How it works:
* Connects to the DIPPID device via UDP 
* Waits for **Button 1** press on the device to start recording
* Records accelerometer (`acc_x/y/z`) and gyroscope (`gyro_x/y/z`) data for **10 seconds**
* Resamples the data to **100 Hz** using pandas
* Saves to `data/<name>-<activity>-<number>.csv` with columns: `id`, `timestamp`, `acc_x`, `acc_y`, `acc_z`, `gyro_x`, `gyro_y`, `gyro_z`

  > **DISCLAIMER:** The folder *data* is not used directly as source folder in activity-recognizer.py since the folder *dataset* contains already the data of all course participants. But otherwise we would have used the same folder for saving the gather-data.py output as the activity-recognizer.py input folder.

**Supported activities:** `running`, `rowing`, `lifting`, `jumpingjacks`

---

# Activity Recognition

The Fitness Trainer uses the files **`activity_recognizer.py`** (to recognize the input activity form the `fitness_trainer.py` live datastream) and the **`fitness_trainer.py`** file (to display the Fitness Trainer Game and to fetch the DIPPID device data).

# Startup guide

## Training Model

### Start with our Dataset

1. **Start in Terminal:**
   ```bash
   python3 activity_recognizer.py
   ```
2. **Output:**
   The Terminal will output in this order:
   
   1. Data fetching from the csv files
      ```text
      pray to any god that the data fetching works
      lets see if the prayer worked
      ```
   2. Creation of the Dataset
      ```text
      finally the test dataset and training dataset was created!
      ```
   3. Start of training the model with the train_set.csv file
      ```text
      Now lets do some training!
      ```
   4. Start the testing of the model with the test_set.csv file
      ```text
      We prepared the Model some meal (data) and fed it. Now lets test if we actually fed it right
      ```
   5. Display of accuracy result
      ```text
      and the accuracy is *drumroll* <accuracy in %>
      ```

### Start with Tutor Dataset

> [!CAUTION]
> There are two ways to include the tutor dataset
* If you want to use your dataset (csv files) <ins>COMBINED</ins> with the ones from everyone than please add your csv files into following existing folder:
  ```text
  dataset
  ```
  * After that follow from Step **iii**
  
* If you want to use <ins>SOLELY</ins> your dataset (csv files) please follow the upcoming instructions:

  1. Upload your csv files into the following folder:
     **`tutor-dataset`**
     > **DISCLAIMER:** Please just through the csv files into the folder without making subfolders. All csv files schould be lying directly in the *tutor-dataset* folder.

  2. Go into following file:
     **`activity_recognizer.py`**

     Follow the TODO steps in line 15-18. The lines look currently like this:
     ```python
     # TODO comment in this line to use the files in the folder tutor-dataset
     # parser.add_argument("--data", type=str, default="./tutor-dataset")
     # TODO comment out this line to use the line above
     parser.add_argument("--data", type=str, default="./dataset")
     args = parser.parse_args()
     ```
     After the changes it should look like this:
     ```python
     # TODO comment in this line to use the files in the folder tutor-dataset
     parser.add_argument("--data", type=str, default="./tutor-dataset")
     # TODO comment out this line to use the line above
     # parser.add_argument("--data", type=str, default="./dataset")
     args = parser.parse_args()
     ```

  3. **Start in Terminal:**
     ```bash
     python3 activity_recognizer.py
     ```
     
  4. **Output:**
     The Terminal will output in this order:
     
     1. Data fetching from the csv files
        ```text
        pray to any god that the data fetching works
        lets see if the prayer worked
        ```
     2. Creation of the Dataset
        ```text
        finally the test dataset and training dataset was created!
        ```
     3. Start of training the model with the train_set.csv file
        ```text
        Now lets do some training!
        ```
     4. Start the testing of the model with the test_set.csv file
        ```text
        We prepared the Model some meal (data) and fed it. Now lets test if we actually fed it right
        ```
     5. Display of accuracy result
        ```text
        and the accuracy is *drumroll* <accuracy in %>
        ```

---

## Start the Fitness App

1. Make sure your Android Device is in the same network as your PC/Notebook
2. Open the DIPPID App on your phone and enter following values:
   * **IP Adress:** 
     ```bash
     <IP Adress of your current PC/Notebook>
     ```
   * **Port:** 
     ```bash
     5700
     ```
3. Now enable the toggle **send data**
4. Start in Terminal:
   ```bash
   python3 fitness_trainer.py
   ```
5. Enjoy doing something good for your health

---

## How it works

### `activity_recignizer.py`

The file **`activity_recignizer.py`** handles the creation of the training and test dataset and the training of the model. 

1. **Cleanup**:
   First all the csv files get cleaned up by deleting all unnecessary columns that are not in our standard column set or rows that have at least one missing values. 
2. **Adding columns**:
   Then the columns **`acc_mag`** and **`gyro_mag`** get created with the magnitude formula and added to the dataset.
3. **Filtering and classification**:
   After that the dataset get filtered by creating the mean average for signal processing. To classify the data each data gets the classification of their corresponding filename. The classification is mapped with a directionary like followed:
   ```python
   class_dict = {"rowing": 0, 
                 "running": 1, 
                 "lifting": 2,
                 "jumpingjacks": 3}
   ```
4. **Finishing**: 
   All data gets then randomized with the seed 42 (answer to everything) and split via the `train_test_split` function into 70% Training Set and 30% Test Set. 
5. **Training**:
   The training data gets loaded from the generated `train_set.csv`. Then a Machine Learning pipeline is set up. First it uses a `StandardScaler` to scale the data. For the actual classification, a `RandomForestClassifier` is used instead of a Support Vector Machine. The pipeline gets fitted with our sensor features and target classifications and is saved as `svm_pipeline.pkl` via joblib.
6. **Testing**:
   To check if the model actually learned something, the test data gets loaded from the `test_set.csv`. The script loads the saved `svm_pipeline.pkl` and uses the predict function on our test features. At the very end, it calculates the overall accuracy score and prints out a detailed classification report.

### `fitness_trainer.py`

The file **`fitness_trainer.py`** is where the actual fun begins! It takes our trained model, connects to the DIPPID device and turns the workout into a little interactive game. The script is split into two main parts: 
* the core functionality 
* the gamification (visualization)

#### Core Functionality

1. **Sensor connection**:
   The script establishes a UDP connection via the DIPPID library (Port 5700) to fetch live accelerometer and gyroscope data straight from form the DIPPID Device.
2. **Live data preparation**:
   Just like in our training script the live data needs to be formatted. The `acc_mag` and `gyro_mag` variables are calculated directly so the real-time data  matches the exact structure our model expects.
3. **Prediction & Smoothing**:
   The live data is fed into our previously saved `svm_pipeline.pkl`. Because raw sensor data can sometimes jitter or have tiny dropouts, the script uses a `prediction_buffer` (saving the last 10 predictions). It picks the most common prediction from that buffer to ensure the activity recognition is smooth and doesn't constantly flicker between different states.

#### Gamification (Visualization)

1. **Workout playlist**:
   A built-in game logic runs you through a `GAME_PLAYLIST` consisting of rowing, running, lifting and jumpingjacks. You get exactly 10 seconds (`TARGET_TIME`) to perform the requested exercise while a UI timer counts down.
2. **Real-Time feedback**:
   The animated character on screen always dynamically changes to show what the model thinks you are doing right now. It also features live text feedback to hype you up and to remind you which exercise you should be doing when you dpo the wrong one.
3. **Scoring**:
   While you sweat, the game counts how many frames you spent doing the correct workout versus the total frames. Once an exercise is done, it calculates your accuracy percentage and gives you a rating (from OK up to PERFECT). After you survived the whole playlist a final overview screen presents your total workout score.

---

## Background to some design choices

### Preparation of Dataset
* In the beginning we excluded all datasets that contained only acceleration into a seperat folder (we did this manually since in discord somebody wrote which folders were only acc data).
* While working we found that the dataset from some had for example two id columns. So we deleted all double columns or colums that are not our standard base columns `['id', 'timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']`.
* Additionally some datasets had rows with some missing values (probably not tracked right or other causes like latency etc.). To clean those up we iterated over every file excluded those rows. We also excluded all files that had not our standard naming convention since from there we know which exercise correlates to the file.
  * The classification which rows to keep was that every row that had one missing value will be deleted (not included in our training/test dataset). Why? Because we can't exchange those missing values with benchmark/baseline values and know from the start that those would be outliers.
* We choose the RandomForest since it's way faster than the svm. That's because the RandomForest has a lot of small decision trees which makes the process faster just choosing between two options to go further. The accuracy grew over 10% with it.
* For this line of code (line 55):
  ```python
  df_cleaned[sensor_col] = df_cleaned[sensor_check].rolling(window=20, min_periods=1).mean()
  ```
  we choose 20 as the window value. We started with 5 and got up to 20 in 5-values. With each increase the accuracy grew up to 2%.
* Adding the columns **`acc_mag`** and **`gyro_mag`** stems from the idea to calculate the geometric length (magnitude) of the 3D vectors from the X, Y, and Z axes of the accelerometer and gyroscope sensors. These columns combine the directional data into a single value that represents the absolute overall intensity of the movement, completely independent of the orientation of the device. We did this because the people who collected the data might have held their phones probably in different ways or positions (see sources for formula).
* We split the training and dataset with 70/30 rule since it's common in Machine Learning like the 80/20 rule, but we wanted to have a little more test data (see sources).

### Gamification
* We wanted to make the game fun thats why the pictures **DONT** display the activity you _should_ do but rather the activity _you are doing_ RIGHT NOW. That way the User can **directly** see what the Fitness Trainer thinks they're doing, since reading text while e.g. jumping is very hard (for some people).

---

## Sources
* **understanding support vector machine:** [Kopal Jain's Medium Article](https://kopaljain95.medium.com/how-to-improve-support-vector-machine-9561ab96ed18) and [Basic comparison between RandomForest, SVM and XGBoost](https://medium.com/@ap.nattapoj_st/basic-comparison-between-randomforest-svm-and-xgboost-0e5862871175)
* **scikit-learn:** [Official Documentation](https://scikit-learn.org/stable/) and [RandomForestClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier)
* **splitting dataset:** [Optimal data split](https://medium.com/@gunkurnia/choosing-the-optimal-data-split-for-machine-learning-80-20-vs-70-30-0fd266710236)
* **pyglet (fancy stuff):** [Graphics Module](https://pyglet.readthedocs.io/en/latest/modules/graphics/index.html)
* **magnitude formula:** [Cuemath](https://www.cuemath.com/magnitude-of-a-vector-formula/)
* **gym pic:** [Müllers Gym](https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fwww.muellers-gym.de%2F&ved=0CBUQjRxqFwoTCLD0z5T0vpQDFQAAAAAdAAAAABAh&opi=89978449)
