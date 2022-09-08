import os
import fileinput
import sys

import_nb = str(sys.argv[1])
key_func = str(sys.argv[2])
key_class = str(sys.argv[3])
key = ["${function}","${class}"]
value = [key_func,key_class]

def update_configValue(rootfilepath, key, value):

    with fileinput.FileInput(rootfilepath, inplace=True) as file:
       	for line in file:
            print(line.replace(key, value.lower()), end='')
	
    newpathName=rootfilepath.replace(key,value)
    print("New Path Name",newpathName)
    if newpathName != rootfilepath:
        os.rename(rootfilepath,newpathName)  

for i in range(len(key)):
	for subdir, file in os.walk(import_nb):
		update_configValue(os.path.join(subdir, file), key[i], value[i])
