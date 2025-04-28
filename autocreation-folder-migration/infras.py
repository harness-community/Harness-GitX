import requests
from utility import EntityDetails, get_repo_url, is_empty
from environments import get_environments


def get_infras(api_key, account_id, org_id, project_id, environment_id):
    # Construct the API URL with additional scope parameters
    url = f"https://app.harness.io/gateway/ng/api/infrastructures"
    page = 0
    params = {
        'accountIdentifier': account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id,
        'environmentIdentifier': environment_id,
        'page': page
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    infras = []
    while True:
        # Send GET request to Harness API with scope parameters
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse JSON response
            content = response.json()['data']['content']
            if len(content) == 0:
                return infras
            infras.extend(content)
            params['page'] += 1
        else:
            # Return error message if the request fails
            return f"Failed to retrieve data: {response.status_code} - {response.text}"


def get_infrastructure_details(api_key, account_id, org_id, project_id, environment_id, infrastructure_id):
    """
    Fetches the details of a specific infrastructure by its ID.

    :param api_key: The Harness API key (Bearer Token)
    :param infrastructure_id: The ID of the infrastructure to fetch details for
    :return: The infrastructure details, or an error message if the request fails.
    """
    # Harness API endpoint for fetching specific infrastructure details
    url = f"https://app.harness.io/ng/api/infrastructures/{infrastructure_id}"

    params = {
        'accountIdentifier': account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id,
        'environmentIdentifier': environment_id
    }

    # Set up headers with the Authorization key
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    # Send GET request to Harness API
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON response and return the details
        return response.json()
    else:
        # Return error message if the request fails
        return f"Failed to retrieve data: {response.status_code} - {response.text}"


def update_infra_git_metadata(api_key, account_id, org_id, project_id, env_id, env_type, infra_id):
    url = f"https://app.harness.io/ng/api/infrastructures/{infra_id}/update-git-metadata"

    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id,
        "environmentIdentifier": env_id,
        "filePath": get_target_file_path(org_id, project_id, infra_id, env_id, env_type)
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    print(f"Updating infra filepath : {params} for infra id : {infra_id}")

    try:
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx and 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error updating Git metadata: {e}")
        return None


def update_infra_file_path(api_key, account_id, org_id, project_id):
    env_list = get_environments(api_key, account_id, org_id, project_id)
    for element in env_list:
        env = element['environment']
        infra_list = get_infras(api_key, account_id, org_id, project_id, env['identifier'])
        for element in infra_list:
            infra = element['infrastructure']
            if infra['storeType'] != 'INLINE':
                update_infra_git_metadata(api_key, account_id, org_id, project_id, env['identifier'], env['type'], infra['identifier'])


def process_infras(api_key, account_id, org_id, project_id):
    env_list = get_environments(api_key, account_id, org_id, project_id)
    entity_data_list = []
    for element in env_list:
        env = element['environment']
        infra_list = get_infras(api_key, account_id, org_id, project_id, env['identifier'])
        if len(infra_list) == 0:
            continue
        for infra in infra_list:
            element = infra['infrastructure']
            try:
                infra_details = get_infrastructure_details(api_key, account_id, org_id, project_id, env['identifier'], element['identifier'])
                data = infra_details['data']['infrastructure']
                print(infra_details)
                print(data)
                if data['storeType'] != 'INLINE':
                    entity_data = EntityDetails(account_id, org_id, project_id, data['identifier'], data['yaml'],
                                            data['entityGitDetails']['repoName'],
                                            get_repo_url(data['entityGitDetails']['fileUrl'],
                                                         data['entityGitDetails']['repoName']))
                    entity_data.sub_type = env['type']
                    entity_data.parent_id = env['identifier']
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
    return get_target_file_path(entity_data.org_identifier, entity_data.project_identifier, entity_data.identifier, entity_data.parent_id, entity_data.sub_type)


def get_target_file_path(org_id, project_id, identifier, env_id, env_type):
    env_type = env_type.lower()
    target_file_path = ".harness/"
    ending_path = "envs/" + env_type + "/" + env_id + "/infras/" + identifier + ".yaml"
    if is_empty(org_id):
        return target_file_path + ending_path
    if is_empty(project_id):
        return target_file_path + "orgs/" + org_id + "/" + ending_path
    return ".harness/orgs/" + org_id + "/projects/" + project_id + "/" + ending_path