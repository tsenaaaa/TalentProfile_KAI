"""
Enhanced Date Parser for Flexible Date Format Handling
Supports Indonesian and international date formats
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any
import dateutil.parser as parser
from dateutil.parser import ParserError

class EnhancedDateParser:
    """Advanced date parser supporting multiple formats and languages"""
    
    # Indonesian month mappings
    INDONESIAN_MONTHS = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
    }
    
    # Common date patterns
    DATE_PATTERNS = [
        # DD/MM/YYYY
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        # DD-MM-YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',
        # DD.MM.YYYY
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',
        # YYYY-MM-DD
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        # DD Month YYYY (Indonesian)
        r'(\d{1,2})\s+(\w+)\s+(\d{4})',
        # Month DD, YYYY
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',
        # DD MMM YYYY
        r'(\d{1,2})\s+(\w{3})\s+(\d{4})',
    ]
    
    @classmethod
    def parse_date(cls, date_string: str) -> Optional[datetime]:
        """
        Parse date from various formats
        
        Args:
            date_string: Input date string
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_string or str(date_string).strip() == '-':
            return None
            
        date_str = str(date_string).strip().lower()
        
        # Clean up common issues
        date_str = re.sub(r'\s+', ' ', date_str)
        date_str = re.sub(r'[^\w\s/.,-]', '', date_str)
        
        # Try dateutil parser first
        try:
            return parser.parse(date_str, dayfirst=True)
        except ParserError:
            pass
            
        # Try manual pattern matching
        for pattern in cls.DATE_PATTERNS:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    if len(groups) == 3:
                        # Handle different order patterns
                        if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        elif any(month in date_str for month in cls.INDONESIAN_MONTHS.keys()):
                            # Indonesian month format
                            day = int(groups[0])
                            month_str = groups[1].lower()
                            year = int(groups[2])
                            
                            # Map Indonesian month
                            if month_str in cls.INDONESIAN_MONTHS:
                                month = cls.INDONESIAN_MONTHS[month_str]
                            else:
                                # Try English month
                                try:
                                    month = datetime.strptime(month_str[:3], '%b').month
                                except:
                                    continue
                        else:
                            # DD/MM/YYYY or similar
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                            
                        return datetime(year, month, day)
                except ValueError:
                    continue
        
        return None
    
    @classmethod
    def format_indonesian_date(cls, date_obj: datetime) -> str:
        """Format date in Indonesian style"""
        if not date_obj:
            return "-"
            
        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        
        return f"{date_obj.day} {months[date_obj.month-1]} {date_obj.year}"
    
    @classmethod
    def extract_place_and_date(cls, combined_string: str) -> Dict[str, Any]:
        """
        Extract place and date from combined string
        
        Args:
            combined_string: String like "Jakarta, 15 Januari 1990"
            
        Returns:
            Dictionary with 'place' and 'date' keys
        """
        if not combined_string or str(combined_string).strip() == '-':
            return {"place": "-", "date": None, "formatted_date": "-"}
            
        combined = str(combined_string).strip()
        
        # Split by comma
        parts = combined.split(',')
        if len(parts) >= 2:
            place = parts[0].strip()
            date_part = ','.join(parts[1:]).strip()
            
            # Parse date
            parsed_date = cls.parse_date(date_part)
            formatted_date = cls.format_indonesian_date(parsed_date) if parsed_date else "-"
            
            return {
                "place": place,
                "date": parsed_date,
                "formatted_date": formatted_date,
                "original": combined
            }
        else:
            # Try to find date in the string
            date_match = re.search(r'\d{1,2}[\s/.,-]+\w+[\s/.,-]+\d{4}', combined)
            if date_match:
                date_str = date_match.group()
                place = combined.replace(date_str, '').strip()
                parsed_date = cls.parse_date(date_str)
                formatted_date = cls.format_indonesian_date(parsed_date) if parsed_date else "-"
                
                return {
                    "place": place,
                    "date": parsed_date,
                    "formatted_date": formatted_date,
                    "original": combined
                }
            
            return {
                "place": combined,
                "date": None,
                "formatted_date": "-",
                "original": combined
            }

    @classmethod
    def validate_date(cls, date_string: str) -> bool:
        """Validate if string can be parsed as date"""
        return cls.parse_date(date_string) is not None
