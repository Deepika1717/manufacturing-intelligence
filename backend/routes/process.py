from fastapi import APIRouter, HTTPException
from services.data_service import get_process_data, detect_anomalies

router = APIRouter()


@router.get("/timeline")
def get_process_timeline():
    df = get_process_data()
    records = df[["Time_Minutes", "Phase", "Temperature_C", "Pressure_Bar",
                   "Humidity_Percent", "Motor_Speed_RPM", "Power_Consumption_kW",
                   "Vibration_mm_s", "Flow_Rate_LPM"]].round(3).to_dict(orient="records")
    return {"data": records, "total_records": len(records)}


@router.get("/phases")
def get_phase_summary():
    df = get_process_data()
    summary = (
        df.groupby("Phase").agg(
            avg_power=("Power_Consumption_kW", "mean"),
            max_power=("Power_Consumption_kW", "max"),
            avg_temp=("Temperature_C", "mean"),
            avg_vibration=("Vibration_mm_s", "mean"),
            duration=("Time_Minutes", "count")
        ).round(2).reset_index()
    )
    return {"phases": summary.to_dict(orient="records")}


@router.get("/anomalies")
def get_anomalies():
    df = get_process_data()
    anomalies = detect_anomalies(df)
    return {"anomalies": anomalies, "count": len(anomalies)}


@router.get("/energy-trend")
def get_energy_trend():
    df = get_process_data()
    records = df[["Time_Minutes", "Phase", "Power_Consumption_kW"]].round(3).to_dict(orient="records")
    phase_avg = df.groupby("Phase")["Power_Consumption_kW"].mean().round(2).to_dict()
    total_energy = round(float(df["Power_Consumption_kW"].mean()), 2)
    return {"trend": records, "phase_averages": phase_avg, "overall_avg": total_energy}
