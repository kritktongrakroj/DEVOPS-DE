import git
import sys
import os
from os.path import isfile, join
from os import listdir
import base64

############################


repo_path = str(sys.argv[1])
repo_url = str(sys.argv[2])
commitid = str(sys.argv[3])
inputtag = str(sys.argv[4])

print(repo_path)
print(repo_url)
repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)

commits_list = list(repo.iter_commits())





print(commits_list)
print ("last commit: ", commits_list[0])
print ("selected commit: ", commitid)

changed_files_firstcommit = []
changed_files_lastcommit = []

changed_files = []
print(commits_list[0].diff(commits_list[-1]))

for x in commits_list[0].diff(commits_list[-1]):
    if x.a_blob.path not in changed_files:
        changed_files.append(x.a_blob.path)
        
    if x.b_blob is not None and x.b_blob.path not in changed_files:
        changed_files.append(x.b_blob.path)
        
print (changed_files_firstcommit)
print (changed_files_lastcommit)
print(changed_files)

for info in changed_files:
        #if file_path.startswith(('dp-bt', 'dp-rlt')):
        #env_config_path = f'{config.REPO_NOTEBOOKS_DIRECTORY}/fw/cmmn/config/environment_config' # Deploy every time
        if info.startswith(repo_path):
            print("in specified folder")
            print(info)
        else:
            print("not interest")
            print(info)

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