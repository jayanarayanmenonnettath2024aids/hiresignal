"""
Scorer module: Compute 4-signal score for resume screening.
Signals: Semantic (SBERT), TF-IDF, Skills match, Years of Experience
"""

import math
import re
from typing import Optional, Dict, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.nlp.embeddings import EmbeddingsManager
from app.nlp.skill_extractor import extract_skills


class ResumeScorer:
    """Score resumes against job descriptions using 4 signals"""
    
    def __init__(self):
        self.tfidf_vectorizer = None
    
    def score_single(
        self,
        jd_text: str,
        resume_text: str,
        jd_skills: List[str],
        jd_yoe: Optional[float],
        weights: Dict[str, float],
        jd_embedding: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Score a single resume against a JD.
        
        Returns:
        {
            'score_semantic': float,
            'score_tfidf': float,
            'score_skills': float,
            'score_experience': float,
            'final_score': float,
            'matched_skills': list,
            'missing_skills': list,
            'years_experience_detected': float or None,
        }
        """
        matched_skills, missing_skills = self._compute_skill_match(jd_skills, resume_text)
        years_experience = self._extract_yoe_from_resume(resume_text)
        
        # Signal 1: Semantic
        if jd_embedding is None:
            jd_embedding = EmbeddingsManager.encode_sync(jd_text)
        resume_embedding = EmbeddingsManager.encode_sync(resume_text)
        score_semantic = float(cosine_similarity([jd_embedding], [resume_embedding])[0][0])
        score_semantic = max(0.0, min(1.0, score_semantic))
        
        # Signal 2: TF-IDF (compute locally for single screen)
        score_tfidf = self._compute_tfidf_score(jd_text, resume_text)
        
        # Signal 3: Skills
        if not jd_skills:
            score_skills = 0.5  # Neutral if no skills in JD
        else:
            score_skills = len(matched_skills) / len(jd_skills)
        
        # Signal 4: Experience
        score_experience = self._compute_experience_score(years_experience, jd_yoe)
        
        # Final score
        final_score = (
            weights.get('semantic', 0.40) * score_semantic +
            weights.get('tfidf', 0.30) * score_tfidf +
            weights.get('skills', 0.20) * score_skills +
            weights.get('experience', 0.10) * score_experience
        )
        final_score = round(final_score, 4)
        
        return {
            'score_semantic': round(score_semantic, 4),
            'score_tfidf': round(score_tfidf, 4),
            'score_skills': round(score_skills, 4),
            'score_experience': round(score_experience, 4),
            'final_score': final_score,
            'matched_skills': sorted(matched_skills),
            'missing_skills': sorted(missing_skills),
            'years_experience_detected': years_experience,
        }
    
    def score_batch(
        self,
        jd_text: str,
        resume_texts: List[str],
        jd_skills: List[str],
        jd_yoe: Optional[float],
        weights: Dict[str, float]
    ) -> List[Dict]:
        """
        Score multiple resumes in batch.
        Uses pre-computed embeddings and TF-IDF for efficiency.
        """
        # Encode JD once
        jd_embedding = EmbeddingsManager.encode_sync(jd_text)
        
        # Batch encode all resumes
        resume_embeddings = EmbeddingsManager.encode_batch_sync(resume_texts)
        
        # Compute all semantic scores
        semantic_scores = cosine_similarity([jd_embedding], resume_embeddings)[0]
        
        # Fit TF-IDF on JD + all resumes
        all_texts = [jd_text] + resume_texts
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True
        )
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        tfidf_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        
        # Score each resume
        results = []
        for i, resume_text in enumerate(resume_texts):
            score_semantic = float(semantic_scores[i])
            score_semantic = max(0.0, min(1.0, score_semantic))
            
            score_tfidf = float(tfidf_scores[i])
            score_tfidf = max(0.0, min(1.0, score_tfidf))
            
            matched_skills, missing_skills = self._compute_skill_match(jd_skills, resume_text)
            years_experience = self._extract_yoe_from_resume(resume_text)
            
            if not jd_skills:
                score_skills = 0.5
            else:
                score_skills = len(matched_skills) / len(jd_skills)
            
            score_experience = self._compute_experience_score(years_experience, jd_yoe)
            
            final_score = (
                weights.get('semantic', 0.40) * score_semantic +
                weights.get('tfidf', 0.30) * score_tfidf +
                weights.get('skills', 0.20) * score_skills +
                weights.get('experience', 0.10) * score_experience
            )
            final_score = round(final_score, 4)
            
            results.append({
                'score_semantic': round(score_semantic, 4),
                'score_tfidf': round(score_tfidf, 4),
                'score_skills': round(score_skills, 4),
                'score_experience': round(score_experience, 4),
                'final_score': final_score,
                'matched_skills': sorted(matched_skills),
                'missing_skills': sorted(missing_skills),
                'years_experience_detected': years_experience,
            })
        
        return results
    
    def _compute_skill_match(self, jd_skills: List[str], resume_text: str) -> tuple:
        """Compute matched and missing skills"""
        jd_skill_set = set(jd_skills)
        resume_skills = set(extract_skills(resume_text))
        
        matched = jd_skill_set & resume_skills
        missing = jd_skill_set - resume_skills
        
        return list(matched), list(missing)
    
    def _compute_tfidf_score(self, jd_text: str, resume_text: str) -> float:
        """Compute TF-IDF cosine similarity"""
        try:
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
            matrix = vectorizer.fit_transform([jd_text, resume_text])
            score = cosine_similarity(matrix[0:1], matrix[1:])[0][0]
            return float(score)
        except:
            return 0.5  # Default neutral score
    
    def _compute_experience_score(self, resume_yoe: Optional[float], jd_yoe: Optional[float]) -> float:
        """Compute experience signal score"""
        if jd_yoe is None or jd_yoe == 0:
            return 0.5  # Neutral
        if resume_yoe is None:
            return 0.5  # Neutral
        
        if resume_yoe >= jd_yoe:
            return 1.0
        elif resume_yoe >= jd_yoe * 0.75:
            return 0.7
        elif resume_yoe >= jd_yoe * 0.5:
            return 0.4
        else:
            return 0.1
    
    def _extract_yoe_from_resume(self, text: str) -> Optional[float]:
        """Extract years of experience from resume text"""
        # Look for patterns like "5 years of experience", "2019-2023"
        patterns = [
            r'(\d+)\s*(?:years?|years)\s+(?:of\s+)?experience',
            r'(\d+)\+\s*years?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    years = float(matches[0])
                    return min(years, 40.0)  # Cap at 40
                except:
                    pass
        
        return None


# Singleton
scorer = ResumeScorer()
