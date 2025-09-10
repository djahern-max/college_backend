# app/api/v1/s2023_is.py
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.s2023_is import S2023_ISService
from app.models.s2023_is import S2023_IS
import tempfile
import os

router = APIRouter()


@router.get("/institution/{unitid}")
async def get_s2023_is_metrics(unitid: str, db: Session = Depends(get_db)):
    """Get S2023_IS metrics for a specific institution"""
    metrics = S2023_ISService.get_by_unitid(db, unitid)
    if not metrics:
        raise HTTPException(
            status_code=404, detail="S2023_IS metrics not found for this institution"
        )

    return metrics.to_dict()


@router.get("/search")
async def search_s2023_is_metrics(
    min_faculty: Optional[int] = Query(None, description="Minimum faculty count"),
    max_faculty: Optional[int] = Query(None, description="Maximum faculty count"),
    diversity_categories: Optional[str] = Query(
        None, description="Comma-separated diversity categories (High,Moderate,Low)"
    ),
    size_categories: Optional[str] = Query(
        None, description="Comma-separated size categories"
    ),
    min_female_percent: Optional[float] = Query(
        None, description="Minimum female faculty percentage"
    ),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Number of records to return"),
    db: Session = Depends(get_db),
):
    """Search institutions by S2023_IS criteria"""

    # Parse comma-separated lists
    diversity_list = diversity_categories.split(",") if diversity_categories else None
    size_list = size_categories.split(",") if size_categories else None

    results = S2023_ISService.search_institutions(
        db=db,
        min_faculty=min_faculty,
        max_faculty=max_faculty,
        diversity_categories=diversity_list,
        size_categories=size_list,
        min_female_percent=min_female_percent,
        skip=skip,
        limit=limit,
    )

    return [result.to_dict() for result in results]


@router.get("/diversity/{category}")
async def get_by_diversity_category(category: str, db: Session = Depends(get_db)):
    """Get institutions by diversity category (High, Moderate, Low)"""
    if category not in ["High", "Moderate", "Low"]:
        raise HTTPException(
            status_code=400, detail="Category must be High, Moderate, or Low"
        )

    results = S2023_ISService.get_by_diversity_category(db, category)
    return [result.to_dict() for result in results]


@router.get("/size/{category}")
async def get_by_size_category(category: str, db: Session = Depends(get_db)):
    """Get institutions by faculty size category"""
    valid_categories = ["Very Small", "Small", "Medium", "Large", "Very Large"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400, detail=f"Category must be one of: {valid_categories}"
        )

    results = S2023_ISService.get_by_size_category(db, category)
    return [result.to_dict() for result in results]


@router.get("/stats")
async def get_s2023_is_stats(db: Session = Depends(get_db)):
    """Get aggregated S2023_IS statistics"""
    return S2023_ISService.get_diversity_stats(db)


@router.post("/import")
async def import_s2023_is_metrics(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Import S2023_IS metrics from CSV file"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Import data
        records_imported = S2023_ISService.bulk_import_from_csv(db, tmp_file_path)

        # Clean up temp file
        os.unlink(tmp_file_path)

        return {
            "message": "S2023_IS metrics imported successfully",
            "records_imported": records_imported,
        }

    except Exception as e:
        # Clean up temp file on error
        if "tmp_file_path" in locals():
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/highlights/{unitid}")
async def get_s2023_is_highlights(unitid: str, db: Session = Depends(get_db)):
    """Get 4-6 S2023_IS highlight bullet points for an institution"""
    metrics = S2023_ISService.get_by_unitid(db, unitid)
    if not metrics:
        raise HTTPException(status_code=404, detail="S2023_IS metrics not found")

    return {"unitid": unitid, "faculty_highlights": metrics.faculty_highlights}
