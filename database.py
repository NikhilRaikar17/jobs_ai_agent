from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Set
import psycopg2

# Define database connection
DB_FILE: str = "postgresql://urlbu4oi0tnewjy0j4sx:3yrsZLeY8y5CDYT5F0SNlTGnrLh1qC@bkzhuga2a53f1cxk7shq-postgresql.services.clever-cloud.com:50013/bkzhuga2a53f1cxk7shq"

engine = create_engine(DB_FILE, echo=False)

# Create a session factory
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id: str = Column(String, primary_key=True)
    site: str = Column(String)
    job_url: str = Column(String, unique=True)
    title: str = Column(String)
    company: str = Column(String)
    location: str = Column(String)
    date_posted: str = Column(String, nullable=True,
                              default=datetime.now().strftime("%Y-%m-%d"))
    description: str = Column(String, default="")
    priority: int = Column(Integer, default=0)
    match_score: str = Column(String, nullable=True)
    extracted_csv: bool = Column(Boolean, default=False)
    applied: bool = Column(Boolean, default=False)


# Initialize the database
Base.metadata.create_all(engine)


def get_existing_job_ids() -> Set[str]:
    """ Retrieve all existing job IDs to filter duplicates. """
    return {job.id for job in session.query(Job.id).all()}


def update_job_scores_in_db(job_id, score, match_score):
    """ Update the match_score and priority fields in the database. """

    job = session.query(Job).filter_by(id=job_id).first()
    job.priority = score
    job.match_score = match_score
    session.commit()


def get_jobs_without_priority():
    """Retrieve all job IDs where priority is NULL."""
    return session.query(Job).filter_by(priority=0).all()

def get_jobs_by_id(job_id):
    """Retrieve all job IDs where priority is NULL."""
    return session.query(Job).filter_by(id=job_id).first()
