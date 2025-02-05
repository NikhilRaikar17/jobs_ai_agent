import json
import os
import requests
import re
from database import update_job_scores_in_db
from database import get_jobs_without_priority


def query_llm(prompt):
    """Sends a prompt to Groq LLM and returns the response."""

    try:

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "API key is missing. Please set the GROQ_API_KEY environment variable.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        url = "https://api.groq.com/openai/v1/chat/completion"

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
        response.raise_for_status()
        response_json = response.json()
        return response_json.get('choices', [{}])[0].get('message', {}).get('content', "No content returned.")

    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"
    except json.JSONDecodeError:
        return "Error decoding the JSON response."
    except KeyError:
        return "Unexpected response format from the API."
    except Exception as e:
        return f"An error occurred: {e}"


def extract_curly_braces_content(input_string):
    match = re.search(r'\{[\s\S]*\}', input_string)
    if match:
        json_str = match.group(0)
        try:
            return json_str
        except json.JSONDecodeError:
            return None
    return None


def filter_jobs_with_ai(resume_text):
    """Uses Groq's LLM to filter job relevance based on resume"""

    print("🤖 AI is checking whether the jobs match your profile")

    filtered_jobs = []
    scores = []
    matches = []

    try:
        jobs = get_jobs_without_priority()
        if jobs:
            for job in jobs:
                print(job.title)
                if not job.title or not job.company or not job.description:
                    break

                prompt = f"""
                Compare the following job description with the candidate's profile summary.
                Rate relevance from 1 (bad) to 10 (excellent).

                **Job Title:** {job.title}
                **Company:** {job.company}
                **Description:** {job.description}

                **Candidate profile summary:**
                {resume_text}

                Return in JSON format:
                {{
                    "match": "Yes/No",
                    "score": (1-10)
                }}
                """
                response = query_llm(prompt)
            
                result = extract_curly_braces_content(response)
                print(job.title)
                print(result)
                decision = json.loads(result)

                scores.append(decision["score"])
                matches.append(decision["match"])

                update_job_scores_in_db(
                    job.id, decision["score"], decision["match"])

                if decision["match"] == "Yes" and decision["score"] >= 6:
                    filtered_jobs.append(job)

            print(f"✅ {len(filtered_jobs)} jobs passed AI filtering.")
        print(f"✅ NO new jobs to filter")

        return jobs
    except Exception as e:
        print("Error processing", e)
