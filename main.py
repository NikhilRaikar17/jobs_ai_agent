from job_scrapper import scrape_jobs_data
from rank import filter_jobs_with_ai

if __name__ == "__main__":
    resume_text = """
    As an ISTQB® Certified Senior Quality Assurance Engineer with over 6+ years of experience, I excel in full
    lifecycle testing, including white box, black box, and regression testing. I am proficient in Cypres
    Selenium, Java, Python, and SQL, and adept at developing and executing test plans, automating tasks, and
    identifying defects to ensure the delivery of high-quality software. My strong analytical skills, combined
    with a collaborative approach, drive the successful delivery of products that consistently meet and exceed
    customer expectations. 
    """
    jobs = scrape_jobs_data()

    print("🚀 Running AI Job Search Agent with Groq...")
    filtered_jobs = filter_jobs_with_ai(jobs, resume_text)
