from jobspy import scrape_jobs
from datetime import date, datetime
from typing import List, Dict, Any
from sqlalchemy.exc import IntegrityError
from database import session, Job, get_existing_job_ids


def save_jobs_to_db(jobs: List[Dict[str, Any]]) -> None:
    """ Save job listings to the database, avoiding duplicates. """

    for job in jobs:
        if isinstance(job.get("date_posted"), (date, datetime)):
            job["date_posted"] = job["date_posted"].strftime("%Y-%m-%d")

        new_job = Job(**job)

        try:
            session.add(new_job)  # Add new job
            session.commit()  # Save to DB
        except IntegrityError:
            session.rollback()  # Prevent duplicate insertions


def scrape_jobs_data(query: str = "Software Tester", location: str = "germany") -> List[Dict[str, Any]]:
    """ Fetch job listings, filter out duplicates, and store them in SQLite via SQLAlchemy. """

    print("🔍 Scraping jobs from LinkedIn & Indeed...")

    # Fetch new job listings
    jobs = scrape_jobs(search_term=query, location=location,
                       site_name=["linkedin", "indeed"],
                       results_wanted=20,
                       hours_old=72,
                       country_indeed='germany',
                       linkedin_fetch_description=True)

    # Add missing columns
    jobs["priority"] = None
    jobs["AI_Match"] = None

    # Select relevant columns
    selected_columns: List[str] = ["id", "site", "job_url", "title", "company",
                                   "location", "date_posted", "description", "priority", "AI_Match"]
    jobs = jobs[selected_columns]
    new_jobs: List[Dict[str, Any]] = jobs.to_dict(orient="records")

    # Ensure `date_posted` is a string in YYYY-MM-DD format
    for job in new_jobs:
        if isinstance(job.get("date_posted"), (date, datetime)):
            job["date_posted"] = job["date_posted"].strftime("%Y-%m-%d")

    # Get existing job IDs from the database
    existing_jobs = get_existing_job_ids()

    # Filter out duplicates
    unique_new_jobs = [
        job for job in new_jobs if job["id"] not in existing_jobs]

    # Save new jobs to the database
    save_jobs_to_db(unique_new_jobs)

    print(f"✅ {len(unique_new_jobs)} new jobs added to the database!")
    return unique_new_jobs
