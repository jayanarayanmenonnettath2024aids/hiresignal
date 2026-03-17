"""
Anomaly detector: Detect keyword stuffing, blank resumes, duplicates.
"""

import hashlib
from typing import Dict, Optional


class AnomalyDetector:
    """Detect anomalies in resumes"""
    
    @staticmethod
    def detect_keyword_stuffing(text: str, skill_count: int) -> bool:
        """
        Detect keyword stuffing using skill density ratio.
        Flagged if skill_count / word_count > 0.35
        """
        if not text or len(text) < 50:
            return False
        
        word_count = len(text.split())
        if word_count == 0:
            return False
        
        skill_density = skill_count / word_count
        return skill_density > 0.35
    
    @staticmethod
    def detect_blank_resume(text: str) -> bool:
        """
        Detect blank or nearly empty resume.
        Flagged if extracted text < 100 characters.
        """
        return len(text.strip()) < 100
    
    @staticmethod
    def compute_content_hash(content: bytes) -> str:
        """Compute SHA256 hash for duplicate detection"""
        return hashlib.sha256(content).hexdigest()[:16]
    
    @staticmethod
    def detect_multilingual(language_detected: str) -> bool:
        """Flag if non-English language detected"""
        return language_detected != "en" and language_detected != "unknown"
    
    @staticmethod
    def get_flags(
        extracted_text: str,
        skill_count: int,
        language_detected: str,
        is_ocr_used: bool,
        invisible_char_count: int = 0,
        total_char_count: int = 0
    ) -> Dict:
        """
        Compute all anomaly flags for a resume.
        Returns dict with flag names as keys, boolean values.
        """
        flags = {}
        
        # Blank resume
        if AnomalyDetector.detect_blank_resume(extracted_text):
            flags['blank_resume'] = True
        
        # Keyword stuffing
        if AnomalyDetector.detect_keyword_stuffing(extracted_text, skill_count):
            flags['keyword_stuffing'] = True
        
        # Multilingual
        if AnomalyDetector.detect_multilingual(language_detected):
            flags['multilingual'] = True
        
        # OCR used
        if is_ocr_used:
            flags['ocr_used'] = True
        
        # Invisible text (PDF only)
        if total_char_count > 0:
            invisible_ratio = invisible_char_count / total_char_count
            if invisible_ratio > 0.05:
                flags['invisible_text'] = True
        
        return flags
