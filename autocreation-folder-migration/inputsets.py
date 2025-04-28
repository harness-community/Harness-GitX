import requests
from utility import EntityDetails, get_repo_url
from pipelines import fetch_pipelines


def get_input_sets(api_key, account_id, org_id, project_id, pipeline_id):
    # Harness API endpoint for fetching input sets for a pipeline
    url = f"https://app.harness.io/gateway/pipeline/api/inputSets"

    # Set up headers with the Authorization key
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    # Query parameters
    params = {
        'accountIdentifier': account_id,
        'orgIdentifier': org_id,
        'projectIdentifier': project_id,
        'pipelineIdentifier': pipeline_id,
        'pageIndex': 0
    }

    input_set_list = []
    while True:
        # Send GET request to Harness API
        response = requests.get(url, headers=headers, params=params)
        # Check if the request was successful
        if response.status_code == 200:
            content = response.json()['data']['content']
            if len(content) == 0:
                return input_set_list
            input_set_list.extend(content)
            params['pageIndex'] += 1
        else:
            # Return error message if the request fails
            print(f"Failed to retrieve input sets: {response.status_code} - {response.text}")
            return []


def get_input_set_details(api_key, account_id, org_id, project_id, pipeline_id,  input_set_id):
    # Harness API endpoint for fetching a specific input set by ID
    url = f"https://app.harness.io/pipeline/api/inputSets/{input_set_id}"

    # Set up headers with the Authorization key
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    # Query parameters
    params = {
        'accountIdentifier': account_id,
        'orgIdentifier': org_id,
        'projectIdentifier': project_id,
        'pipelineIdentifier': pipeline_id
    }

    # Send GET request to Harness API
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse and return the input set details if successful
        return response.json()
    else:
        # Return error message if the request fails
        return f"Failed to retrieve input set details: {response.status_code} - {response.text}"


def update_input_set_git_metadata(api_key, account_id, org_id, project_id, pipeline_id, input_set_id):
    # URL to update Git metadata for the pipeline
    url = f"https://app.harness.io/gateway/pipeline/api/inputSets/{input_set_id}/update-git-metadata"
    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id,
        "pipelineIdentifier": pipeline_id,
        "filePath": get_target_file_path(org_id, project_id, pipeline_id, input_set_id)
    }
    # Headers for authentication
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    print(f"Updating input-set filepath : {params} for input-set id : {input_set_id}")

    # Make the PUT request to update the Git metadata
    response = requests.put(url, headers=headers, params=params)
    if response.status_code == 200:
        print({"status": "success", "message": f"✅ Git metadata for inputset {input_set_id} updated successfully!"})
    else:
        print({"status": "error", "message": "Failed to update Git metadata", "details": response.json()})


def update_input_set_file_path(api_key, account_id, org_id, project_id):
    pipeline_list = fetch_pipelines(api_key, account_id, org_id, project_id)
    for pipeline in pipeline_list:
        input_set_list = get_input_sets(api_key, account_id, org_id, project_id, pipeline['identifier'])
        for input_set in input_set_list:
            try:
                update_input_set_git_metadata(api_key, account_id, org_id, project_id, pipeline['identifier'], input_set['identifier'])
            except Exception as ex:
                print(ex)


def process_input_sets(api_key, account_id, org_id, project_id):
    pipeline_list = fetch_pipelines(api_key, account_id, org_id, project_id)
    entity_data_list = []
    for pipeline in pipeline_list:
        input_set_list = get_input_sets(api_key, account_id, org_id, project_id, pipeline['identifier'])
        for element in input_set_list:
            try:
                input_set_details = get_input_set_details(api_key, account_id, org_id, project_id, pipeline['identifier'], element['identifier'])
                data = input_set_details['data']
                if data['storeType'] != 'INLINE':
                    entity_data = EntityDetails(account_id, org_id, project_id, data['identifier'],
                                                data['inputSetYaml'], data['gitDetails']['repoName'],
                                                get_repo_url(data['gitDetails']['fileUrl'], data['gitDetails']['repoName']))
                    entity_data.parent_id = pipeline['identifier']
                    entity_data.target_file_path = get_target_file_path_from_entity(entity_data)
                    if entity_data.target_file_path == data['gitDetails']['filePath']:
                        print("ignoring the pipeline as its already under conventional filepath:\nMetadata:" + str(pipeline) + "\nDetails:" + str(data))
                        continue
                    entity_data_list.append(entity_data)
            except Exception as ex:
                print(ex)
    return entity_data_list


def get_target_file_path_from_entity(entity_data):
    return get_target_file_path(entity_data.org_identifier, entity_data.project_identifier, entity_data.parent_id, entity_data.identifier)


def get_target_file_path(org_id, project_id, pipeline_id, identifier):
    return ".harness/orgs/" + org_id + "/projects/" + project_id + "/pipelines/" + pipeline_id + "/input_sets/" + identifier + ".yaml"
