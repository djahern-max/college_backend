# app/services/resume_parser.py
"""
Service for parsing resumes using Claude AI API
"""

import anthropic
import json
import logging
from typing import Dict, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse resume text and extract structured profile data using Claude AI"""

    def __init__(self):
        """Initialize Anthropic client"""
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def parse_resume(self, resume_text: str) -> Dict:
        """
        Parse resume text and extract structured data

        Args:
            resume_text: Extracted text from resume

        Returns:
            Dictionary with parsed profile data
        """
        try:
            prompt = self._build_parsing_prompt(resume_text)

            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                temperature=0,  # Use 0 for consistent extraction
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract JSON from response
            response_text = message.content[0].text

            # Parse JSON response
            parsed_data = self._extract_json(response_text)

            # Add metadata
            parsed_data["_metadata"] = {
                "confidence_score": self._calculate_confidence(parsed_data),
                "fields_extracted": self._count_fields(parsed_data),
                "extraction_notes": self._generate_notes(parsed_data),
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise Exception(f"Failed to parse resume: {str(e)}")

    def _build_parsing_prompt(self, resume_text: str) -> str:
        """Build the prompt for Claude to parse the resume"""
        return f"""You are an expert resume parser. Extract the following information from the resume text and return it as valid JSON.

Instructions:
- Extract only information that is clearly stated in the resume
- Use null for fields that are not found
- For dates, use YYYY format for years
- For GPA, include the numeric value (e.g., 3.8, 4.49)
- Be precise and accurate

Return a JSON object with this exact structure:

{{
  "first_name": "string or null",
  "last_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "city": "string or null",
  "state": "2-letter state code or null",
  "zip_code": "string or null",
  "high_school_name": "string or null",
  "graduation_year": "integer or null (e.g., 2026)",
  "gpa": "float or null (e.g., 4.49)",
  "gpa_scale": "string or null (e.g., '4.0', '5.0', 'weighted')",
  "sat_score": "integer or null (e.g., 1400)",
  "act_score": "integer or null (e.g., 32)",
  "intended_major": "string or null",
  "career_goals": "string or null",
  "extracurriculars": [
    {{
      "name": "string",
      "role": "string or null",
      "description": "string or null",
      "years_active": "string or null"
    }}
  ],
  "work_experience": [
    {{
      "title": "string",
      "organization": "string",
      "dates": "string",
      "description": "string or null"
    }}
  ],
  "honors_awards": [
    "string"
  ],
  "skills": [
    "string"
  ],
  "volunteer_hours": "integer or null (total hours if mentioned)"
}}

Resume text:
{resume_text}

Return ONLY the JSON object, no other text."""

    def _extract_json(self, response_text: str) -> Dict:
        """Extract and parse JSON from Claude's response"""
        try:
            # Try to parse the entire response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON in the text
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            raise ValueError("Could not extract valid JSON from response")

    def _calculate_confidence(self, parsed_data: Dict) -> float:
        """
        Calculate confidence score based on number of fields successfully extracted

        Args:
            parsed_data: Parsed profile data

        Returns:
            Confidence score between 0 and 1
        """
        critical_fields = [
            "first_name",
            "last_name",
            "high_school_name",
            "graduation_year",
            "gpa",
        ]
        important_fields = ["email", "phone", "city", "state", "intended_major"]

        critical_count = sum(1 for field in critical_fields if parsed_data.get(field))
        important_count = sum(1 for field in important_fields if parsed_data.get(field))

        # Weight critical fields more heavily
        score = (critical_count / len(critical_fields)) * 0.7 + (
            important_count / len(important_fields)
        ) * 0.3

        return round(score, 2)

    def _count_fields(self, parsed_data: Dict) -> int:
        """Count number of non-null fields extracted"""
        count = 0
        for key, value in parsed_data.items():
            if key == "_metadata":
                continue
            if value is not None:
                if isinstance(value, list) and len(value) > 0:
                    count += 1
                elif not isinstance(value, list):
                    count += 1
        return count

    def _generate_notes(self, parsed_data: Dict) -> List[str]:
        """Generate helpful notes about the extraction"""
        notes = []

        # Check for weighted GPA
        if parsed_data.get("gpa") and parsed_data.get("gpa", 0) > 4.0:
            notes.append(f"GPA appears to be weighted ({parsed_data['gpa']})")

        # Check for missing test scores
        if not parsed_data.get("sat_score") and not parsed_data.get("act_score"):
            notes.append("No standardized test scores found")

        # Check for volunteer hours
        if parsed_data.get("volunteer_hours"):
            notes.append(f"Total volunteer hours: {parsed_data['volunteer_hours']}")

        # Check for graduation year
        if parsed_data.get("graduation_year"):
            notes.append(f"Graduation year: {parsed_data['graduation_year']}")

        return notes
