import git
import sys
import os
from os.path import isfile, join
from os import listdir
import base64

############################


repo_path = str(sys.argv[1])
repo_url = str(sys.argv[2])

print(repo_path)
print(repo_url)
repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)

commits_list = list(repo.iter_commits())

print(commits_list)
print ("last commit: ", commits_list[-1])
print ("prevois commit: ", commits_list[-2])

changed_files = []

for x in commits_list[-1].diff(commits_list[-2]):
    if x.a_blob.path not in changed_files:
        changed_files.append(x.a_blob.path)
        
    if x.b_blob is not None and x.b_blob.path not in changed_files:
        changed_files.append(x.b_blob.path)
        
print (changed_files)

# the below gives us all commits
#repo.commits()

# take the first and last commit

#a_commit = repo.commits()[0]
#b_commit = repo.commits()[1]

# now get the diff
#difrepo = repo.diff(a_commit,b_commit)
#print(difrepo)
