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


# checkout to branch
repo.git.checkout(branchname)

# Get all commit list
commits_list = list(repo.iter_commits())

# get commit id from tag
commitidfromtag = repo.commit(inputtag)
print("this is commit from tag :",commitidfromtag)

#find mapping sequence of commit id
def find_seq():

    for i in range(len(commits_list)):
        #matching tag
        #print(taglist[i])
        eachcommit = str(commits_list[i])
        if commitidfromtag == eachcommit:
            print("OK, get seq", i)

            return i
            break
# send back commit id

seq = find_seq()

# show all commit list in branch
print(commits_list)

#print ("last commit: ", commits_list[-1])
#print ("rollback selected commit: ", commitidfromtag)




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
