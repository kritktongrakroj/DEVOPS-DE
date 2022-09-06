from asyncore import file_dispatcher
import sys
import os
from os.path import isfile, join
from os import listdir
import base64
import glob
from xml.sax.handler import property_interning_dict
import requests
import pathlib

print(sys.argv)

tenant_id= str(sys.argv[1])
client_id=str(sys.argv[2])
client_secret=str(sys.argv[3])
subscription_id=str(sys.argv[4])
resourceGroup=str(sys.argv[5])
workspaceName=str(sys.argv[6])
DBFS_DIRECTORY=str(sys.argv[7])
GIT_DBFS_DIRECTORY=str(sys.argv[8])
to_add = str(sys.argv[9])

to_add_dbfs = to_add.split(',')
print(to_add_dbfs)


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

def create_adb_token_api(endpoint, json_content, file=''):
    api_url = "https://{}/api/{}".format(Workspcae_URL,endpoint)
    headers = {'Authorization': 'Bearer {}'.format(DBRKS_BEARER_TOKEN)}
    print(api_url)
    
    response = ''
    if(file):
        response = requests.post(
            api_url,
            headers=headers,
            files={'contents': file},
            data={'path': json_content['path'],
                  'overwrite': json_content['overwrite']}
        )
    else:
        response = requests.post(
            api_url,
            headers=headers,
            json=json_content
        )
    # Validate response code
    print("The responde status code is :" ,response.status_code)
    if response.status_code != 200:    
        raise Exception("API Failed, Result: {}".format(response.json()))    
        response.raise_for_status()
    return True


Workspcae_Token = create_adb_token_api("2.0/token/create",ADB_TOKEN_REQ_BODY)
print(Workspcae_Token)
if not Workspcae_Token:
    raise Exception("Create adb token failed")

##################################################


def install_library(dbfs_path):

    print(dbfs_path)

    json_content = {
      "cluster_id": cluster_name,
      "libraries": [
        {
          "jar": "dbfs:/" + dbfs_path
        }
      ]
    } 
    
    print("Start install {}.".format(dbfs_path))
    status = create_adb_token_api("2.0/libraries/install",json_content)
    if not status:
        raise "Import {} failed".format(dbfs_path)
    return "Import {} success".format(dbfs_path)


#create new folder for change file if required
if to_add_dbfs:
        
    print("Begin install library")
    for i in range(len(to_add_dbfs)):
        folder_to_create = to_add_dbfs[i]
        split_remove_path_folder_add = pathlib.Path(folder_to_create)
        raw_path_folder_add = pathlib.Path(*split_remove_path_folder_add.parts[3:])
        print(raw_path_folder_add)
        join_raw_path_add = os.path.join(DBFS_DIRECTORY, raw_path_folder_add)
        
        response = install_library(join_raw_path_add)
        
        
        
        

else:
    raise Exception("No file list to import DBFS")
