# Autocreation Folder Migration

This utility helps to migrate existing files into Harness Gitx's conventional folders, used for autocreation as well. Users can directly refer to the source code here to run it on their systems or install and run docker image based solution for quick access.

For more info on GitX Autocreation: https://developer.harness.io/docs/platform/git-experience/autocreation-of-entities/

## How it works

This is a python based utility which will help users to migrate their files in 2 simple steps. It takes the scope of the entities to be migrated and the operation type to be performed as inputs:
### Operation 1

- It fetches yamls from GIT for all remote entities (in given scope) from default branch of GIT repo.
- It forks a new branch in the respective GIT repo and creates new files in the expected autocreation path with the relevant yamls as content.
- It creates pull request from forked branch to default branch of GIT repo.

After performing Operation-1, user needs to review the PR and get it merged. This ensures that the required yamls are present in their expected autocreation filepaths to ensure smooth migration. Current filepaths aren't touched to ensure current operations run as expected.

### Operation 2

- It simply points Harness entity to its newly created filepath.

Both operation-1 and operation-2 are automated and work based on given inputs. There are 3 major inputs:
- The scope of the entities to be migrated eg: project level / org level / account level entities
- The type of entities to be migrated eg: PIPELINE / TEMPLATES / SERVICES etc.
- The operation to be performed, whether its operation-1 or operation-2

Notes:
- It migrates a given type of entity for given scope in one go. It needs to be run separately for all entities and all scopes. Combining more entities and scopes together would run into a complex solution, thus avoided at this point of time.
- Operation-1 and Operation-2 are idempotent in nature. Operation-2 needs to be performed only after Operation-1 to avoid any issues.


key.json sample file
```
{
  "account-id": "your-harness-account-id",
  "harness-api-key": "your-harness-api-key with write perms for given entity",
  "git-token": "your-git-provider-token with write permissions",
  "git-provider": "GITHUB" (Bitbucket/Gitlab/others shall be supported in future),
  "git-domain": "" (Applicable for custom domain GIT systems eg: Harness.github.com)
}
```





## How to use

1. Download docker image from https://hub.docker.com/r/harnesscommunity/gitx-autocreation-folder-migration using docker pull command: ```docker pull harnesscommunity/gitx-autocreation-folder-migration```
2. Now, to run the application, simply use command: `docker run -it -v $(pwd)/keys.json:/app/keys.json harnesscommunity/gitx-autocreation-folder-migration:latest`


