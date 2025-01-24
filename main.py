from agent import Agent
from tools import TimeTool, WeatherTool, JobScrapperTool


def main():
    agent = Agent()

    agent.add_tool(TimeTool())
    agent.add_tool(WeatherTool())
    agent.add_tool(JobScrapperTool())
    agent.run()


if __name__ == "__main__":
    main()
