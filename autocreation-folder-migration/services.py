import requests
from utility import EntityDetails, get_repo_url, is_empty


def fetch_services(api_key, account_identifier, org_identifier, project_identifier):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    services = []
    page = 0
    while True:
        try:
            url = f"https://app.harness.io/ng/api/servicesV2?accountIdentifier={account_identifier}&orgIdentifier={org_identifier}&projectIdentifier={project_identifier}&page={page}"
            # Send GET request to the Harness API
            response = requests.get(url, headers=headers)

            # Check if the request was successful
            response.raise_for_status()

            # Return the JSON response containing services
            content = response.json()['data']['content']
            if len(content) == 0:
                return services
            page += 1
            services.extend(content)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")


def update_service_git_metadata(api_key, account_id, org_id, project_id, service_id):
    url = f"https://app.harness.io/gateway/ng/api/servicesV2/{service_id}/update-git-metadata"

    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id,
        "filePath": get_target_file_path(org_id, project_id, service_id)
    }
    # Headers for authentication
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    print(f"Updating service filepath : {params} for service id : {service_id}")

    try:
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx and 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error updating service Git metadata: {e}")
        return None


def update_service_file_path(api_key, account_id, org_id, project_id):
    service_list = fetch_services(api_key, account_id, org_id, project_id)
    for element in service_list:
        service = element['service']
        if service['storeType'] != 'INLINE':
            update_service_git_metadata(api_key, account_id, org_id, project_id, service['identifier'])


def fetch_service_details(api_key, account_id, org_id, project_id, service_id):
    url = f"https://app.harness.io/gateway/ng/api/servicesV2/{service_id}"
    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id
    }
    # Headers for authentication
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx and 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching service details: {e}")
        return None


def process_services(api_key, account_id, org_id, project_id):
    service_list = fetch_services(api_key, account_id, org_id, project_id)
    entity_data_list = []
    for element in service_list:
        service = element['service']
        try:
            service_details = fetch_service_details(api_key, account_id, org_id, project_id, service["identifier"])
            data = service_details['data']['service']
            if data['storeType'] != 'INLINE':
                entity_data = EntityDetails(account_id, org_id, project_id, service['identifier'], data['yaml'],
                                            data['entityGitDetails']['repoName'], get_repo_url(data['entityGitDetails']['fileUrl'], data['entityGitDetails']['repoName']))
                entity_data.target_file_path = get_target_file_path_from_entity(entity_data)
                if entity_data.target_file_path == data['entityGitDetails']['filePath']:
                    print("ignoring the service as its already under conventional filepath\nMetadata:" + str(
                        service) + "\nDetails:" + str(data))
                    continue
                entity_data_list.append(entity_data)
        except Exception as ex:
            print(ex)
    return entity_data_list


def get_target_file_path_from_entity(entity_data):
    return get_target_file_path(entity_data.org_identifier, entity_data.project_identifier, entity_data.identifier)


def get_target_file_path(org_id, project_id, service_id):
    target_file_path = ".harness/"
    ending_path = "services/" + service_id + ".yaml"
    if is_empty(org_id):
        return target_file_path + ending_path
    if is_empty(project_id):
        return target_file_path + "orgs/" + org_id + "/" + ending_path
    return ".harness/orgs/" + org_id + "/projects/" + project_id + "/" + ending_path
