from job_scrapper import scrape_jobs_data
from others.rank import filter_jobs_with_ai

if __name__ == "__main__":
    resume_text = """
    Senior QA Engineer with 6+ years in Automation Testing, Java, Selenium, and API Testing.
    Looking for remote-friendly or high-priority job roles.
    """
    jobs = scrape_jobs_data()
    filtered_jobs = filter_jobs_with_ai(jobs, resume_text)
