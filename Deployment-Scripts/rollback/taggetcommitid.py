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

print(repo_path)
print(repo_url)
repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)



def find_tag():
    print(inputtag)
    taglist = repo.tags
    print(taglist)

    for tag in taglist:
        # to match taginput and existing tag
        #
        if inputtag in tag:
            print("tag match")
            return tag
        else:
            print("not interest")
            return tag

x = find_tag()
print (x)