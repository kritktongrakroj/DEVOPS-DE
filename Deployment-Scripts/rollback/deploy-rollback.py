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
print ("First commit: ", commits_list[0])


# the below gives us all commits
#repo.commits()

# take the first and last commit

#a_commit = repo.commits()[0]
#b_commit = repo.commits()[1]

# now get the diff
#difrepo = repo.diff(a_commit,b_commit)
#print(difrepo)
