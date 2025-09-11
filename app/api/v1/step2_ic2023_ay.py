# app/api/v1/step2_ic2023_ay.py
"""
API endpoints for Step2_IC2023_AY financial data
Following the same structure as s2023_is endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc
from typing import List, Optional

from app.core.database import get_db
from app.models.step2_ic2023_ay import Step2_IC2023_AY
from app.models.institution import Institution
from app.schemas.step2_ic2023_ay import (
    Step2_IC2023_AYResponse,
    Step2_IC2023_AYCreate,
    Step2_IC2023_AYUpdate,
    Step2_IC2023_AYStats,
    Step2_IC2023_AYList,
    Step2_IC2023_AYSearch,
    Step2_IC2023_AYSummary,
    InstitutionWithFinancialData,
)

router = APIRouter()


@router.get("/", response_model=Step2_IC2023_AYList)
async def get_financial_data(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    min_tuition_in_state: Optional[float] = Query(
        None, ge=0, description="Minimum in-state tuition"
    ),
    max_tuition_in_state: Optional[float] = Query(
        None, ge=0, description="Maximum in-state tuition"
    ),
    min_tuition_out_state: Optional[float] = Query(
        None, ge=0, description="Minimum out-of-state tuition"
    ),
    max_tuition_out_state: Optional[float] = Query(
        None, ge=0, description="Maximum out-of-state tuition"
    ),
    has_comprehensive_data: Optional[bool] = Query(
        None, description="Filter by comprehensive data availability"
    ),
    validation_status: Optional[str] = Query(
        None, description="Filter by validation status"
    ),
    sort_by: str = Query("tuition_in_state", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
):
    """Get financial data with filtering and pagination"""

    # Build query
    query = db.query(Step2_IC2023_AY).options(joinedload(Step2_IC2023_AY.institution))

    # Apply filters
    if min_tuition_in_state is not None:
        query = query.filter(Step2_IC2023_AY.tuition_in_state >= min_tuition_in_state)

    if max_tuition_in_state is not None:
        query = query.filter(Step2_IC2023_AY.tuition_in_state <= max_tuition_in_state)

    if min_tuition_out_state is not None:
        query = query.filter(Step2_IC2023_AY.tuition_out_state >= min_tuition_out_state)

    if max_tuition_out_state is not None:
        query = query.filter(Step2_IC2023_AY.tuition_out_state <= max_tuition_out_state)

    if has_comprehensive_data is not None:
        if has_comprehensive_data:
            query = query.filter(
                Step2_IC2023_AY.tuition_in_state.isnot(None),
                Step2_IC2023_AY.tuition_out_state.isnot(None),
                Step2_IC2023_AY.room_board_on_campus.isnot(None),
            )
        else:
            query = query.filter(
                (Step2_IC2023_AY.tuition_in_state.is_(None))
                | (Step2_IC2023_AY.tuition_out_state.is_(None))
                | (Step2_IC2023_AY.room_board_on_campus.is_(None))
            )

    if validation_status:
        query = query.filter(Step2_IC2023_AY.validation_status == validation_status)

    # Apply sorting
    sort_column = getattr(Step2_IC2023_AY, sort_by, Step2_IC2023_AY.tuition_in_state)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Get total count
    total = query.count()

    # Apply pagination
    financial_records = query.offset(skip).limit(limit).all()

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return Step2_IC2023_AYList(
        items=[record.to_dict() for record in financial_records],
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages,
        has_next=skip + limit < total,
        has_prev=skip > 0,
    )


@router.get("/stats", response_model=Step2_IC2023_AYStats)
async def get_financial_stats(db: Session = Depends(get_db)):
    """Get aggregate financial statistics"""

    # Base query for records with data
    base_query = db.query(Step2_IC2023_AY)

    # Total institutions with financial data
    total_with_data = base_query.filter(
        Step2_IC2023_AY.tuition_in_state.isnot(None)
    ).count()

    # Average costs
    avg_stats = (
        db.query(
            func.avg(Step2_IC2023_AY.tuition_in_state).label("avg_tuition_in_state"),
            func.avg(Step2_IC2023_AY.tuition_out_state).label("avg_tuition_out_state"),
        )
        .filter(Step2_IC2023_AY.tuition_in_state.isnot(None))
        .first()
    )

    # Percentiles for cost ranges
    percentiles_query = (
        db.query(Step2_IC2023_AY.tuition_in_state)
        .filter(Step2_IC2023_AY.tuition_in_state.isnot(None))
        .order_by(Step2_IC2023_AY.tuition_in_state)
        .all()
    )

    cost_ranges = {}
    if percentiles_query:
        tuition_values = [row.tuition_in_state for row in percentiles_query]
        cost_ranges = {
            "tuition_in_state": {
                "min": min(tuition_values),
                "p25": tuition_values[len(tuition_values) // 4],
                "median": tuition_values[len(tuition_values) // 2],
                "p75": tuition_values[3 * len(tuition_values) // 4],
                "max": max(tuition_values),
            }
        }

    # Validation status breakdown
    validation_breakdown = {}
    validation_counts = (
        db.query(Step2_IC2023_AY.validation_status, func.count().label("count"))
        .group_by(Step2_IC2023_AY.validation_status)
        .all()
    )

    for status, count in validation_counts:
        validation_breakdown[status] = count

    return Step2_IC2023_AYStats(
        total_institutions_with_data=total_with_data,
        avg_tuition_in_state=avg_stats.avg_tuition_in_state if avg_stats else None,
        avg_tuition_out_state=avg_stats.avg_tuition_out_state if avg_stats else None,
        median_tuition_in_state=cost_ranges.get("tuition_in_state", {}).get("median"),
        median_tuition_out_state=None,  # Calculate if needed
        avg_total_cost_in_state=None,  # Calculate if needed
        avg_total_cost_out_state=None,  # Calculate if needed
        cost_ranges=cost_ranges,
        validation_breakdown=validation_breakdown,
    )


@router.get("/by-ipeds/{ipeds_id}", response_model=Step2_IC2023_AYResponse)
async def get_financial_data_by_ipeds_id(
    ipeds_id: int,
    db: Session = Depends(get_db),
):
    """Get financial data for a specific institution by IPEDS ID"""

    financial_record = (
        db.query(Step2_IC2023_AY)
        .options(joinedload(Step2_IC2023_AY.institution))
        .filter(Step2_IC2023_AY.ipeds_id == ipeds_id)
        .first()
    )

    if not financial_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial data not found for IPEDS ID {ipeds_id}",
        )

    return financial_record.to_dict()


@router.get("/{record_id}", response_model=Step2_IC2023_AYResponse)
async def get_financial_data_by_id(
    record_id: int,
    db: Session = Depends(get_db),
):
    """Get financial data by record ID"""

    financial_record = (
        db.query(Step2_IC2023_AY)
        .options(joinedload(Step2_IC2023_AY.institution))
        .filter(Step2_IC2023_AY.id == record_id)
        .first()
    )

    if not financial_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial record {record_id} not found",
        )

    return financial_record.to_dict()


@router.post(
    "/", response_model=Step2_IC2023_AYResponse, status_code=status.HTTP_201_CREATED
)
async def create_financial_data(
    financial_data: Step2_IC2023_AYCreate,
    db: Session = Depends(get_db),
):
    """Create new financial data record"""

    # Check if institution exists
    institution = (
        db.query(Institution)
        .filter(Institution.ipeds_id == financial_data.ipeds_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with IPEDS ID {financial_data.ipeds_id} not found",
        )

    # Check if financial data already exists
    existing_record = (
        db.query(Step2_IC2023_AY)
        .filter(Step2_IC2023_AY.ipeds_id == financial_data.ipeds_id)
        .first()
    )

    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Financial data already exists for IPEDS ID {financial_data.ipeds_id}",
        )

    # Create new record
    db_record = Step2_IC2023_AY(**financial_data.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record.to_dict()


@router.put("/{record_id}", response_model=Step2_IC2023_AYResponse)
async def update_financial_data(
    record_id: int,
    financial_data: Step2_IC2023_AYUpdate,
    db: Session = Depends(get_db),
):
    """Update financial data record"""

    db_record = (
        db.query(Step2_IC2023_AY).filter(Step2_IC2023_AY.id == record_id).first()
    )

    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial record {record_id} not found",
        )

    # Update fields
    update_data = financial_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)

    return db_record.to_dict()


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_financial_data(
    record_id: int,
    db: Session = Depends(get_db),
):
    """Delete financial data record"""

    db_record = (
        db.query(Step2_IC2023_AY).filter(Step2_IC2023_AY.id == record_id).first()
    )

    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial record {record_id} not found",
        )

    db.delete(db_record)
    db.commit()


@router.get("/search/institutions", response_model=List[InstitutionWithFinancialData])
async def search_institutions_with_financial_data(
    min_tuition: Optional[float] = Query(None, ge=0),
    max_tuition: Optional[float] = Query(None, ge=0),
    state: Optional[str] = Query(None, description="State abbreviation"),
    control_type: Optional[str] = Query(None, description="Control type"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search institutions with their financial data"""

    query = (
        db.query(Institution)
        .options(joinedload(Institution.step2_financial_data))
        .join(
            Step2_IC2023_AY,
            Institution.ipeds_id == Step2_IC2023_AY.ipeds_id,
            isouter=True,
        )
    )

    # Apply filters
    if min_tuition is not None:
        query = query.filter(Step2_IC2023_AY.tuition_in_state >= min_tuition)

    if max_tuition is not None:
        query = query.filter(Step2_IC2023_AY.tuition_in_state <= max_tuition)

    if state:
        query = query.filter(Institution.state == state.upper())

    if control_type:
        query = query.filter(Institution.control_type == control_type)

    institutions = query.limit(limit).all()

    # Convert to response format
    result = []
    for institution in institutions:
        result.append(
            {
                "ipeds_id": institution.ipeds_id,
                "name": institution.name,
                "city": institution.city,
                "state": institution.state,
                "control_type": institution.control_type.value,
                "financial_data": (
                    institution.step2_financial_data.to_dict()
                    if institution.step2_financial_data
                    else None
                ),
                "has_financial_data": institution.step2_financial_data is not None,
                "financial_summary": (
                    f"In-state: ${institution.step2_financial_data.tuition_in_state:,.0f}"
                    if institution.step2_financial_data
                    and institution.step2_financial_data.tuition_in_state
                    else "No tuition data available"
                ),
            }
        )

    return result
