import json
import time
import os
import requests
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jobspy import scrape_jobs
import csv
import pandas as pd
from datetime import datetime

# Groq API Key (Store in environment variable for security)
os.environ['GROQ_API_KEY'] = "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"

# Email Configuration (Use App Password for Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
RECIPIENT_EMAIL = "recipient-email@gmail.com"


def query_llm(prompt):
    """Sends a prompt to Groq LLM and returns the response."""
    api_key = os.getenv("GROQ_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    url = "https://api.groq.com/openai/v1/chat/completions"

    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama-3.3-70b-versatile",
        "temperature": 1,
        "max_completion_tokens": 1024,
        "top_p": 1,
        "stream": False,
        "response_format": {"type": "json_object"},
        "stop": None
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.json())
    return response.json()['choices'][0]['message']['content']


STORAGE_FILE = "jobs_cache.json"


def load_previous_jobs():
    """Loads previous job listings from a JSON file."""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []


def save_jobs(jobs):
    """Saves job listings to a JSON file, converting date fields to strings."""
    def convert_dates(obj):
        """Convert non-serializable objects like dates to strings."""
        if isinstance(obj, datetime):
            # Convert datetime to string format
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, dict):
            # Recursively process dictionaries
            return {k: convert_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_dates(i) for i in obj]  # Recursively process lists
        return obj

    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(convert_dates(jobs), file, indent=4, ensure_ascii=False)


def scrape_jobs_data(query="Software Tester", location="germany"):
    """ Fetch job listings using JobSpy """

    print("🔍 Scraping jobs from LinkedIn & Indeed...")
    jobs = scrape_jobs(search_term=query, location=location,
                       site_name=["linkedin", "indeed"],
                       results_wanted=20,
                       hours_old=72,
                       country_indeed='germany',
                       linkedin_fetch_description=True)

    new_jobs = jobs.to_dict(orient="records")

    previous_jobs = load_previous_jobs()

    unique_new_jobs = [
        job for job in new_jobs if job not in previous_jobs]

    save_jobs(previous_jobs + unique_new_jobs)

    print(f"✅ {len(unique_new_jobs)} new jobs found!")
    return unique_new_jobs


def extract_curly_braces_content(input_string):
    # Finds JSON enclosed in curly braces
    match = re.search(r'\{[\s\S]*\}', input_string)
    if match:
        json_str = match.group(0)
        try:
            return json_str
        except json.JSONDecodeError:
            return None
    return None


def filter_jobs_with_ai(jobs, resume_text):
    """Uses Groq's LLM to filter job relevance based on resume"""
    print("🤖 Groq AI is filtering relevant jobs...")
    filtered_jobs = []
    scores = []
    matches = []

    for job in jobs:
        prompt = f"""
        Compare the following job description with the candidate's resume.
        Rate relevance from 1 (bad) to 10 (excellent).

        **Job Title:** {job['title']}
        **Company:** {job['company']}
        **Description:** {job['description']}

        **Candidate Resume:**
        {resume_text}

        Return in JSON format:
        {{
            "match": "Yes/No",
            "score": (1-10)
        }}
        """
        response = query_llm(prompt)
        result = extract_curly_braces_content(response)
        decision = json.loads(result)

        scores.append(decision["score"])
        matches.append(decision["match"])

        if decision["match"] == "Yes" and decision["score"] >= 6:
            job["priority"] = decision["score"]
            filtered_jobs.append(job)

    print(f"✅ {len(filtered_jobs)} jobs passed AI filtering.")

    jobs = pd.DataFrame(jobs)
    jobs["priority"] = scores
    jobs["AI_Match"] = matches
    selected_columns = ["id", "site", "job_url", "title", "company",
                        "location", "date_posted", "description", "priority", "AI_Match"]
    jobs = jobs[selected_columns]
    jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC,
                escapechar="\\", index=False)  # to_excel
    return filtered_jobs


# Resume Text for AI Filtering
resume_text = """
Senior QA Engineer with 6+ years in Automation Testing, Java, Selenium, and API Testing.
Looking for remote-friendly or high-priority job roles.
"""

# Run the job search process every hour
if __name__ == "__main__":
    # while True:
    print("🚀 Running AI Job Search Agent with Groq...")
    jobs = scrape_jobs_data()
    # filtered_jobs = filter_jobs_with_ai(jobs, resume_text)
    # send_email_notification(filtered_jobs)
    # print("⏳ Waiting for 1 hour before the next run...")
    # time.sleep(3600)  # Runs every hour
