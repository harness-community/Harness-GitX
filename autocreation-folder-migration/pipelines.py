import requests
from utility import EntityDetails


def fetch_pipelines(api_key, account_identifier, org_identifier, project_identifier):
    """Fetches a list of pipelines from Harness for a given account, org, and project."""

    page = 0
    is_last_page = False
    # Headers with authentication
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    pipelines = []

    while not is_last_page:
        url = (
            f"https://app.harness.io/gateway/pipeline/api/pipelines/list?&"
            f"accountIdentifier={account_identifier}&orgIdentifier={org_identifier}&projectIdentifier={project_identifier}&page={page}"
        )

        response = requests.post(url, headers=headers)
        # Check response status
        if response.status_code == 200:
            data = response.json()
            print(response.json())
            content = data.get("data", {}).get("content", [])
            if len(content) == 0:
                is_last_page = True
            pipelines.extend(content)
            page += 1
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []
    print(pipelines)
    return pipelines


def fetch_pipeline_details(api_key, account_id, org_id, project_id, pipeline_id):
    """Fetches details of a specific pipeline from Harness."""

    # API URL to fetch pipeline details
    url = (
        f"https://app.harness.io/gateway/pipeline/api/pipelines/{pipeline_id}?"
        f"accountIdentifier={account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}"
    )

    # Headers with authentication
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    # Send GET request to Harness API
    response = requests.get(url, headers=headers)

    # Check response status
    if response.status_code == 200:
        return response.json()  # Return pipeline details
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def update_pipeline_git_metadata(api_key, account_id, org_id, project_id, pipeline_id):
    # URL to update Git metadata for the pipeline
    url = f"https://app.harness.io/gateway/pipeline/api/pipelines/{pipeline_id}/update-git-metadata"
    params = {
        "accountIdentifier": account_id,
        "orgIdentifier": org_id,
        "projectIdentifier": project_id,
        "filePath": get_target_file_path(org_id, project_id, pipeline_id)
    }
    # Headers for authentication
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # API Key for authentication
    }

    print(f"Updating pipeline filepath : {params} for pipeline id : {pipeline_id}")

    # Make the PUT request to update the Git metadata
    response = requests.put(url, headers=headers, params=params)
    if response.status_code == 200:
        print({"status": "success", "message": f"✅ Git metadata for pipeline {pipeline_id} updated successfully!"})
    else:
        print({"status": "error", "message": "Failed to update Git metadata", "details": response.json()})


def update_pipeline_file_path(api_key, account_id, org_id, project_id):
    pipeline_list = fetch_pipelines(api_key, account_id, org_id, project_id)
    for pipeline in pipeline_list:
        if pipeline['storeType'] != 'INLINE':
            update_pipeline_git_metadata(api_key, account_id, org_id, project_id, pipeline['identifier'])


def process_pipelines(api_key, account_id, org_id, project_id):
    pipeline_list = fetch_pipelines(api_key, account_id, org_id, project_id)
    entity_data_list = []
    for pipeline in pipeline_list:
        try:
            pipeline_details = fetch_pipeline_details(api_key, account_id, org_id, project_id, pipeline["identifier"])
            data = pipeline_details['data']
            if data['storeType'] != 'INLINE':
                entity_data = EntityDetails(account_id, org_id, project_id, pipeline['identifier'],
                                            data['yamlPipeline'], data['gitDetails']['repoName'],
                                            data['gitDetails']['repoUrl'])
                entity_data.target_file_path = get_target_file_path_from_entity(entity_data)
                if entity_data.target_file_path == data['gitDetails']['filePath']:
                    print("ignoring the pipeline as its already under conventional filepath:\nMetadata:" + str(pipeline) + "\nDetails:" + str(data))
                    continue
                entity_data_list.append(entity_data)
        except Exception as ex:
            print(ex)
    return entity_data_list


def get_target_file_path_from_entity(entity_data):
    return get_target_file_path(entity_data.org_identifier, entity_data.project_identifier, entity_data.identifier)


def get_target_file_path(org_id, project_id, pipeline_id):
    return ".harness/orgs/" + org_id + "/projects/" + project_id + "/pipelines/" + pipeline_id + ".yaml"
