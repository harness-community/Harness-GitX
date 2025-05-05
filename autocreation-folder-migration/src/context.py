import json


class Context:
    account_id = ""
    git_token = ""
    git_provider = ""
    api_key = ""
    git_domain = ""

    @staticmethod
    def init():
        file_path = 'keys.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
            Context.account_id = data['account-id']
            Context.git_token = data['git-token']
            Context.git_provider = data['git-provider']
            Context.api_key = data['harness-api-key']
            Context.git_domain = data['git-domain']
