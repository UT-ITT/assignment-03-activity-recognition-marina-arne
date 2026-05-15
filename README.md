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

## Activity Recognition - Fitness Trainer

Trains a classifier on CSV data and shows live activity predictions:

```bash
python3 fitness_trainer.py --data-dir data
```

With test data:

```bash
python3 fitness_trainer.py --data-dir data test-data
```

Demo mode (no device needed):

```bash
python3 fitness_trainer.py --demo --sample data/arne/arne-running-1.csv
```

Press `ESC` or `Q` to quit.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
