import os
import fileinput
import sys

key = []
value = []
import_nb = str(sys.argv[1])
value[0] = str(sys.argv[2])
value[0] = str(sys.argv[3])
key[0] = "${function}"
key[1] = "${class}"


def update_configValue(rootfilepath):

    with fileinput.FileInput(rootfilepath, inplace=True) as file:
       	for line in file:
            print(line.replace(key[i], value[i].lower()), end='')

for i in range(len(key)):
	for subdir, file in os.walk(import_nb):
		update_configValue(os.path.join(subdir, file))
