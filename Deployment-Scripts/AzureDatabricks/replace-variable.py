import os
import fileinput
import sys

import_nb = str(sys.argv[1])
key_func = str(sys.argv[2])
key_class = str(sys.argv[3])
key = []
value = []
key[0] = "${function}"
value[0] = key_func
key[1] = "${class}"
value[1] = key_class


def update_configValue(rootfilepath):

    with fileinput.FileInput(rootfilepath, inplace=True) as file:
       	for line in file:
            print(line.replace(key[i], value[i].lower()), end='')

for i in range(len(key)):
	for subdir, file in os.walk(import_nb):
		update_configValue(os.path.join(subdir, file))
