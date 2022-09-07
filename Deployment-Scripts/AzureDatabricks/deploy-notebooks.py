import sys
import os
from os.path import isfile, join
from os import listdir
import base64
import glob
import requests
#########################

tenant_id= str(sys.argv[1])
client_id=str(sys.argv[2])
client_secret=str(sys.argv[3])
subscription_id=str(sys.argv[4])
resourceGroup=str(sys.argv[5])
workspaceName=str(sys.argv[6])
NOTEBOOK_DIRECTORY=str(sys.argv[7])
DATABRICKS_NOTEBOOKS_DIRECTORY = str(sys.argv[8])

azure_databricks_resource_id="2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"
resourceId= '/subscriptions/'+subscription_id+'/resourceGroups/'+resourceGroup+'/providers/Microsoft.Databricks/workspaces/'+workspaceName
#print("the valie is",resourceId,azure_databricks_resource_id)


TOKEN_REQ_BODY = {
    'grant_type': 'client_credentials',
    'client_id':  client_id,
    'client_secret':  client_secret}
TOKEN_BASE_URL = 'https://login.microsoftonline.com/' +  tenant_id + '/oauth2/token'
TOKEN_REQ_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


def dbrks_management_token():
        TOKEN_REQ_BODY['resource'] = 'https://management.core.windows.net/'
        response = requests.get(TOKEN_BASE_URL, headers=TOKEN_REQ_HEADERS, data=TOKEN_REQ_BODY)
        if response.status_code == 200:
            print(response.status_code)
        else:
            raise Exception(response.text)
        return response.json()['access_token']


def dbrks_bearer_token():
        TOKEN_REQ_BODY['resource'] = '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d'
        response = requests.get(TOKEN_BASE_URL, headers=TOKEN_REQ_HEADERS, data=TOKEN_REQ_BODY)
        if response.status_code == 200:
            print(response.status_code)
        else:
            raise Exception(response.text)
        return response.json()['access_token']

DBRKS_BEARER_TOKEN = dbrks_bearer_token()
DBRKS_MANAGEMENT_TOKEN = dbrks_management_token()


DBRKS_WorksID_REQ_HEADERS = {
    'Authorization': 'Bearer ' + DBRKS_MANAGEMENT_TOKEN,
    'Content-Type': 'application/json'}

#Management URL
mgmt_url="https://management.azure.com/subscriptions/"+subscription_id+"/resourcegroups/"+resourceGroup+"/providers/Microsoft.Databricks/workspaces/"+workspaceName+"?api-version=2018-04-01"
response = requests.get(mgmt_url,headers=DBRKS_WorksID_REQ_HEADERS)
Workspcae_URL=response.json()['properties']['workspaceUrl']

# Create Folder is does not exist


dbrks_create_dir_url =  "https://"+Workspcae_URL+".azuredatabricks.net/api/2.0/workspace/mkdirs"
dbrks_import_rest_url = "https://"+Workspcae_URL+".azuredatabricks.net/api/2.0/workspace/import"
api_url="https://"+Workspcae_URL+".azuredatabricks.net/api/"

#print(dbrks_import_rest_url)
#print(dbrks_create_dir_url)

DBRKS_REQ_HEADERS = {
    'Authorization': 'Bearer ' +DBRKS_BEARER_TOKEN,
    'X-Databricks-Azure-Workspace-Resource-Id': '/subscriptions/'+ subscription_id +'/resourceGroups/'+resourceGroup+'/providers/Microsoft.Databricks/workspaces/' + workspaceName,
    'X-Databricks-Azure-SP-Management-Token': DBRKS_MANAGEMENT_TOKEN}


def adb_notebook_api(endpoint,json_content):
    api_url = "https://{}/api/{}".format(Workspcae_URL,endpoint)
    headers = {'Authorization': 'Bearer {}'.format(DBRKS_BEARER_TOKEN)}
    
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
    
def createfolder_to_databricks(notebook_path):
    # Create Directory in Databricks Workspace if has directory
    if os.path.dirname(notebook_path) != "/" and os.path.dirname(notebook_path):
        dir_name = os.path.split(notebook_path)[0]
        json_notebook_path = {
            "path" : dir_name
        }
        status = adb_notebook_api("2.0/workspace/mkdirs",json_notebook_path)
        if not status:
            raise Exception("Create directory {} failed".format(dir_name))

def import_to_databricks(notebook_path,full_path_file):
    file_content = open(full_path_file, "r").read()
    content_bytes = file_content.encode('utf-8')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('utf-8')

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
    status = adb_notebook_api("2.0/workspace/import",json_content)
    if not status:
        raise "Import {} failed".format(filename)
    return "Import {} success".format(filename)



DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), DATABRICKS_NOTEBOOKS_DIRECTORY)
TYPE_OF_FILE = "."

            
#Create Folder again
if os.path.exists(DIRECTORY):
        for path, subdirs, files in os.walk(DIRECTORY):
                notebook_full_path_dir = path.split(DATABRICKS_NOTEBOOKS_DIRECTORY)[-1]
                notebook_name_dir = notebook_full_path_dir[1:]
                notebook_abs_path_dir = os.path.join(NOTEBOOK_DIRECTORY,notebook_name_dir)
                dir_name = notebook_abs_path_dir.replace('\\','/')
                print("Dir Name is",dir_name)
                json_notebook_path = {
                "path" : dir_name
                }
                print(json_notebook_path)
                status = adb_notebook_api("2.0/workspace/mkdirs",json_notebook_path)
                if not status:
                   raise Exception("Create directory {} failed".format(dir_name))

                


#create Files
if os.path.exists(DIRECTORY):
        for path, subdirs, files in os.walk(DIRECTORY):
            for file in files:
                notebook_full_path = os.path.join(path.split(DATABRICKS_NOTEBOOKS_DIRECTORY)[-1], file)
                notebook_name = notebook_full_path.split(TYPE_OF_FILE)[0]
                #if notebook_name[0] == "":
                notebook_name = notebook_name[1:]
                # Get Absolute path to import in Databricks Notebook
                notebook_abs_path = os.path.join(NOTEBOOK_DIRECTORY,notebook_name).replace('\\','/')
                #print("printing notebook 0",notebook_name[0],notebook_name[1:])
                print("printint nbote booke abs path",notebook_abs_path)
                # Get Absolute path of python file
                abs_path_file = os.path.join(path,file)
                #print("sending the notebookPath and abs Path",notebook_abs_path,abs_path_file)
                response = import_to_databricks(notebook_abs_path,abs_path_file) 

                #print("the absolute Path",abs_path_file)
                #print("the absolute Path on Server",notebook_abs_path)
else:
    raise Exception("Cannot find directory: {}".format(DIRECTORY))
