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

repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)
print(repo.commit(inputtag))
branch = repo.git.checkout(branchname)

commits_list = list(repo.iter_commits())


###########################################

def find_tag():
    taglist = repo.tags

    for i in range(len(taglist)):

        tagref = str(taglist[i])
        if inputtag == tagref:

            return taglist[i].commit
            break

commitidfromtag = find_tag()
print("Commit id from tag is :", commitidfromtag)

#########################################
    
print(commits_list)
print ("last commit: ", commits_list[-1])
print ("rollback selected commit: ", commitidfromtag)


changed_files = set()
notebook_change_file = []

print(commits_list[0].diff(commits_list[-1]))

for x in commits_list[0].diff(commits_list[-1]):
    if x.a_blob.path:
        changed_files.add(x.a_blob.path)
        
    if x.b_blob.path:
        changed_files.add(x.b_blob.path)
        
print(changed_files)

for info in changed_files:
        if info.startswith(notebook_path):
            print("in specified folder")
            print(info)
            notebook_change_file.append(info)


print(notebook_change_file)
