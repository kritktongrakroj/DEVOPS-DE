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

#get repo
repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)

# Get all commit list
#commits_list = list(repo.iter_commits())

repo.git.checkout(branchname)

# get commit id from tag
commitidfromtag = repo.commit(inputtag)
lastcommit = repo.head.commit
print("this is commit from tag :",commitidfromtag)
print("this is last commit: ", lastcommit)



allcommit = repo.iter_commits(branchname)


for commit in repo.iter_commits(branchname):
    print(commit)

    #diff from the tag
    diffs  = {
            diff.a_path: diff for diff in commit.diff(commitidfromtag)
            }
    for objpath, stats in commit.stats.files.items():
        diff = diffs.get(objpath)

        if commit == lastcommit:
            if not diff:
                for diff in diffs.values():
                    if diff.b_path == repo_path and diff.renamed:
                        print(diff.b_path)
                        break





        











#for i in range(len(changed_files)):
        #matching tag
        #print(taglist[i])
        #path = str(changed_files[i])
        #if path.startswith(notebook_path):
            #print("Hello this is path match")
            #print (path)
            #break

#for info in changed_files:
#        if info.startswith(notebook_path):
#            print("in specified folder")
#            print(info)
#            notebook_change_file.append(info)


#print(notebook_change_file)
