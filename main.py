from job_scrapper import scrape_jobs_data
from rank import filter_jobs_with_ai
from prompts import profile_summary_prompt
# from stepstone_scrapper import scrape_stepstone_jobs

if __name__ == "__main__":

    jobs = scrape_jobs_data()
    # stepstone_scrapper = scrape_stepstone_jobs(
    #     "qa-engineer", "Germany", max_results=10)

    print("🚀 Running AI Job Search Agent with Groq...")
    filtered_jobs = filter_jobs_with_ai(profile_summary_prompt)
    print("🚀 No News jobs found, all LLMS are paused")
