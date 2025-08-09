from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, asc, select, String
from datetime import date
from app.models.scholarship import Scholarship, ScholarshipStatus, ScholarshipType
from app.schemas.scholarship import ScholarshipCreate, ScholarshipUpdate, ScholarshipSearch


class ScholarshipRepository:
    """Repository for scholarship operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, obj_in: ScholarshipCreate) -> Scholarship:
        """Create a new scholarship"""
        db_obj = Scholarship(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get(self, id: int) -> Optional[Scholarship]:
        """Get scholarship by ID"""
        result = await self.db.execute(select(Scholarship).where(Scholarship.id == id))
        return result.scalar_one_or_none()
    
    async def update(self, db_obj: Scholarship, obj_in: ScholarshipUpdate) -> Scholarship:
        """Update a scholarship"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def search_scholarships(self, search_params: ScholarshipSearch) -> Tuple[List[Scholarship], int]:
        """
        Search scholarships with filters and return results with total count
        """
        query = select(Scholarship)
        
        # Text search in title and description
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.where(
                or_(
                    Scholarship.title.ilike(search_term),
                    Scholarship.description.ilike(search_term),
                    Scholarship.provider.ilike(search_term)
                )
            )
        
        # Provider filter
        if search_params.provider:
            query = query.where(Scholarship.provider.ilike(f"%{search_params.provider}%"))
        
        # Type filter
        if search_params.scholarship_type:
            query = query.where(Scholarship.scholarship_type == search_params.scholarship_type)
        
        # Categories filter (simplified for now)
        if search_params.categories:
            # Use JSON contains operator for PostgreSQL
            category_filters = []
            for category in search_params.categories:
                # Check if any element in the JSON array contains the category (case-insensitive)
                category_filters.append(
                    func.lower(func.cast(Scholarship.categories, String)).contains(func.lower(category))
                )
            if category_filters:
                query = query.where(or_(*category_filters))
        
        # Amount filters
        if search_params.min_amount is not None:
            query = query.where(
                or_(
                    Scholarship.amount_min >= search_params.min_amount,
                    Scholarship.amount_max >= search_params.min_amount,
                    Scholarship.amount_exact >= search_params.min_amount
                )
            )
        
        if search_params.max_amount is not None:
            query = query.where(
                or_(
                    and_(Scholarship.amount_min.isnot(None), Scholarship.amount_min <= search_params.max_amount),
                    and_(Scholarship.amount_max.isnot(None), Scholarship.amount_max <= search_params.max_amount),
                    and_(Scholarship.amount_exact.isnot(None), Scholarship.amount_exact <= search_params.max_amount)
                )
            )
        
        # Date filters
        if search_params.deadline_after:
            query = query.where(Scholarship.deadline >= search_params.deadline_after)
        
        if search_params.deadline_before:
            query = query.where(Scholarship.deadline <= search_params.deadline_before)
        
        # Status filter
        if search_params.status:
            query = query.where(Scholarship.status == search_params.status)
        else:
            # Default to active scholarships only
            query = query.where(Scholarship.status == ScholarshipStatus.ACTIVE)
        
        # Verified filter
        if search_params.verified_only:
            query = query.where(Scholarship.verified == True)
        
        # Renewable filter
        if search_params.renewable_only:
            query = query.where(Scholarship.renewable == True)
        
        # Get total count before pagination
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total_count = count_result.scalar()
        
        # Sorting
        sort_column = getattr(Scholarship, search_params.sort_by, Scholarship.created_at)
        if search_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Pagination
        query = query.offset(search_params.skip).limit(search_params.limit)
        
        result = await self.db.execute(query)
        results = result.scalars().all()
        return results, total_count
    
    async def get_by_external_id(self, external_id: str, source: str) -> Optional[Scholarship]:
        """Get scholarship by external ID and source"""
        result = await self.db.execute(
            select(Scholarship).where(
                and_(
                    Scholarship.external_id == external_id,
                    Scholarship.source == source
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_active_scholarships(self, limit: int = 50, offset: int = 0) -> List[Scholarship]:
        """Get active scholarships with pagination"""
        result = await self.db.execute(
            select(Scholarship)
            .where(Scholarship.status == ScholarshipStatus.ACTIVE)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_expiring_soon(self, days: int = 30) -> List[Scholarship]:
        """Get scholarships expiring within specified days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now().date() + timedelta(days=days)
        
        result = await self.db.execute(
            select(Scholarship)
            .where(
                and_(
                    Scholarship.status == ScholarshipStatus.ACTIVE,
                    Scholarship.deadline <= cutoff_date,
                    Scholarship.deadline >= datetime.now().date()
                )
            )
            .order_by(Scholarship.deadline)
        )
        return result.scalars().all()
    
    async def get_by_provider(self, provider: str, limit: int = 50) -> List[Scholarship]:
        """Get scholarships by provider"""
        result = await self.db.execute(
            select(Scholarship)
            .where(Scholarship.provider.ilike(f"%{provider}%"))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_categories(self, categories: List[str], limit: int = 50) -> List[Scholarship]:
        """Get scholarships that match any of the specified categories"""
        category_filters = []
        for category in categories:
            # Use JSON contains for PostgreSQL with case-insensitive search
            category_filters.append(
                func.lower(func.cast(Scholarship.categories, String)).contains(func.lower(category))
            )
        
        result = await self.db.execute(
            select(Scholarship)
            .where(or_(*category_filters))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_application_count(self, scholarship_id: int, increment: int = 1) -> bool:
        """Update application count for a scholarship"""
        scholarship = await self.get(scholarship_id)
        if scholarship:
            scholarship.application_count = (scholarship.application_count or 0) + increment
            await self.db.flush()
            return True
        return False
    
    async def mark_as_verified(self, scholarship_id: int) -> bool:
        """Mark scholarship as verified"""
        scholarship = await self.get(scholarship_id)
        if scholarship:
            scholarship.verified = True
            scholarship.last_verified = date.today()
            await self.db.flush()
            return True
        return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get scholarship statistics"""
        # Total scholarships
        total_result = await self.db.execute(select(func.count(Scholarship.id)))
        total_scholarships = total_result.scalar()
        
        # Active scholarships
        active_result = await self.db.execute(
            select(func.count(Scholarship.id)).where(Scholarship.status == ScholarshipStatus.ACTIVE)
        )
        active_scholarships = active_result.scalar()
        
        # Verified scholarships
        verified_result = await self.db.execute(
            select(func.count(Scholarship.id)).where(Scholarship.verified == True)
        )
        verified_scholarships = verified_result.scalar()
        
        # Get statistics by type
        type_stats_result = await self.db.execute(
            select(Scholarship.scholarship_type, func.count(Scholarship.id))
            .group_by(Scholarship.scholarship_type)
        )
        type_stats = type_stats_result.all()
        
        return {
            "total_scholarships": total_scholarships,
            "active_scholarships": active_scholarships,
            "verified_scholarships": verified_scholarships,
            "verification_rate": (verified_scholarships / total_scholarships * 100) if total_scholarships > 0 else 0,
            "by_type": {str(type_name): count for type_name, count in type_stats}
        }