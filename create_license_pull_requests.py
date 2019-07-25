import json
import requests
import datetime
import base64

#Variables passed in by the user
USERNAME = "btc36"
PASSWORD = "B3nS0l0R3igns!!"

ORGANIZATION = "ben-c-test-organization"
#Determine the current year for the license
YEAR = datetime.datetime.now().year;


#variables that aren't unique to each repository
github_url = 'https://api.github.com/'
repos_url = '{}orgs/{}/repos'.format(github_url, ORGANIZATION)
add_license_branch = 'add-license-branch'
add_license_branch_ref = "refs/heads/{}".format(add_license_branch)
pull_request_title = "Add a MIT License"
pull_request_body = ''
pull_request_base = 'master'
license_file_path = 'license_template.txt'
pull_request_body_path = 'pull_request_body.txt'
license_file_content = ''

#Get pull request body from text file
with open(pull_request_body_path, 'r') as file:
    pull_request_body = file.read()


# Read in the license template file
with open(license_file_path, 'r') as file:
    filedata = file.read()

# Customize the copyright information
filedata = filedata.replace('@year@', str(YEAR))
license_file_content = filedata.replace('@organization@',ORGANIZATION)
#Github API requires file content to be base64 encoded
license_file_content_base64 = base64.b64encode(bytes(license_file_content, 'utf-8')).decode('ascii')



#Create a session and authorize
my_session = requests.Session()
my_session.auth = (USERNAME,PASSWORD)

#Get a list of all private and public repositories in the given organization
repos = json.loads(my_session.get(repos_url).text)

for repo in repos:
    repo_name = repo['name']
    repo_full_name = repo['full_name'];
    curr_license = repo['license']
    #If the repo has a license, no action is taken
    if not curr_license:
        #I need a ref to the master branch to create a new branch
        get_master_branch_sha_url = '{}repos/{}/branches/master'.format(github_url,repo_full_name)
        master_branch = json.loads(my_session.get(get_master_branch_sha_url).text)
        master_sha = master_branch['commit']['sha']
        #Create a new branch that will add the license
        create_branch_url = '{}repos/{}/git/refs'.format(github_url,repo_full_name)
        branchResult =json.loads(my_session.post(create_branch_url,json={"ref":add_license_branch_ref,"sha":master_sha}).text)
        # Add LICENSE.txt file to new branch and commit
        add_license_file_url = '{}repos/{}/contents/{}'.format(github_url,repo_full_name,license_file_path)
        add_file_data = {
           "message": "Adding a MIT License File",
           "content": license_file_content_base64,
            "branch": add_license_branch
        }
        add_license_result = json.loads(my_session.put(add_license_file_url,json=add_file_data).text)
        #Create a pull request to merge the new branch with master
        create_pull_request_url = github_url + 'repos/' + repo_full_name + "/pulls"
        pull_request_result = json.loads(my_session.post(create_pull_request_url,json={'title':pull_request_title, "body":pull_request_body, "head":add_license_branch,"base":pull_request_base}).text)
        
 
