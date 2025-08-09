from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import date
from app.db.repositories.base import BaseRepository
from app.models.scholarship import Scholarship, ScholarshipStatus, ScholarshipType
from app.schemas.scholarship import ScholarshipCreate, ScholarshipUpdate, ScholarshipSearch


class ScholarshipRepository(BaseRepository[Scholarship, ScholarshipCreate, ScholarshipUpdate]):
    """Repository for scholarship operations"""
    
    def __init__(self, db: Session):
        super().__init__(Scholarship, db)
    
    def search_scholarships(self, search_params: ScholarshipSearch) -> tuple[List[Scholarship], int]:
        """
        Search scholarships with filters and return results with total count
        """
        query = self.db.query(Scholarship)
        
        # Text search in title and description
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Scholarship.title.ilike(search_term),
                    Scholarship.description.ilike(search_term),
                    Scholarship.provider.ilike(search_term)
                )
            )
        
        # Provider filter
        if search_params.provider:
            query = query.filter(Scholarship.provider.ilike(f"%{search_params.provider}%"))
        
        # Type filter
        if search_params.scholarship_type:
            query = query.filter(Scholarship.scholarship_type == search_params.scholarship_type)
        
        # Categories filter (JSON contains any of the specified categories)
        if search_params.categories:
            category_filters = []
            for category in search_params.categories:
                category_filters.append(
                    func.json_extract_path_text(Scholarship.categories, '0').ilike(f"%{category}%")
                )
            query = query.filter(or_(*category_filters))
        
        # Amount filters
        if search_params.min_amount is not None:
            query = query.filter(
                or_(
                    Scholarship.amount_min >= search_params.min_amount,
                    Scholarship.amount_max >= search_params.min_amount,
                    Scholarship.amount_exact >= search_params.min_amount
                )
            )
        
        if search_params.max_amount is not None:
            query = query.filter(
                or_(
                    and_(Scholarship.amount_min.isnot(None), Scholarship.amount_min <= search_params.max_amount),
                    and_(Scholarship.amount_max.isnot(None), Scholarship.amount_max <= search_params.max_amount),
                    and_(Scholarship.amount_exact.isnot(None), Scholarship.amount_exact <= search_params.max_amount)
                )
            )
        
        # Date filters
        if search_params.deadline_after:
            query = query.filter(Scholarship.deadline >= search_params.deadline_after)
        
        if search_params.deadline_before:
            query = query.filter(Scholarship.deadline <= search_params.deadline_before)
        
        # Status filter
        if search_params.status:
            query = query.filter(Scholarship.status == search_params.status)
        else:
            # Default to active scholarships only
            query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)
        
        # Verified filter
        if search_params.verified_only:
            query = query.filter(Scholarship.verified == True)
        
        # Renewable filter
        if search_params.renewable_only:
            query = query.filter(Scholarship.renewable == True)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Sorting
        sort_column = getattr(Scholarship, search_params.sort_by, Scholarship.created_at)
        if search_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Pagination
        query = query.offset(search_params.skip).limit(search_params.limit)
        
        results = query.all()
        return results, total_count
    
    def get_by_external_id(self, external_id: str, source: str) -> Optional[Scholarship]:
        """Get scholarship by external ID and source"""
        return self.db.query(Scholarship).filter(
            and_(
                Scholarship.external_id == external_id,
                Scholarship.source == source
            )
        ).first()
    
    def get_active_scholarships(self, limit: int = 50, offset: int = 0) -> List[Scholarship]:
        """Get active scholarships with pagination"""
        return self.db.query(Scholarship).filter(
            Scholarship.status == ScholarshipStatus.ACTIVE
        ).offset(offset).limit(limit).all()
    
    def get_expiring_soon(self, days: int = 30) -> List[Scholarship]:
        """Get scholarships expiring within specified days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now().date() + timedelta(days=days)
        
        return self.db.query(Scholarship).filter(
            and_(
                Scholarship.status == ScholarshipStatus.ACTIVE,
                Scholarship.deadline <= cutoff_date,
                Scholarship.deadline >= datetime.now().date()
            )
        ).order_by(Scholarship.deadline).all()
    
    def get_by_provider(self, provider: str, limit: int = 50) -> List[Scholarship]:
        """Get scholarships by provider"""
        return self.db.query(Scholarship).filter(
            Scholarship.provider.ilike(f"%{provider}%")
        ).limit(limit).all()
    
    def get_by_categories(self, categories: List[str], limit: int = 50) -> List[Scholarship]:
        """Get scholarships that match any of the specified categories"""
        category_filters = []
        for category in categories:
            category_filters.append(
                func.json_extract_path_text(Scholarship.categories, '0').ilike(f"%{category}%")
            )
        
        return self.db.query(Scholarship).filter(
            or_(*category_filters)
        ).limit(limit).all()
    
    def update_application_count(self, scholarship_id: int, increment: int = 1) -> bool:
        """Update application count for a scholarship"""
        scholarship = self.get(scholarship_id)
        if scholarship:
            scholarship.application_count = (scholarship.application_count or 0) + increment
            self.db.commit()
            return True
        return False
    
    def mark_as_verified(self, scholarship_id: int) -> bool:
        """Mark scholarship as verified"""
        scholarship = self.get(scholarship_id)
        if scholarship:
            scholarship.verified = True
            scholarship.last_verified = date.today()
            self.db.commit()
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scholarship statistics"""
        total_scholarships = self.db.query(Scholarship).count()
        active_scholarships = self.db.query(Scholarship).filter(
            Scholarship.status == ScholarshipStatus.ACTIVE
        ).count()
        verified_scholarships = self.db.query(Scholarship).filter(
            Scholarship.verified == True
        ).count()
        
        # Get statistics by type
        type_stats = self.db.query(
            Scholarship.scholarship_type,
            func.count(Scholarship.id)
        ).group_by(Scholarship.scholarship_type).all()
        
        return {
            "total_scholarships": total_scholarships,
            "active_scholarships": active_scholarships,
            "verified_scholarships": verified_scholarships,
            "verification_rate": (verified_scholarships / total_scholarships * 100) if total_scholarships > 0 else 0,
            "by_type": {str(type_name): count for type_name, count in type_stats}
        }