[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/CjRQqtHi)

## gather-data.py

Captures IMU sensor data from a DIPPID device and saves it as a CSV file for activity recognition training.

**Usage:**

1. Start in Terminal:
```
python3 gather-data.py <name> <number>
```

Example: `python3 gather-data.py arne 1`

2. Select activity to capture data from selection list via numbers
```
[1] running
[2] rowing
[3] lifting
[4] jumpingjacks
```
3. Press Button 1 to start the 10 seconds capture
4. Have fun doing something good for science (and your health)

**How it works:**

- Connects to the DIPPID device via UDP 
- Waits for **Button 1** press on the device to start recording
- Records accelerometer (`acc_x/y/z`) and gyroscope (`gyro_x/y/z`) data for **10 seconds**
- Resamples the data to **100 Hz** using pandas
- Saves to `data/<name>-<activity>-<number>.csv` with columns: `id, timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z`

**Supported activities:** `running`, `rowing`, `lifting`, `jumpingjacks`


#TODO UPDATE README
# fitness_trainer.py

# activity_recognizer.py

## Background to some design choices

### Preperation of Dataset
- In the beginning we excluded all datasets that contained only acceleration into a seperat folder (we did this manually since in discord somebody wrote which folders)
- While working we found that the dataset from someone had for example two id columns. So we deleted all double columns or colums that are not our standard base columns ['id', 'timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']
- Additionally some datasets had rows with some missing values (probably not tracked right or other causes like latency etc.). To clean those up we iterated over every file excluded those rows. We also excluded all files that had not our standard naming convention since from there we know which exercise correlates to the file.
    - The classification with rows to keep was that every row that had one missing value will be deleted (not included in our training/test dataset). Why? Because we can't exchange those missing values with benchmark/baseline values and know that those would be outliers.


## sources
- pyglet batch: https://pyglet.readthedocs.io/en/latest/modules/graphics/index.html
- magnitude formula: https://www.cuemath.com/magnitude-of-a-vector-formula/

- gym pic: https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fwww.muellers-gym.de%2F&ved=0CBUQjRxqFwoTCLD0z5T0vpQDFQAAAAAdAAAAABAh&opi=89978449