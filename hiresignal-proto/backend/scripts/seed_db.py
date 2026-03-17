"""Seed database with initial data for demo/testing"""

import asyncio
import uuid
from sqlalchemy.orm import sessionmaker
from app.database import sync_engine, Base
from app.models import Tenant, User, ScreeningJob, ResumeResult
from app.utils import hash_password
from datetime import datetime, timezone, timedelta
import random


def seed_database():
    """Populate database with seed data"""
    
    # Create tables
    Base.metadata.create_all(bind=sync_engine)
    
    Session = sessionmaker(bind=sync_engine)
    db = Session()
    
    try:
        # Check if already seeded
        existing_tenant = db.query(Tenant).first()
        if existing_tenant:
            print("✓ Database already seeded, skipping")
            return
        
        # Create tenants
        acme_tenant = Tenant(
            id=uuid.uuid4(),
            name="Acme Corp",
            slug="acme",
            plan="growth",
            monthly_quota=5000,
            is_active=True
        )
        
        startup_tenant = Tenant(
            id=uuid.uuid4(),
            name="Startup Labs",
            slug="startup",
            plan="starter",
            monthly_quota=500,
            is_active=True
        )
        
        db.add(acme_tenant)
        db.add(startup_tenant)
        db.commit()
        
        print(f"✓ Created tenants: Acme, Startup Labs")
        
        # Create users
        hr_acme = User(
            id=uuid.uuid4(),
            tenant_id=acme_tenant.id,
            email="hr@acme.com",
            hashed_password=hash_password("demo1234"),
            full_name="Alice HR",
            role="hr",
            is_active=True
        )
        
        admin_acme = User(
            id=uuid.uuid4(),
            tenant_id=acme_tenant.id,
            email="admin@acme.com",
            hashed_password=hash_password("demo1234"),
            full_name="Bob Admin",
            role="admin",
            is_active=True
        )
        
        hr_startup = User(
            id=uuid.uuid4(),
            tenant_id=startup_tenant.id,
            email="hr@startup.com",
            hashed_password=hash_password("demo1234"),
            full_name="Charlie HR",
            role="hr",
            is_active=True
        )
        
        db.add(hr_acme)
        db.add(admin_acme)
        db.add(hr_startup)
        db.commit()
        
        print(f"✓ Created users: hr@acme.com, admin@acme.com, hr@startup.com")
        
        # Create sample jobs with results
        job1_id = uuid.uuid4()
        job1 = ScreeningJob(
            id=job1_id,
            tenant_id=acme_tenant.id,
            created_by=hr_acme.id,
            title="Senior Python Backend Engineer",
            jd_text="""We are looking for a Senior Python Backend Engineer to lead our infrastructure team.

Requirements:
- 5+ years of Python experience
- Strong experience with FastAPI, Django, or Flask
- PostgreSQL and Redis expertise
- Docker and Kubernetes knowledge
- AWS or GCP cloud experience
- RESTful API design
- Async/await programming
- CI/CD pipelines (GitHub Actions, GitLab CI)

Nice to have:
- Microservices architecture
- Message queues (Kafka, RabbitMQ)
- Machine learning pipeline experience
- TensorFlow or PyTorch
- Open source contributions

About Us:
Acme Corp is a leading SaaS platform in fintech, serving 10,000+ customers worldwide.
We offer competitive salary, benefits, and professional growth opportunities.""",
            jd_skills_extracted=["python", "fastapi", "postgresql", "redis", "docker", "kubernetes", "aws"],
            jd_quality_score=0.75,
            jd_is_vague=False,
            weight_semantic=0.40,
            weight_tfidf=0.25,
            weight_skills=0.25,
            weight_experience=0.10,
            top_n=5,
            total_submitted=12,
            total_processed=12,
            status="done",
            started_at=datetime.now(timezone.utc) - timedelta(hours=2),
            completed_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        db.add(job1)
        db.commit()
        
        # Add fake resume results for job1
        resume_names = [
            "john_smith.pdf", "emily_johnson.docx", "michael_chen.pdf",
            "sarah_williams.pdf", "alex_rodriguez.docx", "jane_doe.pdf",
            "tony_stark.pdf", "pepper_potts.docx", "steve_rogers.pdf",
            "natasha_romanoff.pdf", "bruce_banner.docx", "thor_odinson.pdf"
        ]
        
        # Simulate realistic score distribution
        scores_high = [0.85, 0.82, 0.78]  # Top candidates
        scores_medium = [0.65, 0.62, 0.58, 0.55]  # Medium
        scores_low = [0.38, 0.32, 0.25, 0.15, 0.08]  # Low
        
        all_scores = scores_high + scores_medium + scores_low
        random.shuffle(all_scores)
        
        matched_skills_options = [
            ["python", "fastapi", "postgresql", "docker"],
            ["python", "django", "postgresql", "kubernetes"],
            ["python", "flask", "redis", "aws"],
            ["python", "fastapi", "mongodb"],
            ["python", "postgresql"],
        ]
        
        for idx, (name, score) in enumerate(zip(resume_names, all_scores)):
            result = ResumeResult(
                id=uuid.uuid4(),
                job_id=job1_id,
                tenant_id=acme_tenant.id,
                filename=name,
                content_hash=f"hash{idx}",
                extracted_text=f"Dummy resume text for {name}",
                extracted_text_length=200 + idx * 10,
                extraction_quality="good",
                language_detected="en",
                score_semantic=score * 1.1 if score < 0.9 else 1.0,
                score_tfidf=score * 0.9,
                score_skills=score + 0.05 if score < 0.95 else 1.0,
                score_experience=score - 0.05 if score > 0.05 else 0.1,
                final_score=score,
                rank=idx + 1,
                matched_skills=matched_skills_options[idx % len(matched_skills_options)],
                missing_skills=["kubernetes", "aws", "redis"][idx % 3:],
                years_experience_detected=float(5 + idx),
                flags={"ocr_used": False} if idx % 5 != 0 else {"ocr_used": True},
                status="done"
            )
            db.add(result)
        
        db.commit()
        print(f"✓ Created job 1: 'Senior Python Backend Engineer' with 12 results")
        
        # Create second job
        job2_id = uuid.uuid4()
        job2 = ScreeningJob(
            id=job2_id,
            tenant_id=acme_tenant.id,
            created_by=hr_acme.id,
            title="Sales Manager — B2B SaaS",
            jd_text="""Acme Corp seeks an experienced Sales Manager to lead our US enterprise sales team.

Requirements:
- 7+ years sales management experience
- Proven track record in B2B SaaS
- Enterprise account management
- Revenue targets and quota achievement
- Team leadership and mentoring
- Salesforce CRM proficiency
- Negotiation and closing skills

Nice to have:
- Fintech industry experience
- Market development
- Speaking engagements""",
            jd_skills_extracted=["sales", "salesforce", "b2b", "account management"],
            jd_quality_score=0.55,
            jd_is_vague=True,
            weight_semantic=0.50,
            weight_tfidf=0.25,
            weight_skills=0.10,
            weight_experience=0.15,
            top_n=3,
            total_submitted=8,
            total_processed=8,
            status="done",
            started_at=datetime.now(timezone.utc) - timedelta(days=1),
            completed_at=datetime.now(timezone.utc) - timedelta(hours=20)
        )
        
        db.add(job2)
        db.commit()
        
        # Add results for job2
        for idx in range(8):
            result = ResumeResult(
                id=uuid.uuid4(),
                job_id=job2_id,
                tenant_id=acme_tenant.id,
                filename=f"sales_candidate_{idx+1}.pdf",
                content_hash=f"sales_hash{idx}",
                extracted_text="Sales manager resume text",
                extracted_text_length=150,
                extraction_quality="good",
                language_detected="en",
                score_semantic=0.6 - (idx * 0.07),
                score_tfidf=0.65 - (idx * 0.08),
                score_skills=0.5 - (idx * 0.06),
                score_experience=0.7 - (idx * 0.08),
                final_score=0.6 - (idx * 0.07),
                rank=idx + 1,
                matched_skills=["sales", "account management"][:2 - (idx % 2)],
                missing_skills=["salesforce", "b2b", "negotiation"][idx % 3:],
                years_experience_detected=8.0 + idx,
                flags={},
                status="done"
            )
            db.add(result)
        
        db.commit()
        print(f"✓ Created job 2: 'Sales Manager — B2B SaaS' with 8 results")
        
        db.close()
        print("\n✓ Database seeding complete!")
        print("\nDemo credentials:")
        print("  Email: hr@acme.com")
        print("  Password: demo1234")
        print("\nOr:")
        print("  Email: hr@startup.com")
        print("  Password: demo1234")
        
    except Exception as e:
        print(f"✗ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
