import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = "data"

def load_data():
    process_df = pd.read_excel(f"{DATA_DIR}/batch_process_data.xlsx")
    production_df = pd.read_excel(f"{DATA_DIR}/batch_production_data.xlsx")
    return process_df, production_df

def compute_energy_features(process_df):
    agg = process_df.groupby('Batch_ID').agg(
        avg_temp=('Temperature_C', 'mean'),
        avg_pressure=('Pressure_Bar', 'mean'),
        avg_humidity=('Humidity_Percent', 'mean'),
        avg_motor_speed=('Motor_Speed_RPM', 'mean'),
        avg_vibration=('Vibration_mm_s', 'mean'),
        avg_flow_rate=('Flow_Rate_LPM', 'mean'),
        avg_compression=('Compression_Force_kN', 'mean'),
        avg_power=('Power_Consumption_kW', 'mean'),
    ).reset_index()
    return agg

class ManufacturingMLService:
    def __init__(self):
        self.quality_models = {}
        self.energy_model = None
        self.scaler_quality = StandardScaler()
        self.scaler_energy = StandardScaler()
        self.golden_batch = None
        self.feature_names = []
        self._train()

    def _train(self):
        process_df, production_df = load_data()
        energy_agg = compute_energy_features(process_df)
        merged = production_df.merge(energy_agg, on='Batch_ID', how='left')

        quality_features = [
            'Granulation_Time', 'Binder_Amount', 'Drying_Temp', 'Drying_Time',
            'Compression_Force', 'Machine_Speed', 'Lubricant_Conc', 'Moisture_Content',
            'avg_temp', 'avg_pressure', 'avg_humidity', 'avg_motor_speed',
            'avg_vibration', 'avg_flow_rate', 'avg_compression'
        ]
        quality_targets = ['Hardness', 'Friability', 'Dissolution_Rate',
                           'Content_Uniformity', 'Disintegration_Time', 'Tablet_Weight']

        merged_clean = merged.dropna(subset=quality_features + quality_targets)
        self.feature_names = quality_features

        X = merged_clean[quality_features]
        Xs = self.scaler_quality.fit_transform(X)

        for target in quality_targets:
            y = merged_clean[target]
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(Xs, y)
            self.quality_models[target] = model

        # Energy model
        energy_features = ['avg_temp', 'avg_pressure', 'avg_humidity',
                           'avg_motor_speed', 'avg_vibration', 'avg_flow_rate', 'avg_compression']
        Xe = energy_agg[energy_features].dropna()
        ye = energy_agg.loc[Xe.index, 'avg_power']
        Xe_s = self.scaler_energy.fit_transform(Xe)
        self.energy_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.energy_model.fit(Xe_s, ye)
        self.energy_feature_names = energy_features

        # Golden batch: best by Hardness/Dissolution
        score = merged_clean['Hardness'] * 0.4 + merged_clean['Dissolution_Rate'] * 0.6
        best_idx = score.idxmax()
        self.golden_batch = merged_clean.loc[best_idx, quality_features].to_dict()

    def predict(self, inp: dict) -> dict:
        # Build feature vector
        feat = {
            'Granulation_Time': inp.get('granulation_time', 16),
            'Binder_Amount': inp.get('binder_amount', 9),
            'Drying_Temp': inp.get('drying_temp', 59),
            'Drying_Time': inp.get('drying_time', 28),
            'Compression_Force': inp.get('compression_force', 11.6),
            'Machine_Speed': inp.get('machine_speed', 169),
            'Lubricant_Conc': inp.get('lubricant_conc', 1.2),
            'Moisture_Content': 2.0,
            'avg_temp': inp.get('temperature', 35),
            'avg_pressure': inp.get('pressure', 1.0),
            'avg_humidity': inp.get('humidity', 38),
            'avg_motor_speed': inp.get('motor_speed', 121),
            'avg_vibration': inp.get('vibration', 2.9),
            'avg_flow_rate': inp.get('flow_rate', 1.6),
            'avg_compression': inp.get('compression_force', 3.0),
        }

        X = pd.DataFrame([feat])[self.feature_names]
        Xs = self.scaler_quality.transform(X)

        quality = {}
        for target, model in self.quality_models.items():
            quality[target] = round(float(model.predict(Xs)[0]), 3)

        # Energy
        Xe = pd.DataFrame([{k: feat[k] for k in self.energy_feature_names}])
        Xe_s = self.scaler_energy.transform(Xe)
        power = float(self.energy_model.predict(Xe_s)[0])
        co2 = power * 0.233  # kg CO2/kWh factor
        efficiency = max(0, min(100, 100 - (power / 66.07) * 100 + 50))

        # SHAP-like importance (use feature importances from RF)
        importances = dict(zip(
            self.energy_feature_names,
            self.energy_model.feature_importances_.tolist()
        ))

        # Root cause analysis
        root_causes = self._analyze_root_causes(inp, power)
        anomaly = self._detect_anomaly(inp, power)

        # Golden deviation
        golden_dev = {}
        for k, v in self.golden_batch.items():
            current = feat.get(k, v)
            dev = round(((current - v) / (abs(v) + 1e-9)) * 100, 1)
            golden_dev[k] = {'current': round(current, 2), 'golden': round(v, 2), 'deviation': dev}

        return {
            'quality': {
                'hardness': quality.get('Hardness', 0),
                'friability': quality.get('Friability', 0),
                'dissolution_rate': quality.get('Dissolution_Rate', 0),
                'content_uniformity': quality.get('Content_Uniformity', 0),
                'disintegration_time': quality.get('Disintegration_Time', 0),
                'tablet_weight': quality.get('Tablet_Weight', 0),
            },
            'energy': {
                'power_consumption': round(power, 2),
                'energy_status': 'High' if power > 40 else 'Normal',
                'co2_emissions': round(co2, 2),
                'efficiency_score': round(efficiency, 1),
            },
            'root_causes': root_causes,
            'anomaly': anomaly,
            'golden_deviation': golden_dev,
            'shap_importance': importances,
        }

    def _analyze_root_causes(self, inp, power):
        causes = []
        if inp.get('vibration', 0) > 7:
            causes.append({'issue': 'High Vibration Detected', 'severity': 'High',
                           'recommendation': 'Inspect motor bearings and mounting fixtures. Schedule preventive maintenance.'})
        if inp.get('humidity', 0) > 55:
            causes.append({'issue': 'Elevated Humidity Level', 'severity': 'Medium',
                           'recommendation': 'Activate dehumidification system. Check HVAC settings and sealing.'})
        if inp.get('temperature', 0) > 55:
            causes.append({'issue': 'Temperature Exceeds Threshold', 'severity': 'High',
                           'recommendation': 'Reduce drying temperature. Check cooling system integrity.'})
        if inp.get('motor_speed', 0) > 700:
            causes.append({'issue': 'Motor Speed Abnormally High', 'severity': 'High',
                           'recommendation': 'Throttle motor speed. Inspect drive belts and transmission system.'})
        if power > 50:
            causes.append({'issue': 'Excessive Power Consumption', 'severity': 'Medium',
                           'recommendation': 'Audit energy usage per phase. Consider load balancing across shifts.'})
        if inp.get('pressure', 1) < 0.7 or inp.get('pressure', 1) > 1.3:
            causes.append({'issue': 'Pressure Out of Range', 'severity': 'Low',
                           'recommendation': 'Calibrate pressure regulators. Check for blockages or leaks.'})
        if not causes:
            causes.append({'issue': 'All Parameters Within Normal Range', 'severity': 'Low',
                           'recommendation': 'System operating optimally. Continue monitoring.'})
        return causes

    def _detect_anomaly(self, inp, power):
        vib = inp.get('vibration', 0)
        hum = inp.get('humidity', 0)
        temp = inp.get('temperature', 0)
        if vib > 8:
            return {'detected': True, 'type': 'Equipment', 'description': f'Vibration {vib:.1f} mm/s → likely mechanical fault (bearing wear or imbalance)'}
        if hum > 58:
            return {'detected': True, 'type': 'Process', 'description': f'Humidity {hum:.1f}% → moisture ingress affecting granulation quality'}
        if temp > 60:
            return {'detected': True, 'type': 'Thermal', 'description': f'Temperature {temp:.1f}°C → overheating risk detected in drying phase'}
        if power > 55:
            return {'detected': True, 'type': 'Energy', 'description': f'Power {power:.1f} kW → energy spike detected, check load profile'}
        return {'detected': False, 'type': None, 'description': None}

    def get_time_series(self):
        process_df, _ = load_data()
        result = []
        for _, row in process_df.iterrows():
            result.append({
                'time': int(row['Time_Minutes']),
                'phase': row['Phase'],
                'temperature': round(row['Temperature_C'], 2),
                'pressure': round(row['Pressure_Bar'], 3),
                'humidity': round(row['Humidity_Percent'], 2),
                'motor_speed': round(row['Motor_Speed_RPM'], 2),
                'power': round(row['Power_Consumption_kW'], 2),
                'vibration': round(row['Vibration_mm_s'], 3),
                'flow_rate': round(row['Flow_Rate_LPM'], 3),
                'compression': round(row['Compression_Force_kN'], 3),
            })
        return result

    def get_batch_summary(self):
        _, production_df = load_data()
        records = []
        for _, row in production_df.iterrows():
            records.append({
                'batch_id': row['Batch_ID'],
                'hardness': row['Hardness'],
                'friability': row['Friability'],
                'dissolution_rate': row['Dissolution_Rate'],
                'content_uniformity': row['Content_Uniformity'],
                'compression_force': row['Compression_Force'],
                'machine_speed': row['Machine_Speed'],
            })
        return records

ml_service = ManufacturingMLService()
