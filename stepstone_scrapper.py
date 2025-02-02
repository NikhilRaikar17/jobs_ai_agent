import json
import agentql as aql
from playwright.sync_api import sync_playwright

DUMMY_EMAIL = "nikhilraikarjobs@gmail.com"
DUMMY_PASSWORD = "Nikhil!995"

STEPSTONE_URL = "https://www.stepstone.de"


def scrape_stepstone_jobs(keyword, location="Germany", max_results=10):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = aql.wrap(browser.new_page())

        page.goto(f"{STEPSTONE_URL}")

        page.click("div[id='ccmgt_explicit_accept']")
        page.click("button[aria-label='Login']")
        page.click("span[class='hf-provider-10nf7hq']")
        page.fill("input[name='email']", DUMMY_EMAIL)
        page.fill("input[name='password']", DUMMY_PASSWORD)
        page.click("button[type='submit']")

        page.wait_for_timeout(5000)

        search_url = f"{STEPSTONE_URL}/jobs/{keyword}/in-{
            location}?radius=100&sort=2&action=sort_publish&ag=age_7"
        page.goto(search_url)
        page.wait_for_timeout(5000)

        query = """
        {
            jobs[] {
                job_title
                company_name
                job_location
                job_url
            }
        }
        """

        result = page.query_data(query)

        jobs_data = []
        for job in result.get('jobs', [])[:max_results]:
            jobs_data.append({
                "title": job.get("job_title", "").strip(),
                "company": job.get("company_name", "").strip(),
                "location": job.get("job_location", "").strip(),
                "link": f"{job.get('job_url', '').strip()}"
            })

        search_url_page2 = f"{STEPSTONE_URL}/jobs/{keyword}/in-{
            location}?radius=100&page=2&sort=2&action=sort_publish&ag=age_7"
        page.goto(search_url_page2)
        page.wait_for_timeout(5000)

        result_2 = page.query_data(query)

        for job in result_2.get('jobs', [])[:max_results]:
            jobs_data.append({
                "title": job.get("job_title", "").strip(),
                "company": job.get("company_name", "").strip(),
                "location": job.get("job_location", "").strip(),
                "link": f"{job.get('job_url', '').strip()}"
            })

        browser.close()

        print(json.dumps(jobs_data, indent=4, ensure_ascii=False))


scrape_stepstone_jobs("qa-engineer", "Germany", max_results=30)
