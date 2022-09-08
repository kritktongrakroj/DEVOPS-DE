from jproperties import Properties
import os
import fileinput
import sys

rootdir = str(sys.argv[1])
key_func = str(sys.argv[2])
key_class = str(sys.argv[3])
key = ["${function}","${class}"]
value = [key_func,key_class]


import os
import fileinput
import sys
configs = Properties()

prop_path= str(sys.argv[1])
rootdir= str(sys.argv[2])

#prop_path=r"/home/runner/work/dataengineering-devops/dataengineering-devops/DataFactory/npr-app-config.properties"
#rootdir = r'/home/runner/work/dataengineering-devops/dataengineering-devops/DataFactory/'

def update_configValue(rootfilepath,key,value):

    with fileinput.FileInput(rootfilepath, inplace=True) as file:
        for line in file:
            if "job_nm" in line:
                print(line.replace(key, value.lower()), end='')
            else:
                print(line.replace(key, value), end='')
    
    newpathName=rootfilepath.replace(key,value)
    print("New Path Name",newpathName)
    if newpathName != rootfilepath:
        os.rename(rootfilepath,newpathName)  
        
def update_Parameter(rootpath,key,value):

    for subdir, dirs, files in os.walk(rootpath):
        for file in files:
            print(os.path.join(subdir, file))
            update_configValue(os.path.join(subdir, file),key,value)

with open(prop_path, 'rb') as config_file:
    configs.load(config_file)
 
items_view = configs.items()
list_keys = []
 
for i in range(len(key)):
    print("the Key is",key[i])
    print("The Key Value is",value[i])
    update_Parameter(rootdir,key[i],value[i])
	
