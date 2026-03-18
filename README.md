# ManufactureIQ — AI-Driven Batch Intelligence System

A production-level manufacturing analytics dashboard with ML-powered predictions,
real-time process monitoring, root cause analysis, and golden batch comparison.

---

## 📁 Project Structure

```
manufacturing-intelligence/
├── backend/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── requirements.txt
│   ├── data/
│   │   ├── batch_process_data.xlsx
│   │   └── batch_production_data.xlsx
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── routes/
│   │   └── prediction.py        # API routes
│   ├── services/
│   │   └── ml_service.py        # ML training + inference
│   └── utils/
├── frontend/
│   └── index.html               # Complete React-style SPA (no build needed)
└── README.md
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: http://localhost:8000
API Docs (Swagger): http://localhost:8000/docs

### 2. Frontend

Simply open `frontend/index.html` in your browser.

**OR** serve it with Python:
```bash
cd frontend
python -m http.server 3000
# Open http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint            | Description                        |
|--------|---------------------|------------------------------------|
| GET    | /                   | Health check                       |
| GET    | /api/health         | Model status                       |
| POST   | /api/predict        | Run ML prediction                  |
| GET    | /api/timeseries     | Full batch T001 time series        |
| GET    | /api/batches        | All 60 historical batches          |
| GET    | /docs               | Swagger interactive API docs       |

### POST /api/predict — Request Body

```json
{
  "temperature": 35.0,
  "pressure": 1.0,
  "humidity": 38.0,
  "motor_speed": 120.0,
  "vibration": 3.0,
  "flow_rate": 1.5,
  "compression_force": 10.0,
  "granulation_time": 16.0,
  "binder_amount": 9.0,
  "drying_temp": 59.4,
  "drying_time": 28.0,
  "machine_speed": 169.0,
  "lubricant_conc": 1.2
}
```

---

## 🧠 ML Models

- **Quality Models**: GradientBoostingRegressor for each quality metric
  - Hardness, Friability, Dissolution Rate, Content Uniformity, Disintegration Time, Tablet Weight
- **Energy Model**: RandomForestRegressor for power consumption prediction
- **Root Cause Engine**: Rule-based + threshold analysis
- **Anomaly Detection**: Multi-parameter threshold monitoring
- **Golden Batch**: Best-performing batch stored and compared against current

---

## 🎯 Features

- ✅ Real-time slider-driven prediction (400ms debounce)
- ✅ KPI cards with pass/fail status
- ✅ Energy trend chart from actual batch T001 data (211 time points)
- ✅ Quality metrics bar chart
- ✅ Energy efficiency gauge
- ✅ Batch performance radar chart
- ✅ Root cause intelligence with severity levels
- ✅ SHAP-style feature importance visualization
- ✅ Golden batch deviation comparison
- ✅ Historical batch database table (60 batches)
- ✅ Anomaly detection banner
- ✅ Works offline (fallback demo mode when backend unavailable)

---

## 📦 Dependencies

### Backend
- FastAPI + Uvicorn
- XGBoost + Scikit-learn
- Pandas + NumPy + OpenPyXL
- Pydantic v2

### Frontend
- Vanilla JS (no build step)
- Chart.js 4.4 (CDN)
- Google Fonts: Syne + JetBrains Mono

---

## 🌐 Production Deployment

```bash
# Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend: deploy index.html to any static host (Vercel, Netlify, S3)
# Update API constant in index.html: const API = 'https://your-api.com'
```
