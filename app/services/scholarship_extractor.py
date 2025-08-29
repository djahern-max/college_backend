# app/services/scholarship_extractor.py
import httpx
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import json

from app.schemas.scholarship import ScholarshipCreate, ScholarshipType, DifficultyLevel
from app.core.config import settings

logger = logging.getLogger(__name__)


class ScholarshipExtractor:
    """
    Service to extract scholarship data from URLs and documents.
    Uses selective extraction to populate scholarship fields automatically.
    """

    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
        )

    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract scholarship data from a URL.
        Returns structured data that can be used to pre-fill a scholarship form.
        """
        try:
            logger.info(f"Extracting scholarship data from: {url}")

            # Fetch the webpage
            response = await self.session.get(url)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract data using multiple strategies
            extracted_data = {
                "source_url": url,
                "extraction_confidence": 0,
                "extraction_method": "web_scraping",
                "extracted_at": datetime.utcnow().isoformat(),
            }

            # Basic information extraction
            extracted_data.update(await self._extract_basic_info(soup, url))

            # Financial information
            extracted_data.update(await self._extract_financial_info(soup))

            # Requirements extraction
            extracted_data.update(await self._extract_requirements(soup))

            # Dates and deadlines
            extracted_data.update(await self._extract_dates(soup))

            # Contact and application info
            extracted_data.update(await self._extract_contact_info(soup, url))

            # Calculate overall confidence score
            extracted_data["extraction_confidence"] = self._calculate_confidence(
                extracted_data
            )

            logger.info(
                f"Extraction completed with {extracted_data['extraction_confidence']}% confidence"
            )
            return extracted_data

        except Exception as e:
            logger.error(f"Error extracting from URL {url}: {str(e)}")
            return {
                "source_url": url,
                "error": str(e),
                "extraction_confidence": 0,
                "extracted_at": datetime.utcnow().isoformat(),
            }

    async def _extract_basic_info(
        self, soup: BeautifulSoup, url: str
    ) -> Dict[str, Any]:
        """Extract title, description, and organization"""
        data = {}

        # Title extraction (multiple strategies)
        title_selectors = [
            "h1",
            ".scholarship-title",
            ".title",
            '[class*="title"]',
            "title",
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                data["title"] = self._clean_text(title_elem.get_text())
                break

        # Description extraction
        desc_selectors = [
            ".description",
            ".summary",
            ".overview",
            '[class*="description"]',
            'meta[name="description"]',
            ".scholarship-description",
        ]

        for selector in desc_selectors:
            if "meta" in selector:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    data["description"] = desc_elem.get("content", "").strip()
                    break
            else:
                desc_elem = soup.select_one(selector)
                if desc_elem and desc_elem.get_text().strip():
                    description = self._clean_text(desc_elem.get_text())
                    if len(description) > 50:  # Only use substantial descriptions
                        data["description"] = description[:1000]  # Limit length
                        break

        # Organization extraction
        org_indicators = [
            ".organization",
            ".sponsor",
            ".provider",
            '[class*="organization"]',
            '[class*="sponsor"]',
        ]

        for selector in org_indicators:
            org_elem = soup.select_one(selector)
            if org_elem and org_elem.get_text().strip():
                data["organization"] = self._clean_text(org_elem.get_text())
                break

        # If no organization found, try to extract from domain
        if "organization" not in data:
            domain = urlparse(url).netloc
            if domain:
                # Clean up domain to make it more readable
                org_name = (
                    domain.replace("www.", "")
                    .replace(".com", "")
                    .replace(".org", "")
                    .replace(".edu", "")
                )
                data["organization"] = (
                    org_name.replace("-", " ").replace("_", " ").title()
                )

        # Website URL (use the base domain)
        data["website_url"] = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        data["application_url"] = url

        return data

    async def _extract_financial_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract amount, renewable status, etc."""
        data = {}

        # Amount extraction using regex patterns
        text_content = soup.get_text().lower()

        # Common amount patterns
        amount_patterns = [
            r"\$[\d,]+(?:\.\d{2})?",  # $5,000 or $5,000.00
            r"[\d,]+\s*dollars?",  # 5000 dollars
            r"up to \$?([\d,]+)",  # up to $5000
            r"worth \$?([\d,]+)",  # worth $5000
            r"award[:\s]+\$?([\d,]+)",  # award: $5000
        ]

        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                # Clean and convert to integer
                amount_str = re.sub(r"[^\d]", "", str(match))
                if amount_str and len(amount_str) >= 3:  # At least $100
                    amounts.append(int(amount_str))

        if amounts:
            # Use the most reasonable amount (not too small, not too large)
            reasonable_amounts = [a for a in amounts if 100 <= a <= 100000]
            if reasonable_amounts:
                amount = max(reasonable_amounts)  # Usually the highest mentioned amount
                data["amount_exact"] = amount

        # Renewable detection
        renewable_keywords = [
            "renewable",
            "renew",
            "multiple years",
            "four years",
            "4 years",
        ]
        if any(keyword in text_content for keyword in renewable_keywords):
            data["is_renewable"] = True

            # Try to extract renewal years
            years_match = re.search(r"(\d+)\s*years?", text_content)
            if years_match:
                data["renewal_years"] = int(years_match.group(1))

        return data

    async def _extract_requirements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract GPA, test scores, and other requirements"""
        data = {}
        text_content = soup.get_text().lower()

        # GPA extraction
        gpa_patterns = [
            r"gpa[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*gpa",
            r"minimum.*gpa.*?(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*minimum.*gpa",
        ]

        for pattern in gpa_patterns:
            match = re.search(pattern, text_content)
            if match:
                gpa = float(match.group(1))
                if 2.0 <= gpa <= 5.0:  # Reasonable GPA range
                    data["min_gpa"] = gpa
                    break

        # SAT score extraction
        sat_patterns = [
            r"sat[:\s]+(\d{3,4})",
            r"(\d{3,4})\s*sat",
            r"minimum.*sat.*?(\d{3,4})",
        ]

        for pattern in sat_patterns:
            match = re.search(pattern, text_content)
            if match:
                sat = int(match.group(1))
                if 400 <= sat <= 1600:  # Valid SAT range
                    data["min_sat_score"] = sat
                    break

        # ACT score extraction
        act_patterns = [
            r"act[:\s]+(\d{1,2})",
            r"(\d{1,2})\s*act",
            r"minimum.*act.*?(\d{1,2})",
        ]

        for pattern in act_patterns:
            match = re.search(pattern, text_content)
            if match:
                act = int(match.group(1))
                if 1 <= act <= 36:  # Valid ACT range
                    data["min_act_score"] = act
                    break

        # Essay requirements
        essay_keywords = [
            "essay",
            "personal statement",
            "written statement",
            "composition",
        ]
        if any(keyword in text_content for keyword in essay_keywords):
            data["essay_required"] = True

            # Check for specific essay types
            if "personal statement" in text_content:
                data["personal_statement_required"] = True
            if "leadership" in text_content and "essay" in text_content:
                data["leadership_essay_required"] = True

        # Recommendation letters
        rec_patterns = [
            r"(\d+)\s*recommendation",
            r"(\d+)\s*reference",
            r"(\d+)\s*letter",
        ]

        for pattern in rec_patterns:
            match = re.search(pattern, text_content)
            if match:
                count = int(match.group(1))
                if 1 <= count <= 5:  # Reasonable range
                    data["recommendation_letters_required"] = count
                    break

        # Transcript requirement
        transcript_keywords = ["transcript", "academic record", "grades"]
        if any(keyword in text_content for keyword in transcript_keywords):
            data["transcript_required"] = True

        return data

    async def _extract_dates(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract application deadlines and other dates"""
        data = {}
        text_content = soup.get_text()

        # Common deadline patterns
        deadline_patterns = [
            r"deadline[:\s]+([a-zA-Z]+\s+\d{1,2},?\s+\d{4})",
            r"due[:\s]+([a-zA-Z]+\s+\d{1,2},?\s+\d{4})",
            r"apply by[:\s]+([a-zA-Z]+\s+\d{1,2},?\s+\d{4})",
            r"(\d{1,2}/\d{1,2}/\d{4})",  # MM/DD/YYYY
            r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
        ]

        for pattern in deadline_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                try:
                    # Try to parse the date
                    parsed_date = self._parse_date(match)
                    if parsed_date and parsed_date > datetime.now():
                        data["deadline"] = parsed_date.isoformat()
                        break
                except:
                    continue
            if "deadline" in data:
                break

        return data

    async def _extract_contact_info(
        self, soup: BeautifulSoup, url: str
    ) -> Dict[str, Any]:
        """Extract contact information and application links"""
        data = {}

        # Look for application links
        links = soup.find_all("a", href=True)
        apply_keywords = ["apply", "application", "submit", "register"]

        for link in links:
            link_text = link.get_text().lower()
            if any(keyword in link_text for keyword in apply_keywords):
                href = link["href"]
                # Convert relative URLs to absolute
                if href.startswith("/"):
                    href = urljoin(url, href)
                elif not href.startswith("http"):
                    href = urljoin(url, href)
                data["application_url"] = href
                break

        return data

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats"""
        date_formats = [
            "%B %d, %Y",  # January 15, 2024
            "%B %d %Y",  # January 15 2024
            "%m/%d/%Y",  # 01/15/2024
            "%Y-%m-%d",  # 2024-01-15
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace and newlines
        text = re.sub(r"\s+", " ", text.strip())
        # Remove common prefixes/suffixes
        text = re.sub(r"^(scholarship|award)[:\s]+", "", text, flags=re.IGNORECASE)
        return text.strip()

    def _calculate_confidence(self, data: Dict[str, Any]) -> int:
        """Calculate confidence score based on extracted data quality"""
        score = 0

        # Required fields boost confidence significantly
        if data.get("title"):
            score += 20
        if data.get("organization"):
            score += 15
        if data.get("description") and len(data.get("description", "")) > 50:
            score += 15

        # Financial info
        if data.get("amount_exact"):
            score += 20

        # Requirements boost confidence
        if data.get("min_gpa"):
            score += 10
        if data.get("min_sat_score") or data.get("min_act_score"):
            score += 10

        # Deadline information
        if data.get("deadline"):
            score += 10

        return min(100, score)

    async def suggest_scholarship_type(
        self, extracted_data: Dict[str, Any]
    ) -> Optional[ScholarshipType]:
        """Suggest scholarship type based on extracted content"""
        text_content = " ".join(
            [
                extracted_data.get("title", ""),
                extracted_data.get("description", ""),
                extracted_data.get("organization", ""),
            ]
        ).lower()

        # Type detection patterns
        type_patterns = {
            ScholarshipType.STEM: [
                "stem",
                "science",
                "technology",
                "engineering",
                "math",
                "computer",
                "software",
            ],
            ScholarshipType.NEED_BASED: [
                "need",
                "financial",
                "low income",
                "poverty",
                "economic",
            ],
            ScholarshipType.ACADEMIC_MERIT: [
                "merit",
                "academic",
                "gpa",
                "grades",
                "honor",
            ],
            ScholarshipType.DIVERSITY: [
                "diversity",
                "minority",
                "underrepresented",
                "inclusion",
                "multicultural",
            ],
            ScholarshipType.FIRST_GENERATION: [
                "first generation",
                "first-generation",
                "family college",
            ],
            ScholarshipType.LEADERSHIP: [
                "leadership",
                "leader",
                "president",
                "captain",
            ],
            ScholarshipType.COMMUNITY_SERVICE: [
                "service",
                "volunteer",
                "community",
                "civic",
            ],
            ScholarshipType.ARTS: ["arts", "music", "theater", "creative", "artistic"],
            ScholarshipType.ATHLETIC: ["athletic", "sports", "athlete", "team"],
        }

        # Score each type
        type_scores = {}
        for scholarship_type, keywords in type_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_content)
            if score > 0:
                type_scores[scholarship_type] = score

        # Return the highest scoring type
        if type_scores:
            return max(type_scores, key=type_scores.get)

        return ScholarshipType.ACADEMIC_MERIT  # Default

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()


class ScholarshipEnrichmentService:
    """
    Service to enrich scholarship data with additional context and validation
    """

    def __init__(self):
        self.extractor = ScholarshipExtractor()

    async def enrich_scholarship_data(
        self, extracted_data: Dict[str, Any]
    ) -> ScholarshipCreate:
        """
        Convert extracted data into a ScholarshipCreate object with enrichment
        """
        # Start with extracted data
        scholarship_data = {}

        # Map extracted fields to schema fields
        field_mapping = {
            "title": "title",
            "description": "description",
            "organization": "organization",
            "website_url": "website_url",
            "application_url": "application_url",
            "amount_exact": "amount_exact",
            "is_renewable": "is_renewable",
            "renewal_years": "renewal_years",
            "min_gpa": "min_gpa",
            "min_sat_score": "min_sat_score",
            "min_act_score": "min_act_score",
            "essay_required": "essay_required",
            "personal_statement_required": "personal_statement_required",
            "leadership_essay_required": "leadership_essay_required",
            "recommendation_letters_required": "recommendation_letters_required",
            "transcript_required": "transcript_required",
            "deadline": "deadline",
        }

        # Copy mapped fields
        for extracted_key, schema_key in field_mapping.items():
            if extracted_key in extracted_data:
                value = extracted_data[extracted_key]
                if value is not None and value != "":
                    scholarship_data[schema_key] = value

        # Add suggested scholarship type
        if "scholarship_type" not in scholarship_data:
            suggested_type = await self.extractor.suggest_scholarship_type(
                extracted_data
            )
            scholarship_data["scholarship_type"] = suggested_type

        # Set difficulty level based on requirements
        difficulty_score = 0
        if scholarship_data.get("min_gpa", 0) > 3.5:
            difficulty_score += 1
        if scholarship_data.get("min_sat_score", 0) > 1400:
            difficulty_score += 1
        if scholarship_data.get("essay_required"):
            difficulty_score += 1
        if scholarship_data.get("recommendation_letters_required", 0) > 2:
            difficulty_score += 1

        # Map difficulty score to enum
        if difficulty_score >= 3:
            scholarship_data["difficulty_level"] = DifficultyLevel.VERY_HARD
        elif difficulty_score == 2:
            scholarship_data["difficulty_level"] = DifficultyLevel.HARD
        elif difficulty_score == 1:
            scholarship_data["difficulty_level"] = DifficultyLevel.MODERATE
        else:
            scholarship_data["difficulty_level"] = DifficultyLevel.EASY

        # Parse deadline if it's a string
        if "deadline" in scholarship_data and isinstance(
            scholarship_data["deadline"], str
        ):
            try:
                scholarship_data["deadline"] = datetime.fromisoformat(
                    scholarship_data["deadline"].replace("Z", "+00:00")
                )
            except:
                del scholarship_data["deadline"]

        return ScholarshipCreate(**scholarship_data)

    async def close(self):
        """Close resources"""
        await self.extractor.close()
