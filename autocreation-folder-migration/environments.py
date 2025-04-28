import requests
from utility import EntityDetails, get_repo_url, is_empty


def get_environments(api_key, account_id, org_id, project_id):
    page = 0
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }
    envs = []

    while True:
        url = f"https://app.harness.io/gateway/ng/api/environmentsV2?accountIdentifier={account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            content = response.json()['data']['content']
            if len(content) == 0:
                return envs
            envs.extend(response.json()['data']['content'])
            page += 1
        else:
            return {"error": f"Failed to fetch environments: {response.status_code}", "details": response.text}


def fetch_environment_details(api_key, account_id, org_id, project_id, env_id):
    url = f"https://app.harness.io/ng/api/environmentsV2/{env_id}"

    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx and 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching environment details: {e}")
        return None


def update_environment_git_metadata(api_key, account_id, org_id, project_id, env_id, env_type):
    url = f"https://app.harness.io/gateway/ng/api/environmentsV2/{env_id}/update-git-metadata"

    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id,
        "filePath": get_target_file_path(org_id, project_id, env_id, env_type)
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    print(f"Updating env filepath : {params} for env id : {env_id}")

    try:
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx and 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error updating Git metadata: {e}")
        return None


def update_env_file_path(api_key, account_id, org_id, project_id):
    env_list = get_environments(api_key, account_id, org_id, project_id)
    for element in env_list:
        env = element['environment']
        if env['storeType'] != 'INLINE':
            update_environment_git_metadata(api_key, account_id, org_id, project_id, env['identifier'], env['type'])


def process_environments(api_key, account_id, org_id, project_id):
    env_list = get_environments(api_key, account_id, org_id, project_id)
    entity_data_list = []
    for element in env_list:
        env = element['environment']
        try:
            env_details = fetch_environment_details(api_key, account_id, org_id, project_id, env["identifier"])
            print(env_details)
            data = env_details['data']['environment']
            if data['storeType'] != 'INLINE':
                entity_data = EntityDetails(account_id, org_id, project_id, env['identifier'], data['yaml'],
                                            data['entityGitDetails']['repoName'], get_repo_url(data['entityGitDetails']['fileUrl'], data['entityGitDetails']['repoName']))
                entity_data.sub_type = env['type']
                entity_data.target_file_path = get_target_file_path_from_entity(entity_data)
                if entity_data.target_file_path == data['entityGitDetails']['filePath']:
                    print("ignoring the env as its already under conventional filepath\nMetadata:" + str(
                        env) + "\nDetails:" + str(data))
                    continue
                entity_data_list.append(entity_data)
        except Exception as ex:
            print(ex)
    return entity_data_list


def get_target_file_path_from_entity(entity_data):
    return get_target_file_path(entity_data.org_identifier, entity_data.project_identifier, entity_data.identifier, entity_data.sub_type)


def get_target_file_path(org_id, project_id, identifier, env_type):
    env_type = env_type.lower()
    target_file_path = ".harness/"
    ending_path = "envs/" + env_type + "/" + identifier + ".yaml"
    if is_empty(org_id):
        return target_file_path + ending_path
    if is_empty(project_id):
        return target_file_path + "orgs/" + org_id + "/" + ending_path
    return ".harness/orgs/" + org_id + "/projects/" + project_id + "/" + ending_path
