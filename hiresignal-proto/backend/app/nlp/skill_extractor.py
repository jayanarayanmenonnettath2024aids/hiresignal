"""
Skill extractor: Extract technical skills from text using taxonomy matching.
"""

import re
from typing import List, Set
from app.nlp.taxonomy.skills import SKILLS_TAXONOMY, ABBREVIATIONS


class SkillExtractor:
    """Extract skills from text using taxonomy"""
    
    def __init__(self):
        self.taxonomy = SKILLS_TAXONOMY
        self.abbreviations = ABBREVIATIONS
        # Pre-compile regex for multi-word skills
        self._build_patterns()
    
    def _build_patterns(self):
        """Build regex patterns for skill matching"""
        # Sort by length descending (longest first to match multi-word before single)
        sorted_skills = sorted(self.taxonomy, key=len, reverse=True)
        
        # Escape special regex chars and build alternation pattern
        escaped = [re.escape(skill) for skill in sorted_skills]
        self.skill_pattern = re.compile(r'\b(' + '|'.join(escaped) + r')\b', re.IGNORECASE)
    
    def extract(self, text: str) -> List[str]:
        """
        Extract and normalize skills from text.
        Returns sorted, deduplicated list of skills.
        """
        if not text or len(text.strip()) < 20:
            return []
        
        # Lowercase for matching
        text_lower = text.lower()
        
        # Find all skill matches
        matches = self.skill_pattern.findall(text_lower)
        matched_skills = set(matches)
        
        # Normalize: remove version numbers
        normalized = self._normalize_skills(text_lower, matched_skills)
        
        # Handle abbreviations
        expanded = self._expand_abbreviations(text_lower, normalized)
        
        return sorted(list(expanded))
    
    def _normalize_skills(self, text: str, skills: Set[str]) -> Set[str]:
        """Remove version numbers and normalize skill names"""
        normalized = set()
        
        for skill in skills:
            # Remove version numbers: "python 3.9" -> "python", "react 18" -> "react"
            normalized_skill = re.sub(r'\s+\d+(\.\d+)*', '', skill)
            normalized_skill = normalized_skill.strip()
            
            if normalized_skill and normalized_skill in self.taxonomy:
                normalized.add(normalized_skill)
            elif skill in self.taxonomy:
                normalized.add(skill)
        
        return normalized
    
    def _expand_abbreviations(self, text: str, skills: Set[str]) -> Set[str]:
        """Expand shorthand abbreviations like 'ml' to 'machine learning'"""
        expanded = set(skills)
        
        for abbrev, full_form in self.abbreviations.items():
            # Check if abbreviation appears as standalone word in text
            abbrev_pattern = rf'\b{re.escape(abbrev)}\b'
            if re.search(abbrev_pattern, text, re.IGNORECASE):
                # Only add if it's in our taxonomy
                if full_form in self.taxonomy:
                    expanded.add(full_form)
        
        return expanded


# Singleton instance
_extractor = SkillExtractor()


def extract_skills(text: str) -> List[str]:
    """Convenience function to extract skills from text"""
    return _extractor.extract(text)
