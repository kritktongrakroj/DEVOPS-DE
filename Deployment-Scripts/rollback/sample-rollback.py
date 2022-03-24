import os
import config
import utils
import git


def main():
    # Init Git repo
    git_changed = {}
    repo = git.Repo()
    current_commit_version = repo.commit(config.CURRENT_VERSION)
    new_commit_version = repo.commit(config.NEW_VERSION)

    # Compare change between current version and new version
    info_list = (repo.git.diff(current_commit_version, new_commit_version, **{'name-status': True})).split("\n")
    print(info_list)

    repo_directory = config.REPO_NOTEBOOKS_DIRECTORY

    for info in info_list:
        change_type, file_path = info.split("\t",1)
        #if file_path.startswith(('dp-bt', 'dp-rlt')):
        #env_config_path = f'{config.REPO_NOTEBOOKS_DIRECTORY}/fw/cmmn/config/environment_config' # Deploy every time
        if file_path.startswith(config.REPO_NOTEBOOKS_DIRECTORY):
            print(change_type, file_path)
            abs_changed_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), file_path)
            git_changed[abs_changed_file_path] = change_type

            # Get Absolute path to import in Databricks Notebook
            notebook_abs_path = utils.getNotebookAbsPath(file_path.split(repo_directory)[-1])
            if change_type == "D":
                # Delete file from workspace
                response = utils.delete_notebook(notebook_abs_path)
                print(response)

    if os.path.exists(config.DIRECTORY):
        for path, subdirs, files in os.walk(config.DIRECTORY):
            for file in files:
                notebook_full_path = os.path.join(path.split(repo_directory)[-1], file)
                notebook_abs_path = utils.getNotebookAbsPath(notebook_full_path)

                # Get Absolute path of file
                abs_path_file = os.path.join(path,file)

                # Get Language
                #print('[DEBUG] file', file)
                extension = file.split('.')[1]
                language = config.TYPES_OF_FILE[extension]
                #print('[DEBUG] extension', extension)

                if git_changed.get(abs_path_file) != None or notebook_abs_path.endswith("environment_config"): # Deploy every time
                    # Import Notebook                
                    print('import', notebook_abs_path, abs_path_file, language)
                    response = utils.import_to_databricks(notebook_abs_path,abs_path_file,language) 

                    print(response)
    else:
        raise Exception("Cannot find directory: {}".format(config.DIRECTORY))

if __name__ == "__main__":
    main()



import os
import config
import utils

def main():
    # Clear existing directory
    utils.delete_existing_notebook_directory()
    
    if os.path.exists(config.DIRECTORY):
        for path, subdirs, files in os.walk(config.DIRECTORY):
            for file in files:
                notebook_full_path = os.path.join(path.split(config.DATABRICKS_NOTEBOOKS_DIRECTORY)[-1], file)
                notebook_name = notebook_full_path.split(config.TYPE_OF_FILE)[0]
               
                if notebook_name[0] == "/":
                    notebook_name = notebook_name[1:]
                # Get Absolute path to import in Databricks Notebook
                notebook_abs_path = os.path.join(config.NOTEBOOK_DIRECTORY,notebook_name)

                # Get Absolute path of python file
                abs_path_file = os.path.join(path,file)
                
                response = utils.import_to_databricks(notebook_abs_path,abs_path_file) 

                print(response)
    else:
        raise Exception("Cannot find directory: {}".format(config.DIRECTORY))


if __name__== "__main__":
   main()