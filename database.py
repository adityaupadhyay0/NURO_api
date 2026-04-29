from sqlalchemy import create_engine, Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now)

class AnalysisTask(Base):
    __tablename__ = 'analysis_tasks'
    id = Column(String, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    media_type = Column(String)
    file_path = Column(String)

    # Audience Parameters (MMP)
    audience_age = Column(String, nullable=True)
    audience_platform = Column(String, nullable=True)
    audience_industry = Column(String, nullable=True)
    audience_awareness = Column(String, nullable=True)

    status = Column(String, default="processing")
    results = Column(JSON, nullable=True) # Predicted Neuro & Marketing KPIs
    ai_advice = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class MarketingResult(Base):
    __tablename__ = 'marketing_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey('analysis_tasks.id'))
    ctr = Column(Float, nullable=True)
    cpc = Column(Float, nullable=True)
    cpa = Column(Float, nullable=True)
    conversion_rate = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

# Database Setup
DB_PATH = "sqlite:///neuromark_pro.db"
engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Initial mock campaign
    if not db.query(Campaign).filter_by(name="Default Campaign").first():
        db.add(Campaign(name="Default Campaign"))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database Initialized.")
