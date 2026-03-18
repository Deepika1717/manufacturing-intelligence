from fastapi import APIRouter
from services.data_service import get_process_data, get_production_data, get_golden_batch
import numpy as np

router = APIRouter()


@router.get("/energy-patterns")
def energy_patterns():
    df = get_process_data()
    patterns = []
    high_vib = df[df["Vibration_mm_s"] > df["Vibration_mm_s"].quantile(0.8)]
    if not high_vib.empty:
        avg_power_high_vib = round(float(high_vib["Power_Consumption_kW"].mean()), 2)
        avg_power_normal = round(float(df[df["Vibration_mm_s"] <= df["Vibration_mm_s"].quantile(0.8)]["Power_Consumption_kW"].mean()), 2)
        patterns.append({
            "pattern": "High Vibration → Increased Energy",
            "condition": "Vibration > 80th percentile",
            "impact": f"+{round(avg_power_high_vib - avg_power_normal, 2)} kW",
            "severity": "High" if avg_power_high_vib - avg_power_normal > 10 else "Medium",
            "description": "Equipment vibration causes mechanical inefficiency, drawing extra power."
        })
    high_humidity = df[df["Humidity_Percent"] > 50]
    if not high_humidity.empty:
        avg_power_high_hum = round(float(high_humidity["Power_Consumption_kW"].mean()), 2)
        avg_power_low_hum = round(float(df[df["Humidity_Percent"] <= 50]["Power_Consumption_kW"].mean()), 2)
        patterns.append({
            "pattern": "High Humidity → Process Inefficiency",
            "condition": "Humidity > 50%",
            "impact": f"+{round(avg_power_high_hum - avg_power_low_hum, 2)} kW",
            "severity": "Medium",
            "description": "High humidity increases drying load and granulation resistance, raising power consumption."
        })
    high_speed = df[df["Motor_Speed_RPM"] > 500]
    if not high_speed.empty:
        avg_power_high_spd = round(float(high_speed["Power_Consumption_kW"].mean()), 2)
        avg_power_low_spd = round(float(df[df["Motor_Speed_RPM"] <= 500]["Power_Consumption_kW"].mean()), 2)
        patterns.append({
            "pattern": "High Motor Speed → Peak Power Draw",
            "condition": "Motor Speed > 500 RPM",
            "impact": f"+{round(avg_power_high_spd - avg_power_low_spd, 2)} kW",
            "severity": "High",
            "description": "Motor operates at high efficiency only within optimal RPM band. Overdriving wastes energy."
        })
    return {"patterns": patterns}


@router.get("/kpi-summary")
def kpi_summary():
    proc = get_process_data()
    prod = get_production_data()
    return {
        "total_batches": int(prod["Batch_ID"].nunique()),
        "avg_hardness": round(float(prod["Hardness"].mean()), 1),
        "avg_dissolution": round(float(prod["Dissolution_Rate"].mean()), 1),
        "avg_energy_kw": round(float(proc["Power_Consumption_kW"].mean()), 2),
        "avg_friability": round(float(prod["Friability"].mean()), 3),
        "avg_uniformity": round(float(prod["Content_Uniformity"].mean()), 1),
        "pass_rate": round(float((
            (prod["Hardness"] >= 60) & (prod["Dissolution_Rate"] >= 85) &
            (prod["Friability"] <= 1.5) & (prod["Content_Uniformity"] >= 90)
        ).mean() * 100), 1)
    }


@router.get("/phase-energy-breakdown")
def phase_energy_breakdown():
    df = get_process_data()
    breakdown = df.groupby("Phase").agg(
        avg_power=("Power_Consumption_kW", "mean"),
        total_energy=("Power_Consumption_kW", "sum"),
        duration_min=("Time_Minutes", "count")
    ).round(2).reset_index()
    breakdown["energy_share_pct"] = round(
        breakdown["total_energy"] / breakdown["total_energy"].sum() * 100, 1
    )
    return {"breakdown": breakdown.to_dict(orient="records")}
