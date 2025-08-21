"""
Enhanced PT KAI Talent Profile App with Duplicate Name Handling
Handles duplicate names (same name, different NIPP) for individual and batch downloads
"""

import base64
import io
import os
import tempfile
import zipfile
import re
from datetime import datetime
from typing import List, Tuple, Dict, Any

import pandas as pd
import streamlit as st
from fpdf import FPDF

# ========== ENHANCED DATE PARSER ==========
class EnhancedDateParser:
    """Advanced date parser supporting multiple Indonesian and international formats"""
    
    INDONESIAN_MONTHS = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
    }
    
    DATE_PATTERNS = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',      # DD/MM/YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',      # DD-MM-YYYY
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',     # DD.MM.YYYY
        r'(\d{4})-(\d{1,2})-(\d{1,2})',      # YYYY-MM-DD
        r'(\d{1,2})\s+(\w+)\s+(\d{4})',       # DD Month YYYY
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',     # Month DD, YYYY
    ]
    
    @classmethod
    def parse_date(cls, date_string: str):
        """Parse date from various formats"""
        if not date_string or str(date_string).strip() in ['-', '', 'nan']:
            return None
            
        date_str = str(date_string).strip().lower()
        date_str = re.sub(r'\s+', ' ', date_str)
        
        # Try dateutil parser if available
        try:
            from dateutil import parser as date_parser
            return date_parser.parse(date_str, dayfirst=True)
        except:
            pass
            
        # Try manual pattern matching
        for pattern in cls.DATE_PATTERNS:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                groups = match
