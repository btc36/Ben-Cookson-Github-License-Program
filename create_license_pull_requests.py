import json
import requests
import datetime
import base64

USERNAME = "btc36"
PASSWORD = "B3nS0l0R3igns!!"

ORGANIZATION = "ben-c-test-organization"
YEAR = datetime.datetime.now().year;


github_url = 'https://api.github.com/'
repos_url = '{}orgs/{}/repos'.format(github_url, ORGANIZATION)
add_license_branch = 'add-license-branch'
add_license_branch_ref = "refs/heads/{}".format(add_license_branch)
pull_request_title = "Add a MIT License"
pull_request_body = ''
pull_request_base = 'master'
license_file_path = 'LICENSE.txt'
pull_request_body_path = 'PullRequestBody.txt'
license_file_content = ''


with open(pull_request_body_path, 'r') as file:
    pull_request_body = file.read()


# Read in the file
with open(license_file_path, 'r') as file:
    filedata = file.read()

# Replace the target string
filedata = filedata.replace('@year@', str(YEAR))
license_file_content = filedata.replace('@organization@',ORGANIZATION)
license_file_content_base64 = base64.b64encode(bytes(license_file_content, 'utf-8')).decode('ascii')




my_session = requests.Session()
my_session.auth = (USERNAME,PASSWORD)

repos = json.loads(my_session.get(repos_url).text)

for repo in repos:
    repo_name = repo['name']
    repo_full_name = repo['full_name'];
    curr_license = repo['license']
    print(repo)
    print(repo_full_name)
    print(curr_license)
    if not curr_license:
        get_master_branch_sha_url = '{}repos/{}/branches/master'.format(github_url,repo_full_name)
        master_branch = json.loads(my_session.get(get_master_branch_sha_url).text)
        master_sha = master_branch['commit']['sha']

        create_branch_url = '{}repos/{}/git/refs'.format(github_url,repo_full_name)

        branchResult =json.loads(my_session.post(create_branch_url,json={"ref":add_license_branch_ref,"sha":master_sha}).text)

        # Add LICENSE.txt file to new branch and commit
        add_license_file_url = '{}repos/{}/contents/{}'.format(github_url,repo_full_name,license_file_path)
        print(add_license_file_url)
        add_file_data = {
           "message": "Adding a MIT License File",
           "content": license_file_content_base64,
            "branch": add_license_branch
        }
        add_license_result = json.loads(my_session.put(add_license_file_url,json=add_file_data).text)
        print(add_license_result)


        create_pull_request_url = github_url + 'repos/' + repo_full_name + "/pulls"
        pull_request_result = json.loads(my_session.post(create_pull_request_url,json={'title':pull_request_title, "body":pull_request_body, "head":add_license_branch,"base":pull_request_base}).text)
        print(pull_request_result)
 
