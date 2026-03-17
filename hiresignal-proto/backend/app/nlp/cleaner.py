"""
Text cleaning module: Clean and normalize text for NLP processing.
"""

import re
from typing import List


class TextCleaner:
    """Clean and normalize resume/JD text"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing extra spaces, fixing line breaks, etc.
        """
        if not text:
            return ""
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove non-printable characters except newline/space
        text = ''.join(c if c.isprintable() or c in '\n\t ' else '' for c in text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_boilerplate(text: str) -> str:
        """
        Remove common HR/job description boilerplate.
        """
        # Patterns to remove
        patterns = [
            r'equal opportunity employer.*?(\n|$)',
            r'we offer (a )?competitive (salary|benefits|package).*?(\n|$)',
            r'only shortlisted candidates.*?(\n|$)',
            r'please (send|email|submit) your (resume|cv|application).*?(\n|$)',
            r'about (us|the company|our company):.*?(?=\n[A-Z]|\Z)',
        ]
        
        result = text
        for pattern in patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.DOTALL)
        
        return result.strip()
    
    @staticmethod
    def extract_sections(text: str) -> dict:
        """
        Extract sections from text based on headers.
        Returns dict with section names as keys.
        """
        sections = {}
        current_section = "metadata"
        current_content = []
        
        # Headers pattern: ends with colon or all caps
        header_pattern = r'^([A-Z][A-Za-z\s]+):?\s*$'
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if re.match(header_pattern, line) or line.isupper():
                # New section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.rstrip(':').lower()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections


def clean_text(text: str) -> str:
    """Convenience function"""
    return TextCleaner.clean_text(text)
