import requests
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
# from netra.decorators import task
# from netra import Netra, ActionModel
from autochangelog import git

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

@tool
# @task
def get_releases(owner: str, repo: str) -> str:
    """Get releases for a GitHub repository. Returns formatted list of recent releases with name, tag, and publish date."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        releases = response.json()
        
        if not releases:
            return "No releases found."
        
        result = []
        for release in releases[:10]:
            result.append(f"- {release['name']} ({release['tag_name']}) - {release['published_at']}")
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching releases: {str(e)}"

@tool
# @task
def get_commits(owner: str, repo: str, per_page: int = 30) -> str:
    """Get recent commits for a GitHub repository. Returns formatted list of commits with SHA, message, and author."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    params = {
        "per_page": min(per_page, 100),
        "page": 1
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        commits = response.json()
        
        if not commits:
            return "No commits found."
        
        result = []
        for commit in commits:
            sha = commit['sha']
            message = commit['commit']['message'].split('\n')[0]
            author = commit['commit']['author']['name']
            result.append(f"- {sha}: {message} (by {author})")
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching commits: {str(e)}"

@tool
# @task
def get_commits_between_releases(owner: str, repo: str, base: str, head: str) -> str:
    """Get commits between two releases/deployments (tags, branches, or commit SHAs). 
    
    Args:
        owner: Repository owner
        repo: Repository name
        base: The base reference (older release/tag/commit)
        head: The head reference (newer release/tag/commit)
    
    Returns formatted list of commits with SHA, message, author, and date.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        comparison = response.json()
        
        commits = comparison.get('commits', [])
        
        if not commits:
            return f"No commits found between {base} and {head}."
        
        result = [f"Commits between {base} and {head} ({len(commits)} total):\n"]
        for commit in commits:
            sha = commit['sha'][:7]
            message = commit['commit']['message'].split('\n')[0]
            author = commit['commit']['author']['name']
            date = commit['commit']['author']['date']
            result.append(f"- {sha}: {message} (by {author} on {date})")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching commits between releases: {str(e)}"
  
@tool
# @task
def get_user_repos(username: str) -> str:
    """Get public repositories for a GitHub user. Returns formatted list of repository names and descriptions."""
    url = f"https://api.github.com/users/{username}/repos"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        repos = response.json()
        
        if not repos:
            return "No repositories found."
        
        result = []
        for repo in repos:
            description = repo['description'] if repo['description'] else "No description"
            result.append(f"- {repo['name']}: {description}")
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching user repositories: {str(e)}"

@tool
# @task
def get_repo_tags(owner: str, repo: str) -> str:
    """Get tags for a GitHub repository. Returns formatted list of tags with name and commit SHA."""
    url = f"https://api.github.com/repos/{owner}/{repo}/tags"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        tags = response.json()
        
        if not tags:
            return "No tags found."
        
        result = []
        for tag in tags:
            result.append(f"- {tag['name']}: {tag['commit']['sha']}")
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching tags: {str(e)}"
    
@tool
# @task
def get_repo_contributors(owner: str, repo: str) -> str:
    """Get contributors for a GitHub repository. Returns formatted list of contributors with username and contributions count."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        contributors = response.json()
        
        if not contributors:
            return "No contributors found."
        
        result = []
        for contributor in contributors:
            result.append(f"- {contributor['login']}: {contributor['contributions']} contributions")
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching contributors: {str(e)}"
    
@tool
# @task
def export_changelog(markdown_content: str, filename: str = "CHANGELOG.md") -> str:
    """Export the given markdown content to a CHANGELOG.md file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        
        with open(filename, "w") as f:
            f.write(markdown_content)
        
        # with Netra.start_span("export_changelog") as span:
        #     action = ActionModel(
        #         action="file",
        #         action_type="write",
        #         success=True,
        #         affected_records=[{
        #             "filename": filename,
        #             "content": markdown_content
        #         }]
        #     )
        #     span.set_action([action])
        #     span.set_success()
        return f"Changelog exported to {filename}"
    except Exception as e:
        print(e)
        return f"Error exporting changelog: {str(e)}"

@tool
# @task
def get_current_user() -> str:
    """Get the current git user name."""
    try:
        author_info = git.get_author_info()
        if author_info and author_info["name"]:
            return author_info["name"]
        else:
            return "Unknown User"
    except Exception as e:
        return f"Error fetching current user: {str(e)}"
    
@tool
# @task
def get_current_repo() -> str:
    """Get the current git repository URL."""
    try:
        repo_url = git.get_current_repo()
        if repo_url:
            return repo_url
        else:
            return "No repository found."
    except Exception as e:
        return f"Error fetching current repository: {str(e)}"