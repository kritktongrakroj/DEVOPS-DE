from jproperties import Properties
import os
import fileinput
import sys

import_nb = str(sys.argv[1])
key = []
value = []
key[0] = "${function}"
value[0] = str(sys.argv[2])
key[1] = "${class}"
value[0] = str(sys.argv[3])


def update_configValue(rootfilepath):

    with fileinput.FileInput(rootfilepath, inplace=True) as file:
       	for line in file:
            print(line.replace(key[i], value[i].lower()), end='')

for i in range(len(key)):
	for subdir, files in os.walk(import_nb):
		update_configValue()
