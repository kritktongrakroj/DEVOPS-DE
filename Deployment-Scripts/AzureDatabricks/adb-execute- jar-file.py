import sys
import os
from os.path import isfile, join
from os import listdir
import base64
import glob
import requests
import json
import sys
import getopt
import time

tenant_id= str(sys.argv[1])
client_id=str(sys.argv[2])
client_secret=str(sys.argv[3])
subscription_id=str(sys.argv[4])
resourceGroup=str(sys.argv[5])
workspaceName=str(sys.argv[6])
NOTEBOOK_DIRECTORY=str(sys.argv[7])
CLUSTER_NAME = str(sys.argv[8])
NOTEBOOK_EXE_PATH = str(sys.argv[9])
sql_function = str(sys.argv[10])
lib_class = str(sys.argv[11])

print(sys.argv)

#Declare REQ BODY for dbrks_bearer_token() and dbrks_management_token()
TOKEN_REQ_BODY = {
    'grant_type': 'client_credentials',
    'client_id':  client_id,
    'client_secret':  client_secret}
TOKEN_BASE_URL = 'https://login.microsoftonline.com/' +  tenant_id + '/oauth2/token'
TOKEN_REQ_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

# Funtion for getting for the global Databricks application.
# The resource name is fixed and never changes.
def dbrks_bearer_token():
        TOKEN_REQ_BODY['resource'] = '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d'
        response = requests.get(TOKEN_BASE_URL, headers=TOKEN_REQ_HEADERS, data=TOKEN_REQ_BODY)
        if response.status_code == 200:
            print(response.status_code)
        else:
            raise Exception(response.text)
        return response.json()['access_token']

# Funtion for getting a token for the Azure management API
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
    'lifetime_seconds': 5000, 
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

###########################################################################################################
# Get Databrick Cluster ID.
def get_adb_cluster_id_api(endpoint):
    api_url = "https://{}/api/{}".format(Workspcae_URL,endpoint)
    headers = {'Authorization': 'Bearer {}'.format(DBRKS_BEARER_TOKEN)}
    print(api_url)

    response = requests.get(
        api_url,
        headers=headers,
    )
    # Validate response code
    if response.status_code != 200:    
        raise Exception("API Failed, Result: {}".format(response.json()))    
        response.raise_for_status()
    
    for adb_cluster in response.json()["clusters"]:
        print(adb_cluster["cluster_name"])
        if adb_cluster["cluster_name"] == CLUSTER_NAME:
            return adb_cluster['cluster_id']

Cluster_ID = get_adb_cluster_id_api("2.0/clusters/list")
print(Cluster_ID)

###########################################################################################################

# workspace = Workspcae_URL
# token = Workspcae_Token
# clusterid = Cluster_ID
# notebookpath = NOTEBOOK_EXE_PATH

print('Running job for:' + NOTEBOOK_EXE_PATH)
values = {'run_name': 'config deploy', 'existing_cluster_id': Cluster_ID, 'timeout_seconds': 4800, 'notebook_task': {'notebook_path': NOTEBOOK_EXE_PATH, 'base_parameters': {'sql_function': func, 'lib_class': lib_class}}}
resp = requests.post('https://'+Workspcae_URL + '/api/2.0/jobs/runs/submit',
                     data=json.dumps(values), auth=("token", Workspcae_Token))
runjson = resp.text
print("runjson:" + runjson)
d = json.loads(runjson)
runid = d['run_id']
i=0
waiting = True
while waiting:
    time.sleep(10)
    jobresp = requests.get('https://'+Workspcae_URL + '/api/2.0/jobs/runs/get-output?run_id='+str(runid),
                     data=json.dumps(values), auth=("token", Workspcae_Token))
    jobjson = jobresp.text
    print("jobjson:" + jobjson)
    j = json.loads(jobjson)
    current_state = j['metadata']['state']['life_cycle_state']
    runid = j['metadata']['run_id']
    if current_state in ['TERMINATED']:
        try:
            status = j['notebook_output']['result']
            if 'SUCCESS' in status:
                break
            else:
                raise ValueError(f'Notebook run result in failure status: {status}')
        except:
            raise ValueError(f'Notebook run result no status, please exit notebook with value "SUCCESS"')
        break
    if current_state in ['INTERNAL_ERROR', 'SKIPPED', 'FAILED', 'TIMED_OUT']:
        raise ValueError(f'Notebook run result in failure state: {current_state}')
        break
    i=i+1

print(json.dumps(j))
