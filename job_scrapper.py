from jobspy import scrape_jobs
from datetime import date, datetime
from typing import List, Dict, Any
from sqlalchemy.exc import IntegrityError
from database import session, Job, get_existing_job_ids, get_jobs_by_id


def save_jobs_to_db(jobs: List[Dict[str, Any]]) -> None:
    """ Save job listings to the database, avoiding duplicates. """

    for job in jobs:
        if isinstance(job.get("date_posted"), (date, datetime)):
            job["date_posted"] = job["date_posted"].strftime("%Y-%m-%d")

        existing_job = get_jobs_by_id(job.id)
        if not existing_job:
            new_job = Job(**job)

            try:
                session.add(new_job)
                session.commit()
            except IntegrityError:
                session.rollback()
        
        print(f"Job with is {job.id} already exists in db")
        return


def scrape_jobs_data(query: str = "Software Tester", location: str = "germany") -> List[Dict[str, Any]]:
    """ Fetch job listings, filter out duplicates, and store them in SQLite via SQLAlchemy. """

    print("🔍 Scraping jobs from LinkedIn & Indeed...")
    jobs = scrape_jobs(search_term=query, location=location,
                       site_name=["linkedin", "indeed"],
                       results_wanted=10,
                       hours_old=72,
                       country_indeed='germany',
                       linkedin_fetch_description=True)

    jobs["priority"] = None
    jobs["match_score"] = None

    selected_columns: List[str] = ["id", "site", "job_url", "title", "company",
                                   "location", "date_posted", "description", "priority", "match_score"]
    jobs = jobs[selected_columns]
    new_jobs: List[Dict[str, Any]] = jobs.to_dict(orient="records")

    for job in new_jobs:
        if isinstance(job.get("date_posted"), (date, datetime)):
            job["date_posted"] = job["date_posted"].strftime("%Y-%m-%d")

    existing_jobs = get_existing_job_ids()

    unique_new_jobs = [
        job for job in new_jobs if job["id"] not in existing_jobs]

    save_jobs_to_db(unique_new_jobs)

    print(f"✅ {len(unique_new_jobs)} new jobs added to the database!")
    return unique_new_jobs
