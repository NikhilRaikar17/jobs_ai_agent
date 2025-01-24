import csv
from jobspy import scrape_jobs
import os
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

os.environ['GROQ_API_KEY'] = "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"

class Job(BaseModel):
    site: str
    company: str
    location: str
    job_url_direct: str

jobs = scrape_jobs(
    site_name=["linkedin", "indeed"],
    search_term="software tester",
    location="germany",
    results_wanted=30,
    hours_old=72,
    country_indeed='germany',
    
    # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
jobs = jobs.to_dict(orient="records")
chunks = [jobs[i:i + 10] for i in range(0, len(jobs), 10)]
groq_model = GroqModel(model_name="gemma2-9b-it")
agent = Agent(model=groq_model)

#jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar=",", index=False) # to_excel
for idx, chunk in enumerate(chunks):
    prompt = f"""
    
    Jobs data:
    {chunk}

    Check the job description, if it exists and see whether you find any of these technologies:
    [java, testing, TestNG, Cypress, manual testing, automation testing, CI/CD pipeline, Docker].
    Rate the job with a score of 1-10, where 1 is not match to any mentioned technologies and 10 begin related.

    if there is no description, make the score as NA

    Provide the output in the following JSON format and give no more infomration:
    [
        {{  
            "title": <title>,
            "job_link": <job_url_direct>,
            "location": <location>,
            "score": <SCORE>
        }}
    ]
    """

    result = agent.run_sync(prompt)
    print("Agent_1: ", result.data)

# message_history = result.new_messages()
# groq_model_1 = GroqModel(model_name="gemma2-9b-it")
# ollama_agent = Agent(model=groq_model_1)
# print("Agent_2: ", ollama_agent.run_sync("Make this in a table format and give back a excel sheet", message_history=message_history).data)