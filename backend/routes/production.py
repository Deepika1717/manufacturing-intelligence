from fastapi import APIRouter
from services.data_service import get_production_data, get_golden_batch

router = APIRouter()


@router.get("/batches")
def get_all_batches():
    df = get_production_data()
    return {"batches": df.to_dict(orient="records"), "count": len(df)}


@router.get("/quality-overview")
def get_quality_overview():
    df = get_production_data()
    quality_cols = ["Hardness", "Friability", "Dissolution_Rate", "Content_Uniformity"]
    stats = df[quality_cols].describe().round(3).to_dict()
    latest = df.tail(5)[["Batch_ID"] + quality_cols].to_dict(orient="records")
    return {"stats": stats, "latest_batches": latest}


@router.get("/golden-batch")
def golden_batch():
    best = get_golden_batch()
    return {"golden_batch": best}


@router.get("/batch/{batch_id}")
def get_batch(batch_id: str):
    df = get_production_data()
    row = df[df["Batch_ID"] == batch_id]
    if row.empty:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    return {"batch": row.iloc[0].to_dict()}


@router.get("/compare/{batch_id}")
def compare_to_golden(batch_id: str):
    df = get_production_data()
    golden = get_golden_batch()
    row = df[df["Batch_ID"] == batch_id]
    if row.empty:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    batch = row.iloc[0].to_dict()
    metrics = ["Hardness", "Friability", "Dissolution_Rate", "Content_Uniformity",
               "Tablet_Weight", "Moisture_Content"]
    comparison = {}
    for m in metrics:
        gv = float(golden.get(m, 0))
        bv = float(batch.get(m, 0))
        dev = round(((bv - gv) / gv) * 100, 2) if gv != 0 else 0
        comparison[m] = {"batch_value": round(bv, 3), "golden_value": round(gv, 3), "deviation_pct": dev}
    return {"batch_id": batch_id, "golden_batch_id": golden.get("Batch_ID"), "comparison": comparison}
