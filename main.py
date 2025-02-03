from job_scrapper import scrape_jobs_data
from rank import filter_jobs_with_ai
from prompts import profile_summary_prompt

if __name__ == "__main__":

    jobs = scrape_jobs_data()

    if jobs:
        print("🚀 Running AI Job Search Agent with Groq...")
        filtered_jobs = filter_jobs_with_ai(jobs, profile_summary_prompt)
    else:
        print("🚀 No News jobs found, all LLMS are paused")
