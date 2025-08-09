from sqlalchemy import Column, String, Text, Numeric, Date, Boolean, JSON, Enum
import enum
from app.db.base import Base


class ScholarshipStatus(str, enum.Enum):
    """Scholarship status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class ScholarshipType(str, enum.Enum):
    """Scholarship type enumeration"""
    MERIT = "merit"
    NEED_BASED = "need_based"
    ATHLETIC = "athletic"
    MINORITY = "minority"
    FIELD_SPECIFIC = "field_specific"
    GEOGRAPHIC = "geographic"
    FIRST_GENERATION = "first_generation"
    COMMUNITY_SERVICE = "community_service"
    OTHER = "other"


class Scholarship(Base):
    """
    Scholarship model for storing scholarship opportunities
    """
    __tablename__ = "scholarships"
    
    # Basic Information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    provider = Column(String(255), nullable=False)  # Organization offering scholarship
    
    # Financial Information
    amount_min = Column(Numeric(10, 2))  # Minimum award amount
    amount_max = Column(Numeric(10, 2))  # Maximum award amount
    amount_exact = Column(Numeric(10, 2))  # For fixed amount scholarships
    renewable = Column(Boolean, default=False)
    max_renewals = Column(String(50))  # e.g., "4 years", "Until graduation"
    
    # Dates and Deadlines
    deadline = Column(Date)
    start_date = Column(Date)  # When scholarship period begins
    end_date = Column(Date)    # When scholarship period ends
    
    # Application Information
    application_url = Column(String(500))
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    
    # Requirements and Criteria (stored as JSON for flexibility)
    eligibility_criteria = Column(JSON)  # GPA, income, citizenship, etc.
    required_documents = Column(JSON)    # Essays, transcripts, letters, etc.
    academic_requirements = Column(JSON) # Major, year in school, institution type
    demographic_criteria = Column(JSON)  # Age, gender, ethnicity, location
    
    # Classification
    categories = Column(JSON)  # Academic field, demographic groups, etc.
    scholarship_type = Column(Enum(ScholarshipType), default=ScholarshipType.MERIT)
    keywords = Column(JSON)    # Searchable keywords
    
    # Administrative
    status = Column(Enum(ScholarshipStatus), default=ScholarshipStatus.ACTIVE)
    external_id = Column(String(100), index=True)  # ID from external source
    source = Column(String(100))  # Which API/scraper found this
    source_url = Column(String(500))  # Original URL where found
    
    # Verification and Quality
    verified = Column(Boolean, default=False)  # Manual verification status
    last_verified = Column(Date)
    application_count = Column(Numeric(10, 0), default=0)  # Track popularity
    
    def __repr__(self):
        return f"<Scholarship(title='{self.title}', provider='{self.provider}', amount='${self.amount_min}-${self.amount_max}')>"