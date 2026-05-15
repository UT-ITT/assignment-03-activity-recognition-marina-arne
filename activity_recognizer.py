import os
import re
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

VALID_ACTIVITIES = ["running", "rowing", "lifting", "jumpingjacks"]


class ActivityRecognizer:
    def __init__(self, data_dirs=None, test_size=0.20, random_state=42):
        self.data_dirs = data_dirs or ["data"]
        self.test_size = test_size
        self.random_state = random_state
        self.classifier = None
        self.scaler = StandardScaler()
        self.feature_names = None

    def find_csv_files(self):
        files = []
        for data_dir in self.data_dirs:
            for root, _, filenames in os.walk(data_dir):
                for filename in filenames:
                    if filename.lower().endswith(".csv"):
                        files.append(os.path.join(root, filename))
        return sorted(files)

    def parse_label(self, path):
        filename = os.path.basename(path).lower()
        match = re.search(r"(running|rowing|lifting|jumpingjacks)", filename)
        if match:
            return match.group(1)
        parent = os.path.basename(os.path.dirname(path)).lower()
        if parent in VALID_ACTIVITIES:
            return parent
        raise ValueError(f"Cannot infer activity label from: {path}")

    def load_csv(self, path):
        columns = ["acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"]
        df = pd.read_csv(path, usecols=columns)
        if df.empty:
            raise ValueError(f"Empty CSV: {path}")
        return df.astype(float)

    def preprocess(self, df):
        df = df.copy()
        axes = ["acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"]
        df[axes] = df[axes].rolling(window=5, min_periods=1, center=True).mean()
        df = df.bfill().ffill().fillna(0.0)
        df["acc_mag"] = np.sqrt((df[["acc_x", "acc_y", "acc_z"]] ** 2).sum(axis=1))
        df["gyro_mag"] = np.sqrt((df[["gyro_x", "gyro_y", "gyro_z"]] ** 2).sum(axis=1))
        return df

    def extract_features(self, df):
        features = {}
        axes = ["acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z", "acc_mag", "gyro_mag"]
        
        for axis in axes:
            values = df[axis].values.astype(float)
            if len(values) == 0:
                values = np.zeros(1)
            values = values - np.mean(values)
            
            # time domain
            features[f"{axis}_mean"] = np.mean(values)
            features[f"{axis}_std"] = np.std(values)
            features[f"{axis}_min"] = np.min(values)
            features[f"{axis}_max"] = np.max(values)
            features[f"{axis}_range"] = features[f"{axis}_max"] - features[f"{axis}_min"]
            
            # frequency domain
            spectrum = np.abs(np.fft.rfft(values))
            features[f"{axis}_spec_mean"] = np.mean(spectrum)
            features[f"{axis}_spec_max"] = np.max(spectrum)
            features[f"{axis}_spec_energy"] = np.sum(spectrum ** 2)
        
        return features

    def build_dataset(self):
        csv_files = self.find_csv_files()
        if not csv_files:
            raise FileNotFoundError("No CSV files found in data directories")

        rows = []
        labels = []
        
        for path in csv_files:
            try:
                label = self.parse_label(path)
                df = self.load_csv(path)
                df = self.preprocess(df)
                rows.append(self.extract_features(df))
                labels.append(label)
            except Exception as e:
                print(f"skipping {path}: {e}")

        if not rows:
            raise FileNotFoundError("No valid CSV files found")
        
        features = pd.DataFrame(rows).fillna(0.0)
        self.feature_names = features.columns.tolist()
        return features.values, np.array(labels), self.feature_names

    def train(self):
        X, y, features = self.build_dataset()
        self.feature_names = features
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, stratify=y, random_state=self.random_state
        )
        
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.classifier = RandomForestClassifier(n_estimators=200, random_state=self.random_state)
        self.classifier.fit(X_train_scaled, y_train)

        y_pred = self.classifier.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)
        
        return {
            "accuracy": f"{accuracy:.3f}",
            "report": report,
            "model": "RandomForestClassifier",
            "samples": str(len(y))
        }

    def predict(self, df):
        if self.classifier is None:
            raise RuntimeError("Model not trained")

        df = self.preprocess(df)
        features = self.extract_features(df)
        row = np.array([features[name] for name in self.feature_names]).reshape(1, -1)
        row_scaled = self.scaler.transform(row)
        
        prediction = self.classifier.predict(row_scaled)[0]
        probs = self.classifier.predict_proba(row_scaled)[0] if hasattr(self.classifier, "predict_proba") else None
        return prediction, probs
