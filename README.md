[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/CjRQqtHi)

## gather-data.py

Captures IMU sensor data from a DIPPID device and saves it as a CSV file for activity recognition training.

**Usage:**

```
python3 gather-data.py <name> <activity> <number> [udp_port]
```

Example: `python3 gather-data.py arne running 1`

**How it works:**

- Connects to the DIPPID device via UDP (default port 5700)
- Waits for **Button 1** press on the device to start recording
- Records accelerometer (`acc_x/y/z`) and gyroscope (`gyro_x/y/z`) data for **10 seconds**
- Resamples the data to **100 Hz** using pandas
- Saves to `data/<name>-<activity>-<number>.csv` with columns: `id, timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z`

**Supported activities:** `running`, `rowing`, `lifting`, `jumpingjacks`
