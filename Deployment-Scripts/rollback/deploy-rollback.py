from sre_constants import BRANCH
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
notebook_path = str(sys.argv[4])
branchname = str(sys.argv[5])

print(branchname)
print(repo_path)
print(repo_url)
print(notebook_path)


repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)


repo.git.checkout(branchname)
commits_list = list(repo.iter_commits())
commitidfromtag = repo.commit(inputtag)

print(commits_list)

#print ("last commit: ", commits_list[-1])
#print ("rollback selected commit: ", commitidfromtag)


changed_files = []
notebook_change_file = []

for x in commits_list[0].diff(commitidfromtag):
    if x.a_blob.path not in changed_files:
        changed_files.append(x.a_blob.path)
        
    if x.b_blob is not None and x.b_blob.path not in changed_files:
        changed_files.append(x.b_blob.path)

print (changed_files)


for i in range(len(changed_files)):
        #matching tag
        #print(taglist[i])
        path = str(changed_files[i])
        if path.startswith(notebook_path):
            print("Hello this is path match")
            print (path)
            break

#for info in changed_files:
#        if info.startswith(notebook_path):
#            print("in specified folder")
#            print(info)
#            notebook_change_file.append(info)


#print(notebook_change_file)
