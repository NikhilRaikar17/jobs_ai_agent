import datetime
import requests
from zoneinfo import ZoneInfo
from abc import ABC, abstractmethod
import pprint
from jobspy import scrape_jobs


class Tool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def use(self, *args, **kwargs):
        pass


class TimeTool(Tool):
    def name(self):
        return "Time Tool"

    def description(self):
        return "Provides the current time for a given city's timezone like Asia/Kolkata, America/New_York etc. If no timezone is provided, it returns the local time."

    def use(self, *args, **kwargs):
        format = "%Y-%m-%d %H:%M:%S %Z%z"
        current_time = datetime.datetime.now()
        input_timezone = args[0]
        if input_timezone:
            print("TimeZone", input_timezone)
            current_time = current_time.astimezone(ZoneInfo(input_timezone))
        return f"The current time is {current_time}."


class WeatherTool(Tool):
    def name(self):
        return "Weather Tool"

    def description(self):
        return "Provides weather information for a given location"

    def use(self, *args, **kwargs):

        location = args[0].split("weather in ")[-1]
        api_key = "aa3a63ca42eb827308e0b716281ef913"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={
            location}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            return f"The weather in {location} is currently {description} with a temperature of {temp}°C."
        else:
            return f"Sorry, I couldn't find weather information for {location}."


class JobScrapperTool(Tool):
    def name(self):
        return "Job scrapper tool"

    def description(self):
        return "Provides all open jobs for a given location"

    def use(self, *args, **kwargs):
        search_term = args[0]
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=search_term,
            location="germany",
            results_wanted=30,
            hours_old=72,
            country_indeed='germany',

            # gets more info such as description, direct job url (slower)
            linkedin_fetch_description=True
            # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
        )
        pprint.pprint(jobs.to_dict(orient="records"))
        return "Here are the results"

class JobScrapperTool(Tool):
    def name(self):
        return "Job scrapper tool"

    def description(self):
        return "Provides all open jobs for a given location"

    def use(self, *args, **kwargs):
        search_term = args[0]
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=search_term,
            location="germany",
            results_wanted=30,
            hours_old=72,
            country_indeed='germany',

            # gets more info such as description, direct job url (slower)
            linkedin_fetch_description=True
            # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
        )
        pprint.pprint(jobs.to_dict(orient="records"))
        return "Here are the results"
