import json
import os
import requests
import re
from database import update_job_scores_in_db

os.environ['GROQ_API_KEY'] = "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"


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

    print("🤖 AI is checking whether the jobs match your profile")

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

        update_job_scores_in_db(
            job["id"], decision["score"], decision["score"])

        if decision["match"] == "Yes" and decision["score"] >= 6:
            job["priority"] = decision["score"]
            filtered_jobs.append(job)

    print(f"✅ {len(filtered_jobs)} jobs passed AI filtering.")

    return jobs
