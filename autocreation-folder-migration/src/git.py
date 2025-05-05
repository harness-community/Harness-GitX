import github


def fork_branch(token, branch, repo, repo_url):
    if is_github(repo_url):
        github.create_branch_from_default(token, repo, branch, repo_url)


def commit_file(token, repo, branch, repo_url, file_path, file_content):
    if is_github(repo_url):
        github.commit_file_to_github(token, repo, branch, file_path, get_commit_message(), file_content, repo_url)


def create_pull_request(token, repo, branch, repo_url):
    PR_TITLE = "Harness auto-creation folder setup"
    if is_github(repo_url):
        github.create_pull_request(token, repo, branch, PR_TITLE, PR_TITLE, repo_url)


def is_github(repo_url):
    if repo_url.startswith("https://github.com"):
        return True
    return False


def get_commit_message():
    return "Harness Commit"
