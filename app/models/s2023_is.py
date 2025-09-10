# app/models/s2023_is.py
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class S2023_IS(Base):
    __tablename__ = "s2023_is"

    id = Column(Integer, primary_key=True, index=True)
    unitid = Column(String(10), unique=True, index=True, nullable=False)
    total_faculty = Column(Integer, nullable=False)
    female_faculty_percent = Column(Float, nullable=False)
    male_faculty_percent = Column(Float, nullable=False)
    diversity_category = Column(String(20), nullable=False)  # High/Moderate/Low
    faculty_size_category = Column(String(20), nullable=False)  # Very Large/Large/etc
    faculty_description = Column(Text, nullable=False)
    diversity_index = Column(Float, nullable=False)
    asian_faculty_percent = Column(Float, nullable=False)
    black_faculty_percent = Column(Float, nullable=False)
    hispanic_faculty_percent = Column(Float, nullable=False)
    white_faculty_percent = Column(Float, nullable=False)

    def __repr__(self):
        return f"<S2023_IS(unitid={self.unitid}, total_faculty={self.total_faculty})>"

    @property
    def faculty_highlights(self):
        """Generate 4-6 bullet points for display"""
        highlights = []

        # Faculty size
        highlights.append(
            f"Faculty: {self.total_faculty:,} professors ({self.faculty_size_category.lower()})"
        )

        # Gender balance
        if self.female_faculty_percent >= 60:
            highlights.append(f"Gender: {self.female_faculty_percent}% female faculty")
        elif self.male_faculty_percent >= 60:
            highlights.append(f"Gender: {self.male_faculty_percent}% male faculty")
        else:
            highlights.append(
                f"Gender: Balanced faculty ({self.female_faculty_percent}% female)"
            )

        # Diversity
        highlights.append(
            f"Diversity: {self.diversity_category.lower()} faculty diversity"
        )

        # Notable demographics (if >15%)
        notable_demos = []
        if self.asian_faculty_percent >= 15:
            notable_demos.append(f"{self.asian_faculty_percent}% Asian")
        if self.black_faculty_percent >= 15:
            notable_demos.append(f"{self.black_faculty_percent}% Black")
        if self.hispanic_faculty_percent >= 15:
            notable_demos.append(f"{self.hispanic_faculty_percent}% Hispanic")

        if notable_demos:
            highlights.append(f"Representation: {', '.join(notable_demos)} faculty")

        return highlights[:4]  # Limit to 4 bullet points

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "unitid": self.unitid,
            "total_faculty": self.total_faculty,
            "female_faculty_percent": self.female_faculty_percent,
            "male_faculty_percent": self.male_faculty_percent,
            "diversity_category": self.diversity_category,
            "faculty_size_category": self.faculty_size_category,
            "faculty_description": self.faculty_description,
            "diversity_index": self.diversity_index,
            "faculty_highlights": self.faculty_highlights,
            "demographics": {
                "asian_percent": self.asian_faculty_percent,
                "black_percent": self.black_faculty_percent,
                "hispanic_percent": self.hispanic_faculty_percent,
                "white_percent": self.white_faculty_percent,
            },
        }
