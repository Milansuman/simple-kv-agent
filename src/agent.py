import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools import get_releases, get_commits, get_user_repos, get_repo_tags, get_repo_contributors, export_changelog
from langchain.messages import HumanMessage, AIMessage
from rich.console import Console
from rich.markdown import Markdown
from observability import initialize_netra, initialize_netra_session, record_agent_thought_process

load_dotenv()
initialize_netra()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

BASE_SYSTEM_PROMPT = f"""
You are a helpful assistant that generates changelogs for GitHub repositories based on user queries.

GUIDELINES:
- Use the provided tools to fetch data about GitHub repositories.
- Format the changelog in markdown
- Word the changelog such that it is readable by the end user and only contains information about user facing changes.
- Bug fixes, security patches and performance improvements need not be elaborated upon. Instead, give them a concise mention.
- Do not include any information about the git commits, authors or commit SHAs in the changelog.
- When saving the changelog, use the guidelines provided to generate the content to be put in the file.
- Always save files with the .md file extension, even if not explicitly mentioned by the user.

EXAMPLE CHANGELOG:
# Multi-Span Filters

Filter traces using multiple span conditions with:

* **AND, OR, NOT** operators for combining conditions
* **Indirectly Calls (->)** and **Directly Calls (=>)** relationship filters
* **Up to 5 filters** to find complex patterns like "spans where A calls B, but not C" or "traces containing both X and Y"
* **Parentheses** to build complex queries and pinpoint the traces that matter
"""

def pretty_print(markdown: str):
    console = Console()
    md = Markdown(markdown)
    console.print(md)

def main():
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="openai/gpt-oss-120b"
    )

    simple_agent = create_agent(
        model=llm,
        tools=[get_releases, get_commits, get_user_repos, get_repo_tags, get_repo_contributors, export_changelog],
        system_prompt=BASE_SYSTEM_PROMPT,
    )

    messages = []

    initialize_netra_session()
    while True:
        user_input = input(">>> Enter your query (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        elif len(user_input.strip()) == 0:
            continue

        messages.append(HumanMessage(content=user_input))
        response = simple_agent.invoke({
            "messages": messages,
        })

        record_agent_thought_process(response["messages"], model="openai/gpt-oss-120b")

        messages.append(response["messages"][-1])
        pretty_print(response["messages"][-1].content)

if __name__ == "__main__":
    main()