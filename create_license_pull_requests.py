import json
import requests
import datetime
import base64
import sys
import time


def pullRequestExists(pull_request_info,title):
    for pull_request in pull_request_info:
        pull_request_title = pull_request['title']
        if pull_request_title == title:
            return True
    return False



#Variables passed in by the user
#Insure the user entered all 3
if sys.argv.__len__() < 4:
    print("Please be sure to add all the following parameters in order: organization, username, password")
    sys.exit()
ORGANIZATION = sys.argv[1]
USERNAME = sys.argv[2]
PASSWORD = sys.argv[3]

#Determine the current year for the license
YEAR = datetime.datetime.now().year;


#variables that aren't unique to each repository
github_url = 'https://api.github.com/'
repos_url = '{}orgs/{}/repos'.format(github_url, ORGANIZATION)
add_license_branch = 'add-license-branch'
add_license_branch_ref = "refs/heads/{}".format(add_license_branch)
pull_request_title = "Add a MIT License"
pull_request_body = None
pull_request_base = 'master'
license_file_path = 'license_template.txt'
pull_request_body_path = 'pull_request_body.txt'
license_file_content = None

#Get pull request body from text file
with open(pull_request_body_path, 'r') as file:
    pull_request_body = file.read()


# Read in the license template file
with open(license_file_path, 'r') as file:
    filedata = file.read()

#If the files weren't read in properly, the code will fail
if not pull_request_body or not license_file_content:
    print("Necessary text files are missing, and the request cannot be implemented")
    sys.exit()

# Customize the copyright information
filedata = filedata.replace('@year@', str(YEAR))
license_file_content = filedata.replace('@organization@',ORGANIZATION)
#Github API requires file content to be base64 encoded
license_file_content_base64 = base64.b64encode(bytes(license_file_content, 'utf-8')).decode('ascii')



#Create a session and authorize
my_session = requests.Session()
my_session.auth = (USERNAME,PASSWORD)

#Get a list of all private and public repositories in the given organization
timeout_count = 0;
authenticated = False
repos = None

#Lets the user reenter password and username if needed
while not authenticated:
    repos_request_response = my_session.get(repos_url)
    #Allow the user to re-enter username and password
    if repos_request_response.status_code == 200:
        authenticated = True
        repos = json.loads(repos_request_response.text)
    elif repos_request_response.status_code == 401:
        print("Authentication Failed. The Username and/or Password were incorrect. Enter 'Quit' to end program")
        USERNAME = input("Username: ")
        if USERNAME == 'Quit':
            sys.exit()
        PASSWORD = input('Github Password: ')
        my_session.auth = (USERNAME, PASSWORD)
    elif repos_request_response.status_code == 404:
        repos = json.loads(repos_request_response.text)
        print("The given organization wasn't found. Please enter it again. Enter 'Quit' to end program")
        ORGANIZATION = input("Organization: ")
        if ORGANIZATION == 'Quit':
            sys.exit()
        repos_url = '{}orgs/{}/repos'.format(github_url, ORGANIZATION)
    elif repos_request_response.status_code == 408:
        #Timeout error, I'll try a few times, but no more than 3, and each time I'll wait a little longer
        timeout_count += 1
        if timeout_count == 4:
            print("The request has timed out")
            sys.exit()
        time.sleep(timeout_count)
    else:
        print("Unknown error accessing organization")
        sys.exit()


for repo in repos:
    repo_name = repo['name']
    repo_full_name = repo['full_name'];
    curr_license = repo['license']
    #If the repo has a license, no action is taken
    if not curr_license:

        #If the pull request already exists, I don't need to do anything
        check_pull_request_url = '{}repos/{}/pulls'.format(github_url,repo_full_name)
        check_pull_request_response = my_session.get(check_pull_request_url)
        check_pull_request_text = json.loads(check_pull_request_response.text)
        if check_pull_request_response.status_code != 200:
            print("There was an error checking pull request status in repo {}. Message: {}".format(repo_full_name,check_pull_request_text['message']))
            continue
        if pullRequestExists(check_pull_request_text,pull_request_title):
            print("Repo {} already has a pull request to create a license".format(repo_name))
            continue

        #I need a ref to the master branch to create a new branch
        get_master_branch_sha_url = '{}repos/{}/branches/master'.format(github_url,repo_full_name)
        master_branch_response = my_session.get(get_master_branch_sha_url)
        master_branch = json.loads(master_branch_response.text)
        if master_branch_response.status_code != 200:
            if master_branch_response.status_code == 404:
                print("The repository {} doesn't have a master branch".format(repo_name))
            elif master_branch_response.status_code == 408:
                print("A request has timed out for repo {}".format(repo_name))
            elif master_branch_response.status_code == 401:
                print("The Authentication has failed for repo {}".format(repo_name))
            else:
                print("Unknown Error on repo {}. Message: {}".format(repo_name,branch_result['message']))
            continue
        master_sha = master_branch['commit']['sha']

        #Create a new branch that will add the license
        create_branch_url = '{}repos/{}/git/refs'.format(github_url,repo_full_name)
        branch_result_content = my_session.post(create_branch_url,json={"ref":add_license_branch_ref,"sha":master_sha})
        branch_result = json.loads(branch_result_content.text)
        #If the branch already exists that's ok
        if branch_result_content.status_code != 200 and branch_result['message'] != 'Reference already exists':
            print("There was an error with repo {}. Message:{}".format(repo_name,branch_result['message']))


        # Add license_template.txt file to new branch and commit
        has_license_file_url = '{}repos/{}/contents/{}'.format(github_url, repo_full_name,"LICENSE.txt")
        has_license_response = my_session.get(has_license_file_url, params={"ref":add_license_branch})
        has_license_text = json.loads(has_license_response.text)

        #I don't need to add the file if it's already there
        if has_license_response.status_code != 200:
            add_license_file_url = '{}repos/{}/contents/{}'.format(github_url, repo_full_name, license_file_path)
            add_file_data = {
            "message": "Adding a MIT License File",
            "content": license_file_content_base64,
            "branch": add_license_branch
            }
            add_license_result_status = my_session.put(add_license_file_url,json=add_file_data)
            add_license_result = json.loads(add_license_result_status.text)
            if add_license_result_status != 200:
                print("There was an error adding the License file to repo{}. Message:{}".format(repo_name,add_license_result['message']))

        #Create a pull request to merge the new branch with master
        create_pull_request_url = github_url + 'repos/' + repo_full_name + "/pulls"
        pull_request_result = my_session.post(create_pull_request_url,json={'title':pull_request_title, "body":pull_request_body, "head":add_license_branch,"base":pull_request_base})
        pull_request_result_text = json.loads(pull_request_result.text)
        if pull_request_result.status_code >= 400:
            print("There was an error creating the pull request for repo{}. Message:{}".format(repo_name,pull_request_result_text['message']))
        else:
            print("A pull request has successfully been added to repo {}".format(repo_name))

    else:
        print("Repo {} already has a license".format(repo_name))



