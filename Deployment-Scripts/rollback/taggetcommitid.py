import git
import sys
import os
from os.path import isfile, join
from os import listdir
import base64

############################


inputtag = str(sys.argv[1])
repo_url = str(sys.argv[2])
repo_path = str(sys.argv[3])

#repo = git.Repo()
# need new clone for tracking all of tags and commit changes 
repo = git.Repo.clone_from(repo_url, repo_path)
#print(repo)


def find_tag():
    #print("Our input tag name",inputtag)
    taglist = repo.tags
    print(taglist)

    for i in range(len(taglist)):
        #matching tag
        #print(taglist[i])
        tagref = str(taglist[i])
        if inputtag == tagref:
            #print("OK, tag match")
            #print("Commit id related to tag ",taglist[i].commit)
            return taglist[i].commit
            break
# send back commit id
commitidfromtag = find_tag()
print (commitidfromtag)