# app/services/scholarship_matching.py
"""
Scholarship matching service to find scholarships that match user profiles.
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from app.models.scholarship import Scholarship, ScholarshipStatus, ScholarshipType
from app.models.profile import UserProfile
from app.services.scholarship import ScholarshipService
from app.services.profile import ProfileService
import logging

logger = logging.getLogger(__name__)


class ScholarshipMatchingService:
    """Service for matching scholarships to user profiles."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scholarship_service = ScholarshipService(db)
        self.profile_service = ProfileService(db)
    
    async def find_matches_for_user(
        self, 
        user_id: int, 
        limit: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Find scholarship matches for a specific user.
        Returns (matches, match_score_average)
        """
        try:
            # Get user profile
            profile = await self.profile_service.get_by_user_id(user_id)
            if not profile or not profile.allow_scholarship_matching:
                logger.info(f"No profile found or matching disabled for user {user_id}")
                return [], 0
            
            # Get active scholarships
            scholarships = await self._get_active_scholarships()
            logger.info(f"Found {len(scholarships)} active scholarships")
            
            if not scholarships:
                logger.info("No active scholarships found")
                return [], 0
            
            # Score and rank scholarships
            scored_scholarships = []
            for scholarship in scholarships:
                try:
                    score = await self._calculate_match_score(profile, scholarship)
                    if score > 0:  # Only include scholarships with some match
                        scored_scholarships.append((scholarship, score))
                        logger.debug(f"Scholarship {scholarship.id} '{scholarship.title}' scored {score}%")
                except Exception as e:
                    logger.error(f"Error scoring scholarship {scholarship.id}: {e}")
                    continue
            
            # Sort by score (highest first) and limit results
            scored_scholarships.sort(key=lambda x: x[1], reverse=True)
            limited_scholarships = scored_scholarships[:limit]
            
            logger.info(f"Found {len(scored_scholarships)} matching scholarships, returning top {len(limited_scholarships)}")
            
            # Convert to dictionaries with robust error handling
            matches = []
            for scholarship, score in limited_scholarships:
                try:
                    match_dict = self._scholarship_to_dict(scholarship, score)
                    matches.append(match_dict)
                except Exception as e:
                    logger.error(f"Error converting scholarship {scholarship.id} to dict: {e}")
                    continue
            
            # Calculate average match score
            avg_score = int(sum(score for _, score in limited_scholarships) / len(limited_scholarships)) if limited_scholarships else 0
            
            return matches, avg_score
            
        except Exception as e:
            logger.error(f"Error in find_matches_for_user for user {user_id}: {e}")
            return [], 0
    
    def _scholarship_to_dict(self, scholarship: Scholarship, score: int) -> Dict[str, Any]:
        """Convert scholarship to dictionary with robust type handling."""
        try:
            return {
                "id": int(scholarship.id) if scholarship.id else 0,
                "title": str(scholarship.title) if scholarship.title else "Untitled Scholarship",
                "provider": str(scholarship.provider) if scholarship.provider else "Unknown Provider",
                "amount_min": str(scholarship.amount_min) if scholarship.amount_min is not None else None,
                "amount_max": str(scholarship.amount_max) if scholarship.amount_max is not None else None,
                "amount_exact": str(scholarship.amount_exact) if scholarship.amount_exact is not None else None,
                "deadline": scholarship.deadline.isoformat() if scholarship.deadline else None,
                "scholarship_type": scholarship.scholarship_type.value if scholarship.scholarship_type else "other",
                "categories": list(scholarship.categories) if scholarship.categories else [],
                "verified": bool(scholarship.verified) if scholarship.verified is not None else False,
                "renewable": bool(scholarship.renewable) if scholarship.renewable is not None else False,
                "application_url": str(scholarship.application_url) if scholarship.application_url else None,
                "contact_email": str(scholarship.contact_email) if scholarship.contact_email else None,
                "description": str(scholarship.description) if scholarship.description else None,
                "created_at": scholarship.created_at.isoformat() if scholarship.created_at else None,
                "match_score": int(score)
            }
        except Exception as e:
            logger.error(f"Error converting scholarship {scholarship.id} to dict: {e}")
            # Return a minimal valid dictionary
            return {
                "id": int(scholarship.id) if scholarship.id else 0,
                "title": "Error Loading Scholarship",
                "provider": "Unknown",
                "amount_min": None,
                "amount_max": None,
                "amount_exact": None,
                "deadline": None,
                "scholarship_type": "other",
                "categories": [],
                "verified": False,
                "renewable": False,
                "application_url": None,
                "contact_email": None,
                "description": "Error loading scholarship details",
                "created_at": None,
                "match_score": int(score)
            }
    
    async def _get_active_scholarships(self) -> List[Scholarship]:
        """Get all active scholarships."""
        try:
            query = select(Scholarship).where(
                Scholarship.status == ScholarshipStatus.ACTIVE
            )
            result = await self.db.execute(query)
            scholarships = list(result.scalars().all())
            logger.info(f"Retrieved {len(scholarships)} active scholarships from database")
            return scholarships
        except Exception as e:
            logger.error(f"Error getting active scholarships: {e}")
            # Try without status filter as fallback
            try:
                query = select(Scholarship)
                result = await self.db.execute(query)
                all_scholarships = list(result.scalars().all())
                logger.info(f"Fallback: Retrieved {len(all_scholarships)} total scholarships")
                return all_scholarships
            except Exception as e2:
                logger.error(f"Fallback query also failed: {e2}")
                return []
    
    async def _calculate_match_score(self, profile: UserProfile, scholarship: Scholarship) -> int:
        """
        Calculate a match score (0-100) between a profile and scholarship.
        Higher scores indicate better matches.
        """
        try:
            score = 0
            max_possible_score = 0
            
            # Athletic matching (30 points possible)
            athletic_score = self._score_athletic_match(profile, scholarship)
            score += athletic_score
            max_possible_score += 30
            
            # Academic matching (25 points possible)
            academic_score = self._score_academic_match(profile, scholarship)
            score += academic_score
            max_possible_score += 25
            
            # Geographic matching (15 points possible)
            geographic_score = self._score_geographic_match(profile, scholarship)
            score += geographic_score
            max_possible_score += 15
            
            # Community service matching (15 points possible)
            community_score = self._score_community_match(profile, scholarship)
            score += community_score
            max_possible_score += 15
            
            # Demographic matching (15 points possible)
            demographic_score = self._score_demographic_match(profile, scholarship)
            score += demographic_score
            max_possible_score += 15
            
            # Return percentage score
            final_score = int((score / max_possible_score) * 100) if max_possible_score > 0 else 0
            
            # For debugging: if we have any profile data, give at least some score
            if final_score == 0 and (profile.sports_played or profile.gpa or profile.state):
                final_score = 25  # Base score for having any relevant data
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 0
    
    def _score_athletic_match(self, profile: UserProfile, scholarship: Scholarship) -> int:
        """Score athletic criteria matching (0-30 points)."""
        try:
            score = 0
            
            # Check if scholarship is athletic type
            if scholarship.scholarship_type == ScholarshipType.ATHLETIC:
                score += 10  # Base athletic scholarship match
                
                # Check specific sports
                if profile.sports_played and scholarship.categories:
                    profile_sports = [sport.lower() for sport in profile.sports_played]
                    scholarship_categories = [cat.lower() for cat in scholarship.categories]
                    
                    # Look for sport matches in categories
                    sport_matches = any(sport in ' '.join(scholarship_categories) for sport in profile_sports)
                    if sport_matches:
                        score += 20  # Strong sport match
            
            # For merit scholarships, give some athletic credit if student plays sports
            elif scholarship.scholarship_type == ScholarshipType.MERIT:
                if profile.sports_played and len(profile.sports_played) > 0:
                    score += 10  # Merit + athletics combo
                        
            # Check for athletic keywords in eligibility criteria
            if scholarship.eligibility_criteria:
                criteria_text = str(scholarship.eligibility_criteria).lower()
                if profile.sports_played:
                    profile_sports = [sport.lower() for sport in profile.sports_played]
                    sport_mentions = any(sport in criteria_text for sport in profile_sports)
                    if sport_mentions:
                        score += 15  # Moderate athletic match
                        
            return min(score, 30)
        except Exception as e:
            logger.error(f"Error in athletic matching: {e}")
            return 0
    
    def _score_academic_match(self, profile: UserProfile, scholarship: Scholarship) -> int:
        """Score academic criteria matching (0-25 points)."""
        try:
            score = 0
            
            # For MERIT scholarships, give strong academic score
            if scholarship.scholarship_type == ScholarshipType.MERIT:
                score += 15  # Strong merit match
            
            # Basic academic score if we have any academic data
            if profile.gpa or profile.sat_score or profile.act_score:
                score += 5  # Base academic score
            
            # GPA matching - check against the scholarship's min GPA (2.5)
            if profile.gpa:
                profile_gpa = float(profile.gpa)
                
                # Check scholarship criteria
                if scholarship.academic_requirements and isinstance(scholarship.academic_requirements, dict):
                    if 'gpa_minimum' in scholarship.academic_requirements:
                        try:
                            min_gpa = float(scholarship.academic_requirements['gpa_minimum'])
                            if profile_gpa >= min_gpa:
                                score += 10  # Meets GPA requirement
                                # Bonus for exceeding
                                if profile_gpa >= min_gpa + 0.5:
                                    score += 5
                        except (ValueError, TypeError):
                            pass
                
                # General GPA scoring
                if profile_gpa >= 3.0:
                    score += 5  # Good GPA
                if profile_gpa >= 3.5:
                    score += 5  # Great GPA
            
            # Test score matching
            if scholarship.eligibility_criteria:
                criteria = scholarship.eligibility_criteria
                if isinstance(criteria, dict):
                    # SAT score matching
                    if profile.sat_score and 'min_sat' in criteria:
                        try:
                            min_sat = int(criteria['min_sat'])
                            if profile.sat_score >= min_sat:
                                score += 5
                        except (ValueError, TypeError):
                            pass
                    
                    # ACT score matching
                    if profile.act_score and 'min_act' in criteria:
                        try:
                            min_act = int(criteria['min_act'])
                            if profile.act_score >= min_act:
                                score += 5
                        except (ValueError, TypeError):
                            pass
            
            return min(score, 25)
        except Exception as e:
            logger.error(f"Error in academic matching: {e}")
            return 0
    
    def _score_geographic_match(self, profile: UserProfile, scholarship: Scholarship) -> int:
        """Score geographic criteria matching (0-15 points)."""
        try:
            score = 0
            
            # Basic geographic score if we have location data
            if profile.state:
                score += 5  # Base score for having location
            
            if scholarship.demographic_criteria and isinstance(scholarship.demographic_criteria, dict):
                criteria = scholarship.demographic_criteria
                
                # State matching
                if profile.state and 'states' in criteria:
                    eligible_states = criteria['states']
                    if isinstance(eligible_states, list):
                        if profile.state.lower() in [state.lower() for state in eligible_states]:
                            score += 10  # Perfect state match
                    elif isinstance(eligible_states, str):
                        if profile.state.lower() in eligible_states.lower():
                            score += 10
                
                # Region matching (partial credit)
                if profile.state and 'region' in criteria:
                    score += 5  # Partial regional match
            
            return min(score, 15)
        except Exception as e:
            logger.error(f"Error in geographic matching: {e}")
            return 0
    
    def _score_community_match(self, profile: UserProfile, scholarship: Scholarship) -> int:
        """Score community service criteria matching (0-15 points)."""
        try:
            score = 0
            
            # Check for community service scholarships
            if scholarship.scholarship_type == ScholarshipType.COMMUNITY_SERVICE:
                score += 10  # Base community service match
                
                # Check volunteer hours
                if profile.volunteer_hours:
                    if profile.volunteer_hours >= 100:
                        score += 5  # Significant volunteer hours
            
            # Basic community score if we have volunteer data
            if profile.volunteer_hours and profile.volunteer_hours > 0:
                score += 5  # Base score for volunteering
            
            # Check eligibility criteria for volunteer requirements
            if scholarship.eligibility_criteria and isinstance(scholarship.eligibility_criteria, dict):
                criteria = scholarship.eligibility_criteria
                if 'min_volunteer_hours' in criteria and profile.volunteer_hours:
                    try:
                        min_hours = int(criteria['min_volunteer_hours'])
                        if profile.volunteer_hours >= min_hours:
                            score += 5
                    except (ValueError, TypeError):
                        pass
            
            return min(score, 15)
        except Exception as e:
            logger.error(f"Error in community matching: {e}")
            return 0
    
    def _score_demographic_match(self, profile: UserProfile, scholarship: Scholarship) -> int:
        """Score demographic criteria matching (0-15 points)."""
        try:
            score = 0
            
            # Basic demographic score
            if profile.graduation_year:
                score += 5  # Base score for having graduation year
            
            # This is a basic implementation - you'd expand based on actual demographic criteria
            if scholarship.demographic_criteria and isinstance(scholarship.demographic_criteria, dict):
                criteria = scholarship.demographic_criteria
                
                # Graduation year matching
                if profile.graduation_year and 'graduation_year' in criteria:
                    eligible_years = criteria['graduation_year']
                    if isinstance(eligible_years, list):
                        if profile.graduation_year in eligible_years:
                            score += 10
                    elif isinstance(eligible_years, int):
                        if profile.graduation_year == eligible_years:
                            score += 10
                
                # First generation college student
                if 'first_generation' in criteria and criteria.get('first_generation'):
                    score += 5  # Placeholder
            
            return min(score, 15)
        except Exception as e:
            logger.error(f"Error in demographic matching: {e}")
            return 0