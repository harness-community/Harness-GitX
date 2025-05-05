class EntityDetails:
    def __init__(self, account_identifier, org_identifier, project_identifier, identifier, yaml, repo, repo_url):
        self.project_identifier = project_identifier
        self.org_identifier = org_identifier
        self.account_identifier = account_identifier
        self.identifier = identifier
        self.repo = repo
        self.yaml = yaml
        self.repo_url = repo_url
        self.target_file_path = ""
        self.sub_type = ""
        self.version = ""
        self.parent_id = ""

    def __repr__(self):
        return (f"EntityDetails(account_identifier='{self.account_identifier}', "
                f"org_identifier='{self.org_identifier}', "
                f"project_identifier='{self.project_identifier}', "
                f"identifier='{self.identifier}', "
                f"repo='{self.repo}', "
                f"repo_url='{self.repo_url}', "
                f"target_file_path='{self.target_file_path}', "
                f"sub_type='{self.sub_type}', "
                f"version='{self.version}', "
                f"parent_id='{self.parent_id}', "
                f"yaml='{self.yaml[:30]}...')")  # Truncated YAML for readability


def find_substring_ending_with(main_str, input_str):
    result = []
    for i in range(len(main_str)):
        substring = main_str[:i+1]  # Get substring from start to i
        if substring.endswith(input_str):  # Check if it ends with input_str
            result.append(substring)
    if len(result) > 0:
        return result[0]
    return None


def get_repo_url(file_url, repo_name):
    return find_substring_ending_with(file_url, repo_name)


def is_empty(entity_identifier):
    if entity_identifier is None or entity_identifier == "":
        return True
    return False
