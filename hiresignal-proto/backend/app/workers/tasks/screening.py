"""
Screening task: Main Celery task for batch resume processing.
This is where the actual NLP scoringand ranking happens.
"""
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import time
import asyncio
from typing import List
from uuid import UUID
import redis
from app.workers.celery_app import celery_app
from app.database import sync_engine, AsyncSessionLocal
from app.services import job_service, resume_service, storage_service
from app.nlp import TextExtractor, AnomalyDetector, extract_skills, scorer, preprocess_jd
from app.config import settings
from sqlalchemy import text, func
from sqlalchemy.orm import sessionmaker

# Sync session for Celery
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(
    bind=True,
    name="app.workers.tasks.screening.process_screening_job",
    queue='default',
    max_retries=3,
)
def process_screening_job(self, job_id: str):
    """
    Main task: process all resumes for a screening job.
    Handles batch scoring, ranking, and progress updates.
    """
    job_id = UUID(job_id)
    db = SyncSession()
    redis_client = redis.from_url(settings.redis_url)
    
    try:
        # Fetch job
        from app.models import ScreeningJob
        job = db.query(ScreeningJob).filter(ScreeningJob.id == job_id).first()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Mark as processing
        job.status = 'processing'
        job.started_at = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
        db.commit()
        
        # Preprocess JD
        jd_info = preprocess_jd(job.jd_text)
        required_skills = jd_info['required_skills']
        min_yoe = jd_info['min_yoe']
        
        # List resume files
        resume_keys = []
        try:
            resume_dir = f"{job.tenant_id}/resumes/{job_id}"
            local_path = __import__('pathlib').Path(settings.upload_dir) / resume_dir
            if local_path.exists():
                for file_path in local_path.iterdir():
                    if file_path.is_file():
                        relative_key = str(file_path.relative_to(settings.upload_dir)).replace("\\", "/")
                        resume_keys.append(relative_key)
        except:
            resume_keys = []
        
        total_resumes = len(resume_keys)
        job.total_submitted = total_resumes
        db.commit()
        
        if total_resumes == 0:
            job.status = 'done'
            job.total_processed = 0
            job.total_failed = 0
            job.completed_at = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
            db.commit()
            return {"status": "done", "processed": 0}

        processed_in_run = 0
        failed_in_run = 0
        
        # Process each resume
        all_resume_texts = []
        resume_metadata = []
        
        for idx, key in enumerate(resume_keys):
            try:
                # Read resume file
                file_path = __import__('pathlib').Path(settings.upload_dir) / key
                content = file_path.read_bytes()
                
                # Extract text
                filename = file_path.name
                text, quality, language = TextExtractor.extract_text(filename, content)
                
                if not text or len(text.strip()) < 50:
                    # Blank or very short
                    from app.models import ResumeResult
                    result = db.query(ResumeResult).filter(
                        ResumeResult.job_id == job_id,
                        ResumeResult.filename == filename
                    ).first()
                    
                    if not result:
                        content_hash = AnomalyDetector.compute_content_hash(content)
                        flags = AnomalyDetector.get_flags(text, 0, language or 'en', False)
                        
                        result = ResumeResult(
                            job_id=job_id,
                            tenant_id=job.tenant_id,
                            filename=filename,
                            content_hash=content_hash,
                            extracted_text=text,
                            extracted_text_length=len(text),
                            extraction_quality=quality,
                            language_detected=language or 'en',
                            final_score=0.0,
                            flags={**flags, 'blank_resume': True},
                            status='done'
                        )
                        db.add(result)
                    else:
                        result.final_score = 0.0
                        result.status = 'done'
                    
                    db.commit()
                    processed_in_run += 1
                    continue
                
                # Check for duplicate
                from app.models import ResumeResult
                content_hash = AnomalyDetector.compute_content_hash(content)
                dup = db.query(ResumeResult).filter(
                    ResumeResult.job_id == job_id,
                    ResumeResult.content_hash == content_hash
                ).first()
                
                if dup:
                    # Skip duplicate
                    import logging
                    logging.info(f"Duplicate resume: {filename}")
                    processed_in_run += 1
                    continue
                
                # Collect for batch scoring
                all_resume_texts.append(text)
                resume_metadata.append({
                    'filename': filename,
                    'content': content,
                    'content_hash': content_hash,
                    'text': text,
                    'extracted_quality': quality,
                    'language': language or 'en'
                })
            
            except Exception as e:
                import logging
                logging.error(f"Error processing {resume_keys[idx]}: {e}")
                job.total_failed += 1
                failed_in_run += 1
                db.commit()
                continue
        
        # Batch score all resumes
        if all_resume_texts:
            scores = scorer.score_batch(
                job.jd_text,
                all_resume_texts,
                required_skills,
                min_yoe,
                {
                    'semantic': job.weight_semantic,
                    'tfidf': job.weight_tfidf,
                    'skills': job.weight_skills,
                    'experience': job.weight_experience
                }
            )
            
            # Store results
            for idx, (metadata, score_result) in enumerate(zip(resume_metadata, scores)):
                try:
                    skill_count = len(score_result['matched_skills'])
                    flags_dict = AnomalyDetector.get_flags(
                        metadata['text'],
                        skill_count,
                        metadata['language'],
                        False
                    )
                    
                    # Apply anomaly penalties
                    final_score = score_result['final_score']
                    if flags_dict.get('keyword_stuffing'):
                        final_score = min(final_score, 0.6)
                    
                    result = db.query(ResumeResult).filter(
                        ResumeResult.job_id == job_id,
                        ResumeResult.filename == metadata['filename']
                    ).first()
                    
                    if not result:
                        result = ResumeResult(
                            job_id=job_id,
                            tenant_id=job.tenant_id,
                            filename=metadata['filename'],
                            content_hash=metadata['content_hash'],
                            extracted_text=metadata['text'],
                            extracted_text_length=len(metadata['text']),
                            extraction_quality=metadata['extracted_quality'],
                            language_detected=metadata['language'],
                            score_semantic=score_result['score_semantic'],
                            score_tfidf=score_result['score_tfidf'],
                            score_skills=score_result['score_skills'],
                            score_experience=score_result['score_experience'],
                            final_score=final_score,
                            matched_skills=score_result['matched_skills'],
                            missing_skills=score_result['missing_skills'],
                            years_experience_detected=score_result['years_experience_detected'],
                            flags=flags_dict,
                            status='done'
                        )
                        db.add(result)
                    else:
                        result.score_semantic = score_result['score_semantic']
                        result.score_tfidf = score_result['score_tfidf']
                        result.score_skills = score_result['score_skills']
                        result.score_experience = score_result['score_experience']
                        result.final_score = final_score
                        result.matched_skills = score_result['matched_skills']
                        result.missing_skills = score_result['missing_skills']
                        result.years_experience_detected = score_result['years_experience_detected']
                        result.flags = flags_dict
                        result.status = 'done'
                    
                    db.add(result)
                    processed_in_run += 1
                    
                    # Broadcast progress every 5 records
                    if processed_in_run % 5 == 0:
                        progress_msg = {
                            'processed': processed_in_run,
                            'total': total_resumes,
                            'status': 'processing',
                            'latest': {
                                'filename': metadata['filename'],
                                'score': final_score
                            }
                        }
                        redis_client.publish(f'job:{job_id}:progress', __import__('json').dumps(progress_msg))
                    
                    if processed_in_run % 10 == 0:
                        db.commit()
                
                except Exception as e:
                    import logging
                    logging.error(f"Error scoring {metadata.get('filename', 'unknown')}: {e}")
                    job.total_failed += 1
                    failed_in_run += 1
        
        # Final commit
        db.commit()
        
        # Update ranks
        results = db.query(ResumeResult).filter(
            ResumeResult.job_id == job_id,
            ResumeResult.status == 'done'
        ).order_by(ResumeResult.final_score.desc()).all()
        
        for rank, res in enumerate(results, start=1):
            res.rank = rank
        
        from app.models import ResumeResult
        processed_count = db.query(func.count(ResumeResult.id)).filter(
            ResumeResult.job_id == job_id,
            ResumeResult.status.in_(['done', 'failed'])
        ).scalar() or 0
        failed_count = db.query(func.count(ResumeResult.id)).filter(
            ResumeResult.job_id == job_id,
            ResumeResult.status == 'failed'
        ).scalar() or 0

        job.total_processed = processed_count
        job.total_failed = failed_count
        db.commit()
        
        # Mark job as done
        job.status = 'done'
        job.completed_at = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
        db.commit()
        
        # Final broadcast
        progress_msg = {
            'processed': processed_count,
            'total': total_resumes,
            'status': 'done'
        }
        redis_client.publish(f'job:{job_id}:progress', __import__('json').dumps(progress_msg))
        
        return {"status": "done", "processed": processed_count}
    
    except Exception as e:
        import logging
        logging.error(f"Error in process_screening_job: {e}")
        
        from app.models import ScreeningJob
        job = db.query(ScreeningJob).filter(ScreeningJob.id == job_id).first()
        if job:
            job.status = 'failed'
            job.completed_at = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
            db.commit()
        
        raise
    
    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="app.workers.tasks.screening.process_single_resume",
    queue='critical',
)
def process_single_resume(self, jd_text: str, resume_file_base64: str, filename: str) -> dict:
    """
    Quick single-screen task. Returns score immediately.
    Used for spot-check feature (<3 seconds).
    """
    import base64
    
    resume_bytes = base64.b64decode(resume_file_base64)
    
    # Extract text
    text, quality, language = TextExtractor.extract_text(filename, resume_bytes)
    
    if len(text.strip()) < 50:
        return {
            'final_score': 0.0,
            'score_semantic': 0.0,
            'score_tfidf': 0.0,
            'score_skills': 0.0,
            'score_experience': 0.0,
            'matched_skills': [],
            'missing_skills': [],
            'years_experience_detected': None,
            'flags': {'blank_resume': True}
        }
    
    # Preprocess JD
    jd_info = preprocess_jd(jd_text)
    required_skills = jd_info['required_skills']
    min_yoe = jd_info['min_yoe']
    
    # Score
    weights = {
        'semantic': 0.40,
        'tfidf': 0.30,
        'skills': 0.20,
        'experience': 0.10
    }
    
    result = scorer.score_single(jd_text, text, required_skills, min_yoe, weights)
    
    # Add flags
    skill_count = len(result['matched_skills'])
    flags = AnomalyDetector.get_flags(text, skill_count, language or 'en', False)
    result['flags'] = flags
    
    return result
