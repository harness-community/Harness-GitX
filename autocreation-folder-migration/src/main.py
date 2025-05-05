from pipelines import process_pipelines, update_pipeline_file_path
from inputsets import process_input_sets, update_input_set_file_path
from templates import process_templates, update_template_file_path
from services import process_services, update_service_file_path
from environments import process_environments, update_env_file_path
from infras import process_infras, update_infra_file_path
import time
from git import fork_branch, commit_file, create_pull_request
from context import Context


ORG_ID = "default"
PROJECT_ID = "test_mohit_11_march"


def handle_operation_1(entity_type, org_id, project_id):
    if entity_type == "PIPELINE":
        entity_data_list = process_pipelines(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "INPUTSET":
        entity_data_list = process_input_sets(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "TEMPLATE":
        entity_data_list = process_templates(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "SERVICE":
        entity_data_list = process_services(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "ENV":
        entity_data_list = process_environments(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "INFRA":
        entity_data_list = process_infras(Context.api_key, Context.account_id, org_id, project_id)
    else:
        print("Invalid entity type as input: " + entity_type)
        return
    print(entity_data_list)
    branch = get_branch_name()
    fork_branches(entity_data_list, branch)
    for entity_data in entity_data_list:
        commit_file(Context.git_token, entity_data.repo, branch, entity_data.repo_url, entity_data.target_file_path, entity_data.yaml)
    raise_pr(entity_data_list, branch)


def handle_operation_2(entity_type, org_id, project_id):
    if entity_type == "PIPELINE":
        update_pipeline_file_path(Context.api_key, Context.account_id, org_id, project_id)
    if entity_type == "INPUTSET":
        update_input_set_file_path(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "TEMPLATE":
        update_template_file_path(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "SERVICE":
        update_service_file_path(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "ENV":
        update_env_file_path(Context.api_key, Context.account_id, org_id, project_id)
    elif entity_type == "INFRA":
        update_infra_file_path(Context.api_key, Context.account_id, org_id, project_id)
    else:
        print("Invalid entity type as input: " + entity_type)


def raise_pr(entity_data_list, branch):
    repo_details_list = get_repo_details(entity_data_list)
    for repo_details in repo_details_list:
        create_pull_request(Context.git_token, repo_details[0], branch, repo_details[1])


def fork_branches(entity_data_list, branch):
    repo_details_list = get_repo_details(entity_data_list)
    for repo_details in repo_details_list:
        fork_branch(Context.git_token, branch, repo_details[0], repo_details[1])


def get_repo_details(entity_data_list):
    repo_details_list = set()
    for entity_data in entity_data_list:
        repo_details_list.add((entity_data.repo, entity_data.repo_url))
    return repo_details_list


def get_branch_name():
    return "HARNESS_GITX_" + str(int(time.time() * 1000))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Context.init()
    print("Please enter the entity scope:")
    org_id = input("Input org id (leave empty for ACCOUNT level operation): ")
    project_id = input("Input project id (leave empty for ACCOUNT/ORG level operation): ")
    entity_type = input("Please enter the entity-type to process (PIPELINE/INPUTSET/TEMPLATE/SERVICE/ENV/INFRA): ")
    operation_type = input("Choose operation: \n1: Create new files and raise PR \n2: Update all file paths\n")
    if operation_type == "1":
        handle_operation_1(entity_type, org_id, project_id)
    else:
        handle_operation_2(entity_type, org_id, project_id)


def exec_with_inputs():
    Context.init()
    operation_type = "1"
    entity_type = "INFRA"
    if operation_type == "1":
        handle_operation_1(entity_type, ORG_ID, PROJECT_ID)
    else:
        handle_operation_2(entity_type, ORG_ID, PROJECT_ID)
