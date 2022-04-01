from asyncore import file_dispatcher
import sys
import os
from os.path import isfile, join
from os import listdir
import base64
import glob
import git
import requests
import pathlib


print(sys.argv)

tenant_id= str(sys.argv[1])
client_id=str(sys.argv[2])
client_secret=str(sys.argv[3])
subscription_id=str(sys.argv[4])
resourceGroup=str(sys.argv[5])
workspaceName=str(sys.argv[6])
NOTEBOOK_DIRECTORY=str(sys.argv[7])
DATABRICKS_NOTEBOOKS_DIRECTORY = str(sys.argv[8])

input_tag = str(sys.argv[9])
branch_name = str(sys.argv[10])
repo_url = str(sys.argv[11])
repo_path = (sys.argv[12])


#########################################################
#Begin Procedure Git

# Get repo
print(branch_name)

repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)

# Get all commit list
#commits_list = list(repo.iter_commits())

# Checkout to that branch name selected
repo.git.checkout(branch_name)

# Sorted tag by date and find the previous tags
tagslist = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
print(tagslist)

def find_tag_position(tag):
    for i in range(len(tagslist)):
        tagref = str(tagslist[i])
        if tagref == tag:
            return i

tag_position = find_tag_position(input_tag)
previoustag = str(tagslist[tag_position - 1])

# Get commit id from both tag
previouscommit = repo.commit(previoustag)
commitidfromtag = repo.commit(input_tag)

print("this tag is :", str(tagslist[tag_position]),"It is in position : ",tag_position, "Its commit ID is : ", commitidfromtag)
print("the previous tag is :", str(tagslist[tag_position - 1]), "Its commit ID is : ", previouscommit)

# Begin get Diff
changed_files = []
changed_type_list = []


from_a = []
from_b = []
changed_type_list_a = []
changed_type_list_b = []



for x in previouscommit.diff(commitidfromtag):
    if x.a_path not in changed_files:
        changed_files.append(x.a_path)
        changed_type_list.append(x.change_type)
        changed_type_list_a.append(x.change_type)
        from_a.append(x.a_path)
            
    if x.b_path is not None and x.b_path not in changed_files:
        changed_files.append(x.b_path)
        changed_type_list.append(x.change_type)
        changed_type_list_b.append(x.change_type)
        from_b.append(x.b_path)



print("file to change : " , changed_files)
print("file change type: ", changed_type_list)

remove_old_name= []

to_change_from_b=[]

# Finding file to remove from B at note book path
for i in range(len(from_b)):
    if from_b[i].startswith(DATABRICKS_NOTEBOOKS_DIRECTORY):
        to_change_from_b.append(from_b[i])


to_change_from_a=[]

# Finding file to remove from B at note book path
for i in range(len(from_a)):
    if from_a[i].startswith(DATABRICKS_NOTEBOOKS_DIRECTORY):
        to_change_from_a.append(from_a[i])

        if changed_type_list_a[i] == 'R':
            remove_old_name.append(from_a[i])

        
        

print("Change on commit a : " , to_change_from_a)

# from_b mean file that rename between commit
print("Change on commit b : " , to_change_from_b)


remove_file_a = []
to_replace = []

# list modified and new file in previous commit
new_file= []
modified_file=[]





            
# Finding file to remove and add in the notebook
for i in range(len(changed_files)):
    if changed_files[i].startswith(DATABRICKS_NOTEBOOKS_DIRECTORY):

        to_replace.append(changed_files[i])

        if changed_type_list[i] == 'M' :
            remove_file_a.append(changed_files[i])
            modified_file.append(changed_files[i])
        elif changed_type_list[i] == 'D' :
            remove_file_a.append(changed_files[i])
        elif changed_type_list[i] == 'A' :
            new_file.append(changed_files[i])

# remove_file_from will remove all changed file M, R and D
        
to_remove = remove_file_a + remove_old_name

# Clear which file is to add in this case we use list of all change file in notebook path - old name file that replace with new name - list of deleted file
# In summary we can import all modify file and new file

#clear_file = set(to_replace) - set(to_remove_from_b) - set(deleted_file)


to_add = to_change_from_b + new_file + modified_file

print("this is all raw replace list : ",to_replace)

print("File need to remove", to_remove) 
print("Summary file to added after remove", to_add)




#########################################################

#Declare REQ BODY for dbrks_bearer_token() and dbrks_management_token()
TOKEN_REQ_BODY = {
    'grant_type': 'client_credentials',
    'client_id':  client_id,
    'client_secret':  client_secret}
TOKEN_BASE_URL = 'https://login.microsoftonline.com/' +  tenant_id + '/oauth2/token'
TOKEN_REQ_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

# Function for getting for the global Databricks application.
# The resource name is fixed and never changes.
def dbrks_bearer_token():
        TOKEN_REQ_BODY['resource'] = '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d'
        response = requests.get(TOKEN_BASE_URL, headers=TOKEN_REQ_HEADERS, data=TOKEN_REQ_BODY)
        if response.status_code == 200:
            print(response.status_code)
        else:
            raise Exception(response.text)
        return response.json()['access_token']

# Function for getting a token for the Azure management API
def dbrks_management_token():
        TOKEN_REQ_BODY['resource'] = 'https://management.core.windows.net/'
        response = requests.get(TOKEN_BASE_URL, headers=TOKEN_REQ_HEADERS, data=TOKEN_REQ_BODY)
        if response.status_code == 200:
            print(response.status_code)
        else:
            raise Exception(response.text)
        return response.json()['access_token']

# Get a token for the global Databricks application.
# Shell script -> token=$(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d | jq -r .accessToken)
DBRKS_BEARER_TOKEN = dbrks_bearer_token()

# Get a token for the Azure management API
DBRKS_MANAGEMENT_TOKEN = dbrks_management_token()

###########################################################################################################

#Declare REQ BODY for getting ADB workspace URL 
DBRKS_WorksID_REQ_HEADERS = {
    'Authorization': 'Bearer ' + DBRKS_MANAGEMENT_TOKEN,
    'Content-Type': 'application/json'}

#Get ADB workspace URL 
mgmt_url="https://management.azure.com/subscriptions/"+subscription_id+"/resourcegroups/"+resourceGroup+"/providers/Microsoft.Databricks/workspaces/"+workspaceName+"?api-version=2018-04-01"
response = requests.get(mgmt_url,headers=DBRKS_WorksID_REQ_HEADERS)
Workspcae_URL = response.json()['properties']['workspaceUrl']
print("ADB Workspace URL: "+Workspcae_URL)

###########################################################################################################
# Get Databrick workspace token.
ADB_TOKEN_REQ_BODY ={
    'lifetime_seconds': 3600, 
    'comment': 'this is an example token'
}

def create_adb_token_api(endpoint,json_content):
    api_url = "https://{}/api/{}".format(Workspcae_URL,endpoint)
    headers = {'Authorization': 'Bearer {}'.format(DBRKS_BEARER_TOKEN)}
    print(api_url)

    response = requests.post(
        api_url,
        headers=headers,
        json=json_content
    )
    # Validate response code
    if response.status_code != 200:    
        raise Exception("API Failed, Result: {}".format(response.json()))    
        response.raise_for_status()
    return True


Workspcae_Token = create_adb_token_api("2.0/token/create",ADB_TOKEN_REQ_BODY)
print(Workspcae_Token)
if not Workspcae_Token:
    raise Exception("Create adb token failed")

##################################################
# Begin create folder that relate to changed


def createfolder_to_databricks(notebook_path):

    # Create Directory in Databricks Workspace if has directory
    if os.path.dirname(notebook_path) != "/" and os.path.dirname(notebook_path):
        print(notebook_path)
        json_notebook_path = {
            "path" : notebook_path
        }
        status = create_adb_token_api("2.0/workspace/mkdirs",json_notebook_path)
        if not status:
            raise Exception("Create directory {} failed".format(notebook_path))
    

# Function to remove file
def delete_existing_notebook_directory(notebook_path):
    json_content = {
        "path": notebook_path,
        "recursive": True
    }
    status = create_adb_token_api("2.0/workspace/delete",json_content)
    if not status:
        raise Exception("Cannot delete {} .".format(notebook_path))


#Function import notebook
def import_to_databricks(notebook_path,full_path_file):
    file_content = open(full_path_file, "r").read()
    content_bytes = file_content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')

    filename = os.path.split(full_path_file)[1]
    if filename.lower().endswith('.sql'):
        language="SQL"
    elif filename.lower().endswith('.scala'):
        language="SCALA"
    elif filename.lower().endswith('.py'):
        language="PYTHON"
    elif filename.lower().endswith('.r'):
        language="R"


    json_content = {
        "content": base64_message,
        "path": notebook_path,
        "language": language,
        "overwrite": True
    } 
    
    print("Start import {}.".format(filename))
    status = create_adb_token_api("2.0/workspace/import",json_content)
    if not status:
        raise "Import {} failed".format(filename)
    return "Import {} success".format(filename)


DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), DATABRICKS_NOTEBOOKS_DIRECTORY)
TYPE_OF_FILE = "."
print(DIRECTORY)

#Create Structure Folder
if os.path.exists(DIRECTORY):
        for path, subdirs, files in os.walk(DIRECTORY):
                notebook_full_path_dir = path.split(DATABRICKS_NOTEBOOKS_DIRECTORY)[-1]
                notebook_name_dir = notebook_full_path_dir[1:]
                notebook_abs_path_dir = os.path.join(NOTEBOOK_DIRECTORY,notebook_name_dir)
                dir_name = notebook_abs_path_dir.replace('\\','/')
                response = createfolder_to_databricks(dir_name)


#create new folder for change file if required
if os.path.exists(DIRECTORY):
    if os.path.exists(DIRECTORY):
        for i in range(len(to_add)):
            folder_to_create = to_add[i]
            split_remove_path_folder_add = pathlib.Path(folder_to_create)
            raw_path_folder_add = pathlib.Path(*split_remove_path_folder_add.parts[2:])
            join_raw_path_add = os.path.join(NOTEBOOK_DIRECTORY, raw_path_folder_add)
            final_dir_folder = os.path.dirname(join_raw_path_add)
            print(final_dir_folder)
            response = createfolder_to_databricks(final_dir_folder)

#Remove All Files that changes
print("Begin remove file")
if os.path.exists(DIRECTORY):
        for i in range(len(to_remove)):
            file_to_remove = to_remove[i]
            split_remove_path = pathlib.Path(file_to_remove)
            raw_path = pathlib.Path(*split_remove_path.parts[2:])
            join_raw_path = os.path.join(NOTEBOOK_DIRECTORY, raw_path)
            final_dir = join_raw_path.split(TYPE_OF_FILE)[0]
            print(final_dir)
            response = delete_existing_notebook_directory(final_dir)


# Add Modify and new file
print("Begin add file")
if os.path.exists(DIRECTORY):
        for i in range(len(to_add)):
            file_to_add = to_add[i]
            split_remove_path_add = pathlib.Path(file_to_add)
            raw_path_add = pathlib.Path(*split_remove_path_add.parts[2:])
            join_raw_path_add = os.path.join(NOTEBOOK_DIRECTORY, raw_path_add)
            final_dir_add = join_raw_path_add.split(TYPE_OF_FILE)[0]
            print(final_dir_add)
            response = import_to_databricks(final_dir_add,file_to_add)


else:
    raise Exception("Cannot find directory: {}".format(DIRECTORY))
