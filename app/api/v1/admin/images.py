# app/api/v1/admin/test_extraction.py
"""
Test endpoints for image extraction functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
from pathlib import Path

from app.core.database import get_db
from app.services.image_extractor import MagicScholarImageExtractor
from app.models.institution import Institution

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test-csv-load")
async def test_csv_load():
    """Test if we can load the sample CSV"""
    csv_path = "data/raw_data/image_upload_sample.csv"

    if not Path(csv_path).exists():
        raise HTTPException(status_code=404, detail=f"CSV not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path)
        first_school = df.iloc[0].to_dict()

        return {
            "status": "success",
            "total_schools": len(df),
            "first_school": first_school,
            "columns": list(df.columns),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")


@router.post("/test-single-school")
async def test_single_school(ipeds_id: int, db: Session = Depends(get_db)):
    """Test extraction on a single school by IPEDS ID"""

    try:
        # Find institution in database
        institution = (
            db.query(Institution).filter(Institution.ipeds_id == ipeds_id).first()
        )

        if not institution:
            raise HTTPException(
                status_code=404, detail=f"Institution {ipeds_id} not found"
            )

        # Initialize extractor
        extractor = MagicScholarImageExtractor(db)

        # Process the institution
        result = extractor.process_institution_from_db(institution)

        # Get processing stats
        stats = extractor.get_processing_stats()

        return {
            "institution": {
                "ipeds_id": institution.ipeds_id,
                "name": institution.name,
                "website": institution.website,
            },
            "extraction_result": result,
            "processing_stats": stats,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing institution {ipeds_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/test-csv-sample")
async def test_csv_sample(
    max_schools: Optional[int] = 3, db: Session = Depends(get_db)
):
    """Test extraction with CSV sample data"""

    csv_path = "data/raw_data/image_upload_sample.csv"

    if not Path(csv_path).exists():
        raise HTTPException(status_code=404, detail=f"Sample CSV not found: {csv_path}")

    try:
        # Initialize extractor
        extractor = MagicScholarImageExtractor(db)

        # Process institutions from CSV
        results = extractor.process_institutions_from_csv(
            csv_path, max_institutions=max_schools
        )

        # Get processing stats
        stats = extractor.get_processing_stats()

        return {
            "status": "completed",
            "processed_count": len(results),
            "results": results,
            "processing_stats": stats,
            "csv_path": csv_path,
        }

    except Exception as e:
        logger.error(f"Error processing CSV sample: {e}")
        raise HTTPException(status_code=500, detail=f"CSV processing failed: {str(e)}")


@router.get("/test-environment")
async def test_environment():
    """Test if environment is properly configured"""

    import os

    # Check required environment variables
    required_vars = [
        "DIGITAL_OCEAN_SPACES_ACCESS_KEY",
        "DIGITAL_OCEAN_SPACES_SECRET_KEY",
        "DIGITAL_OCEAN_SPACES_BUCKET",
        "IMAGE_CDN_BASE_URL",
    ]

    env_status = {}
    missing_vars = []

    for var in required_vars:
        if os.getenv(var):
            env_status[var] = "✓ Set"
        else:
            env_status[var] = "✗ Missing"
            missing_vars.append(var)

    # Check CSV file
    csv_path = "data/raw_data/image_upload_sample.csv"
    csv_exists = Path(csv_path).exists()

    if csv_exists:
        try:
            df = pd.read_csv(csv_path)
            csv_status = f"✓ Found ({len(df)} schools)"
        except Exception as e:
            csv_status = f"✗ Error reading: {str(e)}"
    else:
        csv_status = "✗ Not found"

    return {
        "environment_variables": env_status,
        "missing_variables": missing_vars,
        "csv_file": {"path": csv_path, "status": csv_status},
        "ready_for_testing": len(missing_vars) == 0 and csv_exists,
        "notes": [
            "Missing environment variables will prevent upload to Digital Ocean",
            "You can still test extraction without upload",
            "CSV file is required for batch processing",
        ],
    }


@router.get("/find-test-school")
async def find_test_school(db: Session = Depends(get_db)):
    """Find a school from the database that we can test with"""

    try:
        # Find an institution with a website
        institution = (
            db.query(Institution)
            .filter(Institution.website.isnot(None))
            .filter(Institution.website != "")
            .first()
        )

        if not institution:
            return {
                "message": "No institutions with websites found in database",
                "suggestion": "Import institution data first",
            }

        return {
            "test_institution": {
                "ipeds_id": institution.ipeds_id,
                "name": institution.name,
                "website": institution.website,
                "state": institution.state,
            },
            "test_url": f"/api/v1/admin/test-extraction/test-single-school?ipeds_id={institution.ipeds_id}",
            "message": "Use this institution for testing",
        }

    except Exception as e:
        logger.error(f"Error finding test school: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
