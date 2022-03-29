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
print(inputtag)

#get repo
repo = git.Repo.clone_from(repo_url, repo_path)
print(repo)

# Get all commit list
#commits_list = list(repo.iter_commits())

repo.git.checkout(branchname)

# get commit id from tag
commitidfromtag = repo.commit(inputtag)



tagslist = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
print(tagslist)

# find the position of input tag list to find the previous tags
def find_tag_position(tag):
    for i in range(len(tagslist)):
        tagref = str(tagslist[i])
        if tagref == tag:
            return i

tag_position = find_tag_position(inputtag)
print(tag_position)
print("this tag is :", str(tagslist[tag_position]), "and its previous tag is :", str(tagslist[tag_position - 1]))


#set previos commit id
previouscommit = str(tagslist[tag_position - 1])
latestcommit = repo.commit(previouscommit)
print(latestcommit)
print(commitidfromtag)


#print diff file
#print(latestcommit.diff(commitidfromtag))

diffs = {
    diff.a_path: diff for diff in latestcommit.diff(commitidfromtag)
}
   
changed_files = []
changed_type_list = []

for x in latestcommit.diff(commitidfromtag):
    if x.a_path not in changed_files:
        changed_files.append(x.a_path)
        changed_type_list.append(x.change_type)
            
    if x.b_path is not None and x.b_path not in changed_files:
        changed_files.append(x.b_path)
        changed_type_list.append(x.change_type)

to_add = []
to_replace = []
            

for i in range(len(changed_files)):
    if changed_files[i].startswith(notebook_path):
        if changed_type_list[i] == 'A':
            to_add.append(changed_type_list[i])
        else:
            to_replace.append(changed_type_list[i])








"""
    diffs = {
        diff.a_path: diff for diff in latestcommit.diff(commitidfromtag)
    }


    for objpath, stats in commitidfromtag.stats.files.items():

                # Select the diff for the path in the stats
                diff = diffs.get(objpath)
                print("this is change from commit last",diff)

                # If the path is not in the dictionary, it's because it was
                # renamed, so search through the b_paths for the current name.
                if not diff:
                    for diff in diffs.values():
                        if diff.b_path == repo_path and diff.renamed:
                            print("this is chnage on rename",diff)
                            break
            



    lastcommit = repo.head.commit
"""




        











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
