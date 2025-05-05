from urllib.parse import urlparse

import requests
import base64
from context import Context


def create_branch_from_default(github_token, repo, new_branch, repo_url):
    owner = extract_owner_from_url(repo_url)
    # API URL to fetch repo details (including default branch)
    repo_url = f"{get_github_url()}/repos/{owner}/{repo}"

    # Headers for authentication
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Step 1: Get the default branch of the repository
    response = requests.get(repo_url, headers=headers)

    if response.status_code != 200:
        return f"Error fetching repository details: {response.status_code}, {response.text}"

    repo_data = response.json()
    default_branch = repo_data["default_branch"]  # Get the default branch name

    # Step 2: Get the latest commit SHA of the default branch
    base_branch_url = f"{get_github_url()}/repos/{owner}/{repo}/git/ref/heads/{default_branch}"
    response = requests.get(base_branch_url, headers=headers)

    if response.status_code != 200:
        return f"Error fetching base branch: {response.status_code}, {response.text}"

    latest_sha = response.json()["object"]["sha"]

    # Step 3: Create the new branch
    new_branch_url = f"{get_github_url()}/repos/{owner}/{repo}/git/refs"
    payload = {
        "ref": f"refs/heads/{new_branch}",
        "sha": latest_sha
    }

    response = requests.post(new_branch_url, json=payload, headers=headers)

    if response.status_code == 201:
        print(f"Branch '{new_branch}' created successfully from '{default_branch}' in {repo}!")
    else:
        print(f"Error creating branch: {response.status_code}, {response.text}")


def commit_file_to_github(github_token, repo, branch, file_path, commit_message, file_content, repo_url):
    owner = extract_owner_from_url(repo_url)
    """
    Commits a file to a specific branch in a GitHub repository using the GitHub API.

    Args:
        github_token (str): GitHub personal access token
        owner (str): Repository owner (username or organization)
        repo (str): Repository name
        branch (str): Target branch for the commit
        file_path (str): Path to the file in the repository
        commit_message (str): Commit message
        file_content (str): Content of the file as a string

    Returns:
        dict: API response JSON or error message
    """

    # GitHub API URL for file operations
    base_url = f"{get_github_url()}/repos/{owner}/{repo}/contents/{file_path}"

    # Headers for authentication
    headers = {"Authorization": f"token {github_token}"}

    # Get the file SHA (needed if updating an existing file)
    response = requests.get(base_url, headers=headers, params={"ref": branch})

    file_sha = response.json().get("sha") if response.status_code == 200 else None

    # Convert file content to Base64 (GitHub API requires this format)
    encoded_content = base64.b64encode(file_content.encode()).decode()

    # Prepare JSON payload for commit
    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": branch
    }
    if file_sha:
        data["sha"] = file_sha  # Required for updating existing files

    # Send PUT request to create or update the file
    response = requests.put(base_url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print({"status": "success", "message": f"✅ File '{file_path}' committed to '{branch}'"})
    else:
        print({"status": "error", "details": response.json()})


def create_pull_request(github_token, repo, feature_branch, pr_title, pr_body, repo_url):
    owner = extract_owner_from_url(repo_url)
    """
    Creates a pull request on GitHub using the GitHub API.

    Args:
        github_token (str): GitHub personal access token
        owner (str): Repository owner (username or organization)
        repo (str): Repository name
        base_branch (str): Base branch for the PR (e.g., 'main')
        head_branch (str): Head branch for the PR (e.g., 'feature-branch')
        pr_title (str): Title for the pull request
        pr_body (str): Body description for the pull request

    Returns:
        dict: API response JSON or error message
    """

    repo_url = f"{get_github_url()}/repos/{owner}/{repo}"

    # Headers for authentication
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the repository details to fetch the default branch
    response = requests.get(repo_url, headers=headers)
    if response.status_code != 200:
        return {
            "status": "error",
            "details": response.json()
        }

    default_branch = response.json().get('default_branch')

    # GitHub API URL for creating a pull request
    url = f"{get_github_url()}/repos/{owner}/{repo}/pulls"

    # Headers for authentication
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Data to send in the request
    data = {
        "title": pr_title,
        "head": feature_branch,  # The feature or compare branch
        "base": default_branch,  # The base branch (usually 'main' or 'master')
        "body": pr_body  # Optional: Add description for PR
    }

    # Send the POST request to create a PR
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"✅ Pull Request created successfully!\nURL: {response.json()['html_url']}")
    else:
        print({"status": "error", "details": response.json()})


def extract_owner_from_url(repo_url):
    parsed_url = urlparse(repo_url)

    # Split path to extract owner
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL. Cannot determine owner.")

    owner = path_parts[0]  # First part of the path is the owner
    return owner


def get_github_url():
    if Context.git_domain is None or Context.git_domain == "":
        return "https://api.github.com"
    else:
        return Context.git_domain + "/api/v3"
