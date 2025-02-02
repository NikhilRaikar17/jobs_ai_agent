from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Set

# Define database connection
DB_FILE: str = "sqlite:///jobs.db"
engine = create_engine(DB_FILE, echo=False)

# Create a session factory
Session = sessionmaker(bind=engine)
session = Session()

# Define the Base for ORM models
Base = declarative_base()

# Define the Job table


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
    priority: str = Column(String, nullable=True)
    match_score: str = Column(String, nullable=True)
    extracted_csv: bool = Column(Boolean, default=False)
    applied: bool = Column(Boolean, default=False)


# Initialize the database
Base.metadata.create_all(engine)


def get_existing_job_ids() -> Set[str]:
    """ Retrieve all existing job IDs to filter duplicates. """
    return {job.id for job in session.query(Job.id).all()}  # Fetch all stored job IDs
