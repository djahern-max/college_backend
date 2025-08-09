from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.repositories.scholarship import ScholarshipRepository
from app.models.scholarship import Scholarship, ScholarshipStatus
from app.schemas.scholarship import (
    ScholarshipCreate, 
    ScholarshipUpdate, 
    ScholarshipSearch,
    ScholarshipResponse,
    ScholarshipSummary
)


class ScholarshipService:
    """Service layer for scholarship operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ScholarshipRepository(db)
    
    async def create_scholarship(self, scholarship_data: ScholarshipCreate) -> ScholarshipResponse:
        """Create a new scholarship"""
        try:
            # Check if scholarship with same external_id and source already exists
            if hasattr(scholarship_data, 'external_id') and hasattr(scholarship_data, 'source'):
                external_id = getattr(scholarship_data, 'external_id', None)
                source = getattr(scholarship_data, 'source', None)
                if external_id and source:
                    existing = await self.repository.get_by_external_id(external_id, source)
                    if existing:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Scholarship with this external ID already exists"
                        )
            
            scholarship = await self.repository.create(scholarship_data)
            # Don't manually commit here - let the dependency handle it
            return ScholarshipResponse.model_validate(scholarship)
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating scholarship: {str(e)}"
            )
    
    async def get_scholarship(self, scholarship_id: int) -> ScholarshipResponse:
        """Get a scholarship by ID"""
        scholarship = await self.repository.get(scholarship_id)
        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scholarship not found"
            )
        return ScholarshipResponse.model_validate(scholarship)
    
    async def update_scholarship(
        self, 
        scholarship_id: int, 
        scholarship_data: ScholarshipUpdate
    ) -> ScholarshipResponse:
        """Update a scholarship"""
        scholarship = await self.repository.get(scholarship_id)
        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scholarship not found"
            )
        
        try:
            updated_scholarship = await self.repository.update(scholarship, scholarship_data)
            return ScholarshipResponse.model_validate(updated_scholarship)
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating scholarship: {str(e)}"
            )
    
    async def delete_scholarship(self, scholarship_id: int) -> bool:
        """Delete a scholarship (soft delete by setting status to inactive)"""
        scholarship = await self.repository.get(scholarship_id)
        if not scholarship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scholarship not found"
            )
        
        # Soft delete by updating status
        scholarship.status = ScholarshipStatus.INACTIVE
        return True
    
    async def search_scholarships(
        self, 
        search_params: ScholarshipSearch
    ) -> Tuple[List[ScholarshipSummary], int]:
        """Search scholarships with filters"""
        try:
            results, total_count = await self.repository.search_scholarships(search_params)
            
            # Convert to summary format for list view
            summaries = [ScholarshipSummary.model_validate(scholarship) for scholarship in results]
            
            return summaries, total_count
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching scholarships: {str(e)}"
            )
    
    async def get_active_scholarships(
        self, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ScholarshipSummary]:
        """Get active scholarships"""
        scholarships = await self.repository.get_active_scholarships(limit, offset)
        return [ScholarshipSummary.model_validate(scholarship) for scholarship in scholarships]
    
    async def get_expiring_soon(self, days: int = 30) -> List[ScholarshipSummary]:
        """Get scholarships expiring within specified days"""
        scholarships = await self.repository.get_expiring_soon(days)
        return [ScholarshipSummary.model_validate(scholarship) for scholarship in scholarships]
    
    async def get_by_provider(self, provider: str, limit: int = 50) -> List[ScholarshipSummary]:
        """Get scholarships by provider"""
        scholarships = await self.repository.get_by_provider(provider, limit)
        return [ScholarshipSummary.model_validate(scholarship) for scholarship in scholarships]
    
    async def get_by_categories(
        self, 
        categories: List[str], 
        limit: int = 50
    ) -> List[ScholarshipSummary]:
        """Get scholarships by categories"""
        scholarships = await self.repository.get_by_categories(categories, limit)
        return [ScholarshipSummary.model_validate(scholarship) for scholarship in scholarships]
    
    async def mark_as_verified(self, scholarship_id: int) -> ScholarshipResponse:
        """Mark a scholarship as verified"""
        if not await self.repository.mark_as_verified(scholarship_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scholarship not found"
            )
        
        return await self.get_scholarship(scholarship_id)
    
    async def increment_application_count(self, scholarship_id: int) -> bool:
        """Increment application count for a scholarship"""
        result = await self.repository.update_application_count(scholarship_id, 1)
        return result
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get scholarship statistics"""
        return await self.repository.get_statistics()
    
    async def bulk_create_scholarships(
        self, 
        scholarships_data: List[ScholarshipCreate]
    ) -> List[ScholarshipResponse]:
        """Create multiple scholarships in bulk"""
        created_scholarships = []
        errors = []
        
        for i, scholarship_data in enumerate(scholarships_data):
            try:
                scholarship = await self.repository.create(scholarship_data)
                created_scholarships.append(ScholarshipResponse.model_validate(scholarship))
            except Exception as e:
                errors.append(f"Error creating scholarship {i + 1}: {str(e)}")
        
        if errors:
            # If there were errors, you might want to handle them differently
            # For now, we'll include them in the response
            raise HTTPException(
                status_code=status.HTTP_207_MULTI_STATUS,
                detail={
                    "created": len(created_scholarships),
                    "errors": errors,
                    "scholarships": created_scholarships
                }
            )
        
        return created_scholarships