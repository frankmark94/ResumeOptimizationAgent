"""Utility helper functions for the application."""
import json
import re
from typing import List, Dict, Any
from datetime import datetime


def format_date(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def extract_json_from_text(text: str) -> Dict[str, Any] | None:
    """Extract JSON object from text that may contain other content."""
    try:
        # Try direct parse first
        return json.loads(text)
    except json.JSONDecodeError:
        # Look for JSON in text
        json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'\"/@]', '', text)
    return text.strip()


def calculate_percentage(part: int, whole: int) -> float:
    """Calculate percentage safely."""
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)


def format_skill_list(skills: List[str], max_display: int = 10) -> str:
    """Format a list of skills for display."""
    if not skills:
        return "No skills found"

    if len(skills) <= max_display:
        return ", ".join(skills)

    displayed = ", ".join(skills[:max_display])
    remaining = len(skills) - max_display
    return f"{displayed} (+{remaining} more)"


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """Highlight keywords in text for display (markdown bold)."""
    highlighted = text
    for keyword in keywords:
        # Case insensitive replacement
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted = pattern.sub(f"**{keyword}**", highlighted)
    return highlighted


def parse_bullet_points(text: str) -> List[str]:
    """Parse bullet points from text."""
    # Split by common bullet indicators
    bullets = re.split(r'\n[\s]*[•\-\*]\s*', text)
    bullets = [b.strip() for b in bullets if b.strip()]
    return bullets


def score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A (Excellent)"
    elif score >= 80:
        return "B (Good)"
    elif score >= 70:
        return "C (Fair)"
    elif score >= 60:
        return "D (Poor)"
    else:
        return "F (Needs Work)"


def estimate_reading_time(text: str) -> int:
    """Estimate reading time in minutes (avg 200 words per minute)."""
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return minutes


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:195] + (f'.{ext}' if ext else '')
    return filename


def merge_dicts(*dicts) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def deduplicate_list(items: List[str]) -> List[str]:
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in items:
        item_lower = item.lower().strip()
        if item_lower not in seen:
            seen.add(item_lower)
            result.append(item)
    return result


def format_currency(amount: float | None) -> str:
    """Format amount as currency."""
    if amount is None:
        return "N/A"
    return f"${amount:,.2f}"


def parse_salary_range(text: str) -> tuple[float | None, float | None]:
    """Parse salary range from text."""
    # Look for patterns like $80K-$100K, $80,000 - $100,000, etc.
    pattern = r'\$?(\d{1,3}(?:,?\d{3})*(?:k|K)?)\s*[-–to]\s*\$?(\d{1,3}(?:,?\d{3})*(?:k|K)?)'
    match = re.search(pattern, text)

    if not match:
        return None, None

    def parse_amount(amt_str: str) -> float:
        # Remove commas
        amt_str = amt_str.replace(',', '')
        # Handle K suffix
        if amt_str.lower().endswith('k'):
            return float(amt_str[:-1]) * 1000
        return float(amt_str)

    try:
        min_salary = parse_amount(match.group(1))
        max_salary = parse_amount(match.group(2))
        return min_salary, max_salary
    except (ValueError, AttributeError):
        return None, None


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Remove common separators
    digits = re.sub(r'[\s\-\(\)\.]', '', phone)
    # Check if it's a valid US phone number (10 digits) or international (10-15 digits)
    return len(digits) >= 10 and len(digits) <= 15 and digits.isdigit()
