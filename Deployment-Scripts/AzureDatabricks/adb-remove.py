from asyncore import file_dispatcher
import sys
import os
from os.path import isfile, join
from os import listdir
import base64
import glob
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


to_remove = str(sys.argv[9])



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
    #Validate response code
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


# Function to remove file
def delete_existing_notebook_directory(notebook_path):
    json_content = {
        "path": notebook_path,
        "recursive": True
    }
    status = create_adb_token_api("2.0/workspace/delete",json_content)
    print(status)
    if not status:
        raise Exception("Cannot delete {} .".format(notebook_path))


DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), DATABRICKS_NOTEBOOKS_DIRECTORY)
TYPE_OF_FILE = "."
print(DIRECTORY)
print(DATABRICKS_NOTEBOOKS_DIRECTORY)              
                
to_remove = to_remove.split(',')                
print(f'splited to_remove: {to_remove}')
#create new folder for change file if required
if to_remove :
   
    # Add Modify and new file
    print("Begin Remove File")
    for file_to_remove in to_remove:
        try:
            split_remove_path_add = pathlib.Path(file_to_remove)
            raw_path_add = pathlib.Path(*split_remove_path_add.parts[3:])
            join_raw_path_add = os.path.join(NOTEBOOK_DIRECTORY, raw_path_add)
            final_dir_add_raw = join_raw_path_add.split(TYPE_OF_FILE)[0]
            print(final_dir_add_raw)
            response = delete_existing_notebook_directory(final_dir_add_raw)
        except Exception:
            pass


else:
    #raise Exception("Cannot find directory or empty folder: {}".format(DIRECTORY))
    print("Cannot find directory or empty folder: {}".format(DIRECTORY))
