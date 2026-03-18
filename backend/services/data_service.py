import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

_process_df: pd.DataFrame = None
_production_df: pd.DataFrame = None


def get_process_data() -> pd.DataFrame:
    global _process_df
    if _process_df is None:
        _process_df = pd.read_excel(DATA_DIR / "batch_process_data.xlsx")
    return _process_df.copy()


def get_production_data() -> pd.DataFrame:
    global _production_df
    if _production_df is None:
        _production_df = pd.read_excel(DATA_DIR / "batch_production_data.xlsx")
    return _production_df.copy()


def get_golden_batch() -> dict:
    """Return best performing batch based on composite quality score."""
    df = get_production_data()
    df["quality_score"] = (
        (df["Hardness"] / df["Hardness"].max()) * 0.3
        + (1 - df["Friability"] / df["Friability"].max()) * 0.2
        + (df["Dissolution_Rate"] / df["Dissolution_Rate"].max()) * 0.3
        + (df["Content_Uniformity"] / df["Content_Uniformity"].max()) * 0.2
    )
    best = df.loc[df["quality_score"].idxmax()]
    return best.to_dict()


def get_energy_stats() -> dict:
    df = get_process_data()
    phase_energy = df.groupby("Phase")["Power_Consumption_kW"].agg(["mean", "max", "min"]).round(2)
    return phase_energy.to_dict()


def detect_anomalies(df: pd.DataFrame) -> list:
    anomalies = []
    mean_power = df["Power_Consumption_kW"].mean()
    std_power = df["Power_Consumption_kW"].std()
    high_power = df[df["Power_Consumption_kW"] > mean_power + 2 * std_power]
    if not high_power.empty:
        for _, row in high_power.head(5).iterrows():
            anomalies.append({
                "time": int(row["Time_Minutes"]),
                "phase": row["Phase"],
                "value": round(float(row["Power_Consumption_kW"]), 2),
                "type": "High Power Consumption",
                "severity": "High" if row["Power_Consumption_kW"] > mean_power + 3 * std_power else "Medium"
            })
    high_vib = df[df["Vibration_mm_s"] > df["Vibration_mm_s"].quantile(0.95)]
    if not high_vib.empty:
        for _, row in high_vib.head(3).iterrows():
            anomalies.append({
                "time": int(row["Time_Minutes"]),
                "phase": row["Phase"],
                "value": round(float(row["Vibration_mm_s"]), 3),
                "type": "High Vibration",
                "severity": "Medium"
            })
    return anomalies
