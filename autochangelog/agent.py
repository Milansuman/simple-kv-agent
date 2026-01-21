import os
import argparse
from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM
from langchain.agents import create_agent
from .tools import *
from langchain.messages import HumanMessage
from rich.console import Console
from rich.markdown import Markdown
# from .observability import initialize_netra, initialize_netra_session, record_agent_thought_process
from .git import get_current_repo

load_dotenv()

LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")

if not LITELLM_API_KEY:
    raise ValueError("LITELLM_API_KEY environment variable is not set.")

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
- When getting the changelog of a release, always use the commits between the previous release and the given release.
- If you don't know which user a repo belongs to, get the current user first.
- When given multiple repositories by the user, combine the changelogs of both repositories into a single changelog, clearly indicating which changes belong to which repository.

IMPORTANT:
- Always generate changelogs that are relevant to the end user of the software. i.e. DO NOT talk about README changes or changes to config files unless it's relevant to the end user.
- Always generate changelogs for the latest release unless specified otherwise by the user.
- If the user asks you to save the changelog, you MUST save it to a .md file.
- DO NOT include a description about the changelog generation process in the final output.

EXAMPLES OF CHANGELOG POINTS NOT RELEVANT TO END USERS:
- "Updated README to include setup instructions."
- "Refactored codebase for better maintainability."
- "Improved logging for debugging purposes."
- "Updated configuration files."

EXAMPLES OF CHANGELOG POINTS RELEVANT TO END USERS:
- "Added dark mode support for better user experience in low light conditions."
- "Improved application startup time by 30%."
- "Fixed crash when opening large files."
- "Added support for exporting data in CSV format."

EXAMPLE CHANGELOG:
# Multi-Span Filters

Filter traces using multiple span conditions with:

* **AND, OR, NOT** operators for combining conditions
* **Indirectly Calls (->)** and **Directly Calls (=>)** relationship filters
* **Up to 5 filters** to find complex patterns like "spans where A calls B, but not C" or "traces containing both X and Y"
* **Parentheses** to build complex queries and pinpoint the traces that matter
"""

llm = ChatLiteLLM(
    model="litellm_proxy/gpt-4o",
    api_base="https://llm.keyvalue.systems",
    api_key=LITELLM_API_KEY
)

simple_agent = create_agent(
    model=llm,
    tools=[
        get_releases, 
        get_commits, 
        get_user_repos, 
        get_repo_tags, 
        get_repo_contributors, 
        export_changelog, 
        get_current_user, 
        get_current_repo,
        get_commits_between_releases
    ],
    system_prompt=BASE_SYSTEM_PROMPT,
)

def pretty_print(markdown: str):
    console = Console()
    md = Markdown(markdown)
    console.print(md)

def auto_generate_changelog(output_file: str = "CHANGELOG.md", release_version: str = None, repository: list = None):
    """Automatically generate a changelog since the last release."""
    
    if release_version:
        print(f"Generating changelog for release {release_version}...")
    else:
        print(f"Generating changelog since last release...")
    
    # initialize_netra()
    # initialize_netra_session()
    
    # Create a query to generate changelog
    if release_version:
        query = f"Generate a changelog for release {release_version} and save it to {output_file}."
    else:
        query = f"Generate a changelog for the current repository since the last release and save it to {output_file}."

    if repository:
        if len(repository) > 1:
            repos_str = ", ".join(repository)
            query += f" The repositories are: {repos_str}."
        else:
            query += f" The repository is {repository[0]}."
    else:
        current_repo = get_current_repo()
        if current_repo:
            query += f" The repository is at {current_repo}."
    
    messages = [HumanMessage(content=query)]
    print(query)
    
    response = simple_agent.invoke({
        "messages": messages,
    })
    
    # record_agent_thought_process(response["messages"], model="openai/gpt-oss-120b")
    
    pretty_print(response["messages"][-1].content)
    print(f"\nChangelog generated successfully!")

def main():
    parser = argparse.ArgumentParser(
        prog="netrach",
        description="GitHub Changelog Generator - Generate changelogs for GitHub repositories"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically generate changelog since the last release"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        default="CHANGELOG.md",
        help="Output file path for the changelog (default: CHANGELOG.md)"
    )
    parser.add_argument(
        "-r", "--release",
        type=str,
        help="Specify the release version for the changelog (e.g., v1.2.3)"
    )
    parser.add_argument(
        "--repo",
        type=str,
        nargs='+',
        help="Specify one or more repositories (e.g., owner/repo1 owner/repo2)"
    )
    
    args = parser.parse_args()

    if args.auto:
        auto_generate_changelog(args.file, args.release, args.repo)
        return
    
    # Interactive mode
    messages = []

    # initialize_netra()
    # initialize_netra_session()
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

        # record_agent_thought_process(response["messages"], model="openai/gpt-oss-120b")

        messages.append(response["messages"][-1])
        pretty_print(response["messages"][-1].content)

if __name__ == "__main__":
    main()