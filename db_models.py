from sqlalchemy import Column, String
from main import Base
from datetime import datetime


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    site = Column(String)
    job_url = Column(String, unique=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    date_posted = Column(String, nullable=True,
                         default=datetime.now().strftime("%Y-%m-%d"))
    description = Column(String)
    priority = Column(String, nullable=True)
    AI_Match = Column(String, nullable=True)
