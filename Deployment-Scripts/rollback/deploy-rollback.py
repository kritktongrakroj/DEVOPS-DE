import git
import sys
import os
from os.path import isfile, join
from os import listdir
import base64

############################


path = str(sys.argv[1])
print(path)
repo = git.Repo()
print(repo)

# the below gives us all commits
repo.commits()

# take the first and last commit

a_commit = repo.commits()[0]
b_commit = repo.commits()[1]

# now get the diff
difrepo = repo.diff(a_commit,b_commit)
print(difrepo)
