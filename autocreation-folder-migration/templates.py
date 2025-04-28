import requests
from utility import EntityDetails, is_empty


def fetch_templates(harness_api_key, account_id, org_id, project_id):
    base_url = "https://app.harness.io/gateway/template/api/templates/list-metadata"

    # Construct query parameters based on the given scope
    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id if org_id else None,
        "projectIdentifier": project_id if project_id else None,
        "templateListType": "LastUpdated",
        'page': 0
    }

    # Set headers with authorization
    headers = {
        "Content-Type": "application/json",
        "x-api-key": harness_api_key
    }

    templates = []
    while True:
        # Make GET request
        response = requests.post(base_url, headers=headers, params=params)
        # Check response status
        if response.status_code == 200:
            print (response.json())
            content = response.json()['data']['content']
            if len(content) == 0:
                return templates
            templates.extend(content)
            params['page'] += 1
        else:
            print(f"Failed to fetch templates. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None


def update_template_git_metadata(api_key, account_id, org_id, project_id, template_id, template_version):
    url = f"https://app.harness.io/gateway/template/api/templates/update/git-metadata/{template_id}/{template_version}"

    params = {
        "accountIdentifier": {account_id},
        "orgIdentifier": org_id if org_id else None,
        "projectIdentifier": project_id if project_id else None
    }

    data = {
        "filePath": get_target_file_path(org_id, project_id, template_id, template_version)
    }
    # Set headers with authorization
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    print(f"Updating template filepath : {params} for template id : {template_id} and version : {template_version}")

    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx and 5xx)
        print(response.json())

    except requests.exceptions.RequestException as e:
        print(f"Error updating Git metadata: {e}")
        return None


def update_template_file_path(api_key, account_id, org_id, project_id):
    template_list = fetch_templates(api_key, account_id, org_id, project_id)
    for template in template_list:
        if template['storeType'] != 'INLINE':
            update_template_git_metadata(api_key, account_id, org_id, project_id, template['identifier'], template['versionLabel'])


def fetch_template_details(harness_api_key, account_id, org_id, project_id, template_id, version):
    base_url = f"https://app.harness.io/gateway/template/api/templates/{template_id}"

    # Construct query parameters
    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id if org_id else None,
        "projectIdentifier": project_id if project_id else None,
        "versionLabel": version
    }

    # Set headers with authorization
    headers = {
        "Content-Type": "application/json",
        "x-api-key": harness_api_key
    }

    print(params)
    # Make GET request
    response = requests.get(base_url, headers=headers, params=params)
    # Check response status
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch template details. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def process_templates(api_key, account_id, org_id, project_id):
    template_list = fetch_templates(api_key, account_id, org_id, project_id)
    entity_data_list = []
    if template_list is None:
        print("no templates found to process")
        return entity_data_list
    print(template_list)
    for template in template_list:
        try:
            details = fetch_template_details(api_key, account_id, org_id, project_id, template["identifier"], template['versionLabel'])
            data = details['data']
            if data['storeType'] != 'INLINE':
                entity_data = EntityDetails(account_id, org_id, project_id, template['identifier'],
                                            data['yaml'], data['gitDetails']['repoName'],
                                            data['gitDetails']['repoUrl'])
                entity_data.version = template['versionLabel']
                entity_data.target_file_path = get_target_file_path_from_entity(entity_data)
                if entity_data.target_file_path == data['gitDetails']['filePath']:
                    print("ignoring the template as its already under conventional filepath" + template + ":::" + data)
                    continue
                entity_data_list.append(entity_data)
        except Exception as ex:
            print(ex)
    return entity_data_list


def get_target_file_path_from_entity(entity_data):
    return get_target_file_path(entity_data.org_identifier, entity_data.project_identifier, entity_data.identifier, entity_data.version)


def get_target_file_path(org_id, project_id, template_id, version):
    target_file_path = ".harness/"
    ending_path = "templates/" + template_id + "/" + version + ".yaml"
    if is_empty(org_id):
        return target_file_path + ending_path
    if is_empty(project_id):
        return target_file_path + "orgs/" + org_id + "/" + ending_path
    return ".harness/orgs/" + org_id + "/projects/" + project_id + "/" + ending_path
