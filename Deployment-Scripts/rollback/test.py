import sys
import os
from os.path import isfile, join
from os import listdir
import base64
import glob
import git
import requests

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
repo_path = str(sys.argv[12])


#########################################################
#Begin Procedure Git

# Get repo
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

for x in previouscommit.diff(commitidfromtag):
    if x.a_path not in changed_files:
        changed_files.append(x.a_path)
        changed_type_list.append(x.change_type)
            
    if x.b_path is not None and x.b_path not in changed_files:
        changed_files.append(x.b_path)
        changed_type_list.append(x.change_type)

print("file to change : " , changed_files)

to_add = []
to_remove = []
to_replace = []

            

for i in range(len(changed_files)):
    if changed_files[i].startswith(DATABRICKS_NOTEBOOKS_DIRECTORY):

        to_replace.append(changed_files[i])
        if changed_type_list[i] == 'A':
            to_add.append(changed_files[i])
        else:
            to_replace.append(changed_files[i])

print("File need to add in this tag ", to_add)
print("File need to remove", to_remove) 
print("Summary file to added after remove", to_replace)




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
    return response.json()['token_value']

Workspcae_Token = create_adb_token_api("2.0/token/create",ADB_TOKEN_REQ_BODY)
print(Workspcae_Token)
if not Workspcae_Token:
    raise Exception("Create adb token failed")

##################################################
# Begin create folder that relate to changed


def createfolder_to_databricks(notebook_path):

    # Create Directory in Databricks Workspace if has directory
    if os.path.dirname(notebook_path) != "/" and os.path.dirname(notebook_path):
        print(os.path.dirname(notebook_path))
        dir_name = os.path.split(notebook_path)[0]
        print(dir_name)
        json_notebook_path = {
            "path" : dir_name
        }
        status = create_adb_token_api("2.0/workspace/mkdirs",json_notebook_path)
        if not status:
            raise Exception("Create directory {} failed".format(dir_name))

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





# Recursive create folder relate to change directory
if os.path.exists(DIRECTORY):

        for i in range():


        for path, subdirs, files in os.walk(DIRECTORY):
                notebook_full_path_dir = path.split(DATABRICKS_NOTEBOOKS_DIRECTORY)[-1]
                print(notebook_full_path_dir)
                notebook_name_dir = notebook_full_path_dir[1:]
                print(notebook_name_dir)
                notebook_abs_path_dir = os.path.join(NOTEBOOK_DIRECTORY,notebook_name_dir)
                print(notebook_abs_path_dir)
                dir_name = notebook_abs_path_dir.replace('\\','/')
                print(dir_name)
              

#create Files
if os.path.exists(DIRECTORY):
        for path, subdirs, files in os.walk(DIRECTORY):
            for file in files:
                notebook_full_path = os.path.join(path.split(DATABRICKS_NOTEBOOKS_DIRECTORY)[-1], file)
                print(notebook_full_path)
                print(notebook_full_path.split(TYPE_OF_FILE)[0])
                notebook_name = notebook_full_path.split(TYPE_OF_FILE)[0]
                #if notebook_name[0] == "":
                notebook_name = notebook_name[1:]
                print(notebook_name)
                # Get Absolute path to import in Databricks Notebook
                notebook_abs_path = os.path.join(NOTEBOOK_DIRECTORY,notebook_name).replace('\\','/')
                #print("printing notebook 0",notebook_name[0],notebook_name[1:])
                print("printint nbote booke abs path",notebook_abs_path)
                # Get Absolute path of python file
                abs_path_file = os.path.join(path,file)
                
                print("sending the notebookPath and abs Path",notebook_abs_path,abs_path_file)
                #response = import_to_databricks(notebook_abs_path,abs_path_file) 

                #print("the absolute Path",abs_path_file)
                #print("the absolute Path on Server",notebook_abs_path)
else:
    raise Exception("Cannot find directory: {}".format(DIRECTORY))