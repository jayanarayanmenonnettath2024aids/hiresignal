"""
JD Preprocessor: Clean JD, extract skills, YoE, assess quality.
"""

import re
from typing import Tuple, Optional, List, Dict
from app.nlp.skill_extractor import extract_skills
from app.nlp.cleaner import TextCleaner


class JDPreprocessor:
    """Preprocess and analyze job descriptions"""
    
    @staticmethod
    def preprocess(jd_text: str) -> Dict:
        """
        Preprocess JD: clean, extract skills, YoE, assess quality.
        Returns dict with cleaned_text, required_skills, nice_to_have, min_yoe, quality_score, is_vague.
        """
        # Clean boilerplate
        cleaned_text = TextCleaner.remove_boilerplate(jd_text)
        cleaned_text = TextCleaner.clean_text(cleaned_text)
        
        # Extract sections
        sections = TextCleaner.extract_sections(cleaned_text)
        
        # Extract skills by section
        required_skills, nice_to_have = JDPreprocessor._extract_skills_by_section(cleaned_text, sections)
        
        # Extract YoE
        min_yoe = JDPreprocessor._extract_yoe(cleaned_text)
        
        # Quality score
        quality_score = JDPreprocessor._compute_quality_score(cleaned_text, required_skills)
        is_vague = quality_score < 0.30
        
        return {
            'cleaned_text': cleaned_text,
            'required_skills': required_skills,
            'nice_to_have_skills': nice_to_have,
            'min_yoe': min_yoe,
            'quality_score': quality_score,
            'is_vague': is_vague,
        }
    
    @staticmethod
    def _extract_skills_by_section(text: str, sections: dict) -> Tuple[List[str], List[str]]:
        """Extract required vs nice-to-have skills"""
        required_skills = []
        nice_to_have = []
        
        # Define section keywords
        required_keywords = ['required', 'must have', 'mandatory', 'should have']
        nice_keywords = ['nice to have', 'good to have', 'preferred', 'bonus', 'optional']
        
        # Check sections
        for section_name, section_text in sections.items():
            section_skills = extract_skills(section_text)
            
            if any(kw in section_name for kw in required_keywords):
                required_skills.extend(section_skills)
            elif any(kw in section_name for kw in nice_keywords):
                nice_to_have.extend(section_skills)
        
        # If no sections detected, extract all skills and treat as required
        if not required_skills and not nice_to_have:
            all_skills = extract_skills(text)
            required_skills = all_skills
        
        return sorted(list(set(required_skills))), sorted(list(set(nice_to_have)))
    
    @staticmethod
    def _extract_yoe(text: str) -> Optional[float]:
        """Extract minimum years of experience from JD"""
        # Pattern: "5+ years", "3-5 years", "minimum 2 years"
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)-(\d+)\s*years?(?:\s+of\s+experience)?',
            r'(?:minimum|at least)\s+(\d+)\s*years?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range: return minimum
                    years = min(int(x) for x in matches[0] if x)
                else:
                    years = int(matches[0])
                
                # Sanity check: cap at 40
                return min(float(years), 40.0)
        
        return None
    
    @staticmethod
    def _compute_quality_score(text: str, required_skills: List[str]) -> float:
        """
        Compute JD quality score.
        Based on skill count and text length.
        """
        hard_skill_count = len(required_skills)
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        # Skills per 50 words
        skill_ratio = hard_skill_count / max(total_words / 50, 1)
        
        # Normalize to 0-1
        quality_score = min(skill_ratio, 1.0)
        
        return round(quality_score, 3)


def preprocess_jd(jd_text: str) -> Dict:
    """Convenience function"""
    return JDPreprocessor.preprocess(jd_text)
