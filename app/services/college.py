# app/services/college.py
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc, text
from datetime import datetime
import logging

from app.models.college import College, CollegeFavorite, CollegeSavedSearch
from app.schemas.college import CollegeCreate, CollegeSearchFilters

logger = logging.getLogger(__name__)


class CollegeService:
    """Service for college search and management operations"""

    def __init__(self, db: Session):
        self.db = db

    # ===========================
    # BASIC CRUD OPERATIONS
    # ===========================

    def get_college_by_id(self, college_id: int) -> Optional[College]:
        """Get college by ID"""
        return (
            self.db.query(College)
            .filter(College.id == college_id, College.is_active == True)
            .first()
        )

    def get_college_by_unitid(self, unitid: int) -> Optional[College]:
        """Get college by IPEDS UNITID"""
        return (
            self.db.query(College)
            .filter(College.unitid == unitid, College.is_active == True)
            .first()
        )

    def create_college(self, college_data: CollegeCreate) -> College:
        """Create a new college (for data import)"""
        try:
            db_college = College(**college_data.model_dump(exclude_unset=True))
            self.db.add(db_college)
            self.db.commit()
            self.db.refresh(db_college)

            logger.info(f"Created college: {db_college.id} - {db_college.name}")
            return db_college

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating college: {str(e)}")
            raise Exception(f"Failed to create college: {str(e)}")

    # ===========================
    # SEARCH FUNCTIONALITY
    # ===========================

    def search_colleges(
        self, filters: CollegeSearchFilters, user_id: Optional[int] = None
    ) -> Tuple[List[College], int, Dict[str, Any]]:
        """
        Advanced college search with filters and personalization
        Returns (colleges, total_count, search_metadata)
        """
        try:
            query = self.db.query(College).filter(College.is_active == True)

            # Apply filters
            query = self._apply_search_filters(query, filters)

            # Get total count before pagination
            total_count = query.count()

            # Apply sorting
            query = self._apply_sorting(query, filters.sort_by, filters.sort_order)

            # Apply pagination
            offset = (filters.page - 1) * filters.limit
            colleges = query.offset(offset).limit(filters.limit).all()

            # Generate search metadata
            search_metadata = self._generate_search_metadata(
                filters, total_count, colleges
            )

            logger.info(
                f"College search completed: {len(colleges)} results from {total_count} total"
            )
            return colleges, total_count, search_metadata

        except Exception as e:
            logger.error(f"Error in college search: {str(e)}")
            raise Exception(f"College search failed: {str(e)}")

    def _apply_search_filters(self, query, filters: CollegeSearchFilters):
        """Apply all search filters to the query"""

        # Text search
        if filters.search_query:
            search_term = f"%{filters.search_query}%"
            query = query.filter(
                or_(
                    College.name.ilike(search_term),
                    College.alias.ilike(search_term),
                    College.city.ilike(search_term),
                    College.state.ilike(search_term),
                )
            )

        # Location filters
        if filters.state:
            if isinstance(filters.state, list):
                query = query.filter(College.state.in_(filters.state))
            else:
                query = query.filter(College.state == filters.state)

        if filters.city:
            query = query.filter(College.city.ilike(f"%{filters.city}%"))

        if filters.region:
            query = query.filter(College.region == filters.region)

        # Institution type filters
        if filters.college_type:
            if isinstance(filters.college_type, list):
                query = query.filter(College.college_type.in_(filters.college_type))
            else:
                query = query.filter(College.college_type == filters.college_type)

        if filters.size_category:
            if isinstance(filters.size_category, list):
                query = query.filter(College.size_category.in_(filters.size_category))
            else:
                query = query.filter(College.size_category == filters.size_category)

        if filters.carnegie_classification:
            query = query.filter(
                College.carnegie_classification == filters.carnegie_classification
            )

        # Special designation filters
        if filters.hbcu_only:
            query = query.filter(College.is_hbcu == True)

        if filters.hsi_only:
            query = query.filter(College.is_hsi == True)

        if filters.women_only:
            query = query.filter(College.is_women_only == True)

        if filters.religious_only:
            query = query.filter(College.is_religious == True)

        # Enrollment filters
        if filters.min_enrollment:
            query = query.filter(College.total_enrollment >= filters.min_enrollment)

        if filters.max_enrollment:
            query = query.filter(College.total_enrollment <= filters.max_enrollment)

        # Academic filters
        if filters.min_acceptance_rate:
            query = query.filter(College.acceptance_rate >= filters.min_acceptance_rate)

        if filters.max_acceptance_rate:
            query = query.filter(College.acceptance_rate <= filters.max_acceptance_rate)

        # SAT score filters (student's scores vs college ranges)
        if filters.student_sat_score:
            # Find colleges where student's score is within range
            query = query.filter(
                or_(
                    College.sat_total_25.is_(None),  # No SAT data available
                    and_(
                        College.sat_total_25 <= filters.student_sat_score,
                        College.sat_total_75 >= filters.student_sat_score,
                    ),
                    College.sat_total_25
                    <= filters.student_sat_score,  # Student above range
                )
            )

        # ACT score filters
        if filters.student_act_score:
            query = query.filter(
                or_(
                    College.act_composite_25.is_(None),
                    and_(
                        College.act_composite_25 <= filters.student_act_score,
                        College.act_composite_75 >= filters.student_act_score,
                    ),
                    College.act_composite_25 <= filters.student_act_score,
                )
            )

        # GPA filters
        if filters.student_gpa:
            # This would require additional logic to match GPA requirements
            # For now, we'll use a simple competitiveness filter
            if filters.student_gpa >= 3.8:
                # High GPA students can apply anywhere
                pass
            elif filters.student_gpa >= 3.5:
                # Good GPA - exclude most competitive schools
                query = query.filter(
                    or_(
                        College.acceptance_rate.is_(None), College.acceptance_rate >= 15
                    )
                )
            elif filters.student_gpa >= 3.0:
                # Average GPA - focus on less competitive schools
                query = query.filter(
                    or_(
                        College.acceptance_rate.is_(None), College.acceptance_rate >= 30
                    )
                )

        # Cost filters
        if filters.max_tuition:
            if filters.in_state_student:
                query = query.filter(
                    or_(
                        College.tuition_in_state.is_(None),
                        College.tuition_in_state <= filters.max_tuition,
                    )
                )
            else:
                query = query.filter(
                    or_(
                        College.tuition_out_state.is_(None),
                        College.tuition_out_state <= filters.max_tuition,
                    )
                )

        if filters.max_total_cost:
            cost_field = (
                College.total_cost_in_state
                if filters.in_state_student
                else College.total_cost_out_state
            )
            query = query.filter(
                or_(cost_field.is_(None), cost_field <= filters.max_total_cost)
            )

        # Academic program filters
        if filters.major_interest:
            # Search in popular_majors and all_majors_offered arrays
            query = query.filter(
                or_(
                    College.popular_majors.contains([filters.major_interest]),
                    College.all_majors_offered.contains([filters.major_interest]),
                )
            )

        # Campus features
        if filters.urban_setting:
            query = query.filter(College.campus_setting == "Urban")

        if filters.requires_on_campus_housing is not None:
            query = query.filter(
                College.housing_required == filters.requires_on_campus_housing
            )

        if filters.ncaa_division:
            query = query.filter(College.ncaa_division == filters.ncaa_division)

        # Test optional filter
        if filters.test_optional_only:
            query = query.filter(College.is_test_optional == True)

        return query

    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """Apply sorting to the query"""

        # Map sort fields to actual columns
        sort_mapping = {
            "name": College.name,
            "acceptance_rate": College.acceptance_rate,
            "tuition": College.tuition_out_state,
            "enrollment": College.total_enrollment,
            "sat_score": College.sat_total_75,
            "graduation_rate": College.graduation_rate_6_year,
            "competitiveness": College.competitiveness_score,
            "affordability": College.affordability_score,
            "value": College.value_score,
            "created_at": College.created_at,
        }

        sort_column = sort_mapping.get(sort_by, College.name)

        if sort_order.lower() == "desc":
            # For null values, put them last in descending order
            query = query.order_by(desc(sort_column.nullslast()))
        else:
            # For null values, put them last in ascending order
            query = query.order_by(asc(sort_column.nullslast()))

        return query

    def _generate_search_metadata(
        self, filters: CollegeSearchFilters, total_count: int, colleges: List[College]
    ) -> Dict[str, Any]:
        """Generate metadata about the search results"""

        if not colleges:
            return {
                "total_results": 0,
                "page_info": {
                    "current_page": filters.page,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                },
            }

        total_pages = (total_count + filters.limit - 1) // filters.limit

        # Calculate aggregate statistics
        acceptance_rates = [
            c.acceptance_rate for c in colleges if c.acceptance_rate is not None
        ]
        tuition_costs = []
        for c in colleges:
            if filters.in_state_student and c.tuition_in_state:
                tuition_costs.append(c.tuition_in_state)
            elif c.tuition_out_state:
                tuition_costs.append(c.tuition_out_state)

        sat_scores = [c.sat_total_75 for c in colleges if c.sat_total_75 is not None]

        stats = {}
        if acceptance_rates:
            stats["acceptance_rate"] = {
                "min": min(acceptance_rates),
                "max": max(acceptance_rates),
                "avg": sum(acceptance_rates) / len(acceptance_rates),
            }

        if tuition_costs:
            stats["tuition"] = {
                "min": min(tuition_costs),
                "max": max(tuition_costs),
                "avg": sum(tuition_costs) / len(tuition_costs),
            }

        if sat_scores:
            stats["sat_scores"] = {
                "min": min(sat_scores),
                "max": max(sat_scores),
                "avg": sum(sat_scores) / len(sat_scores),
            }

        # Count by categories
        type_counts = {}
        size_counts = {}
        state_counts = {}

        for college in colleges:
            # Type distribution
            if college.college_type:
                type_counts[college.college_type.value] = (
                    type_counts.get(college.college_type.value, 0) + 1
                )

            # Size distribution
            if college.size_category:
                size_counts[college.size_category.value] = (
                    size_counts.get(college.size_category.value, 0) + 1
                )

            # State distribution
            if college.state:
                state_counts[college.state] = state_counts.get(college.state, 0) + 1

        return {
            "total_results": total_count,
            "results_on_page": len(colleges),
            "page_info": {
                "current_page": filters.page,
                "total_pages": total_pages,
                "items_per_page": filters.limit,
                "has_next": filters.page < total_pages,
                "has_previous": filters.page > 1,
            },
            "statistics": stats,
            "distributions": {
                "by_type": type_counts,
                "by_size": size_counts,
                "by_state": dict(
                    sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                ),  # Top 10 states
            },
            "filters_applied": filters.model_dump(exclude_none=True),
        }

    # ===========================
    # ADVANCED SEARCH FEATURES
    # ===========================

    def find_similar_colleges(self, college_id: int, limit: int = 10) -> List[College]:
        """Find colleges similar to the given college"""

        target_college = self.get_college_by_id(college_id)
        if not target_college:
            return []

        query = self.db.query(College).filter(
            College.is_active == True, College.id != college_id
        )

        # Find colleges with similar characteristics
        similar_conditions = []

        # Same type
        if target_college.college_type:
            similar_conditions.append(
                College.college_type == target_college.college_type
            )

        # Similar size
        if target_college.size_category:
            similar_conditions.append(
                College.size_category == target_college.size_category
            )

        # Same state or region
        if target_college.state:
            similar_conditions.append(College.state == target_college.state)

        if target_college.region:
            similar_conditions.append(College.region == target_college.region)

        # Similar selectivity (within 10% acceptance rate)
        if target_college.acceptance_rate:
            similar_conditions.append(
                and_(
                    College.acceptance_rate >= target_college.acceptance_rate - 10,
                    College.acceptance_rate <= target_college.acceptance_rate + 10,
                )
            )

        # Apply similarity filters with OR logic (flexible matching)
        if similar_conditions:
            query = query.filter(or_(*similar_conditions))

        # Order by multiple similarity factors
        query = query.order_by(
            # Prefer same type
            desc(College.college_type == target_college.college_type),
            # Prefer similar size
            desc(College.size_category == target_college.size_category),
            # Prefer same region
            desc(College.region == target_college.region),
            # Secondary sort by name
            College.name,
        )

        return query.limit(limit).all()

    def get_match_score(
        self, college: College, student_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate a match score between a college and student profile
        Returns score from 0-100
        """
        score = 0.0
        max_possible_score = 0.0

        # Academic match (40% of total score)
        academic_score, academic_max = self._calculate_academic_match(
            college, student_profile
        )
        score += academic_score
        max_possible_score += academic_max

        # Financial match (25% of total score)
        financial_score, financial_max = self._calculate_financial_match(
            college, student_profile
        )
        score += financial_score
        max_possible_score += financial_max

        # Location preference match (20% of total score)
        location_score, location_max = self._calculate_location_match(
            college, student_profile
        )
        score += location_score
        max_possible_score += location_max

        # Size and culture match (15% of total score)
        culture_score, culture_max = self._calculate_culture_match(
            college, student_profile
        )
        score += culture_score
        max_possible_score += culture_max

        if max_possible_score == 0:
            return 50.0  # Neutral score if no criteria to evaluate

        return min(100.0, (score / max_possible_score) * 100)

    def _calculate_academic_match(
        self, college: College, profile: Dict
    ) -> Tuple[float, float]:
        """Calculate academic compatibility score"""
        score = 0.0
        max_score = 40.0

        # GPA compatibility (15 points)
        student_gpa = profile.get("gpa")
        if student_gpa and college.acceptance_rate:
            if college.acceptance_rate <= 25 and student_gpa >= 3.8:
                score += 15.0
            elif college.acceptance_rate <= 50 and student_gpa >= 3.5:
                score += 12.0
            elif college.acceptance_rate <= 75 and student_gpa >= 3.0:
                score += 10.0
            elif student_gpa >= 2.5:
                score += 8.0
        else:
            max_score -= 15.0

        # Test score compatibility (15 points)
        student_sat = profile.get("sat_score")
        student_act = profile.get("act_score")

        if student_sat and college.sat_total_25 and college.sat_total_75:
            if student_sat >= college.sat_total_75:
                score += 15.0
            elif student_sat >= college.sat_total_25:
                score += 12.0
            else:
                score += 8.0
        elif student_act and college.act_composite_25 and college.act_composite_75:
            if student_act >= college.act_composite_75:
                score += 15.0
            elif student_act >= college.act_composite_25:
                score += 12.0
            else:
                score += 8.0
        else:
            max_score -= 15.0

        # Major compatibility (10 points)
        intended_major = profile.get("intended_major")
        if intended_major and college.all_majors_offered:
            if intended_major in college.all_majors_offered:
                score += 10.0
            elif intended_major in (college.popular_majors or []):
                score += 8.0
        else:
            max_score -= 10.0

        return score, max_score

    def _calculate_financial_match(
        self, college: College, profile: Dict
    ) -> Tuple[float, float]:
        """Calculate financial compatibility score"""
        score = 0.0
        max_score = 25.0

        max_budget = profile.get("max_budget")
        in_state = profile.get("state") == college.state

        if max_budget:
            relevant_cost = (
                college.total_cost_in_state
                if in_state
                else college.total_cost_out_state
            )

            if relevant_cost:
                if relevant_cost <= max_budget:
                    # Within budget - score based on how much under budget
                    budget_ratio = relevant_cost / max_budget
                    if budget_ratio <= 0.7:
                        score += 25.0  # Significantly under budget
                    elif budget_ratio <= 0.9:
                        score += 20.0  # Comfortably under budget
                    else:
                        score += 15.0  # Just within budget
                else:
                    # Over budget - penalize based on how much over
                    over_ratio = relevant_cost / max_budget
                    if over_ratio <= 1.2:
                        score += 10.0  # Slightly over
                    elif over_ratio <= 1.5:
                        score += 5.0  # Moderately over
                    # No points if significantly over budget
            else:
                max_score -= 25.0
        else:
            max_score -= 25.0

        return score, max_score

    def _calculate_location_match(
        self, college: College, profile: Dict
    ) -> Tuple[float, float]:
        """Calculate location preference match"""
        score = 0.0
        max_score = 20.0

        preferred_states = profile.get("preferred_states", [])
        preferred_regions = profile.get("preferred_regions", [])
        preferred_setting = profile.get("preferred_setting")  # Urban, Suburban, Rural

        # State preference (10 points)
        if preferred_states:
            if college.state in preferred_states:
                score += 10.0
        else:
            max_score -= 10.0

        # Region preference (5 points)
        if preferred_regions:
            if college.region in preferred_regions:
                score += 5.0
        else:
            max_score -= 5.0

        # Campus setting preference (5 points)
        if preferred_setting:
            if college.campus_setting == preferred_setting:
                score += 5.0
        else:
            max_score -= 5.0

        return score, max_score

    def _calculate_culture_match(
        self, college: College, profile: Dict
    ) -> Tuple[float, float]:
        """Calculate cultural and size compatibility"""
        score = 0.0
        max_score = 15.0

        # Size preference (10 points)
        preferred_size = profile.get("preferred_size")
        if preferred_size:
            if college.size_category and college.size_category.value == preferred_size:
                score += 10.0
            # Partial credit for adjacent sizes
            elif (
                preferred_size == "medium"
                and college.size_category
                and college.size_category.value in ["small", "large"]
            ):
                score += 7.0
        else:
            max_score -= 10.0

        # Special interests (5 points)
        if profile.get("prefer_hbcu") and college.is_hbcu:
            score += 5.0
        elif profile.get("prefer_women_college") and college.is_women_only:
            score += 5.0
        elif profile.get("prefer_religious") and college.is_religious:
            score += 5.0
        else:
            max_score -= 5.0

        return score, max_score

    # ===========================
    # USER FAVORITES & SAVED SEARCHES
    # ===========================

    def add_to_favorites(
        self, user_id: int, college_id: int, notes: Optional[str] = None
    ) -> CollegeFavorite:
        """Add college to user's favorites"""

        # Check if already favorited
        existing = (
            self.db.query(CollegeFavorite)
            .filter(
                CollegeFavorite.user_id == user_id,
                CollegeFavorite.college_id == college_id,
            )
            .first()
        )

        if existing:
            raise ValueError("College already in favorites")

        favorite = CollegeFavorite(user_id=user_id, college_id=college_id, notes=notes)

        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)

        return favorite

    def remove_from_favorites(self, user_id: int, college_id: int) -> bool:
        """Remove college from user's favorites"""

        favorite = (
            self.db.query(CollegeFavorite)
            .filter(
                CollegeFavorite.user_id == user_id,
                CollegeFavorite.college_id == college_id,
            )
            .first()
        )

        if favorite:
            self.db.delete(favorite)
            self.db.commit()
            return True

        return False

    def get_user_favorites(self, user_id: int) -> List[College]:
        """Get user's favorite colleges"""

        favorites = (
            self.db.query(College)
            .join(CollegeFavorite)
            .filter(CollegeFavorite.user_id == user_id, College.is_active == True)
            .order_by(CollegeFavorite.created_at.desc())
            .all()
        )

        return favorites

    def save_search(
        self, user_id: int, search_name: str, search_criteria: Dict[str, Any]
    ) -> CollegeSavedSearch:
        """Save a college search for later use"""

        saved_search = CollegeSavedSearch(
            user_id=user_id,
            search_name=search_name,
            search_criteria=search_criteria,
            results_count=0,  # Will be updated when search is run
        )

        self.db.add(saved_search)
        self.db.commit()
        self.db.refresh(saved_search)

        return saved_search

    def get_user_saved_searches(self, user_id: int) -> List[CollegeSavedSearch]:
        """Get user's saved searches"""

        return (
            self.db.query(CollegeSavedSearch)
            .filter(CollegeSavedSearch.user_id == user_id)
            .order_by(CollegeSavedSearch.created_at.desc())
            .all()
        )

    # ===========================
    # ANALYTICS & INSIGHTS
    # ===========================

    def get_search_insights(self, filters: CollegeSearchFilters) -> Dict[str, Any]:
        """Get insights about search results without returning full results"""

        query = self.db.query(College).filter(College.is_active == True)
        query = self._apply_search_filters(query, filters)

        total_count = query.count()

        if total_count == 0:
            return {"total_results": 0, "suggestions": []}

        # Calculate insights
        insights = {"total_results": total_count, "suggestions": []}

        # If very few results, suggest relaxing criteria
        if total_count < 5:
            insights["suggestions"].append(
                "Consider expanding your search criteria to find more options"
            )

            if filters.max_acceptance_rate and filters.max_acceptance_rate < 50:
                insights["suggestions"].append(
                    "Try including less selective schools (higher acceptance rates)"
                )

            if filters.max_tuition and filters.max_tuition < 30000:
                insights["suggestions"].append(
                    "Consider increasing your budget to see more options"
                )

        # If too many results, suggest narrowing
        elif total_count > 100:
            insights["suggestions"].append(
                "Your search returned many results. Consider adding more specific criteria"
            )

        return insights
