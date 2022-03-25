import git
import sys
import os
from os.path import isfile, join
from os import listdir
import base64

############################


repo_path = str(sys.argv[1])
repo_url = str(sys.argv[2])
inputtag = str(sys.argv[3])

repo = git.Repo()

def find_tag():
    print(inputtag)
    taglist = repo.tags
    print(taglist)

    for tag in taglist:
        # to match taginput and existing tag
        #
        if inputtag in tag:
            print("tag match")
            print(tag)
        else:
            print("not interest")
            print(tag)

find_tag()
